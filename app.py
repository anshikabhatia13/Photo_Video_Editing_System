from flask import Flask, request, jsonify, send_file
import os
import torch
from ruamel.yaml import YAML
from torchvision.io import read_video
from PIL import Image
import shutil
import numpy as np
import torchvision.transforms.functional as Func
import torchvision.transforms as T
import torch.nn.functional as F
from NeurIPS2023_SOC.models import build_model
from NeurIPS2023_SOC.datasets.transforms import RandomResize
import NeurIPS2023_SOC.misc as utils
import cv2
import uuid
import argparse
####
from flask import Flask, render_template , url_for, request, jsonify
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")
####
size_transform = RandomResize(sizes=[360], max_size=640)
transform = T.Compose([
    T.ToTensor(),
    T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# vis_add_mask: This function overlays a segmentation mask onto the original image.
def vis_add_mask(img, mask, color):
    source_img = np.asarray(img).copy()
    origin_img = np.asarray(img).copy()
    color = np.array(color)

    mask = mask.reshape(mask.shape[0], mask.shape[1]).astype('uint8')
    mask = mask > 0.5

    origin_img[mask] = origin_img[mask] * 0.5 + color * 0.5
    origin_img = Image.fromarray(origin_img)
    source_img = Image.fromarray(source_img)
    mask = Image.fromarray(mask)
    return origin_img, source_img, mask

@app.route('/process_video', methods=['POST'])
def process_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video uploaded"}), 400
    if 'text' not in request.form:
        return jsonify({"error": "No text provided"}), 400

    # Get the uploaded video and the accompanying text
    video_file = request.files['video']
    text_input = request.form['text']
    
    # Save the uploaded video to a temporary location
    video_path = os.path.join('./uploads', video_file.filename)
    video_file.save(video_path)
    
    #########################Amitabh
    
    parser = argparse.ArgumentParser('DEMO script')
    parser.add_argument('--config_path', '-c',
                        default='./configs/refer_youtube_vos.yaml', help='path to configuration file')
    parser.add_argument('--running_mode', '-rm', choices=['train', 'test', 'pred', 'resume_train'],
                        default='test',
                        help="mode to run, either 'train' or 'eval'")
    parser.add_argument("--backbone", type=str, required=False,
                        help="the backbone name")
    parser.add_argument("--backbone_pretrained_path", "-bpp", type=str, required=False,
                        help="the backbone_pretrained_path")
    parser.add_argument('--checkpoint_path', '-ckpt', type=str, default='',
                        help='the finetune refytbs checkpoint_path')
    parser.add_argument("--video_dir", type=str, required=False)
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args()

    # Load your config file
    config['video_dir'] = video_path

    with open(args.config_path) as f:
        yaml = YAML(typ='safe', pure=True)
        config = yaml.load(f)
    config = {k: v['value'] for k, v in config.items()}
    config = {**config, **vars(args)}
    config = argparse.Namespace(**config)

    #########################################################################
    
    # Process video using the model, passing the text input
    result_path = process_video_with_model(config, text_input)
    return send_file(result_path, mimetype='image/png')


def create_video_from_frames(frame_list, output_dir='.', fps=30, frame_size=(640, 480)):
    """
    Create a video from a list of frames with a random file name.
    """
    random_filename = f"{str(uuid.uuid4())}.mp4"
    output_file = f"{output_dir}/{random_filename}"
    
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec
    video_writer = cv2.VideoWriter(output_file, fourcc, fps, frame_size)

    for frame in frame_list:
        if frame.shape[1::-1] != frame_size:
            frame = cv2.resize(frame, frame_size)
        video_writer.write(frame)  # Write the frame into the video file

    video_writer.release()  # Release the VideoWriter object
    
    return output_file


# added new: splitting video processing into groups
def process_video_with_model(config, text_input, group_size=10):  # added new
    model, _, _ = build_model(config)
    device = config['device']
    model.to(device)

    checkpoint = torch.load(config.checkpoint_path, map_location='cpu')
    state_dict = checkpoint["model_state_dict"]
    model.load_state_dict(state_dict, strict=False)

    model.eval()
    
    # Read video frames
    video_frames, _, _ = read_video(config.video_dir, pts_unit='sec')
    source_frames = []
    imgs = []

    for i in range(0, len(video_frames), 5):
        source_frame = Func.to_pil_image(video_frames[i].permute(2, 0, 1))
        source_frames.append(source_frame)

    for frame in source_frames:
        origin_w, origin_h = frame.size
        img, _ = size_transform(frame)
        imgs.append(transform(img))

    frame_length = len(imgs)


    
    group_count = (frame_length // group_size) + (1 if frame_length % group_size != 0 else 0)  # added new

    output_dir = './output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    color = [255, 144, 30]
    origin_img_list = []
    global img_h, img_w 

    for group_index in range(group_count):  # added new
        start_idx = group_index * group_size
        end_idx = min(start_idx + group_size, frame_length)
        imgs_group = torch.stack(imgs[start_idx:end_idx], dim=0)  # Group of frames
        samples = utils.nested_tensor_from_videos_list([imgs_group]).to(config['device'])

        with torch.no_grad():
            outputs = model(samples, None, [text_input], None)
        
        pred_masks = outputs["pred_masks"][:, 0, ...]
        pred_masks = F.interpolate(pred_masks.unsqueeze(0), size=(origin_h, origin_w), mode='bilinear', align_corners=False)
        pred_masks = (pred_masks.sigmoid() > 0.5).squeeze(0).cpu().numpy()

        for t in range(start_idx, end_idx):
            origin_img, source_img, mask = vis_add_mask(source_frames[t], pred_masks[t - start_idx], color)
            img_w, img_h = origin_img.size
            origin_img_list.append(origin_img)

    result_path = create_video_from_frames(origin_img_list, output_dir, (img_w, img_h))

    return result_path


if __name__ == '__main__':
    if not os.path.exists('./uploads'):
        os.makedirs('./uploads')
    app.run(debug=True)
