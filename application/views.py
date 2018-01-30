
from flask import render_template,  flash, redirect, url_for, request, g, send_from_directory
from application import celery, UPLOAD_FOLDER
from .forms import PostForm, CommentForm, UserEditForm, ProductForm
from werkzeug import secure_filename
from .models import PostComReaction, ProdComReaction, ProductReaction, ProductImage
from flask_login import current_user
from flask_json import jsonify
from werkzeug.datastructures import CombinedMultiDict


from flask_security import login_required

POSTS_PER_PAGE = 6
from .helpers import *
from PIL import Image, ImageDraw

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page

def save_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'facebook':
        profile = user.get_profile()
        if profile is None:
            return "hi"


@app.before_request
def global_user():
    g.user = current_user

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# @security.register_context_processor
# def security_login_processor():
#     return dict(content='Profile Page',
#         facebook_api=social.facebook.get_api(),
#         facebook_conn=social.facebook.get_connection())

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    posts = get_posts_ordering(Post.published_at.desc()).paginate(1, POSTS_PER_PAGE, False)
    products = get_products_ordering(Product.like_count.desc()).paginate(1, POSTS_PER_PAGE, False)
    list_of_favourite_product = create_list_of_favourite_products(products.items, current_user)
    dict_like_product = product_dict_react(products.items, current_user)
    list_of_favourite_post = create_list_of_favourite_posts(posts.items, current_user)
    dict_like_post = post_dict_react(posts.items, current_user)
    return render_template('home.html', user=current_user,
                           posts=posts,
                           products=products,
                           dict_like_post=dict_like_post, dict_like_product=dict_like_product,
                           list_of_favourite_post=list_of_favourite_post,
                           list_of_favourite_product=list_of_favourite_product)


@app.route('/popular_product', methods=['GET', 'POST'])
@app.route('/popular_product/<int:page>', methods=['GET', 'POST'])
def popular_product(page=1):
    if request.args.get("sort") == "rating":
        products = get_products_ordering(Product.like_count.desc()).paginate(page, POSTS_PER_PAGE, False)
    else:
        products = get_products_ordering(Product.published_at.desc()).paginate(page, POSTS_PER_PAGE, False)
    list_of_favourite = create_list_of_favourite_products(products.items, current_user)
    dict_like=product_dict_react(products.items, current_user)
    print(dict_like)
    return render_template('popular_product.html',
        dict_like = dict_like,
        products = products,
        list_of_favourite=list_of_favourite)


@app.route('/add_post', methods = ['GET', 'POST'])
def add_post():
    form = PostForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'POST' and form.validate_on_submit():
        print(form.file.data)
        filename = create_filename(form.file.data)
        post = create_obj(Post,
                          title=form.title.data.strip(),
                          body=form.body.data.strip(),
                          user_id=current_user.id,
                          image=filename)
        return redirect(url_for('singlepost', postid=post.id))
    return render_template("add_post.html", form=form)



@app.route('/last_posts', methods=['GET', 'POST'])
@app.route('/last_posts/<int:page>', methods=['GET', 'POST'])
def last_posts(page=1):
    if request.args.get("sort") == "data":  # sort by datetime
        posts = get_posts_ordering(Post.published_at.desc()).paginate(page, POSTS_PER_PAGE, False)
    else:  # sort by rating
        posts = get_posts_ordering(Post.like_count.desc()).paginate(page, POSTS_PER_PAGE, False)

    # empty for not authenticated users
    list_of_favourite = create_list_of_favourite_posts(posts.items, current_user)
    # functions return dict with key - object id and value - type of reaction
    dict_like = post_dict_react(posts.items, current_user)
    return render_template('last_posts.html',
                           dict_like=dict_like, posts = posts,
                           list_of_favourite=list_of_favourite,
                           page=page,
                           sort = request.args.get("sort"))


@app.route('/user/<username>')
def user(username):
    user = get_or_abort(User, username=username).first()
    print(user.social_auth_usersocialauth)
    if user is None:
        flash('User ' + username + ' not found.')
        return redirect(url_for('index'))
    posts = get_ordered_list(Post, Post.published_at.desc(),
                             user_id=user.id)



    # show posts, written by profile owner(default), others container rendered by ajax
    # with def user_contain_* functions. This part is showed by included user_contain_post.html
    list_of_favourite = create_list_of_favourite_posts(posts, user)

    # functions return dict with key - object id and value - type of reaction
    dict_like = post_dict_react(posts, user)
    return render_template('user.html',
                           list_of_favourite=list_of_favourite, dict_like=dict_like,
                           user=user, user_id=user.id, posts=posts)



