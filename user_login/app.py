'''
@Author: Vinay gopal
Date: 25/11/2021
'''

# Imports libraries from flask
from flask import Flask, render_template, request, url_for, redirect, session
import pymongo
import bcrypt

app = Flask(__name__)
app.secret_key = "testing"
#connection of mongodb through the pymongo
client = pymongo.MongoClient("mongodb+srv://vinaygopal44:vinaygopal@cluster0.n4auo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.get_database('total_records')
records = db.register

'''
Description: using this index method we are storing the users data in the mongodb and authentication of the user.

Params: fullname, email, password, repeat password

Return: returns the index.html
'''
@app.route("/", methods=['post', 'get'])
def index():
    message = ''
    #if user login through email, session is started and running till the user logsout
    if "email" in session:                      
        return redirect(url_for("logged_in"))
    #send the data through the http POST method to the database 
    if request.method == "POST":    
        user = request.form.get("fullname")
        email = request.form.get("email")
        
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        
        #Checking the user details in the database, if matches shows the appropriate message to the user
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
            #encrypting the user password
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed}
            records.insert_one(user_input)
            
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
   
            return render_template('logged_in.html', email=new_email)
    return render_template('index.html')



'''
Description:  Used to show the user email in the loggged_in

Params: email

Return: if logged_in else login components
'''
@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email)
    else:
        return redirect(url_for("login"))



'''
Description:  Used to login in to the user account

Params: email,password

Return: login
'''
@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

       
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)



'''
Description:  Used to logout the user account, session is terminated

Params: email

Return: index
'''
@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('index.html')


# @app.route("/reset_password", methods=["POST", "GET"])
# def forgot_password():
#     return render_template('forgetpassword.html')



#end of code to run it
if __name__ == "__main__":
  app.run(debug=True)