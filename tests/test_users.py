def test_create_user(client):
    response = client.post("/users", json={"name": "Mohit"})
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Mohit"


def test_create_user_empty_name(client):
    response = client.post("/users", json={"name": "   "})
    assert response.status_code == 422


def test_list_users(client):
    client.post("/users", json={"name": "Mohit"})
    client.post("/users", json={"name": "Rahul"})
    client.post("/users", json={"name": "Ankit"})

    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    names = [u["name"] for u in data]
    assert "Mohit" in names
    assert "Rahul" in names
    assert "Ankit" in names


def test_get_user_by_id(client):
    res = client.post("/users", json={"name": "Mohit", "email": "mohit@example.com"})
    user_id = res.json()["id"]

    res_get = client.get(f"/users/{user_id}")
    assert res_get.status_code == 200
    assert res_get.json()["name"] == "Mohit"
    assert res_get.json()["email"] == "mohit@example.com"


def test_get_nonexistent_user(client):
    response = client.get("/users/999")
    assert response.status_code == 404
