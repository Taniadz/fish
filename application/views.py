import os
from flask import render_template, render_template_string, flash, redirect, url_for, request, g
from application import app, db, ALLOWED_EXTENSIONS, UPLOAD_FOLDER, login_manager
from forms import RegistrationForm, LoginForm, PostForm, CommentForm, UserEditForm, ProductForm, ProductCommentForm
from models import User, Post, Comment, Product, added_post, CommentProduct
from flask_login import login_user, logout_user, current_user, login_required
from flask_json import FlaskJSON, JsonError, json_response, as_json, jsonify
from werkzeug.datastructures import CombinedMultiDict
from werkzeug import secure_filename
from flask.ext.login import login_required
from datetime import datetime
from datetime import timedelta
POSTS_PER_PAGE = 3
from helpers import *



@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.now()
        db.session.add(g.user)
        db.session.commit()



@app.route('/')
@app.route('/index')
def index():
    return render_template('home.html', user=current_user)


@app.route('/popular_product', methods=['GET', 'POST'])
@app.route('/popular_product/<int:page>', methods=['GET', 'POST'])
def popular_product(page = 1):
    products = Product.query.order_by(Product.vote_count.desc()).paginate(page, POSTS_PER_PAGE, False)
    for p in products.items:
        print(p.deleted)
    dict_like = {}
    saved_list=[]
    if current_user.is_authenticated:
        likes = get_user_like(Product)

        for p in current_user.added_product:
            saved_list.append(p.id)
        dict_like=create_dict_like(dict_like, products.items, likes)
    print(dict_like)
    return render_template('popular_product.html',
        dict_like = dict_like,
        products = products,
        saved_list=saved_list)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user=create_element(db.session, User, username=form.username.data,
                            password=form.password.data,
                            email=form.email.data,
                            about_me=form.about_me.data,
                            avatar = "icon-user-default.png"    )

        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        registered_user = get_user(username=form.username.data,password=form.password.data)
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


@app.route('/add_post', methods = ['GET', 'POST'])
def add_post():
    form = PostForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'POST' and form.validate():
        filename = create_filename(form.file.data )
        post = Post(title=form.title.data.strip(), body=form.body.data.strip(), user_id=current_user.id)
        post.image = filename
        db.session.add(post)
        db.session.commit()
        flash("Post published!", 'alert-success')
        return redirect(url_for('singlepost', postid=post.id))
    return render_template("add_post.html", form=form)


@app.route('/last_posts', methods=['GET', 'POST'])
@app.route('/last_posts/<int:page>', methods=['GET', 'POST'])
def last_posts(page = 1):
    posts = Post.query.order_by(Post.published_at.desc()).paginate(page, POSTS_PER_PAGE, False)
    saved_list = []
    dict_like = {}
    if current_user.is_authenticated:
        likes = get_user_like(Post)
        for p in current_user.added_post:
            saved_list.append(p.id)
        dict_like = create_dict_like(dict_like, posts.items, likes)
    return render_template('last_posts.html',
        dict = dict_like,
        posts = posts,
        saved_list=saved_list)


@app.route('/user/<username>')
def user(username):
    user = get_user(username=username)
    if user == None:
        flash('User ' + username + ' not found.')
        return redirect(url_for('index'))
    posts = get_posts_by_user_id(user.id)
    saved_list = []
    dict_like = {}
    if current_user.is_authenticated:
        for p in current_user.added_post:
            saved_list.append(p.id)
        likes = get_user_like(Post)
        dict_like = create_dict_like(dict_like, posts, likes)
    return render_template('user.html',
                           saved_list=saved_list,
                           dict_like=dict_like,
                           user=user,
                           posts=posts)


@app.route('/user_edit/<username>', methods=['GET', 'POST'])
@login_required
def user_edit(username):
    form = UserEditForm(CombinedMultiDict((request.files, request.form)))
    user = get_user(username=username)
    if request.method == 'POST' and form.validate():
        filename = create_filename(form.file.data, "icon-user-default.png")
        user=update_user(db.session, user,filename, form.username.data, form.about_me.data)

        return redirect(url_for('user', username=form.username.data))
    form.username.data = user.username
    form.about_me.data = user.about_me
    return render_template('user_edit.html',
                           user=user,
                           form=form)


