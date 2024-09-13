import React from 'react';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        <h4>About the Project</h4>
        <p>
          This project processes video and text input using a machine learning model to produce 
          an output video, showcasing how AI can assist in understanding and analyzing video content.
        </p>
        <p>&copy; 2024 Video Prediction App</p>
      </div>
    </footer>
  );
};

export default Footer;
