from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 🛠️ Create DB Tables on App Startup
with app.app_context():
    db.create_all()

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict
from uuid import uuid4

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database Models ---
class Expense(db.Model):
    id = db.Column(db.String, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String, nullable=False)
    paid_by = db.Column(db.String, nullable=False)
    participants = db.Column(db.String, nullable=False)  # Comma-separated names

# --- Initialize DB ---
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ✅ Create tables at startup
with app.app_context():
    db.create_all()

# --- API Routes ---

@app.route('/expenses', methods=['GET'])
def get_expenses():
    expenses = Expense.query.all()
    result = []
    for e in expenses:
        result.append({
            "id": e.id,
            "amount": e.amount,
            "description": e.description,
            "paid_by": e.paid_by,
            "participants": e.participants.split(",")
        })
    return jsonify({"success": True, "data": result}), 200

@app.route('/expenses', methods=['POST'])
def add_expense():
    data = request.get_json()
    try:
        amount = float(data['amount'])
        if amount <= 0:
            raise ValueError("Amount must be positive")
        description = data['description']
        paid_by = data['paid_by']
        participants = data.get('participants', [paid_by])

        if not description or not paid_by or not participants:
            return jsonify({"success": False, "message": "Missing required fields"}), 400

        expense = Expense(
            id=str(uuid4()),
            amount=amount,
            description=description,
            paid_by=paid_by,
            participants=",".join(participants)
        )
        db.session.add(expense)
        db.session.commit()

        return jsonify({"success": True, "data": {
            "amount": amount,
            "description": description,
            "paid_by": paid_by,
            "participants": participants
        }, "message": "Expense added successfully"}), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/expenses/<expense_id>', methods=['PUT'])
def update_expense(expense_id):
    data = request.get_json()
    expense = Expense.query.get(expense_id)
    if not expense:
        return jsonify({"success": False, "message": "Expense not found"}), 404

    expense.amount = float(data.get('amount', expense.amount))
    expense.description = data.get('description', expense.description)
    expense.paid_by = data.get('paid_by', expense.paid_by)
    expense.participants = ",".join(data.get('participants', expense.participants.split(",")))
    db.session.commit()

    return jsonify({"success": True, "message": "Expense updated"}), 200

@app.route('/expenses/<expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    expense = Expense.query.get(expense_id)
    if not expense:
        return jsonify({"success": False, "message": "Expense not found"}), 404
    db.session.delete(expense)
    db.session.commit()
    return jsonify({"success": True, "message": "Expense deleted"}), 200

@app.route('/people', methods=['GET'])
def get_people():
    expenses = Expense.query.all()
    people = set()
    for e in expenses:
        people.add(e.paid_by)
        people.update(e.participants.split(","))
    return jsonify({"success": True, "data": sorted(people)}), 200

@app.route('/balances', methods=['GET'])
def get_balances():
    balances = defaultdict(float)
    expenses = Expense.query.all()
    for e in expenses:
        participants = e.participants.split(",")
        share = e.amount / len(participants)
        for p in participants:
            balances[p] -= share
        balances[e.paid_by] += e.amount
    return jsonify({"success": True, "data": balances}), 200

@app.route('/settlements', methods=['GET'])
def get_settlements():
    balances = defaultdict(float)
    expenses = Expense.query.all()
    for e in expenses:
        participants = e.participants.split(",")
        share = e.amount / len(participants)
        for p in participants:
            balances[p] -= share
        balances[e.paid_by] += e.amount

    creditors = []
    debtors = []
    for person, balance in balances.items():
        if balance > 0:
            creditors.append([person, round(balance, 2)])
        elif balance < 0:
            debtors.append([person, round(balance, 2)])

    creditors.sort(key=lambda x: x[1], reverse=True)
    debtors.sort(key=lambda x: x[1])
    settlements = []

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

    return jsonify({"success": True, "data": settlements}), 200

# --- Run Server ---
if __name__ == "__main__":
    app.run(debug=True)