@app.route('/post/<int:postid>', methods=['GET', 'POST'])
def singlepost(postid=None):
    form = CommentForm(CombinedMultiDict((request.files, request.form)))
    ifsaved = False
    ifliked = False
    print(current_user.added_post, 111)
    if current_user.is_authenticated:
        likes = current_user.like_com
    else:
        likes = False
    dict_like = {}
    if request.method == 'GET':

        posts=get_posts_ordering(Post.published_at.desc(), 10)
        post = get_post_by_id(postid).first()
        editable = check_post_editable(post)
        comments = get_comments_by_post_id(post.id)

        if current_user.is_authenticated:
            liked = Post.query.filter(Post.user_like.any(id=current_user.id)).all()
            print(liked)
            ifliked = many_to_many(post, liked)#check if post in many to many table user liked post

            dict_like=create_dict_like(dict_like, comments, likes)
            saved=get_user_save(current_user.id, Post) #get posts saved by user
            ifsaved = many_to_many(post, saved)
        return render_template("single_post.html",
                               editable=editable,
                               posts=posts,
                               post=post,
                               postid=postid,
                               form=form,
                               comments=comments,
                               ifsaved=ifsaved,
                               ifliked=ifliked,
                               dict_like=dict_like,
                               dictionary=get_comment_dict(comments))
    if request.method == 'POST':
        filename = create_filename(form.file.data)
        if request.args.get('parent'):
            parent = request.args.get('parent')
        else:
            parent = 0
        comment = create_element(db.session, Comment,
                        text=form.text.data,
                        user_id=current_user.id,
                        post_id=postid,
                        image = filename,
                        parent=parent)

        comments = get_comments_by_post_id(postid)
        dict_like = create_dict_like(dict_like, comments, likes)
        data = {'comments' : render_template('comments.html',
                                             dict_like=dict_like,
                                             postid=postid,
                                             comments=comments,
                                             dictionary=get_comment_dict(comments),
                                             form=form)}
        return jsonify(data)


@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def singleproduct(product_id=None):

    form = CommentForm(CombinedMultiDict((request.files, request.form)))
    ifsaved = False
    ifliked = False
    if current_user.is_authenticated:
        likes = current_user.like_prod_com
    else:
        likes=False
    dict_like = {}
    if request.method == 'GET':

        product = Product.query.filter_by(id=product_id).first()
        comments = get_prod_comments_by_product_id(product_id)
        if current_user.is_authenticated:
            liked = Product.query.filter(Product.user_like.any(id=current_user.id)).all()
            ifliked=many_to_many(product, liked)
            dict_like = create_dict_like(dict_like, comments, likes)
            saved=get_user_save(current_user.id, Product)

            ifsaved=many_to_many(product, saved)
        dictionary = get_comment_dict(comments)

        return render_template("single_product.html",
                               ifsaved=ifsaved,
                               ifliked=ifliked,
                               dict_like=dict_like,
                               product=product,
                               comments=comments,
                               product_id=product_id,
                               dictionary=dictionary,
                               form=form)
    if request.method == 'POST':
        filename = create_filename(form.file.data)
        if request.args.get('parent'):
            parent = request.args.get('parent')
        else:
            parent = 0
        comment = create_element(db.session, CommentProduct,
                                 text=form.text.data,
                                 user_id=current_user.id,
                                 product_id=product_id,
                                 image=filename,
                                 parent=parent)
        comments = get_prod_comments_by_product_id(product_id)
        dict_like = create_dict_like(dict_like, comments, likes)
        data = {'comments' : render_template('product_comments.html',
                                             dict_like=dict_like,
                                             product_id=product_id,
                                             comments=comments,
                                             dictionary=get_comment_dict(comments),
                                             form=form)}
        return jsonify(data)


@app.route('/add_product', methods = ['GET', 'POST'])
def add_product():
    form = ProductForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'POST' and form.validate():
        f = form.file.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(UPLOAD_FOLDER, filename))
        product=create_element(db.session, Product, title=form.title.data.strip(),
                               price=form.price.data.strip(),
                               description=form.description.data.strip(),
                               user_id=current_user.id,
                               image=filename)


        return redirect(url_for('singleproduct', product_id=product.id))
    return render_template("add_product.html", form=form)


@app.route('/like_post', methods=['POST'])
def like_post():
    id = request.form.get('id')
    post = get_post_by_id(id).first()
    data = check_for_like(db.session, post, current_user)
    return jsonify(data)

@app.route('/like_comment', methods=['POST'])
def like_comment():
    id = request.form.get('id')
    comment = get_comment_by_id(id).first()
    data = check_for_like(db.session, comment, current_user)
    return jsonify(data)

@app.route('/like_product', methods=['POST'])
def like_product():
    id = request.form.get('id')
    product = get_product_by_id(id).first()
    data = check_for_like(db.session, product, current_user)
    return jsonify(data)

