
from flask import render_template,  flash, redirect, url_for, request, g, send_from_directory
from application import celery, UPLOAD_FOLDER, security, cache, db
from .forms import PostForm, CommentForm, UserEditForm, ProductForm, EditPostForm
from werkzeug import secure_filename
from .models import PostComReaction, ProdComReaction, ProductReaction, Pagination, Tag
from flask_json import jsonify
from werkzeug.datastructures import CombinedMultiDict
from urllib.request import urlopen
from flask_security import login_required, current_user
POSTS_PER_PAGE = 6

import pytz

from .helpers import *
from PIL import Image, ImageDraw

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.before_request
def before_request():

    if current_user.is_authenticated:
        current_time = datetime.now()
        delta = timedelta(minutes=10)
        if current_user.last_seen:
            if current_time - current_user.last_seen > delta:
                current_user.last_seen = datetime.utcnow()
                db.session.add(current_user)
                db.session.commit()

def save_profile(backend, user, response, *args, **kwargs):
   if backend.name == 'facebook':
        user = get_one_obj(User, id=user.id)
        url = "http://graph.facebook.com/%s/picture?type=large" % response['id']
        filename = str( response['id']) + "avatar.png"
        avatar = urlopen(url).read()
        fout = open(UPLOAD_FOLDER +"/" + filename , "wb")  # filepath is where to save the image
        fout.write(avatar)
        fout.close()
        update_user_rows(user, username = response.get('name'), avatar = filename, social = True )

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404



@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/confirm_email')
def confirm_email():
    return render_template('confirm_email.html')

@app.route('/')
def index():
    posts = get_posts_ordering(Post.published_at.desc(), 1, POSTS_PER_PAGE)
    products = get_products_ordering(Product.like_count.desc(), 1, POSTS_PER_PAGE)
    return render_template('home.html', user=current_user,
                           posts=posts, products=products,
                           products_relationship=get_products_relationship(products, current_user),
                           posts_relationship = get_posts_relationship(posts, current_user))


@app.route('/popular_product', methods=['GET', 'POST'])
@app.route('/popular_product/<int:page>', methods=['GET', 'POST'])
def popular_product(page=1):
    count = count_all_products()
    if request.args.get("sort") == "rating":
        products = get_products_ordering(Product.like_count.desc(), page, POSTS_PER_PAGE)
    else:
        products = get_products_ordering(Product.published_at.desc(), page, POSTS_PER_PAGE)
    pagination = Pagination(page, POSTS_PER_PAGE, count)
    products_relationships=get_products_relationship(products, current_user)
    return render_template('popular_product.html',
                            products_relationships = products_relationships,
                            sort=request.args.get("sort"),
                            products = products, pagination=pagination,)


@app.route('/last_posts', methods=['GET', 'POST'])
@app.route('/last_posts/<int:page>', methods=['GET', 'POST'])
def last_posts(page=1):
    if request.args.get("sort") == "rating":  # sort by datetime
        posts = get_posts_ordering(Post.like_count.desc(), page, POSTS_PER_PAGE)


    else:  # sort by rating
        posts = get_posts_ordering(Post.published_at.desc(), page, POSTS_PER_PAGE)
    comments = get_last_comments_for_posts()
    comments_rel={}
    get_many_authors(comments, comments_rel)
    get_post_for_comments(comments, comments_rel)
    count = count_all_posts()
    pagination = Pagination(page, POSTS_PER_PAGE, count)
    posts_relationships=get_posts_relationship(posts, current_user)
    tags = get_last_tags()
    return render_template('last_posts.html',
                           posts=posts, comments = comments, tags=tags,
                           posts_relationships = posts_relationships,
                           pagination=pagination, comments_rel=comments_rel,
                           sort=request.args.get("sort"))




