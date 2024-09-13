import React from 'react';

const Sidebar = ({ onPageChange }) => {
  return (
    <div className="sidebar">
      <h3>Select Model</h3>
      <ul className="model-list">
        <li onClick={() => onPageChange('form')}>Model 1</li>
        <li onClick={() => onPageChange('form')}>Model 2</li>
        <li onClick={() => onPageChange('form')}>Model 3</li>
      </ul>
    </div>
  );
};

export default Sidebar;
