const getConnection = require('../config/db');

exports.register=async (req,res,next) =>{
    const connection=getConnection();
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
                return res.status(500).json({message:"Error creating user"});
            }
            console.log("User created successfully");
            const user={id:results.insertId, username,password};
            return res.status(200).json({message:"User created successfully",user});
        });
    }
    catch(err){
        console.error("Error creating user:",err);
        return res.status(500).json({message:"Error creating user"});
    }
};