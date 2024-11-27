import os
import cv2
import numpy as np
import torch
import subprocess
import uuid
from io import BytesIO 
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
from yoloworld.efficientvit.models.efficientvit.sam import EfficientViTSamPredictor #yoloworld\efficientvit\models\efficientvit
from yoloworld.efficientvit.sam_model_zoo import create_sam_model
import supervision as sv
import requests
from PIL import Image, ImageOps
from background_image_remover_python.model import U2NET
from skimage import transform
from inference.models.yolo_world import YOLOWorld
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# URLs and file names for the EfficientViT SAM model
EFFICIENTVIT_SAM_URL = "https://huggingface.co/han-cai/efficientvit-sam/resolve/main"
EFFICIENTVIT_SAM_MODEL = "xl1.pt"

# Directories for video uploads and outputs
UPLOAD_DIR = 'uploads'
OUTPUT_DIR = 'output'

# Ensure the upload/output directories exist
class DirectoryManager:
    def __init__(self, upload_dir, output_dir):
        self.upload_dir = upload_dir
        self.output_dir = output_dir
        self.ensure_directories()

    def ensure_directories(self):
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

# Function to download model weights if not already present
def download_model(url, filename):
    if not os.path.exists(filename):
        print(f"Downloading {filename}...")
        response = requests.get(f"{url}/{filename}", stream=True)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"{filename} downloaded successfully.")
        else:
            print(f"Failed to download {filename}.")
    else:
        print(f"{filename} already exists.")

# Ensure model weights are available
download_model(EFFICIENTVIT_SAM_URL, EFFICIENTVIT_SAM_MODEL)

# Load EfficientViT SAM model
device = "cuda" if torch.cuda.is_available() else "cpu"
sam = EfficientViTSamPredictor(
    create_sam_model(name="xl1", weight_url=EFFICIENTVIT_SAM_MODEL).to(device).eval()
)

# Load YOLOWorld model
yolo_world = YOLOWorld(model_id="yolo_world/x")

# Load U2NET model for segmentation
def load_u2net_model():
    cwd = os.getcwd()
    file_id = '1ElPxUoPkqbiQA45zhLszn_8h72ivJo-Y'
    model_dir = os.path.join(cwd, 'background_image_remover_python', 'saved_models', 'u2net', file_id)
    net = U2NET(3, 1)
    if torch.cuda.is_available():
        net.load_state_dict(torch.load(model_dir))
        net.cuda()
    else:
        net.load_state_dict(torch.load(model_dir, map_location='cpu'))
    return net

u2net_model = load_u2net_model()

# Helper for unique filenames for video
def generate_unique_filename(filename):
    extension = os.path.splitext(filename)[1]  
    unique_filename = f"{uuid.uuid4()}{extension}"
    return unique_filename

# Video Processing Logic
def construct_command(video_filename, text_input):
    command = [
        'cmd.exe', '/C', 'cd .. && '
        'C:/Users/anshi/Desktop/DMLS_PRoj/.venv/Scripts/activate.bat && '
        'cd backend && '
        f'python NeurIPS2023_SOC/demo_video.py '
        '-c NeurIPS2023_SOC/configs/refer_youtube_vos.yaml '
        '-rm test '
        '--backbone video-swin-b '
        '-bpp NeurIPS2023_SOC/pretrained/pretrained_swin_transformer/swin_base_patch244_window877_kinetics400_22k.pth '
        '-ckpt NeurIPS2023_SOC/pretrained_weights/joint_tiny.tar '
        f'--video_dir {os.path.join(UPLOAD_DIR, video_filename)} '
        '--device cpu '
        f'--text "{text_input}"'
    ]
    return command

def process_video_with_script(video_filename, text_input):
    command = construct_command(video_filename, text_input)
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        output_video_dir = os.path.join(OUTPUT_DIR, video_filename.split('.')[0])
        return output_video_dir
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error occurred: {e.stderr}")

