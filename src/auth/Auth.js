const getConnection = require('../config/db');
const bcrypt=require("bcryptjs")

exports.register = async (req,res,next) =>{
    const connection= await getConnection();
    const { username, password }=req.body; 

    if (password.length<6){
        return res.status(400).json({message: "Password must be at least 6 characters long"});
    }
    
    const sql="Insert into users(username,password) values(?,?)";

    try{
        const hash=await bcrypt.hash(password,10);
        const [results,fields]=await connection.query(sql,[username, hash]);
        console.log("User created successfully");
        const user={id:results.insertId, username,hash};
        return res.status(200).json({message:"User created successfully",user});
    }
    catch(err){
        console.error("Error creating user:",err);
        return res.status(401).json({message:"Error creating user"});
    }
};

exports.login = async (req,res,next) => {
    const connection= await getConnection();
    const {username,password}=req.body;

    if(!username || !password){
        return res.status(400).json({message:"Username or password is missing"})
    }

    const sql="Select * from users where username=?";

    try{
        const [rows,fields]=await connection.query(sql,[username]);
            
        if(rows[0].length===0){
            console.log("Login Failed");
            return res.status(401).json({message:"Login failed",error:"User not found"});
        }
        
        if(await bcrypt.compare(password,rows[0].password) ){
            console.log("Login user:",rows);
            return res.status(200).json({message:"Login successful",user:rows[0]});
        }
        else{
            res.status(401).json({message:"Login failed",error:"Incorrect password"})
        }
        

    } catch(error){
        console.log("An error occured",error);
        return res.status(400).json({message:"An error occured",error:error.message});
    }
};