from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd  # For Excel export
import io  # In-memory stream for file handling

# ----------------------- #
# Flask App Configuration
# ----------------------- #

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gymtracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with app
db = SQLAlchemy(app)

# ----------------------- #
# Database Models
# ----------------------- #

# Income model: tracks income from men and girls on a date
class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    men = db.Column(db.Integer, nullable=False)
    girls = db.Column(db.Integer, nullable=False)

# Expense model: tracks expense category and amount on a date
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)

# ----------------------- #
# Routes
# ----------------------- #

# Redirect root to the income entry page
@app.route('/')
def home():
    return redirect(url_for('add_income'))

# ---- INCOME ---- #

# Add a new income record
@app.route('/income', methods=['GET', 'POST'])
def add_income():
    if request.method == 'POST':
        # Extract form data
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        men = int(request.form['men'])
        girls = int(request.form['girls'])

        # Save to database
        new_income = Income(date=date, men=men, girls=girls)
        db.session.add(new_income)
        db.session.commit()

        return redirect(url_for('view_income'))

    return render_template('income.html')

# View all income records
@app.route('/income/view')
def view_income():
    incomes = Income.query.order_by(Income.date.desc()).all()
    # Total income = sum of men + girls
    total_income = db.session.query(
        db.func.coalesce(db.func.sum(Income.men + Income.girls), 0)
    ).scalar()
    return render_template('view_income.html', income_records=incomes, total_income=total_income)

# ---- EXPENSE ---- #

# Add a new expense record
@app.route('/expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        # Extract form data
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        category = request.form['category']
        amount = float(request.form['amount'])

        # Save to database
        new_expense = Expense(date=date, category=category, amount=amount)
        db.session.add(new_expense)
        db.session.commit()

        return redirect(url_for('view_expense'))

    return render_template('expense.html')

# View all expense records
@app.route('/expense/view')
def view_expense():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    # Total expense
    total_expense = db.session.query(
        db.func.coalesce(db.func.sum(Expense.amount), 0)
    ).scalar()
    return render_template('view_expense.html', expense_records=expenses, total_expense=total_expense)

# ---- DASHBOARD ---- #

# Combined dashboard showing income + expenses
@app.route('/dashboard')
def dashboard():
    incomes = Income.query.order_by(Income.date.desc()).all()
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return render_template('dashboard.html', income_records=incomes, expense_records=expenses)

# ---- EXCEL EXPORT ---- #

# Export income and expense records to Excel
@app.route('/export/excel')
def export_excel():
    import pandas as pd
    import io
    from flask import send_file

    # Get all income and expense records from the database
    incomes = Income.query.all()
    expenses = Expense.query.all()

    # Convert income records to a DataFrame
    income_data = [{
        'Date': i.date.strftime('%Y-%m-%d'),
        'Men': i.men,
        'Girls': i.girls
    } for i in incomes]
    df_income = pd.DataFrame(income_data)

    # ✅ Convert expense records to a DataFrame (FIXED)
    expense_data = [{
        'Date': e.date.strftime('%Y-%m-%d'),
        'Category': e.category,
        'Amount': e.amount
    } for e in expenses]
    df_expense = pd.DataFrame(expense_data)

    # Create an in-memory Excel file with both sheets
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if not df_income.empty:
            df_income.to_excel(writer, index=False, sheet_name='Income')
        if not df_expense.empty:
            df_expense.to_excel(writer, index=False, sheet_name='Expense')
    output.seek(0)

    # Return the Excel file as a download
    return send_file(
        output,
        download_name='gym_data.xlsx',
        as_attachment=True
    )

# New route for income + expense form on same page
@app.route('/entry', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'income':
            date = datetime.strptime(request.form['income_date'], '%Y-%m-%d')
            men = int(request.form['men'])
            girls = int(request.form['girls'])
            db.session.add(Income(date=date, men=men, girls=girls))
            db.session.commit()
            return redirect(url_for('add_entry'))

        elif form_type == 'expense':
            date = datetime.strptime(request.form['expense_date'], '%Y-%m-%d')
            category = request.form['category']
            amount = float(request.form['amount'])
            db.session.add(Expense(date=date, category=category, amount=amount))
            db.session.commit()
            return redirect(url_for('add_entry'))

    # 💵 Total income = sum of men + girls
    total_income = db.session.query(
        db.func.coalesce(db.func.sum(Income.men + Income.girls), 0)
    ).scalar()

    # 💸 Total expense = sum of all expenses
    total_expense = db.session.query(
        db.func.coalesce(db.func.sum(Expense.amount), 0)
    ).scalar()

    return render_template('entry.html', total_income=total_income, total_expense=total_expense)

# ----------------------- #
# App Startup
# ----------------------- #

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables exist
    app.run(debug=True)