@app.route('/like_prodcomment', methods=['POST'])
def like_prodcomment():
    id = request.form.get('id')
    comment = get_prod_comment_by_id(id).first()
    data = check_for_like(db.session, comment, current_user)
    return jsonify(data)


@app.route('/unlike_post', methods=['POST'])
def unlike_post():
    id = request.form.get('id')
    post = get_post_by_id(id).first()
    data = check_for_unlike(db.session, post, current_user)
    return jsonify(data)

@app.route('/unlike_comment', methods=['POST'])
def unlike_comment():
    id = request.form.get('id')
    comment = get_comment_by_id(id).first()
    data = check_for_unlike(db.session, comment, current_user)
    return jsonify(data)


@app.route('/unlike_product', methods=['POST'])
def unlike_product():
    id = request.form.get('id')
    product = get_product_by_id(id).first()
    data = check_for_unlike(db.session, product, current_user)
    return jsonify(data)


@app.route('/unlike_prodcomment', methods=['POST'])
def unlike_prodcomment():
    id = request.form.get('id')
    comment = get_prod_comment_by_id(id).first()
    data = check_for_unlike(db.session, comment, current_user)
    return jsonify(data)


@app.route('/comment_form', methods=['POST'])
def comment_form():
    parent_id =request.form.get('parent_id')
    post_id = request.form.get('post_id')
    form = CommentForm(request.form)
    data = {'com_form': render_template('comment_form.html',
                                    post_id=post_id,
                                    parent_id=parent_id,
                                    form=form)}
    return jsonify(data)




@app.route('/product_comment_form', methods=['POST'])
def product_comment_form():
    parent_id =request.form.get('parent_id')
    product_id = request.form.get('product_id')
    form = CommentForm(request.form)
    data = {'com_form': render_template('product_comment_form.html',
                                    product_id=product_id,
                                    parent_id=parent_id,
                                    form=form)}
    return jsonify(data)


@app.route('/user_contain_comment', methods=['POST'])
def user_contain_comment():
    dict_like = {}
    if request.form.get('contain') == "comment":
        if request.form.get('sort') == "data":
            comments = get_comments_by_user_id(request.form.get('user_id'), Comment.timestamp.desc())
        else:
            comments = get_comments_by_user_id(request.form.get('user_id'), Comment.vote_count.desc())
        if current_user.is_authenticated:
            likes = current_user.like_com
            dict_like={}
            dict_like = create_dict_like(dict_like, comments, likes)

        data = {'com_container': render_template('user_contain_comment.html',
                                            dict_like=dict_like,
                                             comments=comments,
                                             )}
    if request.form.get('contain') == "prod_comment":
        if request.form.get('sort') == "data":
            comments = get_prod_comments_by_user_id(request.form.get('user_id'), CommentProduct.timestamp.desc())
        else:
            comments = get_prod_comments_by_user_id(request.form.get('user_id'), CommentProduct.vote_count.desc())
        if current_user.is_authenticated:
            likes = current_user.like_prod_com
            dict_like={}
            dict_like = create_dict_like(dict_like, comments, likes)
        data = {'com_container': render_template('user_contain_prod_comment.html',
                                                 dict_like=dict_like,
                                                 comments=comments,
        )}

    return jsonify(data)

@app.route('/user_contain_product', methods=['POST'])
def user_contain_product():
    if request.form.get('sort') == "data":
        products = get_products_by_user_id(request.form.get('user_id'), Product.published_at.desc())
    else:
        products = get_products_by_user_id(request.form.get('user_id'), Product.vote_count.desc())
    likes = get_user_like(Product)
    saved_list = []
    for p in current_user.added_product:
        saved_list.append(p.id)
    dict_like={}
    dict_like = create_dict_like(dict_like, products, likes)
    data = {'prod_container': render_template('user_contain_product.html',
                                              saved_list=saved_list,
                                              dict_like=dict_like,
                                                 products=products,
        )}
    return jsonify(data)

@app.route('/user_contain_post', methods=['POST', 'GET'])
def user_contain_post():
    if request.form.get('sort') == "data":
        posts = get_posts_by_user_id(request.form.get('user_id'), Post.published_at.desc())
    else:
        posts = get_posts_by_user_id(request.form.get('user_id'), Post.vote_count.desc())
    saved_list = []
    for p in current_user.added_post:
        saved_list.append(p.id)
    likes = get_user_like(Post)
    dict_like = {}
    dict_like = create_dict_like(dict_like, posts, likes)

    data = {'post_container': render_template('user_contain_post.html',
                                              saved_list=saved_list,
                                              dict_like=dict_like,
                                              posts=posts,
    )}
    return jsonify(data)

