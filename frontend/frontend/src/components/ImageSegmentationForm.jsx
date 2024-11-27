import React, { useState } from "react";

const ImageSegmentationForm = () => {
  const [formData, setFormData] = useState({
    imageFile: null,
    query: "",
    confidenceThreshold: 0.3,
    nmsThreshold: 0.2,
  });
  const [inputImagePreview, setInputImagePreview] = useState(null);
  const [outputImage, setOutputImage] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setFormData({
      ...formData,
      imageFile: file,
    });
    setInputImagePreview(URL.createObjectURL(file));
    setOutputImage(null); 
  };

  const handleInputChange = (event) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value,
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setError(null);

    const formDataToSend = new FormData();
    formDataToSend.append("image", formData.imageFile);
    formDataToSend.append("query", formData.query);
    formDataToSend.append("confidence_threshold", formData.confidenceThreshold);
    formDataToSend.append("nms_threshold", formData.nmsThreshold);

    try {
      const response = await fetch("http://localhost:5000/process_image", {
        method: "POST",
        body: formDataToSend,
      });

      if (!response.ok) {
        throw new Error("Error processing the image.");
      }

      const blob = await response.blob();
      setOutputImage(URL.createObjectURL(blob));
    } catch (error) {
      setError("There was an error processing your request.");
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      imageFile: null,
      query: "",
      confidenceThreshold: 0.3,
      nmsThreshold: 0.2,
    });
    setInputImagePreview(null);
    setOutputImage(null);
    setError(null);
    document.getElementById("imageFileInput").value = "";
  };

  return (
    <div
      className="image-segmentation-form-container flex justify-center items-center min-h-screen"
      style={{
        backgroundImage: "url('frontend/new_frontend/src/assets/otbg.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
      }}
    >
      <div
        className="segmentation-box p-16 rounded-lg shadow-lg bg-slate-950 w-full max-w-7xl mx-4"
        style={{
          borderTop: "13px solid #0d9488",
          borderRight: "10px solid #14b8a6",
          borderBottom: "8px solid #2dd4bf",
          borderLeft: "15px solid #5eead4",
        }}
      >
        <h1 className="text-4xl font-bold text-teal-200 text-center mb-6">Custom Portrait Generator</h1>

        <form onSubmit={handleSubmit} encType="multipart/form-data" className="flex flex-col items-center mb-6">
          {/* Image Input */}
          <input
            type="file"
            id="imageFileInput"
            name="image"
            accept="image/*"
            onChange={handleFileChange}
            className="mb-4 text-lg text-center rounded border-2 border-gray-600 bg-gray-700 text-white p-2"
            required
          />

          {/* Query Input */}
          <input
            type="text"
            name="query"
            value={formData.query}
            onChange={handleInputChange}
            placeholder="Enter objects"
            className="mb-4 text-lg text-center rounded border-2 border-gray-600 bg-gray-700 text-white p-2"
            required
          />

          {/* Confidence Threshold */}
          <input
            type="number"
            step="0.01"
            name="confidenceThreshold"
            value={formData.confidenceThreshold}
            onChange={handleInputChange}
            placeholder="Confidence Threshold"
            className="mb-4 text-lg text-center rounded border-2 border-gray-600 bg-gray-700 text-white p-2"
            required
          />

          {/* NMS Threshold */}
          <input
            type="number"
            step="0.01"
            name="nmsThreshold"
            value={formData.nmsThreshold}
            onChange={handleInputChange}
            placeholder="NMS Threshold"
            className="mb-4 text-lg text-center rounded border-2 border-gray-600 bg-gray-700 text-white p-2"
            required
          />

          {/* Submit and Reset Buttons */}
          <div className="flex space-x-4 mb-4">
            <button
              type="submit"
              className={`bg-green-500 text-white text-lg px-6 py-2 rounded hover:bg-green-600 transition duration-200 ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
              disabled={isLoading}
            >
              {isLoading ? "Processing..." : "Submit"}
            </button>

            <button
              type="button"
              onClick={resetForm}
              className="bg-red-500 text-white text-lg px-6 py-2 rounded hover:bg-red-600 transition duration-200"
            >
              Reset
            </button>
          </div>
        </form>

        {/* Input and Output Images Side by Side */}
      <div className="flex justify-center mt-6">
        {/* Input Image Preview */}
        {inputImagePreview && (
          <div className="flex flex-col items-center mr-4">
            <h2 className="text-lg font-bold">Input Image:</h2>
            <img 
              src={inputImagePreview} 
              alt="Input" 
              className="max-w-full h-auto rounded" 
              style={{ maxWidth: "300px" }} 
            />
          </div>
        )}

        {/* Output Image Section */}
        {outputImage ? (
          <div className="flex flex-col items-center">
            <h2 className="text-lg font-bold">Output Image:</h2>
            <img 
              src={outputImage} 
              alt="Output" 
              className="max-w-full h-auto rounded" 
              style={{ maxWidth: "300px" }} 
            />
            {/* Download Button */}
            <a
              href={outputImage}
              download="segmented_image.png"
              className="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition duration-200"
            >
              Download Image
            </a>
          </div>
        ) : (
          inputImagePreview && (
            <div className="flex flex-col items-center">
              <h2 className="text-lg font-bold">Output Image:</h2>
              <img
                src={inputImagePreview} 
                alt="Processing..." 
                className={`max-w-full h-auto rounded blur-md ${isLoading ? "blur-md" : ""}`}
                style={{ maxWidth: "300px" }}
              />
              <p className="text-sm text-gray-400 mt-2">Processing...</p>
            </div>
          )
        )}
      </div>


        {/* Error Handling */}
        {error && <p className="text-red-500">{error}</p>}
      </div>
    </div>
  );
};

export default ImageSegmentationForm;
