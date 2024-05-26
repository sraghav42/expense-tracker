const express=require('express');
const getConnection=require("./src/config/db");
const cookieParser=require("cookie-parser");
const {userAuth}=require("./middleware/TokenAuth");
const cors=require('cors');

const app = express();
const PORT=5000;
const loginserver = app.listen(PORT, () => console.log(`Login server start at port ${PORT}`));

process.on("unhandledRejection",err => {
    console.log(`An error occured: ${err.message}`);
    loginserver.close(() => process.exit(1));
});

//getConnection();

app.use(cors({
    origin:'http://localhost:3000',
    credentials:true
}));
app.use(cookieParser());
app.use(express.json());
app.use("/api/auth",require("./src/auth/Route"));
app.get("/tokencheck",userAuth, (req, res) => res.send("User Route"));
app.get("/basic", userAuth, (req, res) => res.send("User Route"));
app.get('/logout',(req,res) => {
    res.cookie("jwt","",{ maxAge:"1"})
    res.status(200).json({message:"Logged out successfully"})
});