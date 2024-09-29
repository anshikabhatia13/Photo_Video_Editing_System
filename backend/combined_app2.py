import subprocess
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import torch
import numpy as np
import os
import uuid
from skimage import transform
from background_image_remover_python.model import U2NET

app = Flask(__name__)
CORS(app)

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

# Helper for unique filenames for video
def generate_unique_filename(filename):
    extension = os.path.splitext(filename)[1]  
    unique_filename = f"{uuid.uuid4()}{extension}"
    print(f"[DEBUG] Generated unique filename: {unique_filename}")
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
    print(f"[DEBUG] Constructed command: {' '.join(command)}")
    return command

def process_video_with_script(video_filename, text_input):
    command = construct_command(video_filename, text_input)
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"[DEBUG] Script output: {result.stdout}")
        output_video_dir = os.path.join(OUTPUT_DIR, video_filename.split('.')[0])
        print(f"[DEBUG] Output video directory: {output_video_dir}")
        return output_video_dir
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error in subprocess: {e.stderr}")
        raise Exception(f"Error occurred: {e.stderr}")

@app.route('/process_video', methods=['POST'])
def process_video():
    try:
        video_file = request.files['video']
        text_input = request.form['text']
        print(f"[DEBUG] Received video: {video_file.filename}, text: {text_input}")

        unique_video_filename = generate_unique_filename(video_file.filename)
        video_filepath = os.path.join(UPLOAD_DIR, unique_video_filename)
        video_file.save(video_filepath)
        print(f"[DEBUG] Video saved to: {video_filepath}")

        output_video_dir = process_video_with_script(unique_video_filename, text_input)
        output_video_file = os.path.join(output_video_dir, 'SOC', 'visual', '0.png')
        
        if not os.path.exists(output_video_file):
            print(f"[ERROR] Output video file not found: {output_video_file}")
            return jsonify({"status": "error", "message": "Output video or frames not found"}), 500

        return send_file(output_video_file, as_attachment=True, mimetype='image/png')

    except Exception as e:
        print(f"[ERROR] Exception occurred during video processing: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Image Segmentation Logic
def load_u2net_model():
    cwd = os.getcwd()
    file_id = '1ElPxUoPkqbiQA45zhLszn_8h72ivJo-Y'
    model_dir = os.path.join(cwd, 'background_image_remover_python', 'saved_models', 'u2net', file_id)
    print(f"[DEBUG] Loading U2NET model from: {model_dir}")
    net = U2NET(3, 1)
    if torch.cuda.is_available():
        net.load_state_dict(torch.load(model_dir))
        net.cuda()
    else:
        net.load_state_dict(torch.load(model_dir, map_location='cpu'))
    print("[DEBUG] U2NET model loaded successfully.")
    return net

u2net_model = load_u2net_model()

@app.route('/segment', methods=['POST'])
def segment_image():
    try:
        file = request.files['image']
        img = Image.open(file)
        img = np.array(img)
        print(f"[DEBUG] Received image with shape: {img.shape}")

        img_shape = img.shape
        initial_img = img.copy()

        # Resize and preprocess
        img = transform.resize(img, (320, 320), mode='constant')
        tmpImg = np.zeros((img.shape[0], img.shape[1], 3))
        tmpImg[:, :, 0] = (img[:, :, 0] - 0.485) / 0.229
        tmpImg[:, :, 1] = (img[:, :, 1] - 0.456) / 0.224
        tmpImg[:, :, 2] = (img[:, :, 2] - 0.406) / 0.225
        tmpImg = tmpImg.transpose((2, 0, 1))
        tmpImg = np.expand_dims(tmpImg, 0)
        image = torch.from_numpy(tmpImg).type(torch.FloatTensor)
        print(f"[DEBUG] Preprocessed image for U2NET")

        with torch.no_grad():
            d1, *_ = u2net_model(image)
            pred = d1[:, 0, :, :]
            pred = (pred - pred.min()) / (pred.max() - pred.min())
            pred = pred.squeeze().cpu().numpy()
        
        mask = Image.fromarray((pred * 255).astype(np.uint8)).convert('L')
        mask = mask.resize((img_shape[1], img_shape[0]))
        print("[DEBUG] Generated mask for image")

        mask_np = np.array(mask) / 255
        result_img = initial_img * np.expand_dims(mask_np, axis=2)
        result = Image.fromarray(result_img.astype(np.uint8))
        result_path = 'background_image_remover_python/results/segmented_image.png'
        result.save(result_path)
        print(f"[DEBUG] Segmented image saved to: {result_path}")
        
        return send_file(result_path, mimetype='image/png')

    except Exception as e:
        print(f"[ERROR] Exception occurred during image segmentation: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    dm = DirectoryManager(UPLOAD_DIR, OUTPUT_DIR)
    print("[DEBUG] Starting Flask server...")
    app.run(debug=True)
