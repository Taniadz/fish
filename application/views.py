
from flask import render_template,  flash, redirect, url_for, request, g, session
from application import app, db, user_datastore, social, security, celery
from forms import PostForm, CommentForm, UserEditForm, ProductForm
from werkzeug import secure_filename
from models import  PostComReaction, ProdComReaction, ProductReaction, PostReaction
from flask_login import current_user
from flask_json import FlaskJSON, JsonError, json_response, as_json, jsonify
from werkzeug.datastructures import CombinedMultiDict


from flask_security import login_required

POSTS_PER_PAGE = 3
from helpers import *
from PIL import Image, ImageOps, ImageDraw



@security.register_context_processor
def security_login_processor():
    return dict(content='Profile Page',
        facebook_api=social.facebook.get_api(),
        facebook_conn=social.facebook.get_connection())

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    user = User.query.filter(User.id==1).first()
    return render_template('home.html', user=current_user)


@app.route('/popular_product', methods=['GET', 'POST'])
@app.route('/popular_product/<int:page>', methods=['GET', 'POST'])
def popular_product(page = 1):
    if request.args.get("sort") == "rating":
        products = get_products_ordering(Product.like_count.desc()).paginate(page, POSTS_PER_PAGE, False)
    else:
        products = get_products_ordering(Product.published_at.desc()).paginate(page, POSTS_PER_PAGE, False)

    dict_like = {}
    saved_list=[]
    if current_user.is_authenticated:
        likes = current_user.product_react
        print(likes)
        saved_list = create_saved_list(saved_list, products.items, current_user.favourite_product)
        dict_like=product_dict_like(dict_like, products.items, likes)
    return render_template('popular_product.html',
        dict_like = dict_like,
        products = products,
        saved_list=saved_list)

@app.route('/add_post', methods = ['GET', 'POST'])
def add_post():
    form = PostForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'POST' and form.validate():
        filename = create_filename(form.file.data )
        post = create_obj(Post,
                          title=form.title.data.strip(),
                          body=form.body.data.strip(),
                          user_id=current_user.id,
                          image=filename)
        return redirect(url_for('singlepost', postid=post.id))
    return render_template("add_post.html", form=form)


@app.route('/last_posts', methods=['GET', 'POST'])
@app.route('/last_posts/<int:page>', methods=['GET', 'POST'])
def last_posts(page = 1):
    if request.args.get("sort") == "data":
        posts=get_posts_ordering(Post.published_at.desc()).paginate(page, POSTS_PER_PAGE, False)
    else:
        posts=get_posts_ordering(Post.like_count.desc()).paginate(page, POSTS_PER_PAGE, False)

    saved_list = []
    dict_like = {}
    if current_user.is_authenticated:
        likes = current_user.post_react  # all post, liked by current user
        saved_list = create_saved_list(saved_list, posts.items, current_user.favourite_post)

        dict_like = post_dict_like(dict_like, posts.items, likes)
    return render_template('last_posts.html',
        dict_like = dict_like,
        posts = posts,
        saved_list=saved_list)


@app.route('/user/<username>')
def user(username):
    user = get_user(username=username).first()
    if user == None:
        flash('User ' + username + ' not found.')
        return redirect(url_for('index'))
    posts = get_posts_by_user_id(user.id)
    saved_list = []
    dict_like = {}
    if current_user.is_authenticated and current_user.username == username:
        saved_list = create_saved_list(saved_list, posts, current_user.favourite_post)
        likes = get_post_reaction(user_id=current_user.id)
        dict_like = post_dict_like(dict_like, posts, likes)
    return render_template('user.html',
                           saved_list=saved_list,
                           dict_like=dict_like,
                           user=user,
                           posts=posts)


@celery.task
def async_crop(data_image, username):

    user = get_user(username=username)
    width = data_image.get("width")
    width = float(width)
    height = data_image.get("height")
    height = float(height)
    x = data_image.get("x")
    x = float(x)
    x0 = int(x)
    y = data_image.get("y")
    y = float(y)
    y0 = int(y)
    x1 = x0 + width
    y1 = y0 + height
    image = Image.open(os.path.join(UPLOAD_FOLDER, user[0].avatar))
    im = image.crop((x0, y0, x1, y1))
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    im.putalpha(mask)
    filename = secure_filename("min_" + user[0].avatar)
    print filename
    filename_png = filename[:-3] + "png"
    print filename_png
    im.save(os.path.join(UPLOAD_FOLDER, filename_png))
    print filename_png
    update_rows(user, avatar_min=filename_png)
    return True



