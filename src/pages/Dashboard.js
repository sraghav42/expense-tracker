import React, { useEffect, useState } from "react";
import {PieChart, Pie} from 'recharts';

const Dashboard = () => {

  const data=[
    {category:"Food", amount:250},
    {category:"Utlities", amount:150}
  ];
    const [user,setUser]=useState(null);
    const [loading,setLoading]=useState(true);
    const [error,setError]=useState(null);

    useEffect(() =>{
      const fetchUser = async () => {
        try{
          const res=await fetch('http://localhost:5000/getuser',{
            methpd:'GET',
            credentials:'include'
          });
          if(res.ok){
            const data=await res.json();
            setUser(data);
          } else{
            setError('Failed to fetch user data');
          }
        } catch(error){
          setError('An error occured while fetching user data');
        } finally{
          setLoading(false);
        }
      };
      fetchUser();
    },[]);

    if(loading){
      return <div>Loading...</div>;
    }

    if(error){
      return <div>{error}</div>;
    }

    return (
    <div>
      <div>
        <h1>Hello, {user}</h1>
        <h2>Your expenses</h2>
        <table>
          <tr>
            <th>Category</th>
            <th>Amount</th>
          </tr>
          <tr>
            <td>Food</td>
            <td>$250</td>
          </tr>
          <tr>
            <td>Utilities</td>
            <td>$150</td>
          </tr>
          <tr>
            <td><b>Total</b></td>
            <td><b>$400</b></td>
          </tr>
        </table>
      </div>
      <div>
        <PieChart width={500} height={500}>
          <Pie data={data} dataKey={"amount"} outerRadius={150} fill='blue'/>
        </PieChart>
      </div>
    </div>
    );
}

export default Dashboard;