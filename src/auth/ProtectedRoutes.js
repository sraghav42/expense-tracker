import React, {useEffect,useState} from 'react';
import {Navigate} from 'react-router-dom';
import ResponsiveAppBar from '../components/Navbar';

const ProtectedRoute =({Component}) => {
    const [isAuthorized, setIsAuthorized]=useState(false);
    const [isLoading, setisLoading]=useState(true);
    
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
            } finally{
                setisLoading(false);
            }
        }

        checkAuthorization();
    },[]);

    if(isLoading){
        return <div>Loading...</div>;
    }

    if(isAuthorized===null){
        return null;
    }

    return isAuthorized ? (
        <>
            <ResponsiveAppBar/>
            <Component/>
        </>
    ): (<Navigate to="/login"/>);
}

export default ProtectedRoute;