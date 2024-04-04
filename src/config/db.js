const mysql=require('mysql2');
const dotenv=require('dotenv');

dotenv.config();

const connection=mysql.createConnection({
    host : 'localhost',
    user : 'root',
    password : 'password',
    database : 'information_schema',
});

connection.connect((err) => {
    if(err){
        console.error('Error connecting to the database:',err);
        return;
    }
    console.log('Connected to the database');
});

module.exports=connection;