@celery.task
def async_crop(data_image, username):
    user = get_or_abort(User, username=username)

    # get params to crop image
    width = float(data_image.get("width"))
    height = float(data_image.get("height"))
    x0 = int(float(data_image.get("x")))
    y0 = int(float(data_image.get("y")))
    x1 = x0 + width
    y1 = y0 + height

    # crop image and made circle
    image = Image.open(os.path.join(UPLOAD_FOLDER, user[0].avatar))
    im = image.crop((x0, y0, x1, y1))
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    im.putalpha(mask)

    # save image
    filename = secure_filename("min_" + user[0].avatar)
    filename_png = filename[:-3] + "png"  # convert to png
    im.save(os.path.join(UPLOAD_FOLDER, filename_png))
    update_rows(user, avatar_min=filename_png)
    return True



@app.route('/crop_image', methods=['GET', 'POST'])
@login_required
def crop_image():
    username = current_user.username
    user = get_or_abort(User, username=username)
    if request.method == 'POST':
        data_image = request.form.to_dict()
        result = async_crop.delay(data_image, username)  # give it celery
        return redirect(url_for('user', username=username))
    else:
        return render_template('crop_image.html',
                               user=user[0])



@app.route('/user_edit/<username>', methods=['GET', 'POST'])
@login_required
def user_edit(username):
    form = UserEditForm(CombinedMultiDict((request.files, request.form)))
    user = get_or_abort(User, username=username)
    if request.method == 'POST' and form.validate_on_submit():

        filename = create_filename(form.file.data)  # create secure filename
        user = update_rows(user, avatar=filename,
                           username=form.username.data,
                           about_me=form.about_me.data,
                           avatar_min=None)
        if form.file.data is not None:
            return redirect(url_for('crop_image'))
        else:
            return redirect(url_for('user', username=username))
    else:
        form.username.data = user[0].username
        form.about_me.data = user[0].about_me
        return render_template('user_edit.html',
                               user=user[0],
                               form=form)


@app.route('/post/<int:postid>', methods=['GET', 'POST'])
def singlepost(postid=None):
    form = CommentForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'GET':
        post = get_or_abort(Post, id=postid).first()

        if post.deleted:
            return render_template("deleted_object.html", object=post)

        posts = get_posts_ordering(Post.published_at.desc(), 10)  # posts for side box
        editable = check_post_editable(post)  # check if user can edit post
        comments = get_all_obj(Comment, post_id=post.id)
        if_favorite = check_if_favourite(current_user, post)  # check if post added to favourite by user, False for not login too
        dict_like = post_comment_dict_react(comments, current_user)

        if current_user.is_authenticated:
            post_liked = get_one_obj(PostReaction, user_id=current_user.id,
                                   post_id=postid)  # check if the post liked by user
        else:
            post_liked = False    # for not authenticated users
        return render_template("single_post.html", editable=editable,
                               posts=posts, post=post,  form=form,
                               comments=comments, if_favorite=if_favorite,
                               post_liked=post_liked, dict_like=dict_like,
                               comment_tree=get_comment_dict(comments))

    if request.method == 'POST' and form.validate_on_submit():
        filename = create_filename(form.file.data)
        parent = request.args.get('parent')
        if request.args.get('parent') is None:
            parent = 0
        create_obj(Comment, text=form.text.data, user_id=current_user.id,
                   post_id=postid, image=filename, parent=parent)
        comments = get_ordered_list(Comment, Comment.timestamp, post_id=postid)
        data = {'comments': render_template('comments.html', dict_like=post_comment_dict_react(comments,
                                            current_user), comments=comments,
                                            comment_tree=get_comment_dict(comments),  form=form)}
        return jsonify(data)





