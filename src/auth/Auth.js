const getConnection = require('../config/db');
const connection=getConnection();

exports.register= (req,res,next) =>{
    
    const { username, password }=req.body; 

    if (password.length<6){
        return res.status(400).json({message: "Password must be at least 6 characters long"});
    }
    
    const sql="Insert into users(username,password) values(?,?)";
    const values=[username,password];

    try{
        connection.query(sql,values, (error,results) => {
            if(error){
                console.error("Error creating user:",error);
                return res.status(401).json({message:"Error creating user"});
            }
            console.log("User created successfully");
            const user={id:results.insertId, username,password};
            return res.status(200).json({message:"User created successfully",user});
        });
    }
    catch(err){
        console.error("Error creating user:",err);
        return res.status(401).json({message:"Error creating user"});
    }
};

exports.login=(req,res,next) => {
    const {username,password}=req.body;

    if(!username || !password){
        return res.status(400).json({message:"Username or password is missing"})
    }

    const sql="Select username from users where username=? and password=?";

    connection.query(sql,[username,password],(error,rows) => {
        if(error){
            console.log("An error occured",error);
            return res.status(400).json({message:"An error occured",error:error.message});
        }
        if(rows.length===0){
            console.log("User not found");
            return res.status(401).json({message:"Login failed",error:"User not found"});
        }
        
        console.log("Login user:",rows[0]);
        return res.status(200).json({message:"Login successful",user:rows[0]});
    })
};