@app.route('/user_contain_saved', methods=['POST'])
def user_contain_saved():
    id = request.form.get('user_id')

    if request.form.get('contain') == "product":
        if request.form.get('sort') == "data":
            products=get_user_save(id, Product, Product.published_at.desc())
            print(products)
        else:
            products = get_user_save(id, Product, Product.vote_count.desc())
        likes = get_user_like(Product)
        dict_like = {}
        dict_like = create_dict_like(dict_like, products, likes)
        saved_list = []
        for p in current_user.added_product:
            saved_list.append(p.id)

        data = {'saved_container': render_template('user_contain_prod_saved.html',
                                                   dict_like=dict_like,
                                                   products=products,
                                                   saved_list=saved_list,
                                                   )}
    if request.form.get('contain') == "post":
        if request.form.get('sort') == "data":
            posts = get_user_save(id, Post, Post.published_at.desc() )
        else:
            posts = get_user_save(id, Post, Post.vote_count.desc())
        likes = get_user_like(Post)

        dict_like = {}
        dict_like = create_dict_like(dict_like, posts, likes)
        saved_list = []
        for p in current_user.added_post:
            saved_list.append(p.id)

        data = {'saved_container': render_template('user_contain_post_saved.html',
                                                   dict_like=dict_like,
                                                   saved_list=saved_list,
                                                   posts=posts,
                                                       )}
    return jsonify(data)


@app.route('/save_product', methods=['GET'])
def save_product(**kwargs):
    id = request.args.get("product_id")
    User = current_user
    Product = get_product_by_id(id).first()
    User.added_product.append(Product)
    db.session.add(User)
    db.session.commit()
    flash("You have saved", 'alert-success')
    return jsonify(id)

@app.route('/save_post', methods=['GET', 'POST'])
def save_post():
    id = request.args.get("post_id")
    User = current_user
    Post=get_post_by_id(id).first()
    User.added_post.append(Post)

    db.session.add(User)
    db.session.commit()

    return jsonify(id)


@app.route('/delete_post', methods=['GET', 'POST'])
def delete_post():
    id = request.args.get("post_id")
    User = current_user
    Post = get_post_by_id(id).first()
    print(User.added_post)
    print(Post)
    User.added_post.remove(Post)
    db.session.commit()
    return jsonify(id)

@app.route('/delete_product', methods=['GET', 'POST'])
def delete_product():
    id = request.args.get("product_id").first()
    User = current_user
    Product = get_product_by_id(id)
    User.added_product.remove(Product)
    db.session.commit()
    return jsonify(id)

@app.route('/post_contain_comment', methods=['POST'])
def post_contain_comment():
    form = CommentForm(request.form)
    if request.form.get('sort') == "data":
         comments = get_comments_by_post_id(request.form.get('post_id'), Comment.timestamp.desc())
    elif request.form.get('sort') == "rating":
        comments = get_comments_by_post_id(request.form.get('post_id'), Comment.vote_count.desc())
    likes = current_user.like_com
    dict_like = {}
    dict_like = create_dict_like(dict_like, comments, likes)
    dictionary = get_comment_dict(comments, 'sort')
    data = {'comments': render_template('comments.html',
                                        dict_like=dict_like,
                                        postid=request.form.get('post_id'),
                                        comments=comments,
                                        dictionary=dictionary,
                                        form=form)}
    return jsonify(data)


@app.route('/product_contain_comment', methods=['POST'])
def product_contain_comment():
    form = CommentForm(request.form)

    if request.form.get('sort') == "data":
        comments = get_prod_comments_by_product_id(request.form.get('product_id'), CommentProduct.timestamp.desc())
    elif request.form.get('sort') == "rating":
        comments = get_prod_comments_by_product_id(request.form.get('product_id'), CommentProduct.vote_count.desc())

    likes = current_user.like_prod_com
    dict_like = {}
    dict_like = create_dict_like(dict_like, comments, likes)

    dictionary = get_comment_dict(comments, 'sort')
    data = {'comments': render_template('comments.html',
                                        dict_like=dict_like,
                                        product_id=request.form.get('product_id'),
                                        comments=comments,
                                        dictionary=dictionary,
                                        form=form)}
    return jsonify(data)



