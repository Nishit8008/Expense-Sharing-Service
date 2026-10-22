def test_amount_must_be_greater_than_zero(client):
    client.post("/users", json={"name": "Mohit"})
    client.post("/groups", json={"name": "Trip"})
    client.post("/groups/1/members", json={"user_id": 1})

    # Zero amount
    r1 = client.post("/expenses", json={
        "group_id": 1,
        "paid_by": 1,
        "amount": 0,
        "description": "Free item"
    })
    assert r1.status_code == 422

    # Negative amount
    r2 = client.post("/expenses", json={
        "group_id": 1,
        "paid_by": 1,
        "amount": -50,
        "description": "Refund"
    })
    assert r2.status_code == 422


def test_payer_not_in_group_rejected(client):
    client.post("/users", json={"name": "Mohit"})   # id 1
    client.post("/users", json={"name": "Stranger"}) # id 2
    client.post("/groups", json={"name": "Trip"})
    client.post("/groups/1/members", json={"user_id": 1})

    # Stranger (id 2) is not in group 1
    r = client.post("/expenses", json={
        "group_id": 1,
        "paid_by": 2,
        "amount": 100,
        "description": "Coffee"
    })
    assert r.status_code == 400
    assert "not a member" in r.json()["detail"]


def test_expense_on_empty_group_rejected(client):
    client.post("/users", json={"name": "Mohit"})
    client.post("/groups", json={"name": "Empty Group"})

    # Mohit is not in empty group
    r = client.post("/expenses", json={
        "group_id": 1,
        "paid_by": 1,
        "amount": 100,
        "description": "Coffee"
    })
    assert r.status_code == 400


def test_settlement_same_payer_and_payee_rejected(client):
    client.post("/users", json={"name": "Mohit"})

    r = client.post("/settlements", json={
        "payer_id": 1,
        "payee_id": 1,
        "amount": 100
    })
    assert r.status_code == 422
