const mysql=require('mysql2');
//const dotenv=require('dotenv');

//dotenv.config();

function getConnection(){
    const connection=mysql.createConnection({
        //need to figure out how to use .env variables
        host : 'localhost',
        user : 'root',
        password : 'password',
        database : 'expense_tracker_db',
    });

    connection.connect((err) => {
        if(err){
            console.error('Error connecting to the database:',err);
            return;
        }
        console.log('Connected to the database');
    });
    return connection;
}

module.exports=getConnection;