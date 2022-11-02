from flask import  Flask,render_template, request, redirect, url_for, session
import ibm_db

app = Flask(__name__)

try:
    conn = ibm_db.connect("DATABASE=BLUDB;HOSTNAME=2f3279a5-73d1-4859-88f0-a6c3e6b4b907.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=30756;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=rjf76022;PWD=16fw5YDUBoUYyOTx",'','')
    print("Connected to database: ", conn)
except:
    print ("Unable to connect to the database")

@app.route('/',methods = ['POST', 'GET'])
def home():
    if request.method=="POST":
        username=request.form['username']
        rollnumber=request.form['rollnumber']
        email=request.form['email']
        password=request.form['password']
        print(username,rollnumber,email,password)
        sql="SELECT * FROM user where username='"+username+"'"
        print(sql)
        stmt=ibm_db.exec_immediate(conn,sql)
        account=ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            print("This user already exists")
            return render_template('register.html')
        else:
            print("User does not exist")
            insert_query="INSERT INTO user values('"+username+"','"+rollnumber+"','"+email+"','"+password+"')"
            ibm_db.exec_immediate(conn,insert_query)
            print("You are successfully registered")
            return render_template('login.html')

    return render_template('register.html')

@app.route('/login',methods = ['POST', 'GET'])
def login():
    if request.method=="POST":
        email=request.form['email']
        password=request.form['password']
        print(email,password)
        sql="SELECT password FROM user where email='"+email+"'"
        print(sql)
        stmt=ibm_db.exec_immediate(conn,sql)
        pwd=ibm_db.fetch_assoc(stmt)
        key=pwd.get('PASSWORD')
        if password==key.rstrip():
            print("User exists")
            return render_template('welcome.html')
        else:
            print("User does not exist")
            return render_template('welcome.html')

    return render_template('login.html')

if __name__ == "main":
    app.run(debug=True)