def test_create_comment(client):
    client.post(
        "/register",
        json={
            "username": "commentuser",
            "email": "comment@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "comment@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    create_post_response = client.post(
        "/posts",
        json={
            "title": "Comment Post",
            "content": "This post will have a comment."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert create_post_response.status_code == 201

    post_id = create_post_response.json()["id"]

    response = client.post(
        f"/posts/{post_id}/comments",
        json={
            "content": "This is my first comment."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 201
    assert response.json()["content"] == "This is my first comment."
    assert "id" in response.json()
    assert "user_id" in response.json()
    assert response.json()["post_id"] == post_id

def test_create_comment_without_token(client):
    response = client.post(
        "/posts/1/comments",
        json={
            "content": "Unauthorized comment."
        }
    )

    assert response.status_code == 401

def test_create_comment_on_nonexistent_post(client):
    client.post(
        "/register",
        json={
            "username": "comment404user",
            "email": "comment404@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "comment404@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    response = client.post(
        "/posts/999999/comments",
        json={
            "content": "This post does not exist."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"

def test_get_comments(client):
    client.post(
        "/register",
        json={
            "username": "getcommentuser",
            "email": "getcomment@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "getcomment@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    create_post_response = client.post(
        "/posts",
        json={
            "title": "Comment Test Post",
            "content": "Post for testing comments."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert create_post_response.status_code == 201

    post_id = create_post_response.json()["id"]

    create_comment_response = client.post(
        f"/posts/{post_id}/comments",
        json={
            "content": "First comment."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert create_comment_response.status_code == 201

    response = client.get(f"/posts/{post_id}/comments")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["content"] == "First comment."
    assert response.json()[0]["post_id"] == post_id

def test_get_comments_nonexistent_post(client):
    response = client.get("/posts/999999/comments")

    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"

def test_update_comment(client):
    client.post(
        "/register",
        json={
            "username": "updatecommentuser",
            "email": "updatecomment@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "updatecomment@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    create_post_response = client.post(
        "/posts",
        json={
            "title": "Update Comment Post",
            "content": "Post for comment update."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert create_post_response.status_code == 201

    post_id = create_post_response.json()["id"]

    create_comment_response = client.post(
        f"/posts/{post_id}/comments",
        json={
            "content": "Old comment."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert create_comment_response.status_code == 201

    comment_id = create_comment_response.json()["id"]

    response = client.put(
        f"/comments/{comment_id}",
        json={
            "content": "Updated comment."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["id"] == comment_id
    assert response.json()["content"] == "Updated comment."

def test_update_comment_unauthorized(client):
    client.post(
        "/register",
        json={
            "username": "commentowner",
            "email": "commentowner@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "commentowner@example.com",
            "password": "password123"
        }
    )

    owner_token = login_response.json()["access_token"]

    create_post_response = client.post(
        "/posts",
        json={
            "title": "Comment Owner Post",
            "content": "This post has a comment."
        },
        headers={
            "Authorization": f"Bearer {owner_token}"
        }
    )

    assert create_post_response.status_code == 201

    post_id = create_post_response.json()["id"]

    create_comment_response = client.post(
        f"/posts/{post_id}/comments",
        json={
            "content": "Owner's comment."
        },
        headers={
            "Authorization": f"Bearer {owner_token}"
        }
    )

    assert create_comment_response.status_code == 201

    comment_id = create_comment_response.json()["id"]

    client.post(
        "/register",
        json={
            "username": "othercommentuser",
            "email": "othercomment@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "othercomment@example.com",
            "password": "password123"
        }
    )

    other_user_token = login_response.json()["access_token"]

    response = client.put(
        f"/comments/{comment_id}",
        json={
            "content": "Hacked comment."
        },
        headers={
            "Authorization": f"Bearer {other_user_token}"
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to update this comment"

def test_update_nonexistent_comment(client):
    client.post(
        "/register",
        json={
            "username": "comment404update",
            "email": "comment404update@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "comment404update@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    response = client.put(
        "/comments/999999",
        json={
            "content": "This comment does not exist."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found"

def test_delete_comment(client):
    client.post(
        "/register",
        json={
            "username": "deletecommentuser",
            "email": "deletecomment@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "deletecomment@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    create_post_response = client.post(
        "/posts",
        json={
            "title": "Delete Comment Post",
            "content": "Post for testing comment deletion."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert create_post_response.status_code == 201

    post_id = create_post_response.json()["id"]

    create_comment_response = client.post(
        f"/posts/{post_id}/comments",
        json={
            "content": "Comment to delete."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert create_comment_response.status_code == 201

    comment_id = create_comment_response.json()["id"]

    response = client.delete(
        f"/comments/{comment_id}",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Comment deleted successfully"

def test_delete_comment_unauthorized(client):
    # User A
    client.post(
        "/register",
        json={
            "username": "deletecommentowner",
            "email": "deletecommentowner@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "deletecommentowner@example.com",
            "password": "password123"
        }
    )

    owner_token = login_response.json()["access_token"]

    # Create post
    create_post_response = client.post(
        "/posts",
        json={
            "title": "Comment Owner Post",
            "content": "Post for delete authorization."
        },
        headers={
            "Authorization": f"Bearer {owner_token}"
        }
    )

    assert create_post_response.status_code == 201

    post_id = create_post_response.json()["id"]

    # User A creates comment
    create_comment_response = client.post(
        f"/posts/{post_id}/comments",
        json={
            "content": "Owner's comment."
        },
        headers={
            "Authorization": f"Bearer {owner_token}"
        }
    )

    assert create_comment_response.status_code == 201

    comment_id = create_comment_response.json()["id"]

    # User B
    client.post(
        "/register",
        json={
            "username": "deletecommentother",
            "email": "deletecommentother@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "deletecommentother@example.com",
            "password": "password123"
        }
    )

    other_user_token = login_response.json()["access_token"]

    # User B tries to delete User A's comment
    response = client.delete(
        f"/comments/{comment_id}",
        headers={
            "Authorization": f"Bearer {other_user_token}"
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to delete this comment"

def test_delete_nonexistent_comment(client):
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
        "/comments/999999",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found"

def test_create_comment_missing_content(client):
    client.post(
        "/register",
        json={
            "username": "validationcommentuser",
            "email": "validationcomment@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "validationcomment@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    create_post_response = client.post(
        "/posts",
        json={
            "title": "Validation Post",
            "content": "Post for validation testing."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert create_post_response.status_code == 201

    post_id = create_post_response.json()["id"]

    response = client.post(
        f"/posts/{post_id}/comments",
        json={},
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 422

def test_update_comment_missing_content(client):
    client.post(
        "/register",
        json={
            "username": "updatevalidationuser",
            "email": "updatevalidation@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "updatevalidation@example.com",
            "password": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    create_post_response = client.post(
        "/posts",
        json={
            "title": "Validation Post",
            "content": "Post for update validation."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert create_post_response.status_code == 201

    post_id = create_post_response.json()["id"]

    create_comment_response = client.post(
        f"/posts/{post_id}/comments",
        json={
            "content": "Original comment."
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert create_comment_response.status_code == 201

    comment_id = create_comment_response.json()["id"]

    response = client.put(
        f"/comments/{comment_id}",
        json={},
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 422