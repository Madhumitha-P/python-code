import mysql.connector;
from mysql.connector import Error

def db_connection(username,password,host,dbname,table_name):
    
    try:
        my_connection = mysql.connector.connect(host=host,username=username,
                                                password=password,dbname=dbname)
        cursor = my_connection.cursor();
        cursor.execute('Select * from',table_name,'where emp_id=100')
        res = cursor.fetch_all()
        for row in res:
            print(row)
    except Error as e:
        print(e)
    finally:
        if my_connection.is_connected():
            cursor.close()
            my_connection.close()