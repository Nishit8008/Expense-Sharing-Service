def setup_goa_trip(client):
    client.post("/users", json={"name": "Mohit"})
    client.post("/users", json={"name": "Rahul"})
    client.post("/users", json={"name": "Ankit"})

    client.post("/groups", json={"name": "Goa Trip"})
    client.post("/groups/1/members", json={"user_id": 1})
    client.post("/groups/1/members", json={"user_id": 2})
    client.post("/groups/1/members", json={"user_id": 3})


def test_add_expense_equal_split(client):
    setup_goa_trip(client)

    response = client.post("/expenses", json={
        "group_id": 1,
        "paid_by": 1,
        "amount": 1200,
        "description": "Dinner"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 1200
    assert data["paid_by"] == "Mohit"
    assert data["split_type"] == "EQUAL"
    assert len(data["splits"]) == 3
    # Check that each member has 400
    for split in data["splits"]:
        assert split["amount"] == 400.0


def test_list_group_expenses(client):
    setup_goa_trip(client)

    client.post("/expenses", json={
        "group_id": 1,
        "paid_by": 1,
        "amount": 1200,
        "description": "Dinner"
    })

    response = client.get("/groups/1/expenses")
    assert response.status_code == 200
    expenses = response.json()
    assert len(expenses) == 1
    assert expenses[0] == {
        "description": "Dinner",
        "amount": 1200,
        "paid_by": "Mohit"
    }


def test_unequal_custom_split(client):
    setup_goa_trip(client)

    response = client.post("/expenses", json={
        "group_id": 1,
        "paid_by": 1,
        "amount": 1000,
        "description": "Hotel",
        "splits": [
            {"user_id": 1, "amount": 500},
            {"user_id": 2, "amount": 300},
            {"user_id": 3, "amount": 200}
        ]
    })
    assert response.status_code == 201
    data = response.json()
    assert data["split_type"] == "EXACT"
    splits = {s["user_id"]: s["amount"] for s in data["splits"]}
    assert splits[1] == 500.0
    assert splits[2] == 300.0
    assert splits[3] == 200.0


def test_unequal_split_mismatch_sum_rejected(client):
    setup_goa_trip(client)

    response = client.post("/expenses", json={
        "group_id": 1,
        "paid_by": 1,
        "amount": 1000,
        "description": "Hotel",
        "splits": [
            {"user_id": 1, "amount": 500},
            {"user_id": 2, "amount": 300},
            {"user_id": 3, "amount": 100}  # Sums to 900 != 1000
        ]
    })
    assert response.status_code == 400
    assert "Sum of custom splits" in response.json()["detail"]


def test_penny_rounding_equal_split(client):
    setup_goa_trip(client)

    # 100 divided among 3 people: 33.34, 33.33, 33.33
    response = client.post("/expenses", json={
        "group_id": 1,
        "paid_by": 1,
        "amount": 100,
        "description": "Snacks"
    })
    assert response.status_code == 201
    data = response.json()
    total_split_sum = sum(s["amount"] for s in data["splits"])
    assert round(total_split_sum, 2) == 100.00
