# Referred Video Object Segmentation Web App

This repository contains the code for a **Referred Video Object Segmentation** web application. The system allows users to upload a video and provide a text description, and it returns the video with the relevant object segmented. The app uses a **Swin UNetR** model for segmentation and is built with a **ReactJS** frontend and a **Flask** backend.

## Features
- **Video Upload & Text Input**: Users can upload a video and provide text for segmentation.
- **Machine Learning Inference**: The backend loads a pre-trained Swin UNetR model for video object segmentation.
- **Segmented Video Output**: The backend processes the video and text, returning the segmented video to the frontend for display.
- **Responsive Design**: The frontend provides feedback on the status of video processing.

## Technologies
- **Frontend**: ReactJS
- **Backend**: Flask (Python)
- **Machine Learning Model**: Swin UNetR (PyTorch)
- **Video Processing**: OpenCV
- **Deployment**: Docker, Nginx, Gunicorn

## Project Structure

```bash
.
├── backend/                # Flask API backend
│   ├── app.py              # Main application file
│   ├── model/              # Model loading and inference scripts
│   ├── static/             # Static files
│   ├── templates/          # HTML templates
│   └── requirements.txt    # Python dependencies
├── frontend/               # ReactJS frontend
│   ├── public/             # Public assets
│   ├── src/                # Source code
│   ├── package.json        # Node.js dependencies
│   └── README.md           # Frontend-specific README
├── docker-compose.yml      # Docker Compose setup for backend and frontend
└── README.md               # This README file
```
# Getting Started
## Prerequisites
To get started, ensure you have the following installed on your system:

Node.js (for the frontend)
Python 3.x (for the backend)
Docker (for deployment)

## Installation

### Clone the repository:

bash
```
git clone https://github.com/your-username/referred-video-segmentation-app.git
cd referred-video-segmentation-app
```
### Setup the backend:

bash
```
cd backend
python -m venv venv              # Create a virtual environment
source venv/bin/activate         # Activate the environment
pip install -r requirements.txt  # Install dependencies
```
### Setup the frontend:

bash
```
cd frontend
npm install  # Install Node.js dependencies
```
### Run the backend:

bash
```
cd backend
flask run
```
### Run the frontend:

bash
```
cd frontend
npm start
```

# Usage
Open the app in your browser.
Upload a video and input text to describe the object you want to segment.
Click submit and wait for the backend to process the video.
The segmented video will be displayed once processing is complete.
Model
The model used for segmentation is a pre-trained Swin UNetR model. The model is loaded in the backend, where it performs inference based on the user’s video and text input.

