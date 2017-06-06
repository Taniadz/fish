import os
from flask import render_template, render_template_string, flash, redirect, url_for, request, g
from application import app, db, ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from forms import RegistrationForm, LoginForm, PostForm, CommentForm, UserEditForm, ProductForm, ProductCommentForm
from models import User, Post, Comment, Product, ProductLike, PostLike, CommentLike
from flask_login import login_user, logout_user, current_user, login_required
import json
from flask_json import FlaskJSON, JsonError, json_response, as_json, jsonify
from werkzeug.datastructures import CombinedMultiDict
from werkzeug import secure_filename
from datetime import datetime
from sqlalchemy_imageattach.context import store_context
POSTS_PER_PAGE = 2
from helpers import *

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()



@app.route('/')
@app.route('/index')
def index():
    return render_template('home.html', user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data, form.password.data, form.email.data, form.about_me.data)
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


@app.route('/post/<int:postid>', methods=['GET', 'POST'])
def singlepost(postid=None):
    form = CommentForm(request.form)
    form.post_id.data = postid
    if request.method == 'GET':
        post = get_post_by_id(postid)
        comments = get_comments_by_post_id(post.id)

    if request.method == 'POST':

        print form.data
        print request.form.get('parent')
        comment = Comment(text=form.text.data.strip(),
                          user_id=current_user.id,
                          post_id=form.post_id.data)
        if form.parent.data == "":
            comment.parent = 0
        else:
            comment.parent = request.form.get('parent')
        db.session.add(comment)
        db.session.commit()

        flash("Comment published!", 'alert-success')
        childform = CommentForm(request.form)
        data = {'comments' : render_template('comments.html',
                                             comments=get_comments_by_post_id(form['post_id'].data),
                                             dictionary=get_comment_dict(form['post_id'].data),
                                             form=childform)}

        return jsonify(data)

    else:
        return render_template("single_post.html",
                               post=post,
                               form=form,
                               comments=comments,
                               dictionary=get_comment_dict(form['post_id'].data))


@app.route('/add_post', methods = ['GET', 'POST'])
def add_post():
    form = PostForm(request.form)
    if request.method == 'POST' and form.validate():
        post = Post(title=form.title.data.strip(), body=form.body.data.strip(), user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash("Post published!", 'alert-success')
        return redirect(url_for('singlepost', postid=post.id))
    return render_template("add_post.html", form=form)


@app.route('/last_posts', methods=['GET', 'POST'])
@app.route('/last_posts/<int:page>', methods=['GET', 'POST'])
def last_posts(page = 1):
    posts = Post.query.order_by(Post.published_at.desc()).paginate(page, POSTS_PER_PAGE, False)

    return render_template('last_posts.html',
        posts = posts)


@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user == None:
        flash('User ' + username + ' not found.')
        return redirect(url_for('index'))
    posts = Post.query.filter_by(user_id=user.id)
    return render_template('user.html',
                           user=user,
                           posts=posts)


@app.route('/user_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def user_edit(id):
    form = UserEditForm(CombinedMultiDict((request.files, request.form)))
    user = User.query.filter_by(id = id).first()
    if request.method == 'POST' and form.validate():
        f = form.file.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(UPLOAD_FOLDER, filename))
        user.username = form.username.data
        user.about_me = form.about_me.data
        user.avatar = filename
        db.session.add(user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', username=form.username.data))
    else:
         form.username.data = user.username
         form.about_me.data = user.about_me
    return render_template('user_edit.html',
                           user=user,
                           form=form)



@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def singleproduct(product_id=None):
    product = Product.query.filter_by(id=product_id).first()
    comments = get_comments_by_product_id(product_id)
    form = ProductCommentForm(request.form)
    form.product_id.data = product_id

    if form.validate_on_submit() and request.method == 'POST':
        comment = CommentProduct(text=form.text.data.strip(),
                          user_id=current_user.id,
                          product_id=form.product_id.data)
        if form.parent.data == "":
            comment.parent = 0
        else:
            comment.parent = form.parent.data
        db.session.add(comment)
        db.session.commit()
        flash("Comment published!", 'alert-success')
        data = {'comments' : render_template('product_comments.html',
                                             comments=get_comments_by_product_id(form['product_id'].data),
                                             dictionary=get_prod_comment_dict(form['product_id'].data),

                                             form=form)}
        return jsonify(data)
    elif request.method == 'POST':
        product_like = get_or_create(db.session, ProductLike, product=product_id, user=current_user.id )
        if not product_like:
            flash("You have already voted!", 'alert-success')
            return jsonify(product.vote_count)
        else:
            product.vote_count = product.vote_count + 1
            db.session.add(product)
            db.session.commit()
            return jsonify(product.vote_count)

    else:
        return render_template("single_product.html",
                           product=product,
                           comments=comments,
                           dictionary=get_prod_comment_dict(form['product_id'].data),
                           form=form)


@app.route('/add_product', methods = ['GET', 'POST'])
def add_product():
    form = ProductForm(request.form)
    if request.method == 'POST' and form.validate():
        product = Product(title=form.title.data.strip(), description=form.description.data.strip(), user_id=current_user.id)
        db.session.add(product)

        db.session.commit()
        flash("Post published!", 'alert-success')
        return redirect(url_for('singleproduct', product_id=product.id))
    return render_template("add_product.html", form=form)



@app.route('/like_comment', methods=['POST', 'GET'])
def like_comment():
    id = request.form.get('id')
    comment = get_comment_by_id(id)
    comment_like = get_or_create(db.session, CommentLike, comment=id, user=current_user.id)
    if not comment_like:
        flash("You have already voted!", 'alert-success')

        return jsonify(comment.vote_count)
    else:
        comment.vote_count = comment.vote_count + 1
        db.session.add(comment)
        db.session.commit()
        return jsonify(comment.vote_count)


@app.route('/like_post/<int:postid>', methods=['POST', 'GET'])
def like_post(postid):
    post = get_post_by_id(postid)
    if request.method == 'POST':
        post_like = get_or_create(db.session, PostLike, post=postid, user=current_user.id )
        if not post_like:
            flash("You have already voted!", 'alert-success')
            return jsonify(post.vote_count)
        else:
            post.vote_count = post.vote_count + 1
            db.session.add(post)
            db.session.commit()
            return jsonify(post.vote_count)


