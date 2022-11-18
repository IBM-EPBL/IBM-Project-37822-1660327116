from flask import  Flask,render_template, request, redirect, url_for, session
import ibm_db
import os
from dotenv import load_dotenv
import pandas as pd
import smtplib
from email.message import EmailMessage
import requests
import json
from flask_session import Session
from apscheduler.schedulers.background import BackgroundScheduler
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment




app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Loading up the values
load_dotenv()
#DB Creds
database = os.environ.get("DATABASE")
db_hostname = os.environ.get("HOSTNAME")
db_port = os.environ.get("PORT")
db_uid = os.environ.get("UID")
db_pwd = os.environ.get("PWD")
email_pwd = os.environ.get("email_password")



# Database Connection
try:
    conn = ibm_db.connect(
    f'DATABASE={database};HOSTNAME={db_hostname};PORT={db_port};SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID={db_uid};PWD={db_pwd}', '', '')
    print("Connected to database: ", conn)
except Exception as e:
    print (e)


def message(subject="Python Notification",
            text="", img=None, attachment=None):

    # build message contents
    msg = MIMEMultipart()

    f = open("./templates/notifications.html", "r", errors="ignore")
    html_content = f.read()

    html_contentt = Environment().from_string(
        html_content).render(msg=text)

    # Add Subject
    msg['Subject'] = subject

    # Add text contents
    msg.attach(MIMEText(html_contentt, 'html'))
    return msg


def mail():

    # initialize connection to our email server,
    # we will use gmail here
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()

    # Login with your email and password
    smtp.login("jesinthan0703@gmail.com", email_pwd)

    # url = "https://newscatcher.p.rapidapi.com/v1/search_free"
    # querystring = {"q":"Russia","lang":"en","media":"True"}
    # headers = {
    #     "X-RapidAPI-Key": "78394ce5f7msh148449ce3836679p1239b2jsnb6fb656b52e5",
    #     "X-RapidAPI-Host": "newscatcher.p.rapidapi.com"
    # }
    # response = requests.request("GET", url, headers=headers, params=querystring)
    # json_object = json.loads(response.text)

    f = open("sample.json", "r")
    news_data = f.read()
    json_object = json.loads(news_data)

    data = json_object["articles"]

    # Call the message function
    msg = message("Exciting news today!", data[:10])

    sql = "SELECT email FROM users"
    stmt = ibm_db.prepare(conn, sql)
    # ibm_db.bind_param(stmt, 1, "shirleychristabel.23it@licet.ac.in")
    ibm_db.execute(stmt)
    users = []
    # List of emails
    while ibm_db.fetch_row(stmt) != False:
        users.append(ibm_db.result(stmt, 0).strip())

    print(users)
    smtp.sendmail(from_addr="jesinthan0703@gmail.com",
                            to_addrs="jesinthan.23cs@licet.ac.in", msg=msg.as_string())
    print("Email sent successfully")

    smtp.quit()


sched = BackgroundScheduler(daemon=True)
sched.add_job(mail, 'interval', hours=24)
sched.start()

