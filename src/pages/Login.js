import React from 'react';

const Login = () => {

    return (
        <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>Login Page</title>
        </head>
        <body>
            <h1>Login Page</h1>
            <form>
            <div class="error"></div>
            <br />
            <label for="username">Username</label><br />
            <input type="text" id="username" required /><br />
            <label for="password">Password</label><br />
            <input type="password" id="password" required /><br />
            <input type="submit" value="login" /><br />
            </form>
            <a href="/register">Don't have an accout? Register</a>
        </body>
        </html>
    );
};

export default Login;