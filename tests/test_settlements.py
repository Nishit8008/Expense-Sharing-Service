def setup_scenario(client):
    client.post("/users", json={"name": "Mohit"})   # id 1
    client.post("/users", json={"name": "Rahul"})   # id 2
    client.post("/users", json={"name": "Ankit"})   # id 3

    client.post("/groups", json={"name": "Goa Trip"})  # id 1
    client.post("/groups/1/members", json={"user_id": 1})
    client.post("/groups/1/members", json={"user_id": 2})
    client.post("/groups/1/members", json={"user_id": 3})

    # Dinner 1200 paid by Mohit
    client.post("/expenses", json={
        "group_id": 1,
        "paid_by": 1,
        "amount": 1200,
        "description": "Dinner"
    })


def test_settle_full_balance(client):
    """
    Tests Optional Bonus Feature (Page 11):
    Rahul pays Mohit 400
    Updated Balance: Rahul owes Mohit 0 (cleared from owes map)
    """
    setup_scenario(client)

    # Pre-check: Rahul owes Mohit 400
    b_before = client.get("/balances").json()
    assert b_before["Rahul"]["owes"]["Mohit"] == 400

    # Rahul settles 400 to Mohit
    settle_res = client.post("/settlements", json={
        "payer_id": 2,
        "payee_id": 1,
        "amount": 400,
        "group_id": 1,
        "notes": "Paid via UPI"
    })
    assert settle_res.status_code == 201

    # Post-check: Rahul owes Mohit 0 (Rahul eliminated from balances owes map)
    b_after = client.get("/balances").json()
    assert "Rahul" not in b_after or "Mohit" not in b_after.get("Rahul", {}).get("owes", {})
    # Ankit still owes Mohit 400
    assert b_after["Ankit"]["owes"]["Mohit"] == 400


def test_settle_partial_balance(client):
    setup_scenario(client)

    # Rahul settles partial amount 150 to Mohit
    client.post("/settlements", json={
        "payer_id": 2,
        "payee_id": 1,
        "amount": 150,
        "group_id": 1
    })

    b_after = client.get("/balances").json()
    assert b_after["Rahul"]["owes"]["Mohit"] == 250


def test_list_settlements(client):
    setup_scenario(client)

    client.post("/settlements", json={
        "payer_id": 2,
        "payee_id": 1,
        "amount": 400,
        "group_id": 1,
        "notes": "Google Pay"
    })

    res = client.get("/settlements?group_id=1")
    assert res.status_code == 200
    settlements = res.json()
    assert len(settlements) == 1
    assert settlements[0]["payer_name"] == "Rahul"
    assert settlements[0]["payee_name"] == "Mohit"
    assert settlements[0]["amount"] == 400.0
