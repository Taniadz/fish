
from flask import render_template, flash, redirect, url_for, request, g
from application import app, db
from forms import RegistrationForm, LoginForm, PostForm, CommentForm
from models import User, Post, Comment
from flask.ext.login import login_user , logout_user , current_user , login_required



@app.route('/')
@app.route('/index')
def index():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data, form.password.data, form.email.data)
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        registered_user = User.query.filter_by(username=form.username.data,password=form.password.data).first()
        if registered_user is None:
            flash('Username or Password is invalid', 'error')
            return redirect(url_for('login'))
        login_user(registered_user)
        flash('Logged in successfully')
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/post/<int:postid>', methods = ['GET', 'POST'])
def singlepost(postid=None):
    post = Post.query.filter_by(id=postid).first()
    comments = post.comments.all()
    form = CommentForm(request.form)
    if request.method == 'POST' and form.validate():
        comment = Comment(text=form.text.data.strip(), user_id=current_user.id, post_id=postid, parent = form.parent.data)
        db.session.add(comment)
        db.session.commit()
        flash("Comment published!", 'alert-success')
        return redirect(url_for('singlepost', postid=postid))
    return render_template("single_post.html", post=post, form = form, comments = comments)


@app.route('/add_post', methods = ['GET', 'POST'])
def add_post():
    form = PostForm(request.form)
    if request.method == 'POST' and form.validate():
        post = Post(title=form.title.data.strip(), body=form.body.data.strip(), user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash("Post published!", 'alert-success')
        return redirect(url_for('index'))
    return render_template("add_post.html", form=form)