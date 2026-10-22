# Expense Sharing Service — Decentro SDE Assignment

A backend service built with **Python 3.13**, **FastAPI**, and **SQLAlchemy** to track group expenses, calculate split balances, and record debt settlements.

---

## 1. Quick Setup & Run

### Local Setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate | macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python run.py
```
- Interactive API Docs: `http://localhost:8000/docs`

### Docker Setup
```bash
docker-compose up --build -d
```

### Run Tests
```bash
pytest -v
```

---

## 2. Architecture Overview

Follows a layered clean architecture:
- `app/models/`: SQLAlchemy ORM database models.
- `app/schemas/`: Pydantic v2 schemas for request validation & response serialization.
- `app/services/`: Core business logic (splits, netting, settlements, analytics).
- `app/routers/`: FastAPI endpoint routes (`/users`, `/groups`, `/expenses`, `/balances`, `/settlements`).
- `app/utils/`: Graph simplification algorithms (`debt_simplifier.py`).

---

## 3. Database Schema

- **`users`**: `id` (PK), `name`, `email`, `created_at`
- **`groups`**: `id` (PK), `name`, `description`, `created_at`
- **`group_members`**: `id` (PK), `group_id` (FK), `user_id` (FK), `UNIQUE(group_id, user_id)`
- **`expenses`**: `id` (PK), `group_id` (FK), `paid_by` (FK), `amount`, `description`, `category`, `split_type`, `created_at`
- **`expense_splits`**: `id` (PK), `expense_id` (FK), `user_id` (FK), `amount`, `UNIQUE(expense_id, user_id)`
- **`settlements`**: `id` (PK), `payer_id` (FK), `payee_id` (FK), `group_id` (FK), `amount`, `notes`, `created_at`

---

## 4. Key API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/users` | Create user (`{"name": "Mohit"}`) |
| `GET` | `/users` | List all users |
| `POST` | `/groups` | Create group (`{"name": "Goa Trip"}`) |
| `POST` | `/groups/{id}/members` | Add user to group (`{"user_id": 2}`) |
| `GET` | `/groups/{id}/members` | List members of a group |
| `POST` | `/expenses` | Record expense (equal or custom split) |
| `GET` | `/groups/{id}/expenses` | List group expenses (`[{"description", "amount", "paid_by"}]`) |
| `GET` | `/balances` | View pairwise balances between users |
| `POST` | `/settlements` | Settle balances (`payer_id`, `payee_id`, `amount`) |
| `GET` | `/groups/{id}/analytics` | Category breakdown & member spending stats |
| `GET` | `/balances/simplify` | Smart debt simplification (Min-Cash-Flow) |
| `GET` | `/groups/{id}/export/csv`| Export group expenses to CSV |

---

## 5. Product Enhancement: Spending Analytics & Smart Debt Simplification

### Feature 1: Category Analytics (`GET /groups/{id}/analytics`)
- **Why chosen**: Users need visibility into where their money is spent (Food, Travel, Stay), not just who owes whom.
- **Problem it solves**: Prevents budget overruns by highlighting major expense categories and identifying top spenders.
- **Design decisions & Tradeoffs**: Computed dynamically on query to eliminate cache synchronization overhead, ideal for standard group sizes.

### Feature 2: Smart Debt Simplification (`GET /balances/simplify`)
- **Why chosen**: Simplifies circular debts (if A owes B ₹100 and B owes C ₹100, A pays C ₹100 directly).
- **Algorithm**: Greedy Min-Cash-Flow algorithm minimizing total transactions from $O(N^2)$ to at most $N-1$.

---

## 6. Assumptions & Design Decisions

1. **Penny Rounding**: Splitting ₹100 among 3 users divides into ₹33.34, ₹33.33, ₹33.33 so total splits always equal the exact expense amount.
2. **Payer Share**: Payers do not owe themselves; their share is counted as self-funded.
3. **Database Portability**: SQLite by default for zero-config startup, fully compatible with PostgreSQL via `DATABASE_URL`.
4. **Custom Splits**: Supports both default equal splits and custom unequal splits (`splits: [{"user_id": 1, "amount": 500}, ...]`).

---

## 7. Improvements With More Time

1. **Authentication**: JWT-based user login and role-based access control.
2. **Push Notifications**: Real-time webhook/email notifications on expense additions.
3. **Receipt Scanning**: OCR extraction for bill receipts.
4. **Multi-Currency Support**: Real-time currency conversions.