# Home Route
@app.route('/',methods = ['POST', 'GET'])
def home():

    def send_mail(r_mail, content):
        s_mail = "jesinthan0703@gmail.com"
        s_pass = email_pwd
        msg=EmailMessage()
        msg['Subject'] = f"Registration Successful"
        msg['From'] = s_mail
        msg['To'] = r_mail
        msg.set_content(content,subtype="html")

        server = smtplib.SMTP_SSL("smtp.gmail.com",465)

        try:
            server.login(s_mail,s_pass)
            print("Logged In Successfully")
            server.send_message(msg)
            print("Mail Sent")
            server.quit()
        except Exception as e:
            print(e)

    if request.method == 'POST':
        
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        print(first_name, last_name, email, password, confirm_password)

        if(password==confirm_password):
            sql = "SELECT * FROM users WHERE email = '"+email+"' "
            print(sql)
            stmt = ibm_db.exec_immediate(conn, sql)
            
            account = ibm_db.fetch_assoc(stmt)
            print(account)

            if account:
                print("User already exists")
                return render_template('register.html', msg="User already exists, Please login")
            else:
                print("User does not exist")
                try:
                    insert_query = "INSERT INTO users VALUES('"+email+"','"+password+"','"+first_name+"','"+last_name+"')"
                    ibm_db.exec_immediate(conn, insert_query)
                    print("You are successfully registered")
                    with open('mail.html', 'r') as f:
                        mail_content= f.read()
                        send_mail(email, mail_content)
                    return render_template('login.html')
                    
                except Exception as e:
                    print(e)
                
                
        else:
            print("Password does not match")
            return render_template('register.html', msg="Password does not match")
        

    return render_template('register.html',title="Register")

@app.route('/login',methods = ['POST', 'GET'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
      
        print(email,password)

        try:
            sql = "SELECT password FROM users WHERE email = '"+email+"' "
            print(sql)
            stmt = ibm_db.exec_immediate(conn, sql)
            print(stmt)
            pwd = ibm_db.fetch_assoc(stmt)
            print(pwd)
            key = pwd.get('PASSWORD')

            if password==key.strip():
                print("User exists, Logged in successfully")
                session["email"] = email
                print(session["email"])
                return redirect("/dashboard", code=302)
            else:
                print("Password is incorrect")
                return render_template('login.html', msg="Password is incorrect")
        except Exception as e:
            print(e)
            return render_template('login.html', msg="User does not exist, Please register")
   

    return render_template('login.html')

@app.route('/dashboard',methods = ['POST', 'GET'])
def dashboard():
    
    if not session.get("email"):
            return redirect("/login")
    else:

        try:
            #PRODUCTION
            # url = "https://newscatcher.p.rapidapi.com/v1/search_free"
            # querystring = {"q":"Russia","lang":"en","media":"True"}
            # headers = {
            #     "X-RapidAPI-Key": "78394ce5f7msh148449ce3836679p1239b2jsnb6fb656b52e5",
            #     "X-RapidAPI-Host": "newscatcher.p.rapidapi.com"
            # }
            # response = requests.request("GET", url, headers=headers, params=querystring)
            # json_object = json.loads(response.text)

            #DEV
            f = open("sample.json", "r")
            news_data = f.read()
            json_object = json.loads(news_data)
            
            try:
                sql="SELECT * FROM users WHERE email = '"+session["email"]+"' "
                print(sql)
                stmt = ibm_db.exec_immediate(conn, sql)
                print(stmt)
                user = ibm_db.fetch_assoc(stmt)
                first_name = user.get('FIRST_NAME').strip()
                last_name = user.get('LAST_NAME').strip()
                return render_template('dashboard.html',students=json_object, first_name=first_name, last_name=last_name)
            except Exception as e:
                print(e)
                return render_template('dashboard.html',students=json_object)


        except Exception as e:
            print(e)

@app.route('/profile',methods = ['POST', 'GET'])
def profile():
    if not session.get("email"):
            return redirect("/login")
    else:
        try:
            sql = "SELECT first_name, last_name FROM users WHERE email = '"+session["email"]+"' "
            print(sql)
            stmt = ibm_db.exec_immediate(conn, sql)
            print(stmt)
            profile = ibm_db.fetch_assoc(stmt)
            first_name = profile.get('FIRST_NAME').strip()
            last_name = profile.get('LAST_NAME').strip()
            print(first_name, last_name)
            return render_template('profile.html',first_name=first_name, last_name=last_name, email=session["email"])
        except Exception as e:
            print(e)
    return render_template('profile.html')


@app.route("/logout", methods=['POST'])
def logout():

    session.pop("email", None)

    return render_template('login.html')



if __name__ == "main":
    app. run(debug=True, use_reloader=True)
    