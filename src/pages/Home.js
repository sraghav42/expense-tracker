import React from "react";
import {PieChart, Pie} from 'recharts';

function Home() {
    const data=[
      {category:"Food", amount:250},
      {category:"Utlities", amount:150}
    ];

    return (
    <div>
      <div>
        <h1>Hello "Raghav"</h1>
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

export default Home;