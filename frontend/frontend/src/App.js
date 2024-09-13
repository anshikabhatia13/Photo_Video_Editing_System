import React, { useState } from 'react';
import Form from './components/Form';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Footer from './components/Footer';
import Welcome from './components/Welcome';


import "./App.css";

const App = () => {
  const [currentPage, setCurrentPage] = useState('welcome'); // Manage page state

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  return (
    <div>
      <Navbar onPageChange={handlePageChange} />
      <div className="app-container">
        <Sidebar onPageChange={handlePageChange} />
        <div className="content">
          {currentPage === 'welcome' && <Welcome />}
          {currentPage === 'form' && <Form />}
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default App;
