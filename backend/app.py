from flask import Flask, request, jsonify, send_file
import os
import torch
import ruamel.yaml
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

app = Flask(__name__)

size_transform = RandomResize(sizes=[360], max_size=640)
transform = T.Compose([
    T.ToTensor(),
    T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

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

    # Load config file
    config_path = 'NeurIPS2023_SOC/configs/refer_youtube_vos.yaml'
    with open(config_path) as f:
        config = ruamel.yaml.safe_load(f)
    config = {k: v['value'] for k, v in config.items()}

    config['device'] = 'cuda' if torch.cuda.is_available() else 'cpu'
    config['video_dir'] = video_path
    config['checkpoint_path'] = './checkpoints/model_checkpoint.pth' 

    # Process video using the model, passing the text input
    result_path = process_video_with_model(config, text_input)
    
    return send_file(result_path, mimetype='image/png')


def process_video_with_model(config, text_input):
    model, _, _ = build_model(config)
    device = config['device']
    model.to(device)

    checkpoint = torch.load(config['checkpoint_path'], map_location='cpu')
    state_dict = checkpoint["model_state_dict"]
    model.load_state_dict(state_dict, strict=False)

    model.eval()
    

    video_frames, _, _ = read_video(config['video_dir'], pts_unit='sec')
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
    imgs = torch.stack(imgs, dim=0)
    samples = utils.nested_tensor_from_videos_list([imgs]).to(config['device'])

    with torch.no_grad():
        outputs = model(samples, None, [text_input], None)
    
    pred_masks = outputs["pred_masks"][:, 0, ...]
    pred_masks = F.interpolate(pred_masks.unsqueeze(0), size=(origin_h, origin_w), mode='bilinear', align_corners=False)
    pred_masks = (pred_masks.sigmoid() > 0.5).squeeze(0).cpu().numpy()

    # Save output images
    output_dir = './output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    color = [255, 144, 30]
    result_path = os.path.join(output_dir, 'result.png')
    origin_img, source_img, mask = vis_add_mask(source_frames[0], pred_masks[0], color)
    origin_img.save(result_path)

    return result_path


if __name__ == '__main__':
    if not os.path.exists('./uploads'):
        os.makedirs('./uploads')
    app.run(debug=True)
