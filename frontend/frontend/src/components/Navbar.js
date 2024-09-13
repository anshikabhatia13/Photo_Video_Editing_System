import React from 'react';
import "./Navbar.css";
const Navbar = ({ onPageChange }) => {
  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-light">
      <a className="navbar-brand" href="#" onClick={() => onPageChange('welcome')}>Text-based Video Object Segmentation </a>
      <div className="collapse navbar-collapse">
        <ul className="navbar-nav ml-auto">
          <li className="nav-item">
            <a className="nav-link" href="#" onClick={() => onPageChange('form')}>Default Model</a>
          </li>
          <li className="nav-item">
            <a className="nav-link" href="#" onClick={() => onPageChange('about')}>About</a>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
