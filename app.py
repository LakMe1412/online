from flask import Flask,url_for,session,redirect,render_template,request,flash,send_file,send_from_directory
from flask_session import Session 
from flask_mysqldb import MySQL
from otp import genotp
from cmail import sendmail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from tokenreset import token
from tokenr import tokenreset
import random
import os
app=Flask(__name__)
app.secret_key = '23efgbnjuytr'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'online'
Session(app)
mysql = MySQL(app)
@app.route('/',methods=['GET','POST'])
def home():
     if request.method=="POST":
        name=request.form['name']
        emailid=request.form['emailid']
        message=request.form['message']
        cursor=mysql.connection.cursor()
        cursor.execute('insert into contactus(name,emailid,message) values(%s,%s,%s)',[name,emailid,message])
        mysql.connection.commit()
     return render_template('home.html')
#----------------------------admin login---------------------------------------
@app.route('/adminsignin', methods = ['GET','POST'])
def aregister():
    if session.get('admin'):
        return redirect(url_for('admindashboard'))
    if request.method == 'POST':
        adminid= request.form['adminid']
        phonenumber= request.form['phonenumber']
        email = request.form['email']
        password= request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute ('select adminid from admin')
        data = cursor.fetchall()
        cursor.execute ('select email from admin')
        edata = cursor.fetchall()
        if (adminid,)in data:
            flash('user already exits')
            return render_template('admin.html')
        if (email,)in edata:
            flash('email already exits')                                                                                                                                                                                                                                                                                                                                                                                                                                                         
            return render_template('admin.html')
        cursor.close()
        otp = genotp()
        subject = 'thanks for registering'
        body = f'use this otp register {otp}'
        sendmail(email,subject,body)
        return render_template('otp.html',otp=otp,adminid=adminid,phonenumber=phonenumber,email=email,password=password)
    return render_template('admin.html')
@app.route('/alogin',methods=['GET','POST'])#after register login with rollno and password route
def alogin():
    if session.get('admin'):
        return redirect(url_for('admindashboard'))
    if request.method=='POST':
        adminid=request.form['adminid']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from admin where adminid=%s and password=%s',[adminid,password])#if the count is 0 then either username or password is wrong or if it is 1 then it is login successfully
        count=cursor.fetchall()[0]
        if count==0:
            flash('Invalid username or password')
            return render_template('alogin.html')
        else:
            session['admin']=adminid
            return redirect(url_for('admindashboard'))
    return render_template('alogin.html')

@app.route('/alogout')
def alogout():
    if session.get('admin'):
        session.pop('admin')
        return redirect(url_for('alogin'))
    else:
        flash('u are already logged out!')
        return redirect(url_for('alogin'))
        #return redirect(url_for('loginp'))
@app.route('/aotp/<otp>/<adminid>/<email>/<phonenumber>/<password>',methods = ['GET','POST'])
def aotp(otp,adminid,email,phonenumber,password):
    if request.method == 'POST':
        uotp=request.form['otp']
        if otp == uotp:
            cursor = mysql.connection.cursor()
            cursor.execute('insert into admin values(%s,%s,%s,%s)',(adminid,email,phonenumber,password))
            mysql.connection.commit()
            cursor.close()
            flash('Details Registered')#send mail to the user as successful registration
            return redirect(url_for('alogin'))
        else:
            flash('wrong otp')
            return render_template('otp.html',otp = otp,adminid=adminid,email=email,password= password,phonenumber=phonenumber)
@app.route('/forgetpassword',methods=['GET','POST'])
def forget():#after clicking the forget password
    if request.method=='POST':
        adminid=int(request.form['adminid'])# store the id in the rollno
        cursor=mysql.connection.cursor()#connection to mysql
        cursor.execute('select adminid from admin')# fetch the rollno data in the table students
        data=cursor.fetchall()#fetching all the rollno data and store it in the "data" variable 
        if (adminid,) in data:# if the given rollno of the user is present in tha database->data
            cursor.execute('select email from admin where adminid=%s',[adminid])#it fetches email related to the rollno 
            data=cursor.fetchone()[0]#fetch the only one email related to the rollno 
            cursor.close()
            subject=f'Reset Password for {data}'
            body=f'Reset the password using-{request.host+url_for("createpassword",token=token(adminid,120))}'
            sendmail(data,subject,body)
            flash('Reset link sent to your mail')
            return redirect(url_for('alogin'))
        else:
            return 'Invalid user id'
    return render_template('forgot.html')
