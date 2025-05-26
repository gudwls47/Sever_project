import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='your_user',
    password='your_password',
    database='your_database'
)
cursor = conn.cursor(dictionary=True)
