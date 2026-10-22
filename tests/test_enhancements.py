def setup_complex_group(client):
    client.post("/users", json={"name": "Alice"})   # id 1
    client.post("/users", json={"name": "Bob"})     # id 2
    client.post("/users", json={"name": "Charlie"}) # id 3

    client.post("/groups", json={"name": "Euro Trip"})  # id 1
    client.post("/groups/1/members", json={"user_id": 1})
    client.post("/groups/1/members", json={"user_id": 2})
    client.post("/groups/1/members", json={"user_id": 3})


def test_spending_analytics_and_categories(client):
    setup_complex_group(client)

    # Food expense: 300
    client.post("/expenses", json={
        "group_id": 1,
        "paid_by": 1,
        "amount": 300,
        "description": "Italian Dinner",
        "category": "Food"
    })
    # Travel expense: 600
    client.post("/expenses", json={
        "group_id": 1,
        "paid_by": 2,
        "amount": 600,
        "description": "Train Tickets",
        "category": "Travel"
    })

    res = client.get("/groups/1/analytics")
    assert res.status_code == 200
    analytics = res.json()

    assert analytics["total_group_spending"] == 900.0
    assert analytics["total_expenses_count"] == 2
    assert analytics["top_spender"] == "Bob"

    categories = {c["category"]: c for c in analytics["category_breakdown"]}
    assert "Travel" in categories
    assert categories["Travel"]["amount"] == 600.0
    assert categories["Travel"]["percentage"] == 66.7
    assert categories["Food"]["amount"] == 300.0
    assert categories["Food"]["percentage"] == 33.3


def test_smart_debt_simplification(client):
    """
    Test Min Cash Flow algorithm:
    Alice pays 300 for Alice & Bob (Bob owes Alice 150)
    Bob pays 300 for Bob & Charlie (Charlie owes Bob 150)
    Normally: Bob -> Alice 150 AND Charlie -> Bob 150 (2 transactions)
    Simplified: Charlie -> Alice 150 directly! (1 transaction, Bob does nothing!)
    """
    setup_complex_group(client)

    # Alice pays 300 split between Alice and Bob
    client.post("/expenses", json={
        "group_id": 1,
        "paid_by": 1,
        "amount": 300,
        "description": "Lunch",
        "splits": [
            {"user_id": 1, "amount": 150},
            {"user_id": 2, "amount": 150}
        ]
    })

    # Bob pays 300 split between Bob and Charlie
    client.post("/expenses", json={
        "group_id": 1,
        "paid_by": 2,
        "amount": 300,
        "description": "Museum",
        "splits": [
            {"user_id": 2, "amount": 150},
            {"user_id": 3, "amount": 150}
        ]
    })

    res = client.get("/balances/simplify?group_id=1")
    assert res.status_code == 200
    data = res.json()

    # Bob's net balance is 0 (+150 from Charlie, -150 to Alice)
    # Only 1 transaction is needed: Charlie pays Alice 150
    assert len(data["transactions"]) == 1
    txn = data["transactions"][0]
    assert txn["from_user"] == "Charlie"
    assert txn["to_user"] == "Alice"
    assert txn["amount"] == 150.0


def test_search_expenses(client):
    setup_complex_group(client)

    client.post("/expenses", json={
        "group_id": 1,
        "paid_by": 1,
        "amount": 120,
        "description": "Dinner at Beach",
        "category": "Food"
    })
    client.post("/expenses", json={
        "group_id": 1,
        "paid_by": 2,
        "amount": 500,
        "description": "Flight Ticket",
        "category": "Travel"
    })

    # Search by keyword
    r1 = client.get("/expenses/search?q=Beach")
    assert r1.status_code == 200
    assert len(r1.json()) == 1
    assert r1.json()[0]["description"] == "Dinner at Beach"

    # Search by category
    r2 = client.get("/expenses/search?category=Travel")
    assert r2.status_code == 200
    assert len(r2.json()) == 1
    assert r2.json()[0]["description"] == "Flight Ticket"

    # Filter by min_amount
    r3 = client.get("/expenses/search?min_amount=200")
    assert r3.status_code == 200
    assert len(r3.json()) == 1
    assert r3.json()[0]["amount"] == 500.0


def test_export_csv(client):
    setup_complex_group(client)

    client.post("/expenses", json={
        "group_id": 1,
        "paid_by": 1,
        "amount": 250,
        "description": "Groceries",
        "category": "Food"
    })

    res = client.get("/groups/1/export/csv")
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/csv")
    content = res.text
    assert "Expense ID,Description,Amount,Category,Paid By,Split Type,Date" in content
    assert "Groceries" in content
    assert "Alice" in content
