import React, { useState } from 'react';

function CustomBackground() {
  const [foregroundFile, setForegroundFile] = useState(null);
  const [backgroundFile, setBackgroundFile] = useState(null);
  const [segmentedImage, setSegmentedImage] = useState(null);
  const [loading, setLoading] = useState(false);

  const onForegroundChange = (event) => {
    setForegroundFile(URL.createObjectURL(event.target.files[0]));
    setSegmentedImage(null);
  };

  const onBackgroundChange = (event) => {
    setBackgroundFile(URL.createObjectURL(event.target.files[0]));
  };

  const handleSegment = async () => {
    if (!document.getElementById('foreground-upload').files[0] || !document.getElementById('background-upload').files[0]) {
      return;
    }
    setLoading(true);

    const formData = new FormData();
    formData.append('foreground_image', document.getElementById('foreground-upload').files[0]);
    formData.append('background_image', document.getElementById('background-upload').files[0]);

    const response = await fetch('http://localhost:5000/custombgd', {
      method: 'POST',
      body: formData,
    });

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    setSegmentedImage(url);
    setLoading(false);
  };

  const downloadImage = () => {
    const link = document.createElement('a');
    link.href = segmentedImage;
    link.download = 'composited_image.png';
    link.click();
  };

  const removeImages = () => {
    setForegroundFile(null);
    setBackgroundFile(null);
    setSegmentedImage(null);
    document.getElementById('foreground-upload').value = '';
    document.getElementById('background-upload').value = '';
  };

  return (
    <div className="App flex justify-center items-center min-h-screen"
      style={{
        backgroundImage: "url('frontend/new_frontend/src/assets/otbg.jpg')",
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }}>
      <div className="segmentation-box p-16 rounded-lg shadow-lg bg-slate-950 w-full max-w-7xl mx-4"
        style={{
          borderTop: '13px solid #0d9488',
          borderRight: '10px solid #14b8a6',
          borderBottom: '8px solid #2dd4bf',
          borderLeft: '15px solid #5eead4'
        }}>
        <h1 className="text-4xl font-bold text-teal-200 text-center mb-6">Custom Background Compositing</h1>

        <div className="flex flex-col items-center mb-6">
        <label className="text-white text-lg mr-2"> Choose Image  </label>
          <input 
            type="file" 
            id="foreground-upload" 
            onChange={onForegroundChange} 
            className="mb-4 text-lg text-center rounded border-2 border-gray-600 bg-gray-700 text-white p-2"
            accept="image/*"
          />
          <label className="text-white text-lg mr-2"> Choose Background  </label>
          <input 
            type="file" 
            id="background-upload" 
            onChange={onBackgroundChange} 
            className="mb-4 text-lg text-center rounded border-2 border-gray-600 bg-gray-700 text-white p-2"
            accept="image/*"
          />

          <div className="flex space-x-4">
            <button 
              onClick={removeImages} 
              className="bg-red-500 text-white text-lg px-6 py-2 rounded hover:bg-red-600 transition duration-200"
            >
              Remove Images
            </button>
            <button 
              onClick={handleSegment} 
              className="bg-green-500 text-white text-lg px-6 py-2 rounded hover:bg-green-600 transition duration-200"
            >
              Apply Background
            </button>
          </div>
        </div>

        <div className="image-container flex justify-center mt-6">
          <div className="left-side w-1/2 p-2 flex flex-col items-center">
            {foregroundFile && (
              <img src={foregroundFile} alt="Foreground" className="max-w-full h-auto rounded" />
            )}
          </div>
          <div className="right-side w-1/2 p-2 flex flex-col items-center">
            {loading && foregroundFile && (
              <img src={foregroundFile} alt="Blurred" style={{ filter: 'blur(10px)' }} className="max-w-full h-auto rounded" />
            )}
            {segmentedImage && (
              <>
                <img src={segmentedImage} alt="Composited" className="max-w-full h-auto rounded" />
                <button 
                  onClick={downloadImage} 
                  className="mt-2 bg-purple-500 text-white text-lg px-6 py-2 rounded hover:bg-purple-600 transition duration-200"
                >
                  Download Composited Image
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default CustomBackground;
