# 🏋️‍♂️ Gym Tracker Web App

A simple web-based system built with **Flask** and **SQLite** to track **gym income and expenses**, view monthly summaries, and export data to Excel.

---

##  Features

- ✅ Add income (men & girls) with date
- ✅ Add expenses with category, date, and cost
- ✅ Category selection via dropdown menu
- ✅ Dashboard with total income and expense
- ✅ Export all data to Excel file
- ✅ Combined form to submit both income and expenses
- ✅ Responsive and easy-to-use UI

---

## 🛠️ Tech Stack

| Component | Used |
|----------|------|
| Backend  | Python (Flask) |
| Database | SQLite (via SQLAlchemy) |
| Frontend | HTML, |
| Export   | openpyxl, pandas |
| Editor   | Emacs  |

---
Folder structer
Gym-Tracker/
│
├── app.py               # Main application
├── models.py            # SQLAlchemy models
├── templates/           # HTML templates
│   ├── add_income.html
│   ├── add_expense.html
│   ├── view_income.html
│   ├── view_expense.html
│   └── dashboard.html
├── static/              # CSS/JS files (if any)
├── requirements.txt     # Python dependencies
└── README.md            # This file

--Installation and instruction
# 1. Clone the GitHub repository
git clone https://github.com/AhmedB7B7/Gym-Tracker.git
cd Gym-Tracker

# 2. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the Flask app
python app.py


--Usage
## 🧑‍💻 Usage

1. Go to the homepage
2. Add income/expense records
3. View total stats on the dashboard
4. Export data from the export buttons

--Screenshots

