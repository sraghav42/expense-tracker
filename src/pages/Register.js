import React from 'react';

const Register = () => {

    return (
        <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>Register Page</title>
        </head>
        <body>
            <h1>Register Page</h1>
            <form>
            <div class="error" ></div>
            <br />
            <label for="username">Username</label><br />
            <input type="text" id="username" required /><br />
            <label for="password">Password</label><br />
            <input type="password" id="password" required /><br />
            <input type="submit" value="register" /><br />
            </form>
            <a href="/login">Already registered? Login</a>
        </body>
        </html>
    );
};

export default Register;