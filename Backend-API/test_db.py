import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=MarineAI;"
    "Trusted_Connection=yes;"
)

cursor = conn.cursor()

cursor.execute("SELECT TOP 5 * FROM vessels")

for row in cursor:
    print(row)