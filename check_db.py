import pymysql
import sys

try:
    connection = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    print("Connected to MySQL server.")
    with connection.cursor() as cursor:
        cursor.execute("SHOW DATABASES LIKE 'db_perjanjian'")
        result = cursor.fetchone()
        if result:
            print("Database 'db_perjanjian' exists.")
        else:
            print("Database 'db_perjanjian' does NOT exist.")
            # Try to create it
            try:
                cursor.execute("CREATE DATABASE db_perjanjian")
                print("Database 'db_perjanjian' created successfully.")
            except Exception as e:
                print(f"Failed to create database: {e}")
    connection.close()
except Exception as e:
    print(f"Error connecting to MySQL: {e}")
    sys.exit(1)
