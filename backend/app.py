import subprocess
from flask import Flask, request, jsonify, send_file
import os
import uuid

app = Flask(__name__)

# Directory paths for uploads and output
UPLOAD_DIR = 'uploads'
OUTPUT_DIR = 'output'

# Ensure the necessary directories exist
def ensure_directories():
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

# Generate a unique filename for the uploaded video
def generate_unique_filename(filename):
    extension = os.path.splitext(filename)[1]  # Get the file extension (e.g., '.mp4')
    unique_filename = str(uuid.uuid4()) + extension  # Create a unique filename
    return unique_filename

# Construct the command to run the demo_video.py script
def construct_command(video_filename, text_input):
    config_path = 'NeurIPS2023_SOC/configs/refer_youtube_vos.yaml'
    backbone = 'video-swin-b'
    backbone_pretrained_path = 'NeurIPS2023_SOC/pretrained_weights/model.pth'
    checkpoint_path = 'NeurIPS2023_SOC/checkpoint/joint_tiny.tar'
    running_mode = 'test'
    device = 'cuda'  # or 'cpu' depending on your setup

    # Output directory for the processed video and frames
    output_video_dir = os.path.join(OUTPUT_DIR, video_filename.split('.')[0])
    command = [
        'cmd.exe', '/C',
        'cd .. && '
        'C:/Users/anshi/Desktop/DMLS_PRoj/.venv/Scripts/activate.bat && '
        'cd backend && '
        'python NeurIPS2023_SOC/demo_video.py '
        '-c NeurIPS2023_SOC/configs/refer_youtube_vos.yaml '
        '-rm test '
        '--backbone video-swin-b '
        '-bpp NeurIPS2023_SOC/pretrained_weights/model.pth '
        '-ckpt NeurIPS2023_SOC/checkpoint/joint_tiny.tar '
        f'--video_dir {os.path.join(UPLOAD_DIR, video_filename)} '
        '--device cuda '
        f'--text "{text_input}"'
    ]

   
#     command = [
#     'cmd.exe', '/C',  # Run in cmd.exe shell
   
#     'C:/Users/anshi/Desktop/DMLS_PRoj/.venv/Scripts/activate.bat && python NeurIPS2023_SOC/demo_video.py',  
#     '-c', config_path,
#     '-rm', running_mode,
#     '--backbone', backbone,
#     '-bpp', backbone_pretrained_path,
#     '-ckpt', checkpoint_path,
#     '--video_dir', os.path.join(UPLOAD_DIR, video_filename),  # Input video path
#     '--device', device,
#     '--text', text_input  # Text input passed from frontend
# ]


    print(f"Constructed command: {' '.join(command)}")  # Debugging statement
    return command, output_video_dir

# Process the video using the demo_video.py script
def process_video_with_script(video_filename, text_input):
    command, output_video_dir = construct_command(video_filename, text_input)
    try:
        # Run the command and capture the output
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Script output: {result.stdout}")  # Debugging statement
        return output_video_dir
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr}")  # Debugging statement
        raise

# API endpoint to handle video and text input from the frontend
@app.route('/process_video', methods=['POST'])
def process_video():
    try:
        # Get the video file and text input from the request
        video_file = request.files['video']  # Assuming the frontend sends a video file
        text_input = request.form['text']  # Assuming the frontend sends a text input

        # Generate a unique filename for the uploaded video
        unique_video_filename = generate_unique_filename(video_file.filename)
        video_filepath = os.path.join(UPLOAD_DIR, unique_video_filename)

        # Save the video file to the uploads directory
        video_file.save(video_filepath)
        print(f"Video saved to {video_filepath}")  # Debugging statement

        # Process the video using the demo_video.py script
        output_video_dir = process_video_with_script(unique_video_filename, text_input)

        # Check if output exists and pack frames as zip or return video
        output_video_file = os.path.join(output_video_dir, 'SOC', 'visual', '0.png')  # Example path to first frame

        if not os.path.exists(output_video_file):
            return jsonify({"status": "error", "message": "Output video or frames not found"}), 500

        print(f"Sending output video or frames from {output_video_dir}")  # Debugging statement

        # Send the output video/frame as a response to the frontend
        return send_file(output_video_file, as_attachment=True, mimetype='image/png')

    except Exception as e:
        # Handle any errors that occur during processing
        print(f"Error during processing: {str(e)}")  # Debugging statement
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    ensure_directories()  # Ensure the upload and output directories exist
    app.run(debug=True)