@app.route('/edit_prod_comment/<int:comment_id>', methods=['GET', 'POST'])
def edit_prod_comment(comment_id=None):
    if request.method == 'GET':
        comment = get_prod_comment_by_id(id=comment_id).first()
        if not check_com_editable(comment):
            data = {'noedit': "No_editable"}

            return jsonify(data)
        form = CommentForm(CombinedMultiDict((request.files, request.form)))

        form.text.data = comment.text
        data = {'form': render_template('edit_comment.html',
                                        url="edit_prod_comment",
                                        comment=comment,
                                        form=form)}
        return jsonify(data)
    if request.method == 'POST':
        form = CommentForm(CombinedMultiDict((request.files, request.form)))

        filename = create_filename(form.file.data)
        comment = get_prod_comment_by_id(id=comment_id)
        update_rows(comment, text=form.text.data, image=filename)
        comment=comment[0]
        dict_like={}
        for like in current_user.like_prod_com:
            if like == comment:
                dict_like[comment.id]=1
                break
        data = {'comment': render_template('/comment_box/product_comment_box.html',
                                           dict_like=dict_like,
                                           comment=comment)}

        return jsonify(data)


@app.route('/edit_post_comment/<int:comment_id>', methods=['GET', 'POST'])
def edit_post_comment(comment_id=None):
    form = CommentForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'GET':
        comment = get_comment_by_id(id=comment_id).first()
        if not check_com_editable(comment):
            data = {'noedit': "No_editable"}
            print(111)
            return jsonify(data)
        form.text.data = comment.text
        data = {'form': render_template('edit_comment.html',
                                        url = "edit_post_comment",
                                        comment=comment,
                                        form=form)}
        return jsonify(data)
    if request.method == 'POST':
        filename = create_filename(form.file.data)
        comment = get_comment_by_id(comment_id)
        update_rows(comment, text=form.text.data, image=filename)
        comment=comment[0]
        dict_like = {}
        for like in current_user.like_com:
            if like == comment:
                dict_like[comment.id] = 1
                break
        data = {'comment': render_template('/comment_box/post_comment_box.html',
                                           dict_like=dict_like,
                                           comment=comment)}
        return jsonify(data)



@app.route('/delete_post_comment', methods=['POST'])
def del_post_comment():
    id = request.form.get("id")
    comment = get_comment_by_id(id)
    if not check_com_editable(comment[0]):
        data = {'nodelet': "No deletable"}
    else:
        update_rows(comment, deleted=True)

        data = {'deleted': "Comment has been deleted"}

    return jsonify(data)

@app.route('/delete_prod_comment', methods=['POST'])
def del_prod_comment():
    id = request.form.get("id")
    comment = get_prod_comment_by_id(id)
    if not check_com_editable(comment[0]):
        data = {'nodelet': "No deletable"}
    else:
        update_rows(comment, deleted=True)

        data = {'deleted': "Comment has been deleted"}

    return jsonify(data)




@app.route('/user_del_product', methods=['POST'])
def user_del_product():
    id = request.form.get("id")
    product = get_product_by_id(id)
    update_rows(product, deleted=True)
    return redirect(url_for('popular_product'))


@app.route('/user_edit_product', methods=['POST', 'GET'])
def user_edit_product():
    form = ProductForm(CombinedMultiDict((request.files, request.form)))
    id = request.args.get("id")
    if request.method == 'GET':
        product = get_product_by_id(id).first()

        form.description.data = product.description
        form.title.data=product.title
        form.price.data = product.price
    if request.method == 'POST' and form.validate():

        filename = create_filename(form.file.data)
        product = get_product_by_id(id)
        update_rows(product, description=form.description.data,
                                title = form.title.data,
                                price = form.price.data,
                                image= filename)
        return redirect(url_for('singleproduct', product_id=id))
    return render_template("edit_product.html", form=form, id=id)


@app.route('/user_del_post', methods=['POST'])
def user_del_post():
    id = request.form.get("id")
    post = get_post_by_id(id)
    update_rows(post, deleted=True)
    return redirect(url_for('last_posts'))


@app.route('/user_edit_post', methods=['POST', 'GET'])
def user_edit_post():
    id = request.args.get("id")

    form = PostForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'GET':
        post = get_post_by_id(id).first()
        if not check_post_editable(post):
            flash("You can't edit it")
            return redirect(url_for('singlepost', postid=id))
        form.body.data=post.body
        form.title.data=post.title
        return render_template("edit_post.html", form=form, id=id)

    elif request.method == 'POST' and form.validate():


        filename = create_filename(form.file.data)
        post = get_post_by_id(id)
        update_rows(post, body=form.body.data,
             title=form.title.data,
             image=filename)

        return redirect(url_for('singlepost', postid=id))
