def get_auth_header(client):
    """Helper to register/login and return headers with token."""
    # Register
    client.post("/users", json={
        "username": "tester",
        "email": "tester@test.com",
        "rawpassword": "pass123"
    })
    # Login
    response = client.post("/login", json={
        "username": "tester",
        "password": "pass123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_bookmark_unauthorized(client):
    """Try to create a bookmark WITHOUT a token. Should fail 401."""
    response = client.post(
        "/bookmarks",
        json={"actual_url": "https://google.com"}
    )
    assert response.status_code == 401

def test_create_and_read_bookmark(client):
    """Create a bookmark WITH a token, then read it back."""
    headers = get_auth_header(client)
    
    # Create
    create_response = client.post(
        "/bookmarks",
        json={"actual_url": "https://example.com"},
        headers=headers
    )
    assert create_response.status_code == 200
    bookmark_data = create_response.json()
    assert bookmark_data["actual_url"] == "https://example.com"
    assert "id" in bookmark_data
    
    # Read Mine
    read_response = client.get(
        "/bookmarks/mine",
        headers=headers
    )
    assert read_response.status_code == 200
    bookmarks_list = read_response.json()
    assert len(bookmarks_list) >= 1
    assert bookmarks_list[0]["actual_url"] == "https://example.com"

def test_delete_bookmark_not_found(client):
    """Try to delete a non-existent ID. Should fail 404."""
    headers = get_auth_header(client)
    response = client.delete(
        "/bookmarks/9999",
        headers=headers
    )
    assert response.status_code == 404