@app.route('/crop_image', methods=['GET', 'POST'])
@login_required
def crop_image():
    username = current_user.username
    user = get_user(username=username)
    if request.method == 'POST':

        data_image = request.form.to_dict()
        result = async_crop.delay(data_image, username)

        return redirect(url_for('user', username=username))
    else:
        return render_template('crop_image.html',
                               user=user[0])



@app.route('/user_edit/<username>', methods=['GET', 'POST'])
@login_required
def user_edit(username):
    form = UserEditForm(CombinedMultiDict((request.files, request.form)))
    user = get_user(username=username)
    if request.method == 'POST' and form.validate():
        print form.file.data
        filename = create_filename(form.file.data)
        print filename
        user = update_rows(user,
        avatar = filename,
        username = form.username.data,
        about_me = form.about_me.data)
        return redirect(url_for('crop_image'))
    else:
        user = get_user(username=username).first()
        form.username.data = user.username
        form.about_me.data = user.about_me
        return render_template('user_edit.html',
                               user=user,
                               form=form)


@app.route('/post/<int:postid>', methods=['GET', 'POST'])
def singlepost(postid=None):
    form = CommentForm(CombinedMultiDict((request.files, request.form)))
    ifsaved = False  # check if post added to popular by user, False for not login
    post_like = None  # check if post liked by user, None for not login
    if current_user.is_authenticated:
        likes = current_user.post_com_react  # all comments, liked by current user
    else:
        likes = False  # false for not login
    dict_like = {}
    if request.method == 'GET':
        posts=get_posts_ordering(Post.published_at.desc(), 10)
        post = get_post_by_id(postid).first()
        editable = check_post_editable(post) #check if user can edit post
        comments = get_comments_by_post_id(post.id)
        if current_user.is_authenticated:
            post_like = get_one_like(PostReaction, user_id=current_user.id, post_id=post.id) # check if the post liked by user
            if current_user in post.favourite: #if in all userlist saved this post
                ifsaved = True
        dict_like = comment_dict_like(dict_like, comments, likes)
        print(dict_like)
        return render_template("single_post.html",
                               editable=editable, posts=posts,
                               post=post, postid=postid,
                               form=form, comments=comments,
                               ifsaved=ifsaved,post_like=post_like,
                               dict_like=dict_like,
                               dictionary=get_comment_dict(comments)) # create comment tree)
    if request.method == 'POST' and form.validate():
        filename = create_filename(form.file.data)
        if request.args.get('parent'):
            parent = request.args.get('parent')
        else:
            parent = 0
        comment = create_obj(Comment,
                        text=form.text.data,
                        user_id=current_user.id,
                        post_id=postid,
                        image = filename,
                        parent=parent)
        comments = get_comments_by_post_id(postid)
        data = {'comments' : render_template('comments.html',
                                             dict_like=comment_dict_like(dict_like, comments, likes),
                                             postid=postid,
                                             comments=comments,
                                             dictionary=get_comment_dict(comments),  # create comment tree
                                             form=form)}
        return jsonify(data)


@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def singleproduct(product_id=None):
    form = CommentForm(CombinedMultiDict((request.files, request.form)))
    ifsaved = False
    product_like = None
    if current_user.is_authenticated:
        likes = current_user.prod_com_react
    else:
        likes=False
    dict_like = {}
    if request.method == 'GET':
        product = Product.query.filter_by(id=product_id).first()
        comments = get_prod_comments_by_product_id(product_id)
        if current_user.is_authenticated:
            product_like = get_one_like(ProductReaction, user_id=current_user.id,
                                   product_id=product.id)  # check if the product liked by user

            if current_user in product.favourite:  #if in all userlist saved this product
                ifsaved = True

        return render_template("single_product.html",
                               ifsaved=ifsaved, product_like=product_like,
                               dict_like=comment_dict_like(dict_like, comments, likes),
                               product=product, comments=comments,
                               product_id=product_id,
                               dictionary=get_comment_dict(comments),
                               form=form)
    if request.method == 'POST' and  form.validate():
        filename = create_filename(form.file.data)
        if request.args.get('parent'):
            parent = request.args.get('parent')
        else:
            parent = 0
        comment = create_obj(CommentProduct,
                                 text=form.text.data,
                                 user_id=current_user.id,
                                 product_id=product_id,
                                 image=filename,
                                 parent=parent)
        comments = get_prod_comments_by_product_id(product_id)
        dict_like = comment_dict_like(dict_like, comments, likes)

        data = {'comments' : render_template('product_comments.html',
                                             dict_like=dict_like,
                                             product_id=product_id,
                                             comments=comments,
                                             dictionary=get_comment_dict(comments),
                                             form=form)}
        return jsonify(data)




