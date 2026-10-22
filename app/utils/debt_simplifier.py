from typing import Dict, List, Tuple


def simplify_debts(net_balances: Dict[int, float], user_names: Dict[int, str]) -> List[dict]:
    """
    Minimizes cash flow using the greedy algorithm.
    Takes net_balances: {user_id: net_amount} where positive is creditor, negative is debtor.
    user_names: {user_id: name}
    Returns a list of simplified transactions:
    [
        {
            "from_user": "Rahul",
            "from_user_id": 2,
            "to_user": "Mohit",
            "to_user_id": 1,
            "amount": 400.0
        }
    ]
    """
    # Filter out near-zero balances (tolerance 0.01)
    balances = {uid: round(bal, 2) for uid, bal in net_balances.items() if abs(bal) > 0.009}

    transactions = []

    while balances:
        # Find maximum creditor (largest positive) and maximum debtor (largest negative)
        max_creditor_id = max(balances, key=balances.get)
        max_debtor_id = min(balances, key=balances.get)

        max_credit = balances[max_creditor_id]
        max_debt = balances[max_debtor_id]

        if max_credit <= 0.009 or max_debt >= -0.009:
            break

        settle_amount = round(min(max_credit, -max_debt), 2)

        if settle_amount > 0:
            transactions.append({
                "from_user": user_names.get(max_debtor_id, f"User_{max_debtor_id}"),
                "from_user_id": max_debtor_id,
                "to_user": user_names.get(max_creditor_id, f"User_{max_creditor_id}"),
                "to_user_id": max_creditor_id,
                "amount": settle_amount,
            })

            balances[max_creditor_id] = round(balances[max_creditor_id] - settle_amount, 2)
            balances[max_debtor_id] = round(balances[max_debtor_id] + settle_amount, 2)

        if abs(balances[max_creditor_id]) <= 0.009:
            del balances[max_creditor_id]
        if max_debtor_id in balances and abs(balances[max_debtor_id]) <= 0.009:
            del balances[max_debtor_id]

    return transactions
