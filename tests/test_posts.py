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

    assert response.status_code == 201
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

    assert create_response.status_code == 201

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

    assert create_response.status_code == 201

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

    assert create_response.status_code == 201

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

    assert create_response.status_code == 201

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

    assert create_response.status_code == 201

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

    assert create_response.status_code == 201

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

def test_get_post_with_comments(client):
    client.post(
        "/register",
        json={
            "username": "detailuser",
            "email": "detail@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "detail@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    create_post_response = client.post(
        "/posts",
        json={
            "title": "Post With Comments",
            "content": "Testing post details with comments."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert create_post_response.status_code == 201

    post_id = create_post_response.json()["id"]

    comment_response = client.post(
        f"/posts/{post_id}/comments",
        json={
            "content": "This is a test comment."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert comment_response.status_code == 201

    response = client.get(f"/posts/{post_id}")

    assert response.status_code == 200
    assert response.json()["id"] == post_id
    assert response.json()["title"] == "Post With Comments"
    assert response.json()["content"] == "Testing post details with comments."
    assert len(response.json()["comments"]) == 1
    assert response.json()["comments"][0]["content"] == "This is a test comment."

def test_get_posts_with_limit(client):
    client.post(
        "/register",
        json={
            "username": "limituser",
            "email": "limit@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "limit@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    for i in range(3):
        response = client.post(
            "/posts",
            json={
                "title": f"Post {i}",
                "content": f"Content {i}"
            },
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        assert response.status_code == 201

    response = client.get("/posts?limit=2")

    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_posts_with_skip(client):
    client.post(
        "/register",
        json={
            "username": "skipuser",
            "email": "skip@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "skip@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    for i in range(3):
        response = client.post(
            "/posts",
            json={
                "title": f"Post {i}",
                "content": f"Content {i}"
            },
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        assert response.status_code == 201

    response = client.get("/posts?skip=1")

    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_posts_with_title_filter(client):
    client.post(
        "/register",
        json={
            "username": "filteruser",
            "email": "filter@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "filter@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    posts = [
        ("Python Tutorial", "Learn Python"),
        ("FastAPI Guide", "Learn FastAPI"),
        ("Python Testing", "Learn pytest"),
    ]

    for title, content in posts:
        response = client.post(
            "/posts",
            json={
                "title": title,
                "content": content
            },
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        assert response.status_code == 201

    response = client.get("/posts?title=python")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["title"] == "Python Testing"
    assert response.json()[1]["title"] == "Python Tutorial"

def test_get_posts_sorted_oldest(client):
    client.post(
        "/register",
        json={
            "username": "sortuser",
            "email": "sort@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "sort@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    for i in range(3):
        response = client.post(
            "/posts",
            json={
                "title": f"Post {i}",
                "content": f"Content {i}"
            },
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        assert response.status_code == 201

    response = client.get("/posts?sort=oldest")

    assert response.status_code == 200
    assert len(response.json()) == 3
    assert response.json()[0]["title"] == "Post 0"
    assert response.json()[1]["title"] == "Post 1"
    assert response.json()[2]["title"] == "Post 2"

def test_get_posts_sorted_latest(client):
    client.post(
        "/register",
        json={
            "username": "latestuser",
            "email": "latest@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "latest@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    for i in range(3):
        response = client.post(
            "/posts",
            json={
                "title": f"Post {i}",
                "content": f"Content {i}"
            },
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        assert response.status_code == 201

    response = client.get("/posts?sort=latest")

    assert response.status_code == 200
    assert len(response.json()) == 3
    assert response.json()[0]["title"] == "Post 2"
    assert response.json()[1]["title"] == "Post 1"
    assert response.json()[2]["title"] == "Post 0"

def test_get_posts_invalid_limit(client):
    response = client.get("/posts?limit=0")

    assert response.status_code == 422

def test_get_posts_limit_too_large(client):
    response = client.get("/posts?limit=101")

    assert response.status_code == 422

def test_get_posts_negative_skip(client):
    response = client.get("/posts?skip=-1")

    assert response.status_code == 422

def test_get_posts_invalid_sort(client):
    response = client.get("/posts?sort=random")

    assert response.status_code == 422

def test_get_posts_no_results(client):
    response = client.get("/posts?title=doesnotexist")

    assert response.status_code == 200
    assert response.json() == []

def test_delete_nonexistent_post(client):
    client.post(
        "/register",
        json={
            "username": "delete404user",
            "email": "delete404@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "delete404@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    response = client.delete(
        "/posts/999999",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"

def test_update_post_missing_title(client):
    client.post(
        "/register",
        json={
            "username": "updatetitleuser",
            "email": "updatetitle@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "updatetitle@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    create_response = client.post(
        "/posts",
        json={
            "title": "Original Title",
            "content": "Original Content"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert create_response.status_code == 201

    post_id = create_response.json()["id"]

    response = client.put(
        f"/posts/{post_id}",
        json={
            "content": "Updated Content"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 422

def test_update_post_missing_content(client):
    client.post(
        "/register",
        json={
            "username": "updatecontentuser",
            "email": "updatecontent@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "updatecontent@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    create_response = client.post(
        "/posts",
        json={
            "title": "Original Title",
            "content": "Original Content"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert create_response.status_code == 201

    post_id = create_response.json()["id"]

    response = client.put(
        f"/posts/{post_id}",
        json={
            "title": "Updated Title"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 422

def test_create_post_short_title(client):
    client.post(
        "/register",
        json={
            "username": "shorttitleuser",
            "email": "shorttitle@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "shorttitle@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    response = client.post(
        "/posts",
        json={
            "title": "ab",
            "content": "This content is valid."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 422