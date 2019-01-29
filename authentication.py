''' *************************************************************************************************************** '''
'''                                              Start Program                                                      '''
''' *************************************************************************************************************** '''
import constants
import time
from flask import Flask, Blueprint
from database_config import *
from flask_restplus import Api, Resource, fields


app = Flask(__name__)
blueprint = Blueprint('api', __name__, url_prefix='/api')
''' if we put api(app, doc=false) that mean that page would not be for public (the page
 not found because we remove swagger ui from my api)'''
api = Api(blueprint, doc='/doc')
app.register_blueprint(blueprint)

books = []
users = []
users_borrower = []
borrowing_list = []
mycursor = lib_system.cursor()

''' *************************** '''
''' Structs models shape        '''
''' *************************** '''
authentication_model = api.model('authentication', {'user_email': fields.String('the user email '),
                                                    'user_password': fields.String('Password')})

user_model = api.model('User', {'user_id':fields.Integer('user ID'), 'user_name':fields.String('user name'), 'user_email':fields.String('user email'), 'user_role':fields.String('user role'), 'user_password':fields.String('user password')})


book_model = api.model('Book', {'id_book': fields.Integer('The Id Of Book'), 'author': fields.String('The Author Name'),
                          'title': fields.String('The Title of the book'),
                          'book_num': fields.Integer('The Num Of Books')})

borrowing_model =api.model ('borrowing', {'id_book': fields.Integer(' id book'), 'user_email':fields.String('user email ')})
''' *************************** '''
''' End  models shape           '''
''' *************************** '''

''' *************************** '''
''' Create admin instance       '''
''' *************************** '''
user_admin = {
    'user_id': 2424,
    'user_name': 'Elias',
    'user_email': 'elias.khalil@exalt.ps',
    'user_role': 'admin',
    'user_password': '1234'
}
''' ***************************  '''
''' Finish Create admin instance '''
''' ***************************  '''

''' ******************************************************************* '''
''' append admin to users list just the first time you execute the code '''
''' ******************************************************************* '''
admin_data = select_from_user_by_role('admin')  # by role
if (admin_data == "-1"):
    users.append(user_admin)
    insert_into_user(user_admin['user_id'], user_admin['user_name'], user_admin['user_email'], user_admin['user_role'],
                     user_admin['user_password'])
''' ******************************************************************* '''
''' End append admin to users list just the first time you execute the code '''
''' ******************************************************************* '''

''' ***************************  '''
''' authentication process       '''
''' ***************************  '''
@api.route('/user')
class User(Resource):
    # show the login
    @api.expect(authentication_model)
    def post(self):
        user_email_and_password = api.payload
        user_data = select_from_user_by(user_email_and_password['user_email'], user_email_and_password['user_password'])
        if user_data != "-1":
            if user_email_and_password != None:
                if user_data['user_role'] == 'admin':
                    admin_flag_file = open("admin_flag.txt", "w")
                    admin_flag_file.write("True")

                    return {'result': 'Admin logged in '}, constants.REQUEST_SUCCEEDED
                else :
                    admin_flag_file = open("admin_flag.txt", "w")
                    admin_flag_file.write("False")
                    borrower_flag_file = open("borrower_flag.txt", "w")
                    borrower_flag_file.write("True")
                    return {'result': 'Borrower logged in '}, constants.REQUEST_SUCCEEDED
        else:
            return {'result': 'wrong username or password '}, constants.REQUEST_SUCCEEDED
''' ***************************  '''
''' End authentication process   '''
''' ***************************  '''

''' ************************************** '''
''' accessibility to admin to add new user '''
''' ************************************** '''
@api.route('/new_user')
class User(Resource):
    @api.expect(user_model)
    def post(self):
        admin_flag_file = open("admin_flag.txt", "r")
        flag = admin_flag_file.read()
        if flag == "True":
            try:
                user_data = api.payload;
                insert_into_user(user_data['user_id'], user_data['user_name'], user_data['user_email'], user_data['user_role'],
                       user_data['user_password'])
            except mysql.connector.errors.IntegrityError:
                return {'result': 'Duplicated Entry'}, constants.RESOURCE_CREATED
        else:
            api.abort(constants.NOT_AUTHERIZED)
''' ****************************************** '''
''' End accessibility to admin to add new user '''
''' ****************************************** '''

