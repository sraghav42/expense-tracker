const express=require('express');
const getConnection=require("./src/config/db");

const app = express();
const PORT=5000;
const loginserver = app.listen(PORT, () => console.log(`Login server start at port ${PORT}`));

process.on("unhandledRejection",err => {
    console.log(`An error occured: ${err.message}`);
    loginserver.close(() => process.exit(1));
});

//getConnection();

app.use(express.json());
app.use("/api/auth",require("./src/auth/Route"));