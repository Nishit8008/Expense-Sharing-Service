from collections import defaultdict
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.expense import Expense, ExpenseSplit
from app.models.settlement import Settlement
from app.models.user import User
from app.models.group import GroupMember


def calculate_balances(db: Session, group_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Calculates pairwise netted balances between users across all groups or for a specific group.
    Returns format matching assignment specification:
    {
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
    """
    # Fetch all relevant users for mapping IDs to names
    users = {u.id: u.name for u in db.query(User).all()}

    # Matrix: pairwise_debts[debtor_id][creditor_id] = amount
    pairwise_debts: Dict[int, Dict[int, float]] = defaultdict(lambda: defaultdict(float))

    # 1. Process Expenses
    expense_query = db.query(Expense)
    if group_id is not None:
        expense_query = expense_query.filter(Expense.group_id == group_id)

    expenses = expense_query.all()
    for exp in expenses:
        payer_id = exp.paid_by
        splits = db.query(ExpenseSplit).filter(ExpenseSplit.expense_id == exp.id).all()
        for split in splits:
            debtor_id = split.user_id
            # The payer should not owe themselves
            if debtor_id != payer_id:
                pairwise_debts[debtor_id][payer_id] += split.amount

    # 2. Process Settlements
    settlement_query = db.query(Settlement)
    if group_id is not None:
        settlement_query = settlement_query.filter(Settlement.group_id == group_id)

    settlements = settlement_query.all()
    for st in settlements:
        payer_id = st.payer_id
        payee_id = st.payee_id
        # payer paid payee, reducing payer's debt to payee
        pairwise_debts[payer_id][payee_id] -= st.amount

    # 3. Net Pairwise Debts
    all_user_ids = sorted(list(users.keys()))
    net_pairwise: Dict[int, Dict[int, float]] = defaultdict(lambda: defaultdict(float))

    for i in range(len(all_user_ids)):
        for j in range(i + 1, len(all_user_ids)):
            u1 = all_user_ids[i]
            u2 = all_user_ids[j]

            debt_1_to_2 = pairwise_debts[u1][u2]
            debt_2_to_1 = pairwise_debts[u2][u1]
            diff = debt_1_to_2 - debt_2_to_1

            if diff > 0.009:
                net_pairwise[u1][u2] = round(diff, 2)
            elif diff < -0.009:
                net_pairwise[u2][u1] = round(-diff, 2)

    # 4. Construct Output JSON
    result: Dict[str, Any] = {}
    for debtor_id, creditors in net_pairwise.items():
        debtor_name = users.get(debtor_id, f"User_{debtor_id}")
        owes_map = {}
        for creditor_id, amount in creditors.items():
            if amount > 0.009:
                creditor_name = users.get(creditor_id, f"User_{creditor_id}")
                # Convert whole numbers to int (e.g., 400 instead of 400.0) for clean output matching PDF
                formatted_amount = int(amount) if amount == int(amount) else round(amount, 2)
                owes_map[creditor_name] = formatted_amount

        if owes_map:
            result[debtor_name] = {"owes": owes_map}

    return result


def calculate_net_user_balances(db: Session, group_id: Optional[int] = None) -> Dict[int, float]:
    """
    Calculates total net balance for each user.
    Positive: user is owed money (creditor)
    Negative: user owes money (debtor)
    """
    net_balances: Dict[int, float] = defaultdict(float)

    # Expenses
    expense_query = db.query(Expense)
    if group_id is not None:
        expense_query = expense_query.filter(Expense.group_id == group_id)

    expenses = expense_query.all()
    for exp in expenses:
        payer_id = exp.paid_by
        splits = db.query(ExpenseSplit).filter(ExpenseSplit.expense_id == exp.id).all()
        for split in splits:
            if split.user_id != payer_id:
                net_balances[payer_id] += split.amount
                net_balances[split.user_id] -= split.amount

    # Settlements
    settlement_query = db.query(Settlement)
    if group_id is not None:
        settlement_query = settlement_query.filter(Settlement.group_id == group_id)

    settlements = settlement_query.all()
    for st in settlements:
        net_balances[st.payer_id] += st.amount
        net_balances[st.payee_id] -= st.amount

    return {uid: round(val, 2) for uid, val in net_balances.items()}
