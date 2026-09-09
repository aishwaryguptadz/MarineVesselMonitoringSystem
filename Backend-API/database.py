import pyodbc

def get_connection():
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=localhost\SQLEXPRESS;"
        "DATABASE=MarineAi;"
        "Trusted_Connection=yes;"
    )
    return conn

print(pyodbc.drivers())