def create_account(client, user):
    account = {
        "email": f"{user}@gmail.com",
        "username": user,
        "password": f"{user}_password"
    }

    # Register and log in
    register = client.post("/auth/register", json=account)
    assert register.status_code == 201, register.text

    login = client.post(
        "/auth/login",
        json={
            "email": account["email"],
            "password": account["password"]
        }
    )
    assert login.status_code == 200, login.text
    assert client.cookies.get("session_token")

    return register, login
