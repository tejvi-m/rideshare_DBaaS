from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root123'
app.config['MYSQL_DB'] = 'TestDB'

mysql = MySQL(app)

@app.route('/create', methods=['GET', 'POST'])
def create():
    cur = mysql.connection.cursor()
    cur.execute("CREATE TABLE MyUsers ( firstname VARCHAR(30) NOT NULL,  lastname VARCHAR(30) NOT NULL);")
    mysql.connection.commit()
    cur.close()
    return "success"

@app.route('/delete/<name>', methods=['DELETE'])
def delete(name):
    if(request.method == "DELETE"):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM MyUsers WHERE firstname=%s;", (name, ))
        mysql.connection.commit()
        cur.close()
        return "success"
    return "aagalla"

@app.route('/insert', methods=['GET', 'POST'])
def insert():
    if(request.method == "POST"):
        details = request.get_json()
        # print(details["fname"])
        firstName = details['fname']
        lastName = details['lname']
        table = details['table']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO MyUsers(firstName, lastName) VALUES (%s, %s);", (firstName, lastName))
        mysql.connection.commit()
        cur.close()
        return "success"
    return "use POST"


# select and insert are working
# can be morphed to the required schema
@app.route('/select', methods=['GET', 'POST'])
def select():
    if(request.method == "POST"):
        details = request.get_json()
        table = details['table']
        columns = details['columns']
        where = details['where']
        
        cur = mysql.connection.cursor()
        
        query = "SELECT " + columns + " FROM " + table + " WHERE " + where + ";"
        print(query)
        cur.execute(query)        
        data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return jsonify(data)
    return "use POST"


@app.route('/', methods=['GET', 'POST'])
def index():
    return "flask seems to be working !"



if __name__ == '__main__':
    app.run()