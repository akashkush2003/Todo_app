#deploy on heroku cli
#To see the SQL template: SQLite Viewer
#SqlLite : File based database engine
#Jinja2: Template engine in flask to view python variables inside Html
# SQLAlchemy (ORM:Object Relational Mapper) :Allow writing python code to connect with database

from flask import Flask, render_template, request, redirect, url_for, session, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash  # for secure passwords

app = Flask(__name__) #Creation of object,website bnegi yahan
app.secret_key = "your_secret_key_here"  # must be set for session to work

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo2.db"  #Initializing sqlalchemy database file only confugation setup
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
 
# ------------------ MODELS ------------------ 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    todos = db.relationship("Todo", backref="owner", lazy=True)

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(200), nullable = False)
    desc = db.Column(db.String(200), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    def __repr__(self) -> str:                 
        return f"{self.sno} - {self.title}"

# -------Authentication Routes---------
@app.route("/register", methods=["GET", "POST"])
def register():
    message = ''
    if request.method == "POST": #agr post krna h to 
        # Collect username and password from form
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        # Save to database
        user = User(username=username, password=password)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("login"))
        except IntegrityError:
            db.session.rollback()
            message = "Username or password already exists. Please try another."
    return render_template("register.html", message=message) # For get call, new registration karo

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST": #POST request → when login form submitted:
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username = username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("hello_world"))
        else:
            return render_template("login.html", error="Invalid username or password!") #GET request → show login form (login.html).

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for("login"))


# ------------------ Todo APP ------------------
@app.route("/", methods = ["GET", "POST"]) #IMPORTANT calling function to index.html file 
def hello_world(): 
    if "user_id" not in session:   # check if logged in
        return redirect(url_for("login"))
    if request.method == 'POST':
        # print(request.form['title'])
        title = request.form['title']
        desc = request.form['desc']
        # todo = Todo(title = "First Todo", desc = "Start investing in Stock" )
        todo = Todo(title = title, desc = desc, user_id=session["user_id"])
        db.session.add(todo)
        db.session.commit()
        
    allTodo = Todo.query.filter_by(user_id=session["user_id"]).all()
    return render_template('index.html', allTodo=allTodo, user=session["username"]) #is list ko index html m hi call karna
    # return "<p>Hello, World!</p>"
    return render_template('index.html') 

@app.route('/show') #Webpage ko specific function s connect krne k liye
def products():
    allTodo = Todo.query.all()
    print(allTodo)
    return 'This is the productive page or 2nd index html'

@app.route('/search')
def search():
    query = request.args.get('query', '')  # get the search term from url param 'query'
    if query:
        # Example: search todos by title containing the query (case-insensitive)
        results = Todo.query.filter(Todo.title.ilike(f'%{query}%')).all()
    else:
        results = []
    return render_template('search.html', todos=results, query=query)

@app.route('/update/<int:sno>', methods = ["GET", "POST"])
def update(sno):
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        todo = Todo.query.filter_by(sno = sno, user_id=session['user_id']).first_or_404() #new todo nhi bana rahe isliye ise update krna padega
        todo.title = title
        todo.desc = desc
        db.session.add(todo)
        db.session.commit() 
        return redirect('/')

    todo = Todo.query.filter_by(sno = sno, user_id=session['user_id']).first_or_404()
    return render_template('update.html', todo = todo)
    

@app.route('/delete/<int:sno>')
def delete(sno):
    todo = Todo.query.filter_by(sno = sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")

# @app.route('/products')
# def products():
#     return 'This is the productive page or 2nd index html'

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug = False)
