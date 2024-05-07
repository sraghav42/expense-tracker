const express=require('express');
const app=express();
const {userAuth} =require("./middleware/TokenAuth");
const cookieParser = require('cookie-parser');
const path=require("path");

app.use(cookieParser());
app.use(express.json());

app.get('/app',(req,res) => res.sendFile(path.join(__dirname,'public','index.html')));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});