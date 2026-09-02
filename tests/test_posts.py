def test_create_post(client):
    client.post(
        "/register",
        json={
            "username": "postuser",
            "email": "post@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "post@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    response = client.post(
        "/posts",
        json={
            "title": "my first post",
            "content": "this is my first post."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["title"] == "my first post"
    assert response.json()["content"] == "this is my first post."
    assert "id" in response.json()
    assert "user_id" in response.json()

def test_create_post_without_token(client):
    response = client.post(
        "/posts",
        json={
            "title": "Unauthorized Post",
            "content": "this should not be created."
        }
    )

    assert response.status_code == 401

def test_get_posts(client):
    client.post(
        "/register",
        json={
            "username": "getuser",
            "email": "get@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "get@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    create_response = client.post(
        "/posts",
        json={
            "title": "Test Post",
            "content": "Test Content"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert create_response.status_code == 200

    response = client.get("/posts")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Test Post"
    assert response.json()[0]["content"] == "Test Content"

def test_get_single_post(client):
    client.post(
        "/register",
        json={
            "username": "singlepostuser",
            "email": "singlepost@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "singlepost@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    create_response = client.post(
        "/posts",
        json={
            "title": "Single Post",
            "content": "Testing single post retrieval."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert create_response.status_code == 200

    post_id = create_response.json()["id"]

    response = client.get(f"/posts/{post_id}")

    assert response.status_code == 200
    assert response.json()["id"] == post_id
    assert response.json()["title"] == "Single Post"
    assert response.json()["content"] == "Testing single post retrieval."

def test_get_nonexistent_post(client):
    response = client.get("/posts/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"

def test_update_post(client):
    client.post(
        "/register",
        json={
            "username": "updateuser",
            "email": "update@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "update@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    create_response = client.post(
        "/posts",
        json={
            "title": "Old Title",
            "content": "Old Content"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert create_response.status_code == 200

    post_id = create_response.json()["id"]

    response = client.put(
        f"/posts/{post_id}",
        json={
            "title": "Updated Title",
            "content": "Updated Content"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["id"] == post_id
    assert response.json()["title"] == "Updated Title"
    assert response.json()["content"] == "Updated Content"

def test_update_post_unauthorized(client):
    client.post(
        "/register",
        json={
            "username": "owner",
            "email": "owner@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "owner@example.com",
            "password": "password123"
        }
    )

    owner_token = login_response.json()["access_token"]

    create_response = client.post(
        "/posts",
        json={
            "title": "Owner Post",
            "content": "This belongs to User A."
        },
        headers={
            "Authorization": f"Bearer {owner_token}"
        }
    )

    assert create_response.status_code == 200

    post_id = create_response.json()["id"]

    client.post(
        "/register",
        json={
            "username": "otheruser",
            "email": "other@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "other@example.com",
            "password": "password123"
        }
    )

    other_user_token = login_response.json()["access_token"]

    response = client.put(
        f"/posts/{post_id}",
        json={
            "title": "Hacked Title",
            "content": "User B should not be able to do this."
        },
        headers={
            "Authorization": f"Bearer {other_user_token}"
        }
    )

    assert response.status_code == 403

def test_delete_post(client):
    client.post(
        "/register",
        json={
            "username": "deleteuser",
            "email": "delete@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "delete@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    create_response = client.post(
        "/posts",
        json={
            "title": "Post To Delete",
            "content": "This post will be deleted."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert create_response.status_code == 200

    post_id = create_response.json()["id"]

    response = client.delete(
        f"/posts/{post_id}",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    get_response = client.get(f"/posts/{post_id}")

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Post not found"

def test_delete_post_unauthorized(client):
    client.post(
        "/register",
        json={
            "username": "deleteowner",
            "email": "deleteowner@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "deleteowner@example.com",
            "password": "password123"
        }
    )

    owner_token = login_response.json()["access_token"]

    create_response = client.post(
        "/posts",
        json={
            "title": "Owner Post",
            "content": "This belongs to User A."
        },
        headers={
            "Authorization": f"Bearer {owner_token}"
        }
    )

    assert create_response.status_code == 200

    post_id = create_response.json()["id"]

    client.post(
        "/register",
        json={
            "username": "deleteother",
            "email": "deleteother@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "deleteother@example.com",
            "password": "password123"
        }
    )

    other_user_token = login_response.json()["access_token"]

    response = client.delete(
        f"/posts/{post_id}",
        headers={
            "Authorization": f"Bearer {other_user_token}"
        }
    )

    assert response.status_code == 403

def test_create_post_missing_title(client):
    client.post(
        "/register",
        json={
            "username": "validationuser",
            "email": "validation@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "validation@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    response = client.post(
        "/posts",
        json={
            "content": "This post has no title."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 422

def test_create_post_missing_content(client):
    client.post(
        "/register",
        json={
            "username": "validationcontent",
            "email": "validationcontent@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "validationcontent@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    response = client.post(
        "/posts",
        json={
            "title": "Post Without Content"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 422

def test_create_post_null_title(client):
    client.post(
        "/register",
        json={
            "username": "nulltitle",
            "email": "nulltitle@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "nulltitle@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    response = client.post(
        "/posts",
        json={
            "title": None,
            "content": "This has a null title."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 422

def test_get_post_invalid_id(client):
    response = client.get("/posts/abc")

    assert response.status_code == 422

def test_create_post_invalid_token(client):
    response = client.post(
        "/posts",
        json={
            "title": "Fake Token Post",
            "content": "This should not be created."
        },
        headers={
            "Authorization": "Bearer fake-invalid-token"
        }
    )

    assert response.status_code == 401

