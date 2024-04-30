const jwt=require("jsonwebtoken");
const jwtSecret='6ea937c788668eeb860f94c4adbae1310f832fd03fa3342b2996e685c6bfd0c1da2524';

exports.userAuth = (req,res,next) => {
    const token=req.cookies.jwt
    if(token){
        jwt.verify(token,jwtSecret,(err,decodedToken) => {
            if(err){
                return res.status(401).json({message:"Not Authorized"});
            } else{
                next();
            }
        })
    } else{
        return res.status(401).json({message:"Not authorized, token not available"});
    }
}