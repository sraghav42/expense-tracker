import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ResponsiveAppBar from './components/Navbar';
import DetailedReport from './pages/DetailedReport';
import Login from './pages/Login';
import Home from './pages/Home';
import Register from './pages/Register';


function App() {
  return (
    <Router>
      <Routes>
        <Route path='/' element={<Home />} />
        <Route path='/register' element={<Register />} />
        <Route path='/login' element={<Login />} />
        <Route path='/detailed-report' element={
          <div>
            <ResponsiveAppBar />
            <DetailedReport />
          </div>
        } />
      </Routes>
    </Router>
  );
}

export default App;