const mysql=require('mysql2/promise');
//const dotenv=require('dotenv');

//dotenv.config();

async function getConnection(){
    try{
        const connection=await mysql.createConnection({
            //need to figure out how to use .env variables
            host : 'localhost',
            user : 'root',
            password : 'password',
            database : 'expense_tracker_db',
        });

        console.log('Connected to the database');
        return connection;
    }catch(error){
        console.log("Error connecting to database:",error);
        throw error;
    }
}

module.exports=getConnection;