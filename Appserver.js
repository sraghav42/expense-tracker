const express=require('express');
const app=express();
const {userAuth} =require("./middleware/TokenAuth");
const cookieParser = require('cookie-parser');

app.use(cookieParser());
app.use(express.json());

app.get('/app',userAuth,(req,res) => res.send("Dashboard"));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});