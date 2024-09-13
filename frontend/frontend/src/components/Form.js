import React, { useState } from "react";
import "./Form.css"; // Importing the CSS file

const Form = () => {
  // State to manage loading state
  const [isLoading, setIsLoading] = useState(false);
  // State to manage form data
  const [formData, setFormData] = useState({
    textInput: "",
    videoFile: null,
  });
  // State to manage the result URL to display the output
  const [resultURL, setResultURL] = useState(null);
  // State to manage error messages
  const [error, setError] = useState(null);

  const handleTextChange = (event) => {
    setFormData({
      ...formData,
      textInput: event.target.value,
    });
  };

  const handleFileChange = (event) => {
    setFormData({
      ...formData,
      videoFile: event.target.files[0], // Get the first selected file
    });
  };

  // Function to handle the 'Predict' button click
  const handlePredictClick = () => {
    const url = "http://localhost:5000/process_video"; // Updated the endpoint
    setIsLoading(true);
    setError(null);
    setResultURL(null);

    const formDataToSend = new FormData();
    formDataToSend.append("text", formData.textInput); // Updated to 'text'
    formDataToSend.append("video", formData.videoFile); // Updated to 'video'

    // Fetch request to the Flask backend
    fetch(url, {
      method: "POST",
      body: formDataToSend, // Send as multipart/form-data
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Error in response from server");
        }
        return response.blob(); // Expecting output as a Blob (could be image or video)
      })
      .then((blob) => {
        // Create a URL for the result blob
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

  return (
    <>
      <div className="container text-center mt-4">
        <h1 className="text-center">Video and Text Input Prediction</h1>
        <div className="container">
          <form method="post" encType="multipart/form-data">
            {/* Text Input */}
            <div className="text-center mt-3">
              <label>
                <b>Enter Text:</b>
              </label>
              <br />
              <input
                type="text"
                className="form-control"
                id="textInput"
                name="textInput"
                value={formData.textInput}
                onChange={handleTextChange}
                placeholder="Enter some text"
              />
            </div>

            {/* Video File Input */}
            <div className="form-group mt-3">
              <label>
                <b>Upload MP4 Video:</b>
              </label>
              <br />
              <input
                type="file"
                className="form-control"
                id="videoFile"
                name="videoFile"
                accept="video/mp4"
                onChange={handleFileChange}
              />
            </div>

            {/* Submit Button */}
            <div className="form-group mt-3">
              <button
                className="btn btn-primary form-control"
                disabled={isLoading}
                onClick={(e) => {
                  e.preventDefault();
                  handlePredictClick();
                }}
              >
                {isLoading ? "Processing..." : "Predict"}
              </button>
            </div>
          </form>

          {/* Display Error Message */}
          {error && (
            <div className="text-center mt-3">
              <p style={{ color: "red" }}>{error}</p>
            </div>
          )}

          {/* Display Loading State */}
          {isLoading && (
            <div className="text-center mt-3">
              <p>Uploading and processing video...</p>
            </div>
          )}

          {/* Display Result (Could be image or video) */}
          {resultURL && (
            <div className="text-center mt-4">
              <h4>Predicted Output:</h4>
              {formData.videoFile ? (
                <video controls width="500">
                  <source src={resultURL} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              ) : (
                <img src={resultURL} alt="Processed Output" width="500" />
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default Form;