@app.route('/process_video', methods=['POST'])
def process_video():
    try:
        video_file = request.files['video']
        text_input = request.form['text']

        unique_video_filename = generate_unique_filename(video_file.filename)
        video_filepath = os.path.join(UPLOAD_DIR, unique_video_filename)
        video_file.save(video_filepath)

        output_video_dir = process_video_with_script(unique_video_filename, text_input)
        output_video_file = os.path.join(output_video_dir, 'SOC', 'visual', '0.png')
        
        if not os.path.exists(output_video_file):
            return jsonify({"status": "error", "message": "Output video or frames not found"}), 500

        return send_file(output_video_file, as_attachment=True, mimetype='image/png')

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# # Image Segmentation Logic
@app.route('/segment', methods=['POST'])
def segment_image():
    try:
        file = request.files['image']
        background_color = request.form.get('backgroundColor', 'transparent')
        img = Image.open(file).convert("RGBA")  
        img = np.array(img)

        img_shape = img.shape
        initial_img = img[..., :3] 
        img_resized = transform.resize(initial_img, (320, 320), mode='constant')
        tmpImg = np.zeros((img_resized.shape[0], img_resized.shape[1], 3))
        
        tmpImg[:, :, 0] = (img_resized[:, :, 0] - 0.485) / 0.229
        tmpImg[:, :, 1] = (img_resized[:, :, 1] - 0.456) / 0.224
        tmpImg[:, :, 2] = (img_resized[:, :, 2] - 0.406) / 0.225
        tmpImg = tmpImg.transpose((2, 0, 1))
        tmpImg = np.expand_dims(tmpImg, 0)
        image = torch.from_numpy(tmpImg).type(torch.FloatTensor)
        
        with torch.no_grad():
            d1, *_ = u2net_model(image)
            pred = d1[:, 0, :, :]
            pred = (pred - pred.min()) / (pred.max() - pred.min())
            pred = pred.squeeze().cpu().numpy()
        mask = Image.fromarray((pred * 255).astype(np.uint8)).convert('L')
        mask = mask.resize((img_shape[1], img_shape[0]))
        mask_np = np.array(mask) / 255  
        result_img = initial_img * np.expand_dims(mask_np, axis=2)
        
        if background_color == 'transparent':
            transparent_img = np.dstack((result_img, mask_np * 255))
            result = Image.fromarray(transparent_img.astype(np.uint8), 'RGBA')
        else:
            r, g, b = tuple(int(background_color[i:i+2], 16) for i in (1, 3, 5))
            background = np.ones_like(initial_img) * np.array([r, g, b])
            blended_img = result_img + (1 - np.expand_dims(mask_np, axis=2)) * background
            result = Image.fromarray(blended_img.astype(np.uint8), 'RGB') 
        
        result_path = os.path.join(OUTPUT_DIR, 'segmented_image.png')
        result.save(result_path)

        return send_file(result_path, mimetype='image/png')

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

BOUNDING_BOX_ANNOTATOR = sv.BoxAnnotator()
MASK_ANNOTATOR = sv.MaskAnnotator()
LABEL_ANNOTATOR = sv.LabelAnnotator()

def detect(image: np.ndarray, query: str, confidence_threshold: float, nms_threshold: float) -> np.ndarray:
    categories = [category.strip() for category in query.split(",") if category.strip()]
    yolo_world.set_classes(categories)

    results = yolo_world.infer(image, confidence=confidence_threshold)
    detections = sv.Detections.from_inference(results).with_nms(class_agnostic=True, threshold=nms_threshold)

    sam.set_image(image, image_format="RGB")
    masks = []
    for xyxy in detections.xyxy:
        mask, _, _ = sam.predict(box=xyxy, multimask_output=False)
        masks.append(mask.squeeze())
    
    if not masks:
        return cv2.GaussianBlur(image, (51, 51), 0)

    detections.mask = np.array(masks)

    blurred_image = cv2.GaussianBlur(image, (51, 51), 0)

    combined_mask = np.zeros_like(image, dtype=np.uint8)

    stacked_mask = None

    for mask in masks:
        stacked_mask = np.stack([mask] * 3, axis=-1)  
        combined_mask[stacked_mask > 0] = image[stacked_mask > 0]

    if stacked_mask is not None:
        output_image = np.where(stacked_mask > 0, combined_mask, blurred_image)
    else:
        output_image = blurred_image

    return output_image


# def detect(image: np.ndarray, query: str, confidence_threshold: float, nms_threshold: float) -> np.ndarray:
#     # Get the categories from the query
#     categories = [category.strip() for category in query.split(",") if category.strip()]
#     yolo_world.set_classes(categories)

#     # Perform detection with YOLO
#     results = yolo_world.infer(image, confidence=confidence_threshold)
#     detections = sv.Detections.from_inference(results).with_nms(class_agnostic=True, threshold=nms_threshold)

