from flask import Flask, render_template 
import mysql.connector

app = Flask(__name__)

# Configure the MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="project1",
    database="drink_database"
)

@app.route('/drinks')
def get_drinks():
    cursor = db.cursor()
    cursor.execute("SELECT name, alcohol_content FROM drinks")
    drinks = cursor.fetchall()
    print(drinks)
    return render_template('site.html', drinks=drinks)

if __name__ == '__main__':
    app.run()