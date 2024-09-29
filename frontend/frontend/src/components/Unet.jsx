import React, { useState } from 'react';

function Unet() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [segmentedImage, setSegmentedImage] = useState(null);
  const [loading, setLoading] = useState(false);

  const onFileChange = (event) => {
    setSelectedFile(URL.createObjectURL(event.target.files[0]));
    setSegmentedImage(null);
  };

  const handleSegment = async () => {
    if (!document.getElementById('file-upload').files[0]) return; 
    setLoading(true);
    const formData = new FormData();
    formData.append('image', document.getElementById('file-upload').files[0]);

    const response = await fetch('http://localhost:5000/segment', {
      method: 'POST',
      body: formData
    });

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    setSegmentedImage(url);
    setLoading(false);
  };

  const downloadImage = () => {
    const link = document.createElement('a');
    link.href = segmentedImage;
    link.download = 'segmented_image.png'; 
    link.click();
  };

  const removeImage = () => {
    setSelectedFile(null);
    setSegmentedImage(null);
    document.getElementById('file-upload').value = ""; 
  };

  return (
    <div
      className="App flex justify-center items-center min-h-screen"
      style={{
        backgroundImage: "url('frontend/new_frontend/src/assets/otbg.jpg')", // Same background as Form.js
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
      }}
    >
      <div
        className="segmentation-box p-16 rounded-lg shadow-lg bg-slate-950 w-full max-w-7xl mx-4"
        style={{
          borderTop: "13px solid #0d9488", // Top border red #38bdf8"
          borderRight: "10px solid #14b8a6", // Right border green
          borderBottom: "8px solid #2dd4bf", // Bottom border blue
          borderLeft: "15px solid #5eead4", // Left border purple
        }}
      >
        <h1 className="text-4xl font-bold text-teal-200 text-center mb-6">Image Background Removal</h1>

        <div className="flex flex-col items-center mb-6">
          <input 
            type="file" 
            id="file-upload" 
            onChange={onFileChange} 
            className="mb-4 text-lg text-center rounded border-2 border-gray-600 bg-gray-700 text-white p-2"
          />
          <div className="flex space-x-4">
            <button 
              onClick={removeImage} 
              className="bg-red-500 text-white text-lg px-6 py-2 rounded hover:bg-red-600 transition duration-200"
            >
              Remove Image
            </button>
            <button 
              onClick={handleSegment} 
              className="bg-green-500 text-white text-lg px-6 py-2 rounded hover:bg-green-600 transition duration-200"
            >
              Segment
            </button>
          </div>
        </div>

        <div className="image-container flex justify-center mt-6">
          <div className="left-side w-1/2 p-2 flex flex-col items-center">
            {selectedFile && (
              <img src={selectedFile} alt="Uploaded" className="max-w-full h-auto rounded" />
            )}
          </div>
          <div className="right-side w-1/2 p-2 flex flex-col items-center">
            {loading && selectedFile && (
              <img src={selectedFile} alt="Blurred" style={{ filter: 'blur(10px)' }} className="max-w-full h-auto rounded" />
            )}
            {segmentedImage && (
              <>
                <img src={segmentedImage} alt="Segmented" className="max-w-full h-auto rounded" />
                <button 
                  onClick={downloadImage} 
                  className="mt-2 bg-purple-500 text-white text-lg px-6 py-2 rounded hover:bg-purple-600 transition duration-200"
                >
                  Download Segmented Image
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Unet;