''' *********************************************************************** '''
''' accessibility to borrower to present Book(show all books, add new book) '''
''' *********************************************************************** '''
@api.route('/book')
class Book(Resource):
    # get all the books from the database

    def get(self):

        book = {'book': []}
        sql = "SELECT * FROM book"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()

        for x in myresult:
            str = json.dumps(x)
            book['book'].append(map_book(str))
        # return all books
        return book


    # add new book to the database
    @api.expect(book_model)
    def post(self):
        admin_flag_file = open("admin_flag.txt", "r")
        flag = admin_flag_file.read()
        if flag == "True":
            new_book = api.payload
            books.append(new_book)
            new_book_str = json.dumps(new_book)
            sql = "INSERT INTO book (id_book, author, title, book_num) VALUES (%s, %s,%s,%s)"
            val = (new_book['id_book'], new_book['author'], new_book['title'], new_book['book_num'])
            mycursor.execute(sql, val)
            lib_system.commit()
            return {'result': 'book added'}, constants.RESOURCE_CREATED
        else:
            api.abort(constants.NOT_AUTHERIZED)
''' *************************************************************************** '''
''' End accessibility to borrower to present Book(show all books, add new book) '''
''' *************************************************************************** '''

''' ********************************************** '''
''' accessibility to user to search book by its id '''
''' ********************************************** '''
@api.route('/book/<id>')
@api.doc(params={'id': 'An ID'})
class MyResource(Resource):
    # get method used to search for the book by using id
    def get(self, id):
        admin_flag_file = open("admin_flag.txt", "r")
        flag = admin_flag_file.read()
        if flag == "True":
            data = {'data': []}
            i=0
            sql = "SELECT * FROM book"
            mycursor.execute(sql)
            myresult = mycursor.fetchall()

            for x in myresult:
                str = json.dumps(x)
                data['data'].append(map_book(str))

            for id1 in data['data']:
                if id1['id_book'].__str__() == id:
                    return id1
            api.abort(constants.NOT_FOUND)
        else:
            api.abort(constants.NOT_AUTHERIZED)
''' ************************************************** '''
''' End accessibility to user to search book by its id '''
''' ************************************************** '''

''' ********************************************** '''
''' accessibility to user to delete book by its id '''
''' ********************************************** '''
@api.route('/book/<id>')
@api.doc(params={'id': 'An ID'})
class Delete_Book(Resource):
    def delete(self, id):
        admin_flag_file = open("admin_flag.txt", "r")
        flag = admin_flag_file.read()
        if flag== "True":
            book = {'book': []}
            sql = "SELECT * FROM book"
            mycursor.execute(sql)
            all_books = mycursor.fetchall()
            for book_reference in all_books:
                str = json.dumps(book_reference)
                book['book'].append(map_book(str))
            for book_instance in book['book']:
                if int(book_instance['id_book']) == int(id):
                    sql = "DELETE FROM book WHERE id_book = {}".format(id)
                    mycursor.execute(sql)
                    lib_system.commit()
                    return {"Deleted success":"Delete"},constants.REQUEST_SUCCEEDED
            api.abort(constants.NOT_FOUND)
        else :
            api.abort(constants.NOT_AUTHERIZED)
''' ************************************************** '''
''' End accessibility to user to delete book by its id '''
''' ************************************************** '''

''' **************************************** '''
''' accessibility to admin to edit book data '''
''' **************************************** '''
@api.expect(book_model)
@api.route('/book/editing')
class Editing_book(Resource):
    def put(self):
        admin_flag_file = open("admin_flag.txt", "r")
        flag = admin_flag_file.read()
        if flag == "True":
            book = {'book': []}
            sql = "SELECT * FROM book"
            mycursor.execute(sql)
            all_books = mycursor.fetchall()
            for book_reference in all_books:
                str = json.dumps(book_reference)
                str = str.replace("[", "")
                str = str.replace("]", "")
                list_of_books = str.split(',')
                book['book'].append({
                    "idBook": list_of_books[0].strip(),
                    "Author": list_of_books[1].strip().strip("\""),
                    "Title": list_of_books[2].strip().strip("\""),
                    "Book_num": list_of_books[3].strip()
                })
                book_form_swagger_model = api.payload
                if int(book_form_swagger_model['id_book']) == int(list_of_books[0]):
                    sql = "UPDATE book SET  title = %s , author = %s , book_num= %s WHERE id_book = %s"
                    val = ( book_form_swagger_model['title'],book_form_swagger_model['author'],book_form_swagger_model['book_num'],book_form_swagger_model['id_book'])
                    mycursor.execute(sql,val)
                    lib_system.commit()
                    return {"UPDATE success":"UPDATE"},constants.REQUEST_SUCCEEDED
            api.abort(constants.NOT_FOUND)
        else:
            api.abort(constants.NOT_AUTHERIZED)