#     # Set the image for SAM
#     sam.set_image(image, image_format="RGB")
#     masks = []
#     for xyxy in detections.xyxy:
#         mask, _, _ = sam.predict(box=xyxy, multimask_output=False)
#         masks.append(mask.squeeze())
#     detections.mask = np.array(masks)

#     # Prepare a blurred version of the image
#     blurred_image = cv2.GaussianBlur(image, (21, 21), 0)

#     # Prepare a blank mask for combining
#     combined_mask = np.zeros_like(image, dtype=np.uint8)

#     # Iterate over each mask to keep the segmented objects sharp
#     for mask in masks:
#         # Stack the mask to match the number of color channels (RGB)
#         stacked_mask = np.stack([mask] * 3, axis=-1)  # Convert from (H, W) to (H, W, 3)
#         # Apply mask to the sharp (original) image
#         combined_mask[stacked_mask > 0] = image[stacked_mask > 0]

#     # Create the final output: sharp objects with a blurred background
#     output_image = np.where(combined_mask > 0, combined_mask, blurred_image)

#     return output_image

@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    query = request.form.get('query', '')
    confidence_threshold = float(request.form.get('confidence_threshold', 0.3))
    nms_threshold = float(request.form.get('nms_threshold', 0.5))

    img = Image.open(file)
    img = np.array(img)

    processed_image = detect(img, query, confidence_threshold, nms_threshold)
    result_path = os.path.join(OUTPUT_DIR, 'detected_image.png')
    cv2.imwrite(result_path, processed_image)

    return send_file(result_path, mimetype='image/png')

@app.route('/custombgd', methods=['POST'])
def custome_bgd():
    try:
        foreground_file = request.files['foreground_image']
        background_file = request.files.get('background_image')
        background_color = request.form.get('backgroundColor', 'transparent')
        fg_img = Image.open(foreground_file).convert("RGBA")
        fg_np = np.array(fg_img)
        img_shape = fg_np.shape
        initial_img = fg_np[..., :3]

        img_resized = transform.resize(initial_img, (320, 320), mode='constant')
        tmpImg = np.zeros((img_resized.shape[0], img_resized.shape[1], 3))
        tmpImg[:, :, 0] = (img_resized[:, :, 0] - 0.485) / 0.229
        tmpImg[:, :, 1] = (img_resized[:, :, 1] - 0.456) / 0.224
        tmpImg[:, :, 2] = (img_resized[:, :, 2] - 0.406) / 0.225
        tmpImg = tmpImg.transpose((2, 0, 1))
        tmpImg = np.expand_dims(tmpImg, 0)

        image = torch.from_numpy(tmpImg).type(torch.FloatTensor)
        with torch.no_grad():
            d1, *_ = u2net_model(image)
            pred = d1[:, 0, :, :]
            pred = (pred - pred.min()) / (pred.max() - pred.min())
            pred = pred.squeeze().cpu().numpy()
            
        mask = Image.fromarray((pred * 255).astype(np.uint8)).convert('L')
        mask = mask.resize((img_shape[1], img_shape[0]))
        mask_np = np.array(mask) / 255  
        result_img = initial_img * np.expand_dims(mask_np, axis=2)
        if background_file:
            bg_img = Image.open(background_file).resize(fg_img.size).convert("RGB")
            bg_np = np.array(bg_img)
            blended_img = result_img + (1 - np.expand_dims(mask_np, axis=2)) * bg_np
            result = Image.fromarray(blended_img.astype(np.uint8), 'RGB')
        else:
            if background_color == 'transparent':
                transparent_img = np.dstack((result_img, mask_np * 255))
                result = Image.fromarray(transparent_img.astype(np.uint8), 'RGBA')
            else:
                r, g, b = tuple(int(background_color[i:i+2], 16) for i in (1, 3, 5))
                background = np.ones_like(initial_img) * np.array([r, g, b])
                blended_img = result_img + (1 - np.expand_dims(mask_np, axis=2)) * background
                result = Image.fromarray(blended_img.astype(np.uint8), 'RGB')

        result_path = os.path.join(OUTPUT_DIR, 'segmented_image.png')
        result.save(result_path)

        return send_file(result_path, mimetype='image/png')

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    DirectoryManager(UPLOAD_DIR, OUTPUT_DIR)
    # app.run(host='0.0.0.0', port=5000)
    app.run(debug=True, threaded=False)
