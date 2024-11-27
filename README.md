# Photo & Video Editing Web App

This repository contains the code for a **Photo and Video Editing Web Application**. Users can upload photos or videos and apply editing tools such as background removal, object segmentation, and enhancement. The system utilizes deep learning models like **U^2Net**, **Swin UNetR**, **U-Net**, **YOLO-World + Efficient SAM** and **Referring Video Object Segmentation (RVOS)** for performing these tasks. The app is built with a **React (Vite)** frontend and a **Flask** backend. Designed for applications such as video editing, autonomous systems, and smart surveillance, the pipeline offers robust performance and modular scalability.
## Documentation
https://docs.google.com/document/d/18vM6KMFk_ggLlgySi4jCKJ5gUYyA01UK8SoF1rByZ0Q/edit?usp=sharing

## Features

- **Photo & Video Upload**: Users can upload photos or videos for editing.
- **Background Removal**: Removes background from images and videos using **U^2Net**.
- **Object Segmentation**: Performs object segmentation in images using **U-Net**, **YOLO-World+Efficient SAM** and video using **Swin UNetR** and **Referring Video Object Segmentation (RVOS)**.
- **Enhancement Tools**: Various filters and enhancement features (contrast, brightness adjustment).
- **Download**: Users can download the edited photos and videos.
- **Responsive Interface**: Real-time preview and a user-friendly interface for easy editing.

## Technologies Used

- **Frontend**: ReactJS (Vite)
- **Backend**: Flask (Python)
- **Machine Learning Models**: 
  - **U^2Net**: Image background removal.
  - **Swin UNetR**: Video object segmentation.
  - **U-Net**: Image segmentation.
- **Media Processing**: OpenCV, PyTorch.
- **Deployment**: Docker, Nginx, Gunicorn.

## Project Structure

```
.
├── backend/                # Flask API backend
│   ├── app.py              # Main backend application
│   ├── model/              # Model loading and inference scripts
│   ├── static/             # Static files
│   ├── templates/          # HTML templates (if needed)
│   └── requirements.txt    # Backend dependencies
├── frontend/               # ReactJS frontend
│   ├── public/             # Public assets
│   ├── src/                # Source code
│   ├── package.json        # Frontend dependencies
│   └── README.md           # Frontend-specific documentation
├── docker-compose.yml      # Docker Compose setup for backend and frontend
└── README.md               # Main README file
```

## Prerequisites
- Python 3.8+
- PyTorch 1.11+
- Node.js 16+
- CUDA-enabled GPU (optional for faster inference)
