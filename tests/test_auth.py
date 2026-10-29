def test_register_user(client):
    response = client.post(
        "/users",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "rawpassword": "secret123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Registered!"
    assert "id" in data

def test_login_success(client):
    # First, register
    client.post("/users", json={
        "username": "bob",
        "email": "bob@example.com",
        "rawpassword": "pass123"
    })
    
    # Then, login
    response = client.post(
        "/login",
        json={
            "username": "bob",
            "password": "pass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    # Register
    client.post("/users", json={
        "username": "charlie",
        "email": "c@c.com",
        "rawpassword": "right_pass"
    })
    
    # Try wrong password
    response = client.post(
        "/login",
        json={
            "username": "charlie",
            "password": "wrong_pass"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"