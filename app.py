from flask import Flask,render_template,request,redirect,session,flash
from database import init_db
from database import check_user,register_user,get_user_passwords,add_password_entry
import secrets

app=Flask(__name__)
app.secret_key=secrets.token_hex(16)
init_db()

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']

        user=check_user(username,password)
        if user:
            session["user_id"]=user[0]
            return redirect('/dashboard')
        else:
            flash("Invalid username or password", "error")
            return redirect('/login')
    return render_template('login.html')


@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form["username"]
        password=request.form["password"]
        success=register_user(username,password)
        if success:
            return redirect('/login')
        else:
            flash("Username already exists", "error")
            return redirect('/register')
    return render_template("register.html")



@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
        
    if "user_id" not in session:
        flash("Please log in to view your dashboard.", "info")
        return redirect('/login')      
    else:
        user_id=session["user_id"]

        if request.method=='POST':
            website_name = request.form['website']
            username = request.form['username']
            password = request.form['password']

            success = add_password_entry(
            user_id, 
            website_name,  
            username, 
            password
        )
            if success:
                flash(f"Password added successfully!", "success")
            else:
                flash("An error occurred while adding the password.", "error")
            return redirect('/dashboard')
        passwords_data=get_user_passwords(user_id)
        return render_template('dashboard.html',passwords=passwords_data)



if __name__ == "__main__":
    app.run(debug=True)