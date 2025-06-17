# Split-App---Backend-Assignment
Core Features Implemented:
Expense Tracking
POST /expenses: Add an expense (amount, description, paid_by, participants).
GET /expenses: Retrieve all expenses.
PUT /expenses/<id>: Update an existing expense.
DELETE /expenses/<id>: Delete an expense.

Participant Management
GET /people: Get a unique list of all participants involved in any expense.

Balance Calculation
GET /balances: Shows how much each person owes or is owed.

Settlement Suggestions
GET /settlements: Auto-calculates who should pay whom to settle all debts fairly and efficiently.

💾 Database Support
Uses SQLite via SQLAlchemy ORM to persist expenses.


