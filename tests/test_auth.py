import uuid

def test_user_signup_and_login(client):
    user_data = {"email": f"test{uuid.uuid4()}@example.com", "password": "password123"}

    res = client.post("/auth/signup", json=user_data)
    assert res.status_code == 200

    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    res = client.post("/auth/login", data=login_data)
    assert res.status_code == 200
    assert "access_token" in res.json()