''' ******************************************** '''
''' End accessibility to admin to edit book data '''
''' ******************************************** '''

''' *************************************************** '''
''' accessibility to admin to present all borrower data '''
''' *************************************************** '''
@api.route('/borrower')
class Borrower(Resource):
    # get all the books from the database
    def get(self):
        admin_flag_file = open("admin_flag.txt", "r")
        flag = admin_flag_file.read()
        if flag == "True":
            user_data = {'user': []}
            user_data=select_from_user()
            return user_data
        else:
            api.abort(constants.NOT_AUTHERIZED)
''' ******************************************************* '''
''' End accessibility to admin to present all borrower data '''
''' ******************************************************* '''


''' ******************************************************** '''
''' accessibility to admin to delete specific borrower by id '''
''' ******************************************************** '''
@api.route('/borrower/<id>')
@api.doc(params={'id': 'An ID'})
class Delete_user(Resource):
    def delete(self, id):
        admin_flag_file = open("admin_flag.txt", "r")
        flag = admin_flag_file.read()
        if flag == "True":
            user_data = select_from_user()
            for id2 in user_data['user']:
                if id2['user_id'].__str__() == id:
                    sql = "DELETE FROM user WHERE user_id = {}".format(id)
                    mycursor.execute(sql)
                    lib_system.commit()
                    return {"Deleted success":"Delete User"},constants.REQUEST_SUCCEEDED
            api.abort(constants.NOT_FOUND)
        else:
            api.abort(constants.NOT_AUTHERIZED)
''' ******************************************************** '''
''' End accessibility to admin to delete specific borrower by id '''
''' ******************************************************** '''

''' ******************************************************** '''
''' accessibility to admin to edit specific borrower         '''
''' ******************************************************** '''
@api.expect(user_model)
@api.route('/borrower/editing')
class user_editing(Resource):
    def put(self):
        admin_flag_file = open("admin_flag.txt", "r")
        flag = admin_flag_file.read()
        if flag=="True":

            user_data = {'user': []}
            i=0
            sql = "SELECT * FROM user"
            mycursor.execute(sql)
            all_users = mycursor.fetchall()
            for user_reference in all_users:

                str = json.dumps(user_reference)
                str = str.replace("[", "")
                str = str.replace("]", "")
                result = str.split(',')

                user_data['user'].append({
                    "user_id": result[0].strip(),
                    "user_name": result[1].strip().strip("\""),
                    "user_email": result[2].strip().strip("\""),
                    "user_role": result[3].strip().strip("\""),
                    "user_password": result[4].strip().strip("\"")
                })
                user_from_swagger_model = api.payload
                if int(user_from_swagger_model['user_id']) == int(result[0]):
                    sql = "UPDATE user SET  user_name =%s, user_email = %s , user_role=%s, user_password = %s  WHERE user_id = %s"
                    val = (user_from_swagger_model['user_name'], user_from_swagger_model['user_email'],user_from_swagger_model['user_role'],user_from_swagger_model['user_password'],user_from_swagger_model['user_id'])
                    mycursor.execute(sql,val)
                    lib_system.commit()
                    return {"UPDATE success":"UPDATE"},constants.RESOURCE_CREATED
            api.abort(constants.NOT_FOUND)
        else:
            return api.abort(constants.NOT_AUTHERIZED)
''' ******************************************************** '''
'''  End accessibility to admin to edit specific borrower    '''
''' ******************************************************** '''

''' ******************************************* '''
''' function that writes False to specific file '''
''' ******************************************* '''
def write_false(file_name):
    file = open(file_name, "w")
    file.write("False")

''' *********************************************** '''
''' End function that writes False to specific file '''
''' *********************************************** '''

