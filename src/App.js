import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ResponsiveAppBar from './components/Navbar';
import DetailedReport from './pages/DetailedReport';
import Home from './pages/Home';

function App() {
  return (
    <Router>
      <ResponsiveAppBar />
        <Routes>
          <Route path ="/" element={<Home/>} />
          <Route path ="/detailed-report" element={<DetailedReport />} />
        </Routes>
    </Router>
  );
}

export default App;