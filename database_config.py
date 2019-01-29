import mysql.connector
import json
import constants
from flask_restplus import Api
lib_system = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="1234",
  database="lib_system"
)


# select all books form mysql database
def select_from_book():
    book={'book':[]}
    mycursor = lib_system.cursor()
    sql = "SELECT * FROM book"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()

    for x in myresult:
        str = json.dumps(x)
        book['book'].append(map_book(str))
    return book

# select book by condition of id_book
def select_from_book_by_id(id):
    mycursor = lib_system.cursor()
    sql = "SELECT * FROM book WHERE id_book = %s"
    val = (id,)
    mycursor.execute(sql, val)
    book = mycursor.fetchall()
    str = json.dumps(book)
    book_by_id = map_book(str)
    if book_by_id == "[]":
        return "-1"
    return book_by_id

# select all users from database
def select_from_user():
    user={'user':[]}
    mycursor = lib_system.cursor()
    sql = "SELECT * FROM user"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()

    for x in myresult:
        str = json.dumps(x)
        user['user'].append(map_user(str))
    return user

# select user by condition of role
def select_from_user_by_role(role):
    mycursor = lib_system.cursor()
    sql = "SELECT * FROM user WHERE user_role = %s"
    val = (role,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    str = json.dumps(myresult)
    user_by_role = map_user(str)
    return user_by_role

# select user by condition of role
def select_from_user_by(user_email, user_password):
    mycursor = lib_system.cursor()
    sql = "SELECT * FROM user WHERE user_email = %s and user_password = %s"
    val = (user_email,user_password )
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    str = json.dumps(myresult)
    if str == "[]":
        return "-1"
    user_by_user_name_and_password = map_user(str)
    return user_by_user_name_and_password

# insert row in user database
def insert_into_user(user_id, user_name, user_email, user_role, user_password):
    mycursor = lib_system.cursor()
    sql = "INSERT INTO user (user_id, user_name, user_email, user_role,user_password) VALUES (%s, %s,%s,%s,%s)"
    val = (user_id, user_name, user_email, user_role, user_password)
    mycursor.execute(sql, val)
    lib_system.commit()

def map_user(str):
    str = str.replace("[", "")
    str = str.replace("]", "")
    result = str.split(',')
    if result == ['']:
        return "-1"

    return {
        "user_id": result[0].strip(),
        "user_name": result[1].strip().strip("\""),
        "user_email": result[2].strip().strip("\""),
        "user_role": result[3].strip().strip("\""),
        "user_password": result[4].strip().strip("\"")
    }

def map_book(str):
    str = str.replace("[", "")
    str = str.replace("]", "")
    result = str.split(',')

    return {
        "id_book": result[0].strip(),
        "author": result[1].strip().strip("\""),
        "title": result[2].strip().strip("\""),
        "book_num": result[3].strip()
    }

def map_borrwing(str):
    str = str.replace("[", "")
    str = str.replace("]", "")
    result = str.split(',')

    return{
        "id_book": result[0].strip(),
        "user_email": result[1].strip().strip("\""),
        "start_time": result[2].strip().strip("\""),
        "end_time": result[3].strip().strip("\"")
    }