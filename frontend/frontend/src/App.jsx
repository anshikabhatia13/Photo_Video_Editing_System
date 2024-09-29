import ButtonGradient from "./assets/svg/ButtonGradient";
import Benefits from "./components/Benefits";
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Footer from "./components/Footer";
import Header from "./components/Header";
import Hero from "./components/Hero";
import Unet from "./components/Unet";
import Form from "./components/Form";


const App = () => {
  return (
    
    <div>
      <div className="pt-[4.75rem] lg:pt-[5.25rem] overflow-hidden">
        <Header />
       
        <Hero />
        <Benefits />
        <Unet/>
        <Form/>
        <Footer />
      </div>

      <ButtonGradient />
    </div>
  );
};

export default App;
