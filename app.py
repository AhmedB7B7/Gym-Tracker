# app.py

# Import Flask and related functions
from flask import Flask, render_template, request, redirect, url_for, send_file

# Import SQLAlchemy for database operations
from flask_sqlalchemy import SQLAlchemy

# Import datetime to handle date formats
from datetime import datetime

# Import pandas (not used directly in this version, but useful for Excel export)
import pandas as pd

# For creating Excel files in memory
import io

# ----------------------- #
# Flask App Configuration
# ----------------------- #

# Create the Flask app
app = Flask(__name__)

# Set the database URI (SQLite database named gymtracker.db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gymtracker.db'

# Turn off modification tracking to save memory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database object and bind it to the app
db = SQLAlchemy(app)

# ----------------------- #
# Database Models
# ----------------------- #

# Define the Income model/table
class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)              # Unique ID
    date = db.Column(db.Date, nullable=False)                 # Date of income
    men = db.Column(db.Integer, nullable=False)               # Men income amount
    girls = db.Column(db.Integer, nullable=False)             # Girls income amount

# Define the Expense model/table
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)              # Unique ID
    date = db.Column(db.Date, nullable=False)                 # Date of expense
    category = db.Column(db.String(50), nullable=False)       # Expense dropup (e.g. rent, salary)
    cost = db.Column(db.Float, nullable=False)                # Cost of the expense

# ----------------------- #
# Routes
# ----------------------- #

# Route to check if the Expense table exists and works
@app.route('/check-db')
def check_db():
    try:
        count = Expense.query.count()  # Count records in Expense table
        return f" Expense table exists. Total records: {count}"  # Show count
    except Exception as e:
        return f" Error: {e}"  # Show error message if table doesn't work

# Redirect root URL (/) to the income page
@app.route('/')
def home():
    return redirect(url_for('add_income'))

# ---- INCOME ---- #

# Route to add income (GET to show form, POST to submit form)
@app.route('/income', methods=['GET', 'POST'])
def add_income():
    if request.method == 'POST':
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')  # Parse date
        men = int(request.form['men'])                               # Get men income
        girls = int(request.form['girls'])                           # Get girls income

        new_income = Income(date=date, men=men, girls=girls)         # Create new income object
        db.session.add(new_income)                                   # Add to database
        db.session.commit()                                          # Save changes

        return redirect(url_for('view_income'))                      # Redirect to view page

    return render_template('income.html')                            # Show income form

# Route to view income records
@app.route('/income/view')
def view_income():
    incomes = Income.query.order_by(Income.date.desc()).all()       # Get all records, newest first

    total_income = db.session.query(
        db.func.coalesce(db.func.sum(Income.men + Income.girls), 0) # Calculate total income
    ).scalar()

    return render_template('view_income.html', income_records=incomes, total_income=total_income)

# ---- EXPENSE ---- #

# Route to add new expense
@app.route('/expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        date = request.form['date']                                   # Get date
        category = request.form['category']                           # Get category
        amount = float(request.form['amount'])                        # Get amount

        expense = Expense(date=date, category=category, cost=amount)  # Create expense object
        db.session.add(expense)                                       # Add to DB
        db.session.commit()                                           # Save changes
        return redirect('/expense/view')
                              # Go to view page
    categories = ['Gym Equipment', 'Trainer Salary', 'Rent', 'Maintenance', 'Electricity']
    return render_template('add_expense.html', categories=categories)

# Route to view expenses
@app.route('/expense/view')
def view_expense():
    expenses = Expense.query.order_by(Expense.date.desc()).all()     # Get all expenses

    total_expense = db.session.query(
        db.func.coalesce(db.func.sum(Expense.cost), 0)               # Calculate total expense
    ).scalar()

    return render_template('view_expense.html', expense_records=expenses, total_expense=total_expense)

# ---- DASHBOARD ---- #

# Combined dashboard route to show totals and records
@app.route('/dashboard')
def dashboard():
    income = Income.query.all()                          # Get all income
    expense = Expense.query.all()                        # Get all expenses

    total_income = sum(i.men + i.girls for i in income)  # Total income calculation
    total_expense = sum(e.cost for e in expense)         # Total expense calculation

    return render_template("dashboard.html",
                           total_income=total_income,
                           total_expense=total_expense,
                           income_records=income,
                           expense_records=expense)

# ---- EXCEL EXPORT ---- #

# Route to export both income and expense to an Excel file
@app.route('/export/excel')
def export_excel():
    income = Income.query.all()                          # Get all income
    expense = Expense.query.all()                        # Get all expenses

    from openpyxl import Workbook                        # Import here for Excel creation
    from io import BytesIO                               # In-memory file object

    wb = Workbook()                                      # Create workbook
    ws1 = wb.active                                      # Get default worksheet
    ws1.title = "Income"                                 # Rename it to "Income"

    ws1.append(["Date", "Source", "Amount"])             # Header row
    total_income = 0
    for i in income:
        ws1.append([i.date, "Men + Girls", i.men + i.girls])  # Add each income row
        total_income += i.men + i.girls

    ws1.append(["", "Total", total_income])              # Total income row

    ws2 = wb.create_sheet(title="Expense")               # New sheet for expenses
    ws2.append(["Date", "Category", "Amount"])           # Header row
    total_expense = 0
    for e in expense:
        ws2.append([e.date, e.category, e.cost])         # Add each expense row
        total_expense += e.cost

    ws2.append(["", "Total", total_expense])             # Total expense row

    output = BytesIO()                                   # Create memory buffer
    wb.save(output)                                      # Save workbook to buffer
    output.seek(0)                                       # Go to start of buffer

    return send_file(output, download_name="gym_data.xlsx", as_attachment=True)  # Send file to user

# ---- COMBINED ENTRY FORM ---- #

# Route for one page to submit both income and expense
@app.route('/entry', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        form_type = request.form.get('form_type')        # Know which form was submitted

        # If income form submitted
        if form_type == 'income':
            date = datetime.strptime(request.form['income_date'], '%Y-%m-%d')
            men = int(request.form['men'])
            girls = int(request.form['girls'])
            db.session.add(Income(date=date, men=men, girls=girls))  # Add income
            db.session.commit()
            return redirect(url_for('add_entry'))

        # If expense form submitted
        elif form_type == 'expense':
            date = datetime.strptime(request.form['expense_date'], '%Y-%m-%d')
            category = request.form['category']
            amount = float(request.form['amount'])
            db.session.add(Expense(date=date, category=category, cost=amount))  # Add expense
            db.session.commit()
            return redirect(url_for('add_entry'))

    # Total income and expense to display on entry page
    total_income = db.session.query(
        db.func.coalesce(db.func.sum(Income.men + Income.girls), 0)
    ).scalar()

    total_expense = db.session.query(
        db.func.coalesce(db.func.sum(Expense.cost), 0)
    ).scalar()
    categories = ['Gym Equipments', 'Trainer Salary', 'Rent', 'Maintance', 'Electricity']
    return render_template('entry.html', total_income=total_income, total_expense=total_expense, categories=categories)

# ----------------------- #
# App Startup
# ----------------------- #

# When app is run directly (not imported), start the server
if __name__ == '__main__':
    with app.app_context():
        db.create_all()       # Create tables if they don't exist
    app.run(debug=True)       # Start server with debugging enabled
