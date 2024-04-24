import React, { useState } from 'react';

const Login = () => {
    const [username,setUsername]=useState('');
    const [password,setPassword]=useState('');
    const [error,setError]=useState('');

    const handleSubmit= async (e) => {
        e.preventDefault();
        setError('');
        
        try{
            const res=await fetch('http://localhost:5000/api/auth/login',{
                method:'POST',
                body:JSON.stringify({username,password}),
                headers:{'Content-Type':'application/json'}
            });

            const data=await res.json();
            if(res.status===400 || res.status===401 || res.status===404){
                setError(`${data.message}. ${data.error ? data.error : ''}`);
            } else{
                window.location.assign('/');
            }
        } catch(err){
            console.log("Error : ",err);
            setError('An unexpected error occurred. Please try again.');
        }
    };
    return (
      <div>
        <h1>Login Page</h1>
        <form onSubmit={handleSubmit}>
            {error && <div className='error' style={{backgroundColor:'red'}}>{error}</div>}
            <br />
            <label htmlFor='username'>Username</label>
            <br />
            <input type='text' id='username' value={username} onChange={(e) => setUsername(e.target.value)} required />
            <br />
            <label htmlFor='password'>Password</label>
            <br />
            <input type='password' id='password' value={password} onChange={(e) => setPassword(e.target.value)} required />
            <br />
            <input type='submit' value='login' />
            <br />
        </form>
        <a href='/register'>Don't have an account? Register</a>
      </div>  
    );
};

export default Login;