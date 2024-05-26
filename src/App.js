import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import DetailedReport from "./pages/DetailedReport";
import Login from './pages/Login';
import Home from './pages/Home';
import Register from './pages/Register';
import ProtectedRoute from './auth/ProtectedRoutes';


function App() {
  return (
    <Router>
      <Routes>
        <Route path='/' element={<Home />} />
        <Route path='/register' element={<Register />} />
        <Route path='/login' element={<Login />} />
        <Route path='/dashboard' 
               element={<ProtectedRoute Component={Dashboard}/>}/>
        <Route path='/detailed-report' 
               element={<ProtectedRoute Component={DetailedReport}/>}/>
      </Routes>
    </Router>
  );
}

export default App;