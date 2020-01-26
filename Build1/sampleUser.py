from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root123'
app.config['MYSQL_DB'] = 'TestDB'

mysql = MySQL(app)


#why doesn't the put method work??
@app.route('/api/v1/users', methods=['GET', 'POST'])
def add_user():
    if(request.method == "POST"):
        details = request.get_json()
        
        firstName = details['name']
        passwd = details['pwd']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Users(name, pwd) VALUES (%s, %s);", (firstName, passwd))
        mysql.connection.commit()
        cur.close()
        return "aayto"
    return "use POST"

@app.route('/api/v1/users/<name>', methods=['DELETE'])
def delete(name):
    if(request.method == "DELETE"):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM Users WHERE name=%s;", (name, ))
        mysql.connection.commit()
        cur.close()
        return "done."
    return "aagalla"

# select and insert are working
# can be morphed according to the required schema
@app.route('/select', methods=['GET', 'POST'])
def selectFromDB():
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



if __name__ == '__main__':
    app.run()