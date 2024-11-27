import React, { useState } from "react";

const Form = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    textInput: "",
    videoFile: null,
    videoURL: null,
  });
  const [resultURL, setResultURL] = useState(null);
  const [error, setError] = useState(null);

  const handleTextChange = (event) => {
    setFormData({
      ...formData,
      textInput: event.target.value,
    });
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setFormData({
      ...formData,
      videoFile: file,
      videoURL: URL.createObjectURL(file),
    });
    setResultURL(null);
  };

  const handlePredictClick = () => {
    const url = "http://localhost:5000/process_video";
    setIsLoading(true);
    setError(null);
    setResultURL(null);

    const formDataToSend = new FormData();
    formDataToSend.append("text", formData.textInput);
    formDataToSend.append("video", formData.videoFile);

    fetch(url, {
      method: "POST",
      body: formDataToSend,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Error in response from server");
        }
        return response.blob();
      })
      .then((blob) => {
        const resultObjectURL = URL.createObjectURL(blob);
        setResultURL(resultObjectURL);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error("Error:", error);
        setError("There was an error processing the request.");
        setIsLoading(false);
      });
  };

  const removeVideo = () => {
    setFormData({
      ...formData,
      videoFile: null,
      videoURL: null,
    });
    setResultURL(null);
    document.getElementById("videoFile").value = "";
  };

  return (
    <div
      className="App flex justify-center items-center min-h-screen"
      style={{
        backgroundImage: "url('frontend/new_frontend/src/assets/otbg.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
      }}
    >
      {/* Larger box with non-uniform borders */}
      <div
        className="form-box p-16 rounded-lg shadow-lg bg-slate-950 w-full max-w-7xl mx-4"
        style={{
          borderTop: "13px solid #6366f1",
          borderRight: "10px solid #818cf8",
          borderBottom: "8px solid #a5b4fc",
          borderLeft: "15px solid #4f46e5",
        }}
      >
        <a
          href="http://172.26.32.243:5000/" // Change this URL to your desired link
          target="_blank"
          rel="noopener noreferrer"
        >
          <h1 className="text-4xl font-bold text-indigo-200 text-center mb-6">
            Referred Video Object Segmentation
          </h1>
        </a>

        <div className="flex flex-col items-center mb-6">
          {/* Text Input */}
          <label className="text-lg text-white mb-4">
            <b>Enter Text:</b>
          </label>
          <input
            type="text"
            className="form-control bg-gray-700 text-white p-2 rounded mb-6"
            id="textInput"
            name="textInput"
            value={formData.textInput}
            onChange={handleTextChange}
            placeholder="Enter some text"
          />

          {/* Video File Input */}
          <label className="text-lg text-white mb-4">
            <b>Upload MP4 Video:</b>
          </label>
          <input
            type="file"
            className="form-control bg-gray-700 text-white p-2 rounded mb-6"
            id="videoFile"
            name="videoFile"
            accept="video/mp4"
            onChange={handleFileChange}
          />

          <div className="flex space-x-4">
            <button
              className={`bg-green-500 text-white text-lg px-6 py-2 rounded hover:bg-green-600 transition duration-200 ${
                isLoading ? "cursor-not-allowed" : ""
              }`}
              disabled={isLoading}
              onClick={(e) => {
                e.preventDefault();
                handlePredictClick();
              }}
            >
              {isLoading ? "Processing..." : "Segment"}
            </button>
            <button
              className="bg-red-500 text-white text-lg px-6 py-2 rounded hover:bg-red-600 transition duration-200"
              onClick={removeVideo}
            >
              Remove Video
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="text-center mt-4">
            <p style={{ color: "red" }}>{error}</p>
          </div>
        )}

        {/* Loading State */}
        {isLoading && formData.videoURL && (
          <div className="text-center mt-4">
            <p className="text-white mb-2">Uploading and processing video...</p>
            <video
              controls
              width="500"
              className="rounded shadow-lg mb-4"
              style={{ filter: "blur(10px)" }}
            >
              <source src={formData.videoURL} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
        )}

        {/* Display Original Video */}
        {formData.videoURL && !isLoading && (
          <div className="text-center mt-6">
            <h4 className="text-white text-xl mb-4">Uploaded Video:</h4>
            <video controls width="500" className="rounded shadow-lg">
              <source src={formData.videoURL} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
        )}

        {/* Display Result (Processed Video Output) */}
        {resultURL && (
          <div className="text-center mt-6">
            <h4 className="text-white text-xl mb-4">Predicted Output:</h4>
            <video controls width="500" className="rounded shadow-lg">
              <source src={resultURL} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
            <p className="text-white mt-4">
              Part of the processed video is displayed here
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Form;
