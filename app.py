from flask import Flask, render_template, request, redirect, flash
import mysql.connector
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.secret_key = "expense-tracker-secret-key"

load_dotenv()
print("MYSQL_HOST:", os.getenv("MYSQL_HOST"))
print("MYSQL_USER:", os.getenv("MYSQL_USER"))
print("MYSQL_DATABASE:", os.getenv("MYSQL_DATABASE"))

db = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
)

@app.route("/")
def home():
    cursor = db.cursor()

    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()

    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0]

    cursor.close()

    if total is None:
        total = 0

    return render_template(
        "index.html",
        expenses=expenses,
        total=total
    )


@app.route("/add", methods=["POST"])
def add_expense():
    name = request.form["name"]
    amount = request.form["amount"]
    category = request.form["category"]

    if not name.strip():
        flash("Expense name is required!", "error")
        return redirect("/")

    if not category.strip():
        flash("Category is required!", "error")
        return redirect("/")

    if float(amount) <= 0:
        flash("Amount must be greater than 0!", "error")
        return redirect("/")

    cursor = db.cursor()

    query = """
        INSERT INTO expenses (name, amount, category)
        VALUES (%s, %s, %s)
    """

    values = (name, amount, category)

    cursor.execute(query, values)
    db.commit()
    cursor.close()

    flash("Expense added successfully!", "success")
    return redirect("/")


@app.route("/delete/<int:id>", methods=["POST"])
def delete_expense(id):
    cursor = db.cursor()

    query = "DELETE FROM expenses WHERE id = %s"

    cursor.execute(query, (id,))
    db.commit()
    cursor.close()

    flash("Expense deleted successfully!", "success")
    return redirect("/") 


@app.route("/edit/<int:id>")
def edit_expense(id):
    cursor = db.cursor()

    query = "SELECT * FROM expenses WHERE id = %s"

    cursor.execute(query, (id,))
    expense = cursor.fetchone()

    cursor.close()

    return render_template("edit.html", expense=expense)


@app.route("/update/<int:id>", methods=["POST"])
def update_expense(id):
    name = request.form["name"]
    amount = request.form["amount"]
    category = request.form["category"]

    if not name.strip():
        flash("Expense name is required!", "error")
        return redirect(f"/edit/{id}")

    if not category.strip():
        flash("Category is required!", "error")
        return redirect(f"/edit/{id}")

    if float(amount) <= 0:
        flash("Amount must be greater than 0!", "error")
        return redirect(f"/edit/{id}")

    cursor = db.cursor()

    query = """
        UPDATE expenses
        SET name = %s,
            amount = %s,
            category = %s
        WHERE id = %s
    """

    values = (name, amount, category, id)

    cursor.execute(query, values)
    db.commit()
    cursor.close()

    flash("Expense updated successfully!", "success")
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)