@app.route('/add_post', methods = ['GET', 'POST'])
@login_required
def add_post():
    form = PostForm(CombinedMultiDict((request.files, request.form)))
    if request.is_xhr:
        tags = get_tags_all()
        filtered_tags =  filter_tags(tags, request.form.get("letter"))
        data = {'tags_menu': render_template('tags_menu.html',
                                            tags=filtered_tags)}
        return jsonify(data)

    if request.method == 'POST' and form.validate_on_submit():
        filename = create_filename(form.file.data)
        post = create_obj(Post,
                          title=form.title.data.strip(),
                          body=form.body.data.strip(),
                          user_id=current_user.id,
                          image=filename)

        for t in form.tags.data:
            tag_name = t["name"][:32]
            if tag_name:
                tag = get_or_create(Tag, name = tag_name)
                if tag[1]: # if tag created
                    post.tags.append(tag[0])
                    db.session.commit()
        return redirect(url_for('singlepost', postid=post.id))
    return render_template("add_post.html", form=form)






@app.route('/user/<username>')
def user(username):
    page = 1
    user = get_or_abort_user(User, username=username)
    # check_is_social(user)

    rating = count_user_rating(user)
    POSTS_PER_USER_PAGE = count_post_by_user_id(user.id)
    side_posts = get_posts_ordering(Post.published_at.desc(), page, POSTS_PER_PAGE)

    # show posts, written by profile owner(default), others container rendered by ajax
    # with def user0_contain_* functions. This part is showed by included user_contain_post.html
    posts = get_posts_ordering(Post.published_at.desc(), page, POSTS_PER_USER_PAGE, user_id=user.id)
    print(posts)
    posts_relationships = get_posts_relationship(posts, current_user)
    return render_template('user.html', posts_relationships =posts_relationships,tags=get_last_tags(),
                           user=user, user_id=user.id, posts=posts, side_posts=side_posts, rating=rating)



@celery.task
def async_crop(data_image, username):
    user = get_for_update(User, username=username)

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
    delete_user_cache(username)
    return True



@app.route('/crop_image', methods=['GET', 'POST'])
@login_required
def crop_image():
    username = current_user.username
    user = get_one_obj(User, username=username)
    if request.method == 'POST':
        data_image = request.form.to_dict()
        result = async_crop.delay(data_image, username)  # give it celery
        return redirect(url_for('user', username=username))
    else:
        return render_template('crop_image.html',
                               user=user)



@app.route('/user_edit/<username>', methods=['GET', 'POST'])
@login_required
def user_edit(username):
    form = UserEditForm(CombinedMultiDict((request.files, request.form)))
    user = get_one_obj(User, username=username)
    if current_user == user:
        if request.method == 'POST' and form.validate_on_submit():
            if form.file.data:
                filename = create_filename(form.file.data)  # create secure filename
            else:
                filename = user.avatar
            user = update_user_rows(user, avatar=filename,
                               username=form.username.data,
                               about_me=form.about_me.data)
            if form.file.data is not None:
                return redirect(url_for('crop_image'))
            else:
                return redirect(url_for('user', username=username))
        else:
            form.username.data = user.username
            form.about_me.data = user.about_me
            return render_template('user_edit.html',
                                   user=user,
                                   form=form)
    else:
        return render_template('home.html')


@app.route('/post/<int:postid>', methods=['GET', 'POST'])
def singlepost(postid=None):
    form = CommentForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'GET':
        post = get_or_abort_post(Post, id=postid)

        if post.deleted:
            return render_template("deleted_object.html", object=post)

        posts = get_posts_ordering(Post.published_at.desc(), 1, POSTS_PER_PAGE) # posts for side box
        editable = check_post_editable(post)  # check if user can edit post
        comments = get_all_comments_by_post_id(post.id)

        post_author = get_one_obj(User, id=post.user_id)
        if_favorite = check_if_post_favourite(current_user, post)  # check if post added to favourite by user, False for not login too
        comments_relationships = get_post_comment_relationships(comments, current_user)
        if current_user.is_authenticated:
            post_liked = get_one_obj(PostReaction, user_id=current_user.id,
                                   post_id=postid)  # check if the post liked by user
        else:
            post_liked = False    # for not authenticated users
        return render_template("single_post.html", editable=editable, post_author=post_author,
                               comments_relationships=comments_relationships, tags=get_last_tags(),
                               posts=posts, post=post,  form=form, comments=comments, if_favorite=if_favorite,
                               post_liked=post_liked, comment_tree=get_comment_dict(comments))

    if request.method == 'POST' and form.validate_on_submit():
        filename = create_filename(form.file.data)
        parent = request.args.get('parent')
        if request.args.get('parent') is None:
            parent = 0
        print(parent, "parent")
        create_obj(Comment, text=form.text.data, user_id=current_user.id,
                   post_id=postid, image=filename, parent=parent)
        comments = get_all_comments_by_post_id(postid)
        comments_relationships = get_post_comment_relationships(comments, current_user)

        data = {'comments': render_template('comments.html', comments_relationships=comments_relationships, comments=comments,
                                            comment_tree=get_comment_dict(comments),  form=form)}
        return jsonify(data)