@app.route('/createpassword/<token>',methods=['GET','POST'])
def createpassword(token):#to create new password and conform the password
        try:
            s=Serializer(app.config['SECRET_KEY'])
            adminid=s.loads(token)['admin']
            if request.method=='POST':
                npass=request.form['npassword']
                cpass=request.form['cpassword']
                if npass==cpass:
                    cursor=mysql.connection.cursor()
                    cursor.execute('update admin set password=%s where adminid=%s',[npass,adminid])
                    mysql.connection.commit()
                    return 'Password reset Successfull'
                else:
                    return 'Password mismatch'
            return render_template('newpassword.html')
        except Exception as e:
            print(e)
            return 'Link expired try again'
#------------------------------------user login---------------------------
@app.route('/signin', methods = ['GET','POST'])
def register():
    if session.get('user'):
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password= request.form['password']
        phno= request.form['phno']
        state=request.form['state']
        address=request.form['address']
        pincode=request.form['pincode']
        cursor=mysql.connection.cursor()
        cursor.execute ('select username from user')
        data = cursor.fetchall()
        cursor.execute ('select email from user')
        edata = cursor.fetchall()
        if (username,)in data:
            flash('user already exits')
            return render_template('usersignin.html')
        if (email,)in edata:
            flash('email already exits')                                                                                                                                                                                                                                                                                                                                                                                                                                                         
            return render_template('usersignin.html')
        cursor.close()
        otp = genotp()
        subject = 'thanks for registering'
        body = f'use this otp register {otp}'
        sendmail(email,subject,body)
        return render_template('otp1.html',otp=otp,username=username,email=email,password=password,phno=phno,state=state,address=address,pincode=pincode)
    return render_template('usersignin.html')
@app.route('/login',methods=['GET','POST'])
def login():
    if session.get('user'):
        return redirect(url_for('home'))
    if request.method=='POST':
        username=request.form['name']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from user where username=%s and password=%s',[username,password])
        count=cursor.fetchone()[0]
        if count==0:
            flash('invalid user name or password')
            return render_template('userlogin.html')
        else:
            session['user']=username
            return redirect(url_for('home'))
    return render_template('userlogin.html')

@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('login'))
    else:
        flash('u are already logged out!')
        return redirect(url_for('login'))
        #return redirect(url_for('loginp'))
@app.route('/otp/<otp>/<username>/<email>/<password>/<phno>/<state>/<address>/<pincode>',methods = ['GET','POST'])
def otp(otp,username,email,password,phno,state,address,pincode):
    if request.method == 'POST':
        uotp=request.form['otp']
        if otp == uotp:
            cursor = mysql.connection.cursor()
            cursor.execute('insert into user values(%s,%s,%s,%s,%s,%s,%s)',(username,email,password,phno,state,address,pincode))
            mysql.connection.commit()
            cursor.close()
            flash('Details Registered')#send mail to the user as successful registration
           
            return redirect(url_for('login'))
        else:
            flash('wrong otp')
            return render_template('otp1.html',otp = otp,name = name,email=email,password= password,phno=phno,state=state,address=address,pincode=pincode)


@app.route('/rforgetpassword',methods=['GET','POST'])
def rforget():#after clicking the forget password
    if request.method=='POST':
        username=request.form['username']# store the id in the rollno
        cursor=mysql.connection.cursor()#connection to mysql
        cursor.execute('select username from user')# fetch the username data in the table students
        data=cursor.fetchall()#fetching all the rollno data and store it in the "data" variable 
        if (username,) in data:# if the given rollno of the user is present in tha database->data
            cursor.execute('select email from user where username=%s',[username])#it fetches email related to the rollno 
            data=cursor.fetchone()[0]#fetch the only one email related to the rollno 
            #print(data)
            cursor.close()
            subject=f'Reset Password for {data}'
            body=f'Reset the password using-{request.host+url_for("rcreatepassword",token=token(username,200))}'
            sendmail(data,subject,body)
            flash('Reset link sent to your mail')
            return redirect(url_for('login'))
        else:
            return 'Invalid username'
    return render_template('rforget.html')
@app.route('/rcreatepassword/<token>',methods=['GET','POST'])
def rcreatepassword(token):#to create noe password and conform the password
        try:
            s=Serializer(app.config['SECRET_KEY'])
            username=s.loads(token)['user']
            if request.method=='POST':
                npass=request.form['npassword']
                cpass=request.form['cpassword']
                if npass==cpass:
                    cursor=mysql.connection.cursor()
                    cursor.execute('update user set password=%s where username=%s',[npass,username])
                    mysql.connection.commit()
                    return 'Password reset Successfull'
                    return redirect(url_for('login'))
                else:
                    return 'Password mismatch'
            return render_template('newpassword.html')
        except Exception as e:
            print(e)
            return 'Link expired try again'

