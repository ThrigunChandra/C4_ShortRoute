def create_account(c):
    account = {
            "email":"test_user@gmail.com",
            "username" : "test_user",
            "password": "test_user_password"
        }
    
    # Register and Login
    register = c.post(
        "/auth/register",
        json=account
    )
    assert register.status_code == 201, register.text
    login = c.post(
        "/auth/login",
        json={
            "email": account["email"],
            "password" : account["password"]
        }
    )
    assert login.status_code == 200, login.text 
    token = c.cookies.get("session_token")
    assert token 

    return register, login