@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def singleproduct(product_id=None):
    form = CommentForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'GET':
        product = get_or_abort_product(Product, id=product_id)
        product_author = get_one_obj(User, id=product.user_id)
        product_images= get_all_obj(ProductImage, product_id = product.id)

        if product.deleted:
            return render_template("deleted_object.html", object=product)
        products=get_products_ordering(Product.published_at.desc(), 1, 10)  # products for side box
        images_dict={}
        products_images=get_many_images(products, images_dict)
        comments = get_all_comments_by_product_id(product_id)
        for c in comments:
            print(c.product_id, "single")
        if_favorite = check_if_product_favourite(current_user, product)  # check if post added to favourite by user, False for not login too
        if current_user.is_authenticated:
            product_liked = get_one_obj(ProductReaction, user_id=current_user.id,
                                product_id=product.id)  # check if the product liked by user
        else:
            product_liked = False
        comments_relationships = get_prod_comment_relationships(comments, current_user)

        return render_template("single_product.html",
                               if_favorite=if_favorite, product_liked=product_liked, products_images=products_images,
                                products=products, comments_relationships=comments_relationships,
                               product=product, comments=comments, product_author=product_author,
                               form=form, product_images=product_images, comment_tree=get_comment_dict(comments))
    if request.method == 'POST' and form.validate_on_submit():
        filename = create_filename(form.file.data)
        parent = request.args.get('parent')
        if request.args.get('parent') is None:
            parent = 0
        comment = create_obj(CommentProduct, text=form.text.data,
                             user_id=current_user.id, product_id=product_id,
                             image=filename, parent=parent)
        comments = get_all_comments_by_product_id(product_id)

        data = {'comments' : render_template('product_comments.html',
                                             comments_relationships=get_prod_comment_relationships(comments, current_user),
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
                             user_id=current_user.id )
        images = request.files.getlist("images")
        if images:
            for img in images:
                filename = create_filename(img)
                print(filename, "filenameeeeeee")
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
    post = get_one_obj(Post, id=request.form.get('id'))
    data = increase_count(post, PostReaction, react_type,
                          post_id=request.form.get('id'), user_id=current_user.id)  # increase vote count of post
    return jsonify(data)


@app.route('/like_comment', methods=['POST'])
def like_comment():
    react_type = request.form.get('type')
    if react_type == None:
        react_type = "like"
    comment = get_one_obj(Comment, id=request.form.get('id'))
    data = increase_count(comment, PostComReaction, react_type,
                          comment_id=request.form.get('id'), user_id=current_user.id)  # increase vote count of post
    return jsonify(data)



@app.route('/like_product', methods=['POST'])
def like_product():
    react_type = request.form.get('type')
    if react_type == None:
        react_type = "like"
    product = get_one_obj(Product, id=request.form.get('id'))
    data = increase_count(product, ProductReaction, react_type, product_id=request.form.get('id'),
                               user_id=current_user.id)  # increase vote count of post
    return jsonify(data)


@app.route('/like_prodcomment', methods=['POST'])
def like_prodcomment():
    react_type = request.form.get('type')
    if react_type == None:
        react_type = "like"
    comment = get_one_obj(CommentProduct, id=request.form.get('id'))
    data = increase_count(comment, ProdComReaction, react_type, comment_id=request.form.get('id'),
                          user_id=current_user.id)  # increase vote count of comment
    return jsonify(data)



@app.route('/unlike_post', methods=['POST'])
def unlike_post():
    post = get_one_obj(Post, id=request.form.get('id'))
    data = check_decrease_count(post, PostReaction, post_id=request.form.get('id'),
                                user_id=current_user.id)  # increase vote count of post if like doesn't exist
    return jsonify(data)


@app.route('/unlike_comment', methods=['POST'])
def unlike_comment():
    comment = get_one_obj(Comment, id=request.form.get('id'))
    data = check_decrease_count(comment, PostComReaction, comment_id=request.form.get('id'),
                                user_id=current_user.id)  # increase vote count of post if like doesn't exist
    return jsonify(data)


@app.route('/unlike_product', methods=['POST'])
def unlike_product():
    product = get_one_obj(Product, id=request.form.get('id'))
    data = check_decrease_count(product, ProductReaction, product_id=request.form.get('id'),
                                user_id=current_user.id)  # increase vote count of post if like doesn't exist
    return jsonify(data)


@app.route('/unlike_prodcomment', methods=['POST'])
def unlike_prodcomment():
    comment = get_one_obj(CommentProduct, id=request.form.get('id'))
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
    data = {'com_form': render_template('product_comment_form.html',
                                        product_id=request.form.get('product_id'),
                                        parent_id=request.form.get('parent_id'), form=form)}
    return jsonify(data)


# user_contain* - are the views, that render with ajax part of user container(in profile)
# These are posts, product, comments and favourites written(added) by user
@app.route('/user_contain_comment', methods=['POST'])
def user_contain_comment():
    page =1
    if request.form.get('contain') == "comment":
        COMMENTS_PER_PAGE = count_post_comments_by_user_id(request.form.get('user_id'))
        if request.form.get('sort') == "date":
            comments = get_post_comments_by_user_id(Comment.timestamp.desc(), request.form.get('user_id'), page, COMMENTS_PER_PAGE)
        else:
            comments = get_post_comments_by_user_id(Comment.like_count.desc(), request.form.get('user_id'), page, COMMENTS_PER_PAGE)
        comments_relationships = get_post_comment_relationships(comments, current_user)

        data = {'com_container': render_template('/user_container/user_contain_comment.html',
                                                 comments_relationships=comments_relationships, comments=comments,
                user_id=request.form.get('user_id')
                )}
    else:
        COMMENTS_PER_PAGE = count_product_comments_by_user_id(request.form.get('user_id'))
        if request.form.get('sort') == "date":
            comments = get_product_comments_by_user_id(CommentProduct.timestamp.desc(), request.form.get('user_id'), page, COMMENTS_PER_PAGE)
        else:
            comments = get_product_comments_by_user_id( CommentProduct.like_count.desc(), request.form.get('user_id'), page, COMMENTS_PER_PAGE)
        print(comments)
        comments_relationships = get_prod_comment_relationships(comments, current_user)
        data = {'com_container': render_template('/user_container/user_contain_prod_comment.html',
                                                comments_relationships=comments_relationships, comments=comments,
                user_id=request.form.get('user_id')
        )}
    return jsonify(data)



@app.route('/user_contain_product', methods=['POST'])
def user_contain_product():
    page = 1
    PRODUCTS_PER_PAGE = count_product_by_user_id(request.form.get('user_id'))
    if request.form.get('sort') == "date":
        products = get_products_ordering(Product.published_at.desc(), page, PRODUCTS_PER_PAGE, request.form.get('user_id'))

    else:
        products = get_products_ordering(Product.like_count.desc(), page, PRODUCTS_PER_PAGE, request.form.get('user_id'))
    products_relationship = get_products_relationship(products, current_user)

    data = {'product_container': render_template('/user_container/user_contain_product.html',
         products_relationship=products_relationship, products=products,
            user_id=request.form.get('user_id'),
        )}
    return jsonify(data)


@app.route('/user_contain_post', methods=['POST', 'GET'])
def user_contain_post():
    page = 1
    POSTS_PER_USER_PAGE = count_post_by_user_id(request.form.get('user_id'))
    if request.form.get('sort') == "date":
        posts = get_posts_ordering(Post.published_at.desc(), page, POSTS_PER_USER_PAGE,  user_id=request.form.get('user_id'))
    else:
        posts = get_posts_ordering(Post.like_count.desc(),page, POSTS_PER_USER_PAGE, user_id=request.form.get('user_id'))
    posts_relationships = get_posts_relationship(posts, current_user)
    data = {'post_container': render_template('/user_container/user_contain_post.html',
                                              posts_relationships=posts_relationships,
            posts=posts,
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

        data = {'favourite_container': render_template('/user_container/user_contain_prod_saved.html',
        products_relationships = get_products_relationship(products, current_user),
                                                   products=products,
                                                   user_id=request.form.get('user_id')
                                                   )}
    if request.form.get('contain') == "post":
        if request.form.get('sort') == "date":
            posts = get_favourite(id, Post, Post.published_at.desc(), )
        else:
            posts = get_favourite(id, Post, Post.like_count.desc())

        data = {'favourite_container': render_template('/user_container/user_contain_post_saved.html',
                                                   posts_relationship = get_posts_relationship(posts, current_user),
                                                   posts=posts,
                                                   user_id=request.form.get('user_id')
                                                    )}

    return jsonify(data)


@app.route('/add_fav_product', methods=['POST'])
def add_fav_product():
    product = get_or_abort_product(Product, id=request.form.get("product_id"))
    add_prod_fav(current_user, product)
    return jsonify(request.form.get("product_id"))


@app.route('/add_fav_post', methods=['GET', 'POST'])
def add_fav_post():
    post=get_or_abort_post(Post, id=request.form.get("post_id"))
    add_post_fav(current_user, post)
    return jsonify(request.form.get("post_id"))


@app.route('/delete_fav_post', methods=['GET', 'POST'])
def delete_fav_post():
    post = get_or_abort_post(Post, id=request.form.get("post_id"))
    delete_post_fav(current_user, post)
    return jsonify(request.form.get("post_id"))



@app.route('/delete_fav_product', methods=['GET', 'POST'])
def delete_fav_product():
    product = get_or_abort_product(Product, id=request.form.get("product_id"))
    delete_prod_fav(current_user, product)
    return jsonify(request.form.get("product_id"))



# sort comment on page '/single_post' and update data with ajax
@app.route('/post_contain_comment', methods=['POST'])
def post_contain_comment():
    form = CommentForm(request.form)
    comments = get_all_comments_by_post_id(request.form.get('post_id'))
    comment_tree = get_comment_dict(comments, Comment, request.form.get('sort'), post_id=request.form.get('post_id'))
    data = {'comments': render_template('comments.html',
            comments_relationships=get_post_comment_relationships(comments, current_user),
                                        postid=request.form.get('post_id'),
                                        comments=comments,
                                        comment_tree=comment_tree,
                                        form=form)}
    return jsonify(data)


# sort comment on page '/single_product' and update data with ajax
@app.route('/product_contain_comment', methods=['POST'])
def product_contain_comment():
    form = CommentForm(request.form)
    print(request.form.get('product_id'), "idddddddddddddd")
    comments = get_all_comments_by_product_id(request.form.get('product_id'))
    for c in comments:
        print(c.product_id)
    comment_tree = get_comment_dict(comments, CommentProduct, request.form.get('sort'), product_id=request.form.get('product_id'))
    data = {'comments': render_template('product_comments.html',
                                        comments_relationships=get_prod_comment_relationships(comments, current_user),
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
        comment = get_one_obj(CommentProduct, id=comment_id)
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
        comment = get_one_obj(CommentProduct, id=comment_id)
        update_comments_row(comment, text=form.text.data, image=filename)
        comment_list =[]
        comment_list.append(comment)
        comments_relationships = get_prod_comment_relationships(comment_list, current_user)

        data = {'comment': render_template('/comment_box/product_comment_box.html',
                                           comments_relationships=comments_relationships,
                                           comment=comment)}

        return jsonify(data)


@app.route('/edit_post_comment/<int:comment_id>', methods=['GET', 'POST'])
def edit_post_comment(comment_id=None):
    form = CommentForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'GET':
        comment = get_one_obj(Comment, id=comment_id)
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
        comment = get_one_obj(Comment, id=comment_id)
        update_comments_row(comment, text=form.text.data, image=filename)
        comment_list = []
        comment_list.append(comment)
        data = {'comment': render_template('/comment_box/post_comment_box.html',
                                           comments_relationships=get_post_comment_relationships(comment_list, current_user),
                comment=comment)}
        return jsonify(data)




@app.route('/delete_post_comment', methods=['POST'])
def delete_post_comment():
    comment = get_one_obj(Comment, id = request.form.get("id"))
    print(comment, request.form.get("id"), "hhhhhhhhhhhhhheeeeeeeeeelp")
    if not check_com_editable(comment):
        data = {'nodelet': "No deletable"}
    else:
        delete_object(comment)
        data = {'deleted': "Comment has been deleted"}
    return jsonify(data)


@app.route('/delete_prod_comment', methods=['POST'])
def delete_prod_comment():
    comment = get_one_obj(CommentProduct, id=request.form.get("id"))
    if not check_com_editable(comment):
        data = {'nodelet': "No deletable"}
    else:
        delete_object(comment)
        data = {'deleted': "Comment has been deleted"}
    return jsonify(data)


@app.route('/delete_product', methods=['POST'])
def delete_product():
    product = get_one_obj(Product, id=request.form.get("id"))
    delete_object(product)
    return redirect(url_for('popular_product'))


@app.route('/edit_product', methods=['POST', 'GET'])
def edit_product():
    form = ProductForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'GET':
        product = get_one_obj(Product, id=request.args.get("id"))
        form.description.data = product.description
        form.title.data=product.title
        form.price.data = product.price

    if request.method == 'POST' and form.validate_on_submit():

        product = get_one_obj(Product, id=request.args.get("id"))
        update_product_rows(product, description=form.description.data,
                                title=form.title.data,
                                price=form.price.data,)
        images = request.files.getlist("images")
        if images:
            for img in images:
                filename = create_filename(img)
                print(filename, "filename")
                new_image = create_obj(ProductImage, user_id=current_user.id,
                                       filename=filename,
                                       product_id=product.id)

        return redirect(url_for('singleproduct', product_id=request.args.get("id")))
    return render_template("edit_product.html", form=form, id=request.args.get("id"))


@app.route('/delete_post', methods=['POST'])
def delete_post():
    post = get_one_obj(Post, id=request.form.get("id"))
    delete_object(post)
    return redirect(url_for('last_posts'))


@app.route('/edit_post', methods=['POST', 'GET'])
def edit_post():
    form = EditPostForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'GET':
        print("geeeeet")
        post = get_one_obj(Post, id=request.args.get("id"))
        if not check_post_editable(post):
            return redirect(url_for('singlepost', postid=request.args.get("id")))
        form.body.data=post.body
        form.title.data=post.title
        return render_template("edit_post.html", form=form, id=request.args.get("id"))
    # elif request.method == 'POST':
    #     print("nnnnnnnnnnnn")
    #     print(form.data, "ffffffffffffffffffffff")
    #     for errorMessages in form.errors.items():
    #         for err in errorMessages:
    #             print(err, "err")
    #     return render_template("edit_post.html", form=form, id=request.args.get("id"))

    elif request.method == 'POST' and form.validate_on_submit():
        print("poooooooooooooooo")
        print(form.data, "ffffffffffffffffffffff")
        post = get_one_obj(Post, id=request.args.get("id"))
        if form.file.data:
            filename = create_filename(form.file.data)
        else:
            filename = post.image
        update_post_rows(post,  body=form.body.data,
             title=form.title.data,
             image=filename)
        return redirect(url_for('singlepost', postid=request.args.get("id")))


@app.route('/search', methods = ['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query = g.search_form.search.data))


@app.route('/search_results/<query>')
@login_required
def search_results(query):
    only_tag = request.args.get("only_tag")
    # if search only by tagname
    if only_tag:
        posts= get_posts_by_tagname(query)
        print(query)
        print(posts, "only tag")

    else:    #if use tagname search and full text search
        posts = get_posts_search(query)

    return render_template('search_results.html',
        query = query,
        posts = posts,
                        posts_relationships = get_posts_relationship(posts, current_user))