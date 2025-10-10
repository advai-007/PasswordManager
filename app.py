from flask import Flask,render_template,request,redirect,session,flash
from database import init_db
from database import check_user,register_user,get_user_passwords,add_password_entry,delete_password_entry
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
            session["key"] = user[1]
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
        key=session['key']

        if request.method=='POST':
            website_name = request.form['website']
            username = request.form['username']
            password = request.form['password']

            success = add_password_entry(
            user_id, 
            website_name,  
            username, 
            password,
            key
        )
            if success:
                flash(f"Password added successfully!", "success")
            else:
                flash("An error occurred while adding the password.", "error")
            return redirect('/dashboard')
        passwords_data=get_user_passwords(user_id, key)
        return render_template('dashboard.html',passwords=passwords_data)


@app.route('/delete_password', methods=['POST'])
def delete_password():
    # 1. Check for user authentication
    if "user_id" not in session:
        flash("Please log in to perform this action.", "error")
        return redirect('/login')

    user_id = session["user_id"]
    
    # 2. Get the password ID from the form data
    password_id = request.form.get('password_id')
    
    if not password_id:
        flash("Invalid password ID provided.", "error")
        return redirect('/dashboard')
    
    try:
        password_id = int(password_id)
    except ValueError:
        flash("Invalid password ID format.", "error")
        return redirect('/dashboard')

    # 3. Attempt to delete the entry
    success = delete_password_entry(password_id, user_id)

    # 4. Flash message and redirect
    if success:
        flash("Password entry successfully deleted.", "success")
    else:
        # This covers cases where deletion fails or the password_id doesn't belong to the user
        flash("Error deleting password or password not found.", "error")

    return redirect('/dashboard')
    
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect('/login')



if __name__ == "__main__":
    app.run(debug=True)