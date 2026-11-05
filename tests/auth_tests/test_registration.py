def test_valid_url(client, db_session):
    from sqlalchemy import select
    from app.models.user import User


    response = client.post(
        '/auth/register',
        json = {"email":"user@gmail.com", "username":"user", "password":"password of user"}
    )

    assert response.status_code == 201, response.text

    body = response.json()

    assert body["Message"] == f"user Created Successfully."

    saved_user = db_session.scalar(select(User).where(User.username == "user"))

    assert saved_user is not None
    assert saved_user.email == "user@gmail.com"

def test_user_with_same_email(client):
    response = client.post(
        '/auth/register', 
        json = {"email":"user_email@gmail.com", "username":"user", "password":"password of user"}
    )

    assert response.status_code == 409, response.text

    assert response.json()["detail"] == "Email is already registered"

def test_user_with_same_username(client):
    response = client.post(
        '/auth/register', 
        json = {"email":"fresh@gmail.com", "username":"user_username", "password":"password of user"}
    )

    assert response.status_code == 409, response.text

    assert response.json()["detail"] == "Username is already taken"