@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def singleproduct(product_id=None):
    form = CommentForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'GET':
        product = get_one_obj(Product, id=product_id)

        if product.deleted:
            return render_template("deleted_object.html", object=product)
        products=get_products_ordering(Product.published_at.desc(), 10)  # products for side box
        comments = get_all_obj(CommentProduct, product_id=product_id)
        if_favorite = check_if_favourite(current_user, product)  # check if post added to favourite by user, False for not login too
        dict_like = prod_comment_dict_react(comments, current_user)
        if current_user.is_authenticated:
            product_liked = get_one_obj(ProductReaction, user_id=current_user.id,
                                product_id=product.id)  # check if the product liked by user
        else:
            product_liked = False
        return render_template("single_product.html",
                               if_favorite=if_favorite, product_liked=product_liked,
                               dict_like=dict_like, products=products,
                               product=product, comments=comments,
                               product_id=product_id, form=form,
                               comment_tree=get_comment_dict(comments))
    if request.method == 'POST' and form.validate_on_submit():
        filename = create_filename(form.file.data)
        parent = request.args.get('parent')
        if request.args.get('parent') is None:
            parent = 0
        comment = create_obj(CommentProduct, text=form.text.data,
                             user_id=current_user.id, product_id=product_id,
                             image=filename, parent=parent)
        comments = get_all_obj(CommentProduct, product_id=product_id)
        data = {'comments' : render_template('product_comments.html',
                                             dict_like=prod_comment_dict_react(comments, current_user),
                                             comments=comments,
                                             comment_tree=get_comment_dict(comments), form=form)}
        return jsonify(data)




