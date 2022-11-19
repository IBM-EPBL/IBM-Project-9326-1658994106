from flask import Flask, render_template, request, redirect, url_for, session, redirect, request
import ibm_db
import numpy as np
import math
import requests
import json
app=Flask(__name__)

API_KEY = "SS8i1WCFH5jzJJP3jlCreoL23etchiEv3PNTzZSXZXpL"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]
header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}
conn = None

##connecting database db2
try:
   conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=764264db-9824-4b7c-82df-40d1b13897c2.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=32536;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=szx03624;PWD=E6uxPM2dowb0NSAr;PROTOCOL=TCPIP",'','')
   print("Successfully connected with db2")
except:
     print("Unable to connect: ", ibm_db.conn_errormsg())

def check(emailid):
    sql = "SELECT * FROM user WHERE emailid = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, emailid)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    return account

@app.route('/')
@app.route('/entry')
@app.route('/home')
def entry():
    return render_template('index1.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/Login')
def Login():
    return render_template('Login.html')

@app.route('/uniReg')
def uniReg():
    return render_template('uniReg.html')

@app.route('/result')
def result():
    return render_template('result.html')

@app.route("/adduser", methods=["POST"])
def adduser():
    username = request.form.get("username")
    lastname = request.form.get("lastname")
    emailid = request.form.get("emailid")
    password = request.form.get("password")
    tel = request.form.get("tel")
    gender = request.form.get("gender")
    dob = request.form.get("dob")
    address = request.form.get("address")
    

    # sql = "SELECT * FROM user WHERE emailid = ?"
    # stmt = ibm_db.prepare(conn, sql)
    # ibm_db.bind_param(stmt, 1, emailid)
    # ibm_db.execute(stmt)
    # account = ibm_db.fetch_assoc(stmt)
    account=check(emailid)
    if account:
        return render_template('Login.html', ibm1="You are already a member, please login using your details")
    else:
        insert_sql = "INSERT INTO user VALUES (?,?,?,?,?,?,?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, username)
        ibm_db.bind_param(prep_stmt, 2, lastname)
        ibm_db.bind_param(prep_stmt, 3, emailid)
        ibm_db.bind_param(prep_stmt, 4, password)
        ibm_db.bind_param(prep_stmt, 5, tel)
        ibm_db.bind_param(prep_stmt, 6, gender)
        ibm_db.bind_param(prep_stmt, 7, dob)
        ibm_db.bind_param(prep_stmt, 8, address)
        ibm_db.execute(prep_stmt)
        return render_template('Login.html', ibm="You are Successfully Registered, please login using your crendentials")


@app.route("/checkuser", methods=["POST"])
def checkuser():
    emailid = request.form.get("emailid")
    password = request.form.get("password")
    account=check(emailid)
    # sql = "SELECT * FROM user WHERE emailid = ?"
    # stmt = ibm_db.prepare(conn, sql)
    # ibm_db.bind_param(stmt, 1, emailid)
    # ibm_db.execute(stmt)
    # account = ibm_db.fetch_assoc(stmt)
    if account:
        if(password == str(account['PASSWORD']).strip()):
            return render_template('uniReg.html',msg = "successfully logged in")
        else:
            return render_template('Login.html', msg="Please enter the correct password")
    else:
        return render_template('Login.html', msg="No Account found! \n Please Signup")
        

@app.route("/predict" , methods=['GET','POST'])
def predict():
    if request.method == 'POST' :
        g = int(request.form["gre"])
        t = int(request.form["toefl"])
        r = int(request.form["university_rating"])
        s = float(request.form["sop"])
        l = float(request.form["lor"])
        c = float(request.form["cgpa"])
        re = request.form["research"]
        if( re == "Research"):
           re = 1
        else:
           re = 0
        S = [[g,t,r,s,l,c,re]]
        print("************************************************")
        payload_scoring = {"input_data": [{"field": ["GRE Score","TOEFL Score","University Rating","SOP","LOR" ,"CGPA","Research"], "values": [S]}]}
        response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/581582bf-4a79-41d8-a47b-85fc2f47260f/predictions?version=2022-11-17', json=payload_scoring,headers={'Authorization': 'Bearer ' + mltoken})
        print("Scoring response")
        predictions = response_scoring.json()
        output= predictions['predictions'][0]['values'][0][0]
        r =round(output,2)
        print(r)
        predict = int(r*100)
        p = '%'
        #output = output*100
        #z = str(output[0])
        
        if r ==  1:
            return render_template('result.html',ibm2="Your Chance of admit   =   " ,x= predict,per=p,rs=" Eligible Universities" ,u = "1. Harvard University" ,u1="2.University of Cambridge ", u2="3. University of Toronto", u3="4. Seoul National University" ,u4="5. University of Copenhagen")    
        elif r ==  2:
            return render_template('result.html',ibm2="Your Chance of admit   =   " ,x= predict,per=p,rs=" Eligible Universities" ,u ="1.  Massachusetts Institute of Technology" , u1="2. University of Oxford", u2="3. Kyoto University ", u3="4. Paris-Saclay University" , u4="5. Peking University ")
        elif r ==  3:
            return render_template('result.html',ibm2="Your Chance of admit   =   " ,x= predict,per=p,rs=" Eligible Universities" ,u ="1. University of British Columbia", u1="2. Sorbonne University" , u2="3. University of Chinese Academy of Sciences",  u3="4. Osaka University",  u4="5. Leiden University")
        elif r == 4:
            return render_template('result.html',ibm2="Your Chance of admit   =   " ,x= predict,per=p,rs=" Eligible Universities" ,u ="1. University of Alberta" ,u1="2. Heidelberg University" , u2="3. Institut Polytechnique de Paris", u3="4. University of Sydney" ,  u4="5. University of Basel")
        else:
            return render_template('result.html',ibm2="Your Chance of admit   =   " ,x= predict,per=p,rs=" Eligible Universities" ,u ="1. Columbia University", u1="2. University of Paris",  u2="3. King's College London" , u3="4. Technical University of Munich" ,  u4="5. Zhejiang University" )

    else :
        return "No method"



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