''' ******************************************************* '''
''' Show all borrowed books  and post def to borrowing book '''
''' ******************************************************* '''
@api.route('/borrowing/book')
class Book(Resource):
    def get(self):
        admin_flag_file = open("admin_flag.txt", "r")
        flag = admin_flag_file.read()
        if flag == "True":
            borrowed_books = {'borrowed_books': []}
            # select all data from borrowing table: to get all books borrowed by borrowers
            sql = "SELECT * FROM borrowing"
            mycursor.execute(sql)
            myresult = mycursor.fetchall()
            # storing data from table borrowing into array data1
            for x in myresult:
                str = json.dumps(x)
                borrowed_books['borrowed_books'].append(map_borrwing(str))

            return borrowed_books
        else:
           return api.abort(constants.NOT_AUTHERIZED)

    @api.expect(borrowing_model)
    def post(self):
        borrower_flag_file = open("borrower_flag.txt", "r")
        flag_borrower = borrower_flag_file.read()
        admin_flag_file = open("admin_flag.txt", "r")
        flag_admin = admin_flag_file.read()
        if flag_borrower == "True" or flag_admin == "True":
            new_borrowing = api.payload  # store coming data into new_borrowing
            borrowing_list.append(new_borrowing)

            book_from_database = select_from_book_by_id(new_borrowing['id_book'])
            print("duaa")
            print(book_from_database)
            if book_from_database == "-1":
                return api.abort(constants.NOT_FOUND)
            try:
                # this command is used to borrow book with start and end time
                localtime = time.asctime(time.localtime(time.time()))
                endtime = time.asctime(time.localtime(time.time() + constants.BORROWING_PERIOD))
                sql = "INSERT INTO borrowing (id_book, user_email, start_time,end_time) VALUES (%s, %s,%s,%s)"
                val = (new_borrowing['id_book'], new_borrowing['user_email'], localtime, endtime)
                mycursor.execute(sql, val)
            except mysql.connector.errors.IntegrityError:
                return {'result': 'Duplicated Entry'}, constants.REQUEST_SUCCEEDED


            # this condition used to check if there is no available books in the database
            # else : decrement every book is borrowed by 1
            if book_from_database['book_num'] == "0":
                api.abort(constants.NOT_FOUND)
            else:
                book_n = int(book_from_database['book_num']) - 1
                sql2 = "UPDATE book SET  book_num= %s WHERE id_book = %s"
                val2 = (book_n, book_from_database['id_book'])
                mycursor.execute(sql2, val2)
                lib_system.commit()
                return {'Result': 'borrowing Done'}, constants.REQUEST_SUCCEEDED
        else:
            return  api.abort(constants.NOT_AUTHERIZED)
''' *********************************************************** '''
''' End show all borrowed books  and post def to borrowing book '''
''' *********************************************************** '''

''' *********************************************************** '''
''' Return Book to database by book id and user email           '''
''' *********************************************************** '''
@api.route('/borrowing/book/return/<id_book>/<user_email>')   #1
@api.doc(params={'id_book': 'Book ID', 'user_email':'user email'})
class MyResource(Resource):
    # get method used to search for the book by using id
    def get(self, id_book, user_email):
        admin_flag_file = open("admin_flag.txt", "r")
        flag_borrower = admin_flag_file.read()
        admin_flag_file = open("admin_flag.txt", "r")
        flag_admin = admin_flag_file.read()
        if flag_borrower == "True" or flag_admin == "True":
            # return the book to the library
            sql = "DELETE FROM borrowing WHERE id_book = %s and user_email = %s"
            val = (id_book, user_email,)
            mycursor.execute(sql, val)
            lib_system.commit()

            #select from database (book)
            # get the book borrowed from book table by its id
            sql2 = "SELECT * FROM book where id_book = %s"
            val2 = (id_book,)
            mycursor.execute(sql2, val2)
            all_books= mycursor.fetchall()

            str = json.dumps(all_books)
            str = str.replace("[", "")
            str = str.replace("]", "")
            result = str.split(',')

            if result  == ['']:
                api.abort(constants.NOT_FOUND)

            book_object = {
                "id_book": result[0].strip(),
                "author": result[1].strip().strip("\""),
                "title": result[2].strip().strip("\""),
                "book_num": result[3].strip()
            }

            book_n = int(book_object["book_num"])+1
            sql = "UPDATE book SET  book_num= %s WHERE id_book = %s"
            val = (book_n, id_book)
            mycursor.execute(sql,val)
            lib_system.commit()
            return {"result" : "Returned Book Done !!!"},constants.RESOURCE_CREATED
        else:
            api.abort(constants.NOT_AUTHERIZED)
''' *********************************************************** '''
''' End Return Book to database by book id and user email       '''
''' *********************************************************** '''

''' ***************************** '''
''' start running file from here: '''
''' ***************************** '''
if __name__ == '__main__':
    write_false("admin_flag.txt")
    write_false("borrower_flag.txt")
    app.run(debug=True)
''' ********************************* '''
''' End start running file from here: '''
''' ********************************* '''