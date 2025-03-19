import { useState, useEffect } from "react";
import {BrowserRouter as Router, Routes, Route} from "react-router-dom";
import Navbar from './components/Navbar';
import Home from './pages/dashboard';
import Shipping from './pages/shipping';
import MainLayout from './layout/MainLayout';


function App() {
    return (
        <Router>
            <Navbar />

            <Routes>
                <Route path="/" element={<MainLayout />} />
                <Route path="/shipping" element={<Shipping />} />

           </Routes>
    </Router>
    );

}

export default App;