@app.route('/add_product', methods = ['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'POST' and form.validate():
        filename = create_filename(form.file.data)
        product=create_obj(Product, title=form.title.data.strip(),
                               price=form.price.data.strip(),
                               description=form.description.data.strip(),
                               user_id=current_user.id,
                               image=filename)
        return redirect(url_for('singleproduct', product_id=product.id))
    return render_template("add_product.html", form=form)



@app.route('/like_post', methods=['POST'])
def like_post():
    id = request.form.get('id')
    react_type = request.form.get('type')
    if react_type == None:
        react_type = "like"
    print(react_type, "in view")
    post = get_post_by_id(id)
    data = increase_count(post, PostReaction, react_type, post_id=id, user_id=current_user.id)  # increase vote count of post
    return jsonify(data)


@app.route('/like_comment', methods=['POST'])
def like_comment():
    id = request.form.get('id')
    react_type = request.form.get('type')
    if react_type == None:
        react_type = "like"
    comment = get_comment_by_id(id)
    data = increase_count(comment, PostComReaction, react_type, comment_id=id, user_id=current_user.id)  # increase vote count of post
    return jsonify(data)

@app.route('/like_product', methods=['POST'])
def like_product():
    id = request.form.get('id')
    react_type = request.form.get('type')
    if react_type == None:
        react_type = "like"
    post = get_product_by_id(id)
    data = increase_count(post, ProductReaction, react_type, product_id=id,
                               user_id=current_user.id)  # increase vote count of post
    return jsonify(data)

@app.route('/like_prodcomment', methods=['POST'])
def like_prodcomment():
    id = request.form.get('id')
    react_type = request.form.get('type')
    if react_type == None:
        react_type = "like"
    comment = get_prod_comment_by_id(id)
    data = increase_count(comment, ProdComReaction, react_type, comment_id=id,
                          user_id=current_user.id)  # increase vote count of post
    return jsonify(data)



@app.route('/unlike_post', methods=['POST'])
def unlike_post():
    id = request.form.get('id')
    post = get_post_by_id(id)
    data = check_decrease_count(post, PostReaction, post_id=id, user_id=current_user.id)  # increase vote count of post if like doesn't exist
    return jsonify(data)


@app.route('/unlike_comment', methods=['POST'])
def unlike_comment():
    id = request.form.get('id')
    comment = get_comment_by_id(id)
    data = check_decrease_count(comment, PostComReaction, comment_id=id, user_id=current_user.id)  # increase vote count of post if like doesn't exist
    return jsonify(data)


@app.route('/unlike_product', methods=['POST'])
def unlike_product():
    id = request.form.get('id')
    product = get_product_by_id(id)

    data = check_decrease_count(product, ProductReaction, product_id=id,
                                user_id=current_user.id)  # increase vote count of post if like doesn't exist
    return jsonify(data)


@app.route('/unlike_prodcomment', methods=['POST'])
def unlike_prodcomment():
    id = request.form.get('id')
    comment = get_prod_comment_by_id(id)
    data = check_decrease_count(comment, ProdComReaction, comment_id=id,
                                user_id=current_user.id)  # increase vote count of post if like doesn't exist
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
            comments = get_comments_by_user_id(request.form.get('user_id'), Comment.like_count.desc())
        if current_user.is_authenticated:
            likes = current_user.post_com_react
            dict_like={}
            dict_like = comment_dict_like(dict_like, comments, likes)

        data = {'com_container': render_template('/user_container/user_contain_comment.html',
                                            dict_like=dict_like,
                                             comments=comments,
                                             )}
    if request.form.get('contain') == "prod_comment":
        if request.form.get('sort') == "data":
            comments = get_prod_comments_by_user_id(request.form.get('user_id'), CommentProduct.timestamp.desc())
        else:
            comments = get_prod_comments_by_user_id(request.form.get('user_id'), CommentProduct.like_count.desc())
        if current_user.is_authenticated:
            likes = current_user.prod_com_react
            dict_like={}
            dict_like = comment_dict_like(dict_like, comments, likes)
        data = {'com_container': render_template('/user_container/user_contain_prod_comment.html',
                                                 dict_like=dict_like,
                                                 comments=comments,
        )}

    return jsonify(data)



@app.route('/user_contain_product', methods=['POST'])
def user_contain_product():
    if request.form.get('sort') == "data":
        products = get_products_by_user_id(request.form.get('user_id'), Product.published_at.desc())
    else:
        products = get_products_by_user_id(request.form.get('user_id'), Product.like_count.desc())
    likes = current_user.product_react
    saved_list = []
    saved_list = create_saved_list(saved_list, products, current_user.favourite_product)
    dict_like={}
    dict_like = product_dict_like(dict_like, products, likes)
    data = {'prod_container': render_template('/user_container/user_contain_product.html',
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
        posts = get_posts_by_user_id(request.form.get('user_id'), Post.like_count.desc())
    saved_list = []
    saved_list = create_saved_list(saved_list, posts, current_user.favourite_post)

    likes = current_user.post_react
    dict_like = {}
    dict_like = post_dict_like(dict_like, posts, likes)
    data = {'post_container': render_template('/user_container/user_contain_post.html',
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
            products=get_favourite(id, Product, Product.published_at.desc())


        else:
            products = get_favourite(id, Product, Product.like_count.desc())
        likes = current_user.product_react
        dict_like = {}
        dict_like = product_dict_like(dict_like, products, likes)
        saved_list=[]
        saved_list = create_saved_list(saved_list, products, current_user.favourite_product)

        data = {'saved_container': render_template('/user_container/user_contain_prod_saved.html',
                                                   dict_like=dict_like,
                                                   products=products,
                                                   saved_list=saved_list,
                                                   )}
    if request.form.get('contain') == "post":
        if request.form.get('sort') == "data":
            posts = get_favourite(id, Post, Post.published_at.desc() )
        else:
            posts = get_favourite(id, Post, Post.like_count.desc())
        likes = current_user.post_react

        dict_like = {}
        dict_like = post_dict_like(dict_like, posts, likes)
        saved_list = []
        saved_list = create_saved_list(saved_list, posts, current_user.favourite_post)

        data = {'saved_container': render_template('/user_container/user_contain_post_saved.html',
                                                   dict_like=dict_like,
                                                   saved_list=saved_list,
                                                   posts=posts,
                                                       )}
    return jsonify(data)


@app.route('/add_fav_product', methods=['GET'])
def add_fav_product():
    id = request.args.get("product_id")
    user = current_user
    product = get_product_by_id(id).first()
    add_prod_fav(user, product)
    return jsonify(id)


@app.route('/add_fav_post', methods=['GET', 'POST'])
def add_fav_post():
    id = request.args.get("post_id")
    user = current_user
    post=get_post_by_id(id).first()
    add_post_fav(user, post)
    return jsonify(id)


@app.route('/delete_fav_post', methods=['GET', 'POST'])
def delete_fav_post():
    id = request.args.get("post_id")
    user = current_user
    post = get_post_by_id(id).first()
    delete_post_fav(user, post)
    print 1
    return jsonify(id)


@app.route('/delete_fav_product', methods=['GET', 'POST'])
def delete_fav_product():
    id = request.args.get("product_id")
    user = current_user
    product = get_product_by_id(id).first()
    delete_prod_fav(user, product)
    print 1
    return jsonify(id)


@app.route('/post_contain_comment', methods=['POST'])
def post_contain_comment():
    form = CommentForm(request.form)
    if request.form.get('sort') == "data":
         comments = get_comments_by_post_id(request.form.get('post_id'), Comment.timestamp.desc())
    elif request.form.get('sort') == "rating":
        comments = get_comments_by_post_id(request.form.get('post_id'), Comment.like_count.desc())
    likes = current_user.post_com_react
    dict_like = {}
    dict_like = comment_dict_like(dict_like, comments, likes)
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
        comments = get_prod_comments_by_product_id(request.form.get('product_id'), CommentProduct.like_count.desc())

    likes = current_user.prod_com_react
    dict_like = {}
    dict_like = comment_dict_like(dict_like, comments, likes)
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
    form = CommentForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'GET':
        comment = get_prod_comment_by_id(id=comment_id).first()
        if not check_com_editable(comment):
            data = {'noedit': "No_editable"}
            return jsonify(data)
        form.text.data = comment.text
        data = {'form': render_template('edit_comment.html',
                                        url="edit_prod_comment",
                                        comment=comment,
                                        form=form)}
        return jsonify(data)
    if request.method == 'POST':
        filename = create_filename(form.file.data)
        comment = get_prod_comment_by_id(id=comment_id)
        update_rows(comment, text=form.text.data, image=filename)
        comment=comment[0]
        dict_like={}
        if get_one_like(ProdComReaction, user_id = current_user.id, comment_id=comment.id):
                dict_like[comment.id]=1

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
        if get_one_like(PostComReaction, user_id = current_user.id, comment_id=comment.id):
                dict_like[comment.id]=1
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
