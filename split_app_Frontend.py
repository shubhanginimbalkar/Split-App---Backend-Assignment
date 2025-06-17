import streamlit as st
import uuid
from collections import defaultdict

# --- Session State Setup ---
if "expenses" not in st.session_state:
    st.session_state.expenses = []

# --- Helper Functions ---
def add_expense(amount, description, paid_by, participants):
    expense = {
        "id": str(uuid.uuid4()),
        "amount": float(amount),
        "description": description,
        "paid_by": paid_by,
        "participants": participants
    }
    st.session_state.expenses.append(expense)

def delete_expense(expense_id):
    st.session_state.expenses = [e for e in st.session_state.expenses if e["id"] != expense_id]

def calculate_balances():
    balances = defaultdict(float)
    for expense in st.session_state.expenses:
        share = expense["amount"] / len(expense["participants"])
        for person in expense["participants"]:
            balances[person] -= share
        balances[expense["paid_by"]] += expense["amount"]
    return balances

def simplify_debts(balances):
    creditors = []
    debtors = []
    for person, balance in balances.items():
        if balance > 0:
            creditors.append([person, round(balance, 2)])
        elif balance < 0:
            debtors.append([person, round(balance, 2)])

    settlements = []
    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1])

    while debtors and creditors:
        debtor, debt = debtors[0]
        creditor, credit = creditors[0]
        settled_amount = min(-debt, credit)
        settlements.append(f"{debtor} pays ₹{settled_amount:.2f} to {creditor}")

        debtors[0][1] += settled_amount
        creditors[0][1] -= settled_amount

        if abs(debtors[0][1]) < 1e-2:
            debtors.pop(0)
        if abs(creditors[0][1]) < 1e-2:
            creditors.pop(0)
    return settlements

# --- Streamlit App UI ---
st.title("💸 Split App - Expense Splitter")
st.markdown("Easily split bills among friends and track settlements.")

st.header("➕ Add Expense")
with st.form("add_expense_form"):
    amount = st.number_input("Amount (₹)", min_value=1.0, step=1.0)
    description = st.text_input("Description")
    paid_by = st.text_input("Paid by (Name)")
    participants_input = st.text_input("Participants (comma-separated names)")
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        participants = [name.strip() for name in participants_input.split(",") if name.strip()]
        if not description or not paid_by or not participants:
            st.error("All fields are required.")
        else:
            add_expense(amount, description, paid_by, participants)
            st.success("Expense added!")

st.header("📋 All Expenses")
if st.session_state.expenses:
    for expense in st.session_state.expenses:
        st.write(f"**{expense['description']}** - ₹{expense['amount']:.2f} | Paid by: {expense['paid_by']} | Split between: {', '.join(expense['participants'])}")
        if st.button("Delete", key=expense["id"]):
            delete_expense(expense["id"])
            st.experimental_rerun()
else:
    st.info("No expenses added yet.")

st.header("📊 Balances")
balances = calculate_balances()
if balances:
    for person, balance in balances.items():
        status = "owes" if balance < 0 else "gets"
        st.write(f"**{person}** {status} ₹{abs(balance):.2f}")
else:
    st.info("No balances to show.")

st.header("🤝 Settlement Summary")
settlements = simplify_debts(balances)
if settlements:
    for s in settlements:
        st.success(s)
else:
    st.info("All settled up!")

# Footer
st.markdown("---")
st.caption("Built with ❤️ using Streamlit | Example: Shantanu, Sanket, Om")
