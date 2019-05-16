from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:jessie@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __init__(self,title,body,owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40))
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self,username,password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup','blog','index']
    if request.endpoint not in allowed_routes  and 'username' not in session:
        return redirect('/login')

@app.route('/',methods=['GET'])
def index():
    switch = 0
    user_id = request.args.get('id')
    if user_id == None:
        users = User.query.all()
        return render_template('index.html',title="Authors",users=users,switch=switch)
    else:
        switch = 1
        users = User.query.filter_by(id=user_id).all()
        posts = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('index.html',title="Posts by " + users[0].username,users=users,posts=posts,switch=switch)

@app.route('/blog',methods=['GET'])
def blog():
    post_id = request.args.get('id')
    if post_id == None:
        posts = Blog.query.all()
        return render_template('blog.html',title="Build A Blog: Posts",posts=posts)
    else:
        posts = Blog.query.filter_by(id=post_id).all()
        return render_template('blog.html',title="Build A Blog: Posts",posts=posts)

@app.route('/newpost',methods = ['POST','GET'])
def newpost():

    if request.method == 'POST':
        owner = User.query.filter_by(username=session['username']).first()
        title = request.form['title']
        body = request.form['body']
        new_post = Blog(title,body,owner)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/blog')


    return render_template('newpost.html',title="Add a New Post")

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        users = User.query.filter_by(username=username,password=password).all()
        no_match = "Username/Password Does Not Match"
        if len(users) == 0:
            return render_template('login.html', title = "Sign Up",
                                name=username,password=password,no_match=no_match)
        else:
            session['username'] = username
            return redirect('/newpost')
    return render_template('login.html')

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':

        name = request.form['name']
        password = request.form['password']
        verify = request.form['verify']
        email = request.form['email']

        name_spaces = 0
        for i in range(len(str(name))):
            if name[i] == " ":
                name_spaces = name_spaces + 1

        pass_spaces = 0
        for i in range(len(str(password))):
            if password[i] == " ":
                pass_spaces = pass_spaces + 1

        email_spaces = 0
        email_at = 0
        email_per = 0

        for i in range(len(str(email))):
            if email[i] == " ":
                email_spaces = email_spaces + 1
            if email[i] == "@":
                email_at = email_at + 1
            if email[i] == ".":
                email_per = email_per + 1

        no_match = "    Passwords didn't match!"
        not_long = "    Must be less than 20 characters!"
        too_long = "    Must be more than 3 characters!"
        no_space = "    No spaces allowed!"
        invalid_email = "   Invalid eMail!"

        pass_not = not_long
        pass_too = too_long
        name_not = not_long
        name_too = too_long
        name_np = no_space
        pass_np = no_space
        inv_email = invalid_email

        check = 0
        if (email_spaces == 0)and(email_at == 1)and(email_per == 1):
            inv_email = ""
            check = check + 1
        if name_spaces == 0:
            name_np = ""
            check = check + 1
        if pass_spaces == 0:
            pass_np = ""
            check = check + 1
        if password == verify:
            no_match = ""
            check = check + 1
        if len(password) >= 3:
            pass_too = ""
            check = check + 1
        if len(password) <= 20:
            pass_not = ""
            check = check + 1
        if len(name) >= 3:
            name_too = ""
            check = check + 1
        if len(name) <= 20:
            name_not = ""
            check = check + 1

        if check != 8:
            return render_template('signup.html', title = "Sign Up",
                                name=name,password=password,verify=verify,
                                email=email,no_match=no_match,
                                pass_not=pass_not,pass_too=pass_too,
                                name_not=name_not,name_too=name_too,
                                name_np=name_np,pass_np=pass_np,
                                inv_email=inv_email)
        else:
            new_user = User(name,password)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/login')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


if __name__ == '__main__':
    app.run()