@app.route('/complaint', methods=['GET', 'POST'])
def complaint():
    if session.get('user'):
        
        if request.method == "POST":
            id1=genotp()
            email = request.form['email']
            problem = request.form['problem']
            address=request.form['address']
            image=request.files['image']
            categorie=request.form['categorie']
            cursor=mysql.connection.cursor()
            filename=id1+'.jpg'
            data=cursor.execute('select * from complaint')
            print(data)
            cursor.execute('INSERT INTO complaint (id,username,email,problem,address,categorie) VALUES (%s,%s,%s,%s,%s,%s)',[id1,session.get('user'),email,problem,address,categorie]) 
            mysql.connection.commit()
            cursor.close()
            path=r"C:\Users\chith\OneDrive\Desktop\onlinecomplain\static"
            image.save(os.path.join(path,filename))
            
            subject = 'complaint deatils'
            body = 'complaint are submitted' 
            sendmail(email,subject,body)
            flash('complaint submitted')
            return redirect(url_for('home'))
        return render_template('complaintform.html')
    else:
        return redirect(url_for('login'))
        
@app.route('/admindashboard')
def admindashboard():
    if session.get('admin'):
        cursor=mysql.connection.cursor()
        cursor.execute('select * from complaint')
        details = cursor.fetchall()
        return render_template('admindashboard.html',details=details)
    else:
        return redirect(url_for('alogin'))
@app.route('/notsolved')
def notsolved():
    if session.get('admin'):
        cursor=mysql.connection.cursor()
        cursor.execute('select * from complaint where status="Not Started"')
        details=cursor.fetchall()
        '''if request.method=="POST":
            id1=request.form['id1']
            status=request.form['status']
            cursor.execute('update complaint set status=%s where id=%s',[id1,status])
            cursor.commit()'''
        return render_template('unsolved.html',details=details)
    else:
        return redirect(url_for('alogin'))
@app.route('/update/<id1>',methods=['GET','POST'])
def update(id1):
    if session.get('admin'):
        cursor=mysql.connection.cursor()
        cursor.execute('select * from complaint where id=%s',[id1])
        data=cursor.fetchone()
        cursor.close()
        if request.method=='POST':
            status=request.form['status']
            cursor=mysql.connection.cursor()
            cursor.execute('update complaint set status=%s where id=%s',[status,id1])
            mysql.connection.commit()
            cursor.execute('select email from complaint where id=%s',[id1])
            
            email=cursor.fetchone()[0]
            print(email)
            cursor.close()
            subject = 'complaint deatils'#--------------------
            body = f'the status of the complaint {status}' #-----------------------------
            sendmail(email,subject,body)#-----------------
            flash('updated successfully')
            cursor.close()
            flash('updated successfully')
            return redirect(url_for('notsolved'))
     
    else:
        return redirect(url_for('alogin'))
    return render_template('update.html',data=data)
@app.route('/currently')
def currently():
    if session.get('admin'):
        cursor=mysql.connection.cursor()
        cursor.execute('select * from complaint where status="In Progress"')
        details=cursor.fetchall()
        return render_template('inprogress.html',details=details)
    else:
        return redirect(url_for('alogin'))
@app.route('/oldcomplaint')
def oldcomplaint():
    if session.get('admin'):
        cursor=mysql.connection.cursor()
        cursor.execute('select * from complaint where status="resolved"')
        details=cursor.fetchall()
        return render_template('inprogress.html',details=details)
    else:
        return redirect(url_for('alogin'))
@app.route('/user')
def user():
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('select * from complaint where username=%s',[session.get('user')])
        details=cursor.fetchall()
        return render_template('userstatus.html',details=details)

@app.route('/view/<id1>')
def view(id1):
        path=os.path.dirname(os.path.abspath(__file__))
        static_path=os.path.join(path,'static')
        return send_from_directory(static_path,f'{id1}.jpg')
@app.route('/viewcontactus')
def contactusview():
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('select * from contactus order by date desc')
        data=cursor.fetchall()
        return render_template('viewcontactus.html',data=data)
    else:
        return redirect(url_for('login'))


    
app.run(use_reloader=True,debug=True)

