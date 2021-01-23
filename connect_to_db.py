import mysql.connector
from mysql.connector import Error

def connect_to_db(db_host, user, passwd):
    try:
        connection = mysql.connector.connect(
          host=db_host,
          user= user,
          passwd=passwd,
          database="nagiosql"
        )
    except Error as e:
        print(e)
        print("could not connect to database. please check credentials and connectivity.")
        connection = ''
    if connection:
        return connection

def connect_to_remote_db(db_host, user, passwd):
    try:
        connection = mysql.connector.connect(
          host=db_host,
          user= user,
          passwd=passwd
        )
    except Error as e:
        print(e)
        print("could not connect to database. please check credentials and connectivity.")
        connection = ''
    if connection:
        return connection
