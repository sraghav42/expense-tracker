import React, {useEffect,useState} from 'react';
import {Navigate} from 'react-router-dom';
import Dashboard from '../pages/Dashboard';

const ProtectedRoute =() => {
    const [isAuthorized, setIsAuthorized]=useState(false);
    
    useEffect(() => {
        const checkAuthorization=async () => {
            try{
                const res=await fetch('http://localhost:5000/tokencheck',{
                    method:'GET',
                    credentials:'include'
                });
                if (res.status===200){
                    setIsAuthorized(true);
                }else{
                    setIsAuthorized(false);
                }
            } catch(error){
                console.log('Error connecting to authorization service',error);
                setIsAuthorized(false);
            }
        }

        checkAuthorization();
    },[]);

    if(isAuthorized===null){
        return null;
    }

    return isAuthorized ? (<Dashboard />): (<Navigate to="/login"/>);
}

export default ProtectedRoute;