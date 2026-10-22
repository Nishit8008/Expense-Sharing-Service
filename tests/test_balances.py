def setup_users_and_trip(client):
    client.post("/users", json={"name": "Mohit"})   # id 1
    client.post("/users", json={"name": "Rahul"})   # id 2
    client.post("/users", json={"name": "Ankit"})   # id 3

    client.post("/groups", json={"name": "Goa Trip"})  # id 1
    client.post("/groups/1/members", json={"user_id": 1})
    client.post("/groups/1/members", json={"user_id": 2})
    client.post("/groups/1/members", json={"user_id": 3})


def test_example_scenario_balance_view(client):
    """
    Directly tests the example from Page 3, 4, 7 & 8 of the assignment document:
    Dinner = 1200, Paid by Mohit, Participants = Mohit, Rahul, Ankit
    Expected Result:
    Rahul owes Mohit 400
    Ankit owes Mohit 400
    """
    setup_users_and_trip(client)

    client.post("/expenses", json={
        "group_id": 1,
        "paid_by": 1,
        "amount": 1200,
        "description": "Dinner"
    })

    response = client.get("/balances")
    assert response.status_code == 200
    balances = response.json()

    expected = {
        "Rahul": {
            "owes": {
                "Mohit": 400
            }
        },
        "Ankit": {
            "owes": {
                "Mohit": 400
            }
        }
    }
    assert balances == expected


def test_pairwise_netting_balances(client):
    """
    Mohit pays 1200 for (Mohit, Rahul, Ankit) -> Rahul owes Mohit 400
    Rahul pays 300 for (Mohit, Rahul) -> Mohit owes Rahul 150
    Net: Rahul owes Mohit 250, Ankit owes Mohit 400
    """
    setup_users_and_trip(client)

    # Mohit pays 1200 for all 3
    client.post("/expenses", json={
        "group_id": 1,
        "paid_by": 1,
        "amount": 1200,
        "description": "Dinner"
    })

    # Rahul pays 300 split between Mohit and Rahul
    client.post("/expenses", json={
        "group_id": 1,
        "paid_by": 2,
        "amount": 300,
        "description": "Cab",
        "splits": [
            {"user_id": 1, "amount": 150},
            {"user_id": 2, "amount": 150}
        ]
    })

    response = client.get("/balances")
    assert response.status_code == 200
    balances = response.json()

    assert balances["Rahul"]["owes"]["Mohit"] == 250
    assert balances["Ankit"]["owes"]["Mohit"] == 400
    assert "Mohit" not in balances  # Mohit is a net creditor, doesn't owe anyone
