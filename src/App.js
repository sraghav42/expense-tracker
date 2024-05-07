import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ResponsiveAppBar from './components/Navbar';
import Dashboard from './pages/Dashboard';
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
        <Route path='/dashboard' element={
          <div>
            <ResponsiveAppBar/>
            <ProtectedRoute/>
          </div>
        } />
      </Routes>
    </Router>
  );
}

export default App;