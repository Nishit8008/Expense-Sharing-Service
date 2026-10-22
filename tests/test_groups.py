def test_create_group(client):
    response = client.post("/groups", json={"name": "Goa Trip"})
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Goa Trip"


def test_add_user_to_group(client):
    # Setup user and group
    client.post("/users", json={"name": "Mohit"})
    client.post("/groups", json={"name": "Goa Trip"})

    response = client.post("/groups/1/members", json={"user_id": 1})
    assert response.status_code == 201
    assert response.json()["user_id"] == 1
    assert response.json()["group_id"] == 1


def test_add_duplicate_user_to_group(client):
    client.post("/users", json={"name": "Mohit"})
    client.post("/groups", json={"name": "Goa Trip"})

    res1 = client.post("/groups/1/members", json={"user_id": 1})
    assert res1.status_code == 201

    res2 = client.post("/groups/1/members", json={"user_id": 1})
    assert res2.status_code == 400
    assert "already a member" in res2.json()["detail"]


def test_list_group_members(client):
    client.post("/users", json={"name": "Mohit"})
    client.post("/users", json={"name": "Rahul"})
    client.post("/groups", json={"name": "Goa Trip"})

    client.post("/groups/1/members", json={"user_id": 1})
    client.post("/groups/1/members", json={"user_id": 2})

    response = client.get("/groups/1/members")
    assert response.status_code == 200
    members = response.json()
    assert len(members) == 2
    names = [m["name"] for m in members]
    assert "Mohit" in names
    assert "Rahul" in names


def test_get_group_details(client):
    client.post("/users", json={"name": "Mohit"})
    client.post("/groups", json={"name": "Goa Trip", "description": "Trip with college friends"})
    client.post("/groups/1/members", json={"user_id": 1})

    response = client.get("/groups/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Goa Trip"
    assert data["description"] == "Trip with college friends"
    assert len(data["members"]) == 1
