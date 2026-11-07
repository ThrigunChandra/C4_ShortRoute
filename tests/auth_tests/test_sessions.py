# Three tasks Login -> Check Me -> Logout 
def test_login_me_logout(client):
    # User Account details 
    account = {
        "username" : "user",
        "email" : "user@example.com",
        "password" : "userpassword"
    }


    # # Register request 
    registered = client.post(
        "/auth/register",
        json = account
    )
    assert registered.status_code == 201, registered.text 

    ## Login Request 
    login = client.post("/auth/login", json={
        "email":account["email"],
        "password" : account["password"]
    })
    assert login.status_code == 200, login.text 

    # Check for token
    token = client.cookies.get("session_token")
    assert token 


    # # Check for me 
    me = client.get("/auth/me")

    assert me.status_code == 200, me.text 
    assert me.json()["username"] == account["username"]
    assert me.json()["membership_tier"] == "free"

    logout = client.post("/auth/logout")

    assert logout.status_code == 200, logout.text
    assert client.cookies.get("session_token") is None

    replay = client.get("/auth/me", headers={"Cookie": f"session_token={token}"})

    assert replay.status_code == 401, replay.text 

def test_invalid_email(client):
    response = client.post(
        "/auth/login",
        json = {
            "email":"not_registered@gmail.com",
            "password":"just need to fill requirements 8 letters"
        }
    )

    assert response.status_code == 401, response.text 
    assert response.json()["detail"] == "Invalid email or password"

def test_invalid_password(client):
    register = client.post(
        "/auth/register", 
        json={
            "email":"right_email@gmail.com",
            "username":"right_email",
            "password":"right_email_password"
        }
    )

    assert register.status_code == 201, register.text 
    assert register.json()['Message'] == f"right_email Created Successfully."

    response = client.post(
        "/auth/login",
        json={
            "email"         :   "right_email@gmail.com",
            # It doesn't matter though 
            "password"      :   "wrong_password"
        }
    )

    assert response.status_code == 401, response.text 
    assert response.json()["detail"] == "Invalid email or password"


def test_login_login_again_without_login(client):
    # Account 
    account = {
        "email":"registered@gmail.com",
        "username":"registered",
        "password":"registeredpassword"
    }

    # Register the user Account 
    register = client.post(
        "/auth/register",
        json=account
    )

    assert register.status_code == 201, register.text 
    assert register.json()["Message"] == "registered Created Successfully."

    # Send login 
    responseA = client.post(
        "/auth/login",
        json={
            "email" : account["email"],
            "password": account["password"]
        }
    )

    assert responseA.status_code == 200, responseA.text
    assert responseA.json()["message"] == "Login Successful"

    tokenA = client.cookies.get("session_token")

    assert tokenA

    # Send login again 
    responseB = client.post(
        "/auth/login",
        json={
            "email" : account["email"],
            "password": account["password"]
        }
    )

    assert responseB.status_code == 200, responseB.text 
    assert responseB.json()['message'] == "Login Successful"

    tokenB = client.cookies.get("session_token")

    assert tokenB

    assert tokenA != tokenB