@app.route('/add_product', methods = ['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'POST' and form.validate():
        product = create_obj(Product, title=form.title.data.strip(),
                             price=form.price.data.strip(),
                             description=form.description.data.strip(),
                             user_id=current_user.id,
                             )
        print(product.id, "prod.id")
        images = request.files.getlist("images")
        print(images, "images")
        for img in images:
            print(img)
            filename = create_filename(img)
            print(filename, "filename")
            new_image = create_obj(ProductImage, user_id=current_user.id,
                                   filename=filename,
                                   product_id=product.id)


        return redirect(url_for('singleproduct', product_id=product.id))
    return render_template("add_product.html", form=form)



@app.route('/like_post', methods=['POST'])
def like_post():
    react_type = request.form.get('type')
    if react_type == None:
        react_type = "like"
    post = get_or_abort(Post, id=request.form.get('id'))
    data = increase_count(post, PostReaction, react_type,
                          post_id=request.form.get('id'), user_id=current_user.id)  # increase vote count of post
    return jsonify(data)


@app.route('/like_comment', methods=['POST'])
def like_comment():
    react_type = request.form.get('type')
    if react_type == None:
        react_type = "like"
    comment = get_or_abort(Comment, id=request.form.get('id'))
    data = increase_count(comment, PostComReaction, react_type,
                          comment_id=request.form.get('id'), user_id=current_user.id)  # increase vote count of post
    return jsonify(data)

@app.route('/like_product', methods=['POST'])
def like_product():
    react_type = request.form.get('type')
    if react_type == None:
        react_type = "like"
    product = get_or_abort(Product, id=request.form.get('id'))
    data = increase_count(product, ProductReaction, react_type, product_id=request.form.get('id'),
                               user_id=current_user.id)  # increase vote count of post
    return jsonify(data)


@app.route('/like_prodcomment', methods=['POST'])
def like_prodcomment():
    react_type = request.form.get('type')
    if react_type == None:
        react_type = "like"
    comment = get_or_abort(CommentProduct, id=request.form.get('id'))
    data = increase_count(comment, ProdComReaction, react_type, comment_id=request.form.get('id'),
                          user_id=current_user.id)  # increase vote count of comment
    return jsonify(data)



@app.route('/unlike_post', methods=['POST'])
def unlike_post():
    post = get_or_abort(Post, id=request.form.get('id'))
    print(request.form.get('id'))
    data = check_decrease_count(post, PostReaction, post_id=request.form.get('id'),
                                user_id=current_user.id)  # increase vote count of post if like doesn't exist
    return jsonify(data)


@app.route('/unlike_comment', methods=['POST'])
def unlike_comment():
    comment = get_or_abort(Comment, id=request.form.get('id'))
    data = check_decrease_count(comment, PostComReaction, comment_id=request.form.get('id'),
                                user_id=current_user.id)  # increase vote count of post if like doesn't exist
    return jsonify(data)


@app.route('/unlike_product', methods=['POST'])
def unlike_product():
    product = get_or_abort(Product, id=request.form.get('id'))
    data = check_decrease_count(product, ProductReaction, product_id=request.form.get('id'),
                                user_id=current_user.id)  # increase vote count of post if like doesn't exist
    return jsonify(data)


@app.route('/unlike_prodcomment', methods=['POST'])
def unlike_prodcomment():

    comment = get_or_abort(CommentProduct, id=request.form.get('id'))
    data = check_decrease_count(comment, ProdComReaction, comment_id=request.form.get('id'),
                                user_id=current_user.id)  # increase vote count of post if like doesn't exist
    return jsonify(data)


# render comment form for comment with parent (after click discussion button)
@app.route('/comment_form', methods=['POST'])
def comment_form():
    form = CommentForm(request.form)
    data = {'com_form': render_template('comment_form.html', post_id=request.form.get('post_id'),
                                        parent_id=request.form.get('parent_id'), form=form)}
    return jsonify(data)


# render comment form for comment with parent (after click discussion button)
@app.route('/product_comment_form', methods=['POST'])
def product_comment_form():
    form = CommentForm(request.form)
    print(request.form.get('product_id'),request.form.get('parent_id'))
    data = {'com_form': render_template('product_comment_form.html',
                                        product_id=request.form.get('product_id'),
                                        parent_id=request.form.get('parent_id'), form=form)}
    return jsonify(data)


# user_contain* - are the views, that render with ajax part of user container(in profile)
# These are posts, product, comments and favourites written(added) by user
@app.route('/user_contain_comment', methods=['POST'])
def user_contain_comment():
    if request.form.get('contain') == "comment":
        if request.form.get('sort') == "date":
            comments = get_ordered_list(Comment, Comment.timestamp.desc(), user_id=request.form.get('user_id'))
        else:
            comments = get_ordered_list(Comment, Comment.like_count.desc(), user_id=request.form.get('user_id'))
        dict_like = post_comment_dict_react(comments, current_user)
        data = {'com_container': render_template('/user_container/user_contain_comment.html',
                dict_like=dict_like, comments=comments,
                user_id=request.form.get('user_id')
                )}
    else:
        if request.form.get('sort') == "date":
            comments = get_ordered_list(CommentProduct, CommentProduct.timestamp.desc(), user_id=request.form.get('user_id'))
        else:
            comments = get_ordered_list(CommentProduct, CommentProduct.like_count.desc(), user_id=request.form.get('user_id'))

        dict_like = prod_comment_dict_react(comments, current_user)
        data = {'com_container': render_template('/user_container/user_contain_prod_comment.html',
                dict_like=dict_like, comments=comments,
                user_id=request.form.get('user_id')
        )}
    return jsonify(data)



@app.route('/user_contain_product', methods=['POST'])
def user_contain_product():
    if request.form.get('sort') == "date":
        products = get_ordered_list(Product, Product.published_at.desc(),
                                    user_id=request.form.get('user_id'))
    else:
        products = get_ordered_list(Product, Product.like_count.desc(),
                                    user_id=request.form.get('user_id'))
    list_of_favourite = create_list_of_favourite_products(products, current_user)
    dict_like = product_dict_react(products, current_user)
    data = {'product_container': render_template('/user_container/user_contain_product.html',
            list_of_favourite=list_of_favourite,
            dict_like=dict_like, products=products,
            user_id=request.form.get('user_id')
        )}
    return jsonify(data)


@app.route('/user_contain_post', methods=['POST', 'GET'])
def user_contain_post():
    if request.form.get('sort') == "date":
        posts = get_ordered_list(Post, Post.published_at.desc(),
                                    user_id=request.form.get('user_id'))
    else:
        posts = get_ordered_list(Post, Post.like_count.desc(),
                                    user_id=request.form.get('user_id'))

    list_of_favourite = create_list_of_favourite_posts(posts, current_user)
    dict_like = post_dict_react(posts, current_user)
    data = {'post_container': render_template('/user_container/user_contain_post.html',
            list_of_favourite=list_of_favourite,
            dict_like=dict_like, posts=posts,
            user_id=request.form.get('user_id')
    )}
    return jsonify(data)


@app.route('/user_contain_favourite', methods=['POST'])
def user_contain_favourite():
    id = request.form.get('user_id')
    if request.form.get('contain') == "product":
        if request.form.get('sort') == "date":
            products=get_favourite(id, Product, Product.published_at.desc())
        else:
            products = get_favourite(id, Product, Product.like_count.desc())

        dict_like = product_dict_react(products, current_user)
        list_of_favourite = create_list_of_favourite_products(products, current_user)

        data = {'favourite_container': render_template('/user_container/user_contain_prod_saved.html',
                dict_like=dict_like,
                                                   products=products,
                                                   list_of_favourite=list_of_favourite,
                                                   user_id=request.form.get('user_id')
                                                   )}
    if request.form.get('contain') == "post":
        if request.form.get('sort') == "data":
            posts = get_favourite(id, Post, Post.published_at.desc() )
        else:
            posts = get_favourite(id, Post, Post.like_count.desc())

        dict_like = post_dict_react(posts, current_user)
        list_of_favourite = create_list_of_favourite_posts(posts, current_user)

        data = {'favourite_container': render_template('/user_container/user_contain_post_saved.html',
                                                   dict_like=dict_like,
                                                   list_of_favourite=list_of_favourite,
                                                   posts=posts,
                                                   user_id=request.form.get('user_id')
                                                       )}
    return jsonify(data)


@app.route('/add_fav_product', methods=['POST'])
def add_fav_product():
    print(request.form.get("product_id"))
    product = get_or_abort(Product, id=request.form.get("product_id")).first()

    add_prod_fav(current_user, product)
    return jsonify(request.form.get("product_id"))


@app.route('/add_fav_post', methods=['GET', 'POST'])
def add_fav_post():
    post=get_or_abort(Post, id=request.form.get("post_id")).first()
    add_post_fav(current_user, post)
    return jsonify(request.form.get("post_id"))


@app.route('/delete_fav_post', methods=['GET', 'POST'])
def delete_fav_post():
    post = get_or_abort(Post, id=request.form.get("post_id")).first()
    delete_post_fav(current_user, post)
    return jsonify(request.form.get("post_id"))


@app.route('/delete_fav_product', methods=['GET', 'POST'])
def delete_fav_product():
    product = get_or_abort(Product, id=request.form.get("product_id")).first()
    delete_prod_fav(current_user, product)
    return jsonify(request.form.get("product_id"))



# sort comment on page '/single_post' and update data with ajax
@app.route('/post_contain_comment', methods=['POST'])
def post_contain_comment():
    form = CommentForm(request.form)
    if request.form.get('sort') == "data":
        comments = get_ordered_list(Comment, Comment.timestamp.desc(), post_id=request.form.get('post_id'))
    elif request.form.get('sort') == "rating":
        comments = get_ordered_list(Comment, Comment.like_count.desc(), post_id=request.form.get('post_id'))
    dict_like = post_comment_dict_react(comments, current_user)
    comment_tree = get_comment_dict(comments, 'sort')
    data = {'comments': render_template('comments.html',
            dict_like=dict_like,
                                        postid=request.form.get('post_id'),
                                        comments=comments,
                                        comment_tree=comment_tree,
                                        form=form)}
    return jsonify(data)


# sort comment on page '/single_product' and update data with ajax
@app.route('/product_contain_comment', methods=['POST'])
def product_contain_comment():
    form = CommentForm(request.form)
    if request.form.get('sort') == "data":
        comments = get_ordered_list(CommentProduct, CommentProduct.timestamp.desc(), product_id=request.form.get('product_id'))
    elif request.form.get('sort') == "rating":
        comments = get_ordered_list(CommentProduct, CommentProduct.like_count.desc(), product_id=request.form.get('product_id'))

    dict_like = product_dict_react(comments, current_user)

    comment_tree = get_comment_dict(comments, 'sort')

    data = {'comments': render_template('comments.html',
                                        dict_like=dict_like,
                                        product_id=request.form.get('product_id'),
                                        comments=comments,
                                        comment_tree=comment_tree,
                                        form=form)}
    return jsonify(data)


# The form rendered(get request) under the comment, that must be edited;
# with post request renders with ajax part of page, that contain one comment with update data;
# only one comment reloaded on the page this way
@app.route('/edit_prod_comment/<int:comment_id>', methods=['GET', 'POST'])
def edit_prod_comment(comment_id=None):
    form = CommentForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'GET':
        comment = get_or_abort(CommentProduct, id=comment_id).first()
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
        comment = get_or_abort(CommentProduct, id=comment_id)
        update_rows(comment, text=form.text.data, image=filename)
        comment=comment[0]
        dict_like={}
        if get_one_obj(ProdComReaction, user_id = current_user.id, comment_id=comment.id):
                dict_like[comment.id]=1

        data = {'comment': render_template('/comment_box/product_comment_box.html',
                                           dict_like=dict_like,
                                           comment=comment)}

        return jsonify(data)


@app.route('/edit_post_comment/<int:comment_id>', methods=['GET', 'POST'])
def edit_post_comment(comment_id=None):
    form = CommentForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'GET':
        comment = get_or_abort(Comment, id=comment_id).first()
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
        comment = get_or_abort(Comment, id=comment_id)
        update_rows(comment, text=form.text.data, image=filename)
        comment=comment[0]
        dict_like = {}
        if get_one_obj(PostComReaction, user_id = current_user.id, comment_id=comment.id):
                dict_like[comment.id]=1
        data = {'comment': render_template('/comment_box/post_comment_box.html',
                                           dict_like=dict_like,
                                           comment=comment)}
        return jsonify(data)


@app.route('/delete_post_comment', methods=['POST'])
def delete_post_comment():
    comment = get_or_abort(Comment, id = request.form.get("id"))
    if not check_com_editable(comment[0]):
        data = {'nodelet': "No deletable"}
    else:
        update_rows(comment, deleted=True)
        data = {'deleted': "Comment has been deleted"}
    return jsonify(data)


@app.route('/delete_prod_comment', methods=['POST'])
def delete_prod_comment():
    comment = get_or_abort(CommentProduct, id=request.form.get("id"))
    if not check_com_editable(comment[0]):
        data = {'nodelet': "No deletable"}
    else:
        update_rows(comment, deleted=True)
        data = {'deleted': "Comment has been deleted"}
    return jsonify(data)


@app.route('/delete_product', methods=['POST'])
def delete_product():
    product = get_or_abort(Product, id=request.form.get("id"))
    print("we are just delete this product")
    update_rows(product, deleted=True)
    return redirect(url_for('popular_product'))


@app.route('/edit_product', methods=['POST', 'GET'])
def edit_product():
    form = ProductForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'GET':
        product = get_or_abort(Product, id=request.args.get("id")).first()
        form.description.data = product.description
        form.title.data=product.title
        form.price.data = product.price

    if request.method == 'POST' and form.validate_on_submit():
        filename = create_filename(form.file.data)
        product = get_or_abort(Product, id=request.args.get("id"))
        update_rows(product, description=form.description.data,
                                title=form.title.data,
                                price=form.price.data,
                                image=filename)
        return redirect(url_for('singleproduct', product_id=request.args.get("id")))
    return render_template("edit_product.html", form=form, id=request.args.get("id"))


@app.route('/delete_post', methods=['POST'])
def delete_post():
    post = get_or_abort(Post, id=request.form.get("id"))
    update_rows(post, deleted=True)
    return redirect(url_for('last_posts'))


@app.route('/edit_post', methods=['POST', 'GET'])
def edit_post():
    form = PostForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'GET':
        post = get_one_obj(Post, id=request.args.get("id"))
        if not check_post_editable(post):
            return redirect(url_for('singlepost', postid=request.args.get("id")))
        form.body.data=post.body
        form.title.data=post.title
        return render_template("edit_post.html", form=form, id=request.args.get("id"))

    elif request.method == 'POST' and form.validate_on_submit():
        filename = create_filename(form.file.data)
        post = get_or_abort(Post, id=request.args.get("id"))
        update_rows(post, body=form.body.data,
             title=form.title.data,
             image=filename)
        return redirect(url_for('singlepost', postid=request.args.get("id")))
