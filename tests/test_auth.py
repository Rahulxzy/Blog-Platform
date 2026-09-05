def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "hello world"}

def test_register_user(client):
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 201
    assert response.json()["username"] == "testuser"
    assert response.json()["email"] == "test@example.com"
    assert "password" not in response.json()

def test_register_duplicate_email(client):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }

    response = client.post("/register", json=user_data)
    assert response.status_code == 201

    duplicate_response = client.post(
        "/register",
        json={
            "username": "anotheruser",
            "email": "test@example.com",
            "password": "password123"
        }
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == "email already registered"

def test_login(client):
    client.post(
        "/register",
        json = {
            "username": "loginuser",
            "email":"login@example.com",
            "password": "password123"
        }
    )

    response = client.post(
        "/auth/login",
        data={
            "username":"login@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password(client):
    client.post(
        "/register",
        json={
            "username": "wrongpassuser",
            "email": "wrongpass@example.com",
            "password": "password123"
        }
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "wrongpass@example.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

def test_login_unknown_email(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "doesnotexist@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

def test_get_me(client):
    client.post(
        "/register",
        json={
            "username": "meuser",
            "email": "me@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username" :"me@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["username"] == "meuser"
    assert response.json()["email"] == "me@example.com"

def test_get_me_without_token(client):
    response = client.get("/me")

    assert response.status_code == 401

