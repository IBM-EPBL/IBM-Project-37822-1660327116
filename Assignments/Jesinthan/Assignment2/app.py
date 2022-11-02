from flask import  Flask,render_template, request, redirect, url_for, session
import ibm_db

app = Flask(__name__)


# Database Connection
try:
    conn = ibm_db.connect("DATABASE=BLUDB;HOSTNAME=fbd88901-ebdb-4a4f-a32e-9822b9fb237b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32731;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=tfy84094;PWD=9ibreJkzJF8l0ZTA",'','')
    print("Connected to database: ", conn)
except:
    print ("Unable to connect to the database")

@app.route('/',methods = ['POST', 'GET'])
def home():
    if request.method == 'POST':

        username = request.form['username']
        rollnumber = request.form['rollnumber']
        email = request.form['email']
        password = request.form['password']
        print(username,rollnumber,email,password)

        sql = "SELECT * FROM user WHERE username = '"+username+"' "
        print(sql)
        stmt = ibm_db.exec_immediate(conn, sql)
        
        account = ibm_db.fetch_assoc(stmt)
        print(account)

        if account:
            print("User already exists")
            return render_template('register.html')
        else:
            print("User does not exist")
            insert_query = "INSERT INTO user VALUES('"+username+"','"+email+"','"+password+"','"+rollnumber+"')"
            ibm_db.exec_immediate(conn, insert_query)
            print("You are successfully registered")
            return render_template('login.html')

    return render_template('register.html')

@app.route('/login',methods = ['POST', 'GET'])
def login():
    print("Login")
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
      
        print(email,password)

        sql = "SELECT password FROM user WHERE email = '"+email+"' "
        print(sql)
        stmt = ibm_db.exec_immediate(conn, sql)
        print(stmt)
        pwd = ibm_db.fetch_assoc(stmt)
        print(pwd)
        key = pwd.get('PASSWORD')

        if password==key.rstrip():
            print("User exists")
            return render_template('welcome.html')
        else:
            print("User does not exist")
            return render_template('register.html')

    return render_template('login.html')

if __name__ == "main":
    app.run(debug=True)
    