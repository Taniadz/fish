from models import User, Post, Comment, CommentProduct, Product
import os
from werkzeug.exceptions import abort
from collections import OrderedDict
from application import UPLOAD_FOLDER, db
from werkzeug import secure_filename
from flask_login import current_user
from datetime import datetime, timedelta




def create_dict(d, child, parent=0,):
    if parent == 0:
         d[child] = OrderedDict()
         return

    if type(d)==type(OrderedDict()):
        for k in d:
            if k == parent:
                d[parent][child] = OrderedDict()

                return
            create_dict(d[k], child, parent)


def get_comment_dict(comments, sort=None):

    comment_dict = OrderedDict()
    if sort == None:

        for comment in comments:
            create_dict(comment_dict, comment.id, comment.parent)
        return comment_dict

    else:
        for comment in comments:
            if comment.parent == 0:
                create_dict(comment_dict, comment.id, comment.parent)

        for comment in comments:
            if comment.parent != 0:
                create_dict(comment_dict, comment.id, comment.parent)
        return comment_dict



def get_comments_by_post_id(post_id, sorting=Comment.timestamp):
    comments = Comment.query.filter_by(post_id = post_id ).order_by(sorting).all()
    if comments is None:
        abort(404)
    return comments




def get_prod_comments_by_user_id(user_id, sorting=None):
    comments = CommentProduct.query.filter_by(user_id=user_id).order_by(sorting).all()
    if comments is None:
        abort(404)
    return comments

def get_prod_comments_by_product_id(product_id, sorting=CommentProduct.timestamp):
    comments = CommentProduct.query.filter_by(product_id=product_id).order_by(sorting).all()
    if comments is None:
        abort(404)
    return comments


def get_comments_by_user_id(user_id, sorting=None):
    comments = Comment.query.filter_by(user_id=user_id).order_by(sorting).all()
    if comments is None:
        abort(404)
    return comments


def get_products_by_user_id(user_id, sorting=None):
    products = Product.query.filter_by(user_id=user_id).order_by(sorting).all()
    if products is None:
        abort(404)
    return products


def get_posts_by_user_id(user_id, sorting=None):
    posts = Post.query.filter_by(user_id=user_id).order_by(sorting).all()
    if posts is None:
        abort(404)
    return posts

def get_comment_by_id(id):
    comment = Comment.query.filter_by(id=id)
    if comment is None:
        abort(404)
    return comment

def get_prod_comment_by_id(id):
    comment = CommentProduct.query.filter_by(id=id)
    if comment is None:
        abort(404)
    return comment


def get_post_by_id(id):
    post = Post.query.filter_by(id=id)
    if post is None:
        abort(404)
    else:
        return post

def get_product_by_id(id):
    product = Product.query.filter_by(id=id)
    if product is None:
        abort(404)
    return product

def get_or_create(session, model, **kwargs):
    instance = model.query.filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:

        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance, True

def check_for_like(obj, user):
    if user in obj.user_like:
        return obj.vote_count
    else:
        obj.user_like.append(user)
        obj.vote_count = obj.vote_count + 1
    db.session.add(obj)
    db.session.commit()
    return obj.vote_count


def check_for_unlike(obj, user):
    if user not in obj.user_like:
        return obj.vote_count
    else:
        obj.user_like.remove(user)
        obj.vote_count = obj.vote_count - 1
    db.session.add(obj)
    db.session.commit()
    return obj.vote_count


def create_filename(data, default=None):
    if  data != None:
        f = data
        filename = secure_filename(f.filename)
        f.save(os.path.join(UPLOAD_FOLDER, filename))
    else:
        filename = default
    return filename


def create_dict_like(dict_like, model, likes):

    for m in model:

        for l in likes:
            if m.id == l.id:
                dict_like[m.id] = 1
    return(dict_like)



def get_posts_ordering(order, limit=None):
    posts = Post.query.order_by(order).limit(limit)
    return posts

def get_products_ordering(order, limit=None):
    products = Product.query.order_by(order).limit(limit)
    return products


def get_user(**kwargs):
    user = User.query.filter_by(**kwargs)

    return user


def get_user_save(id, model, sorting=None):
    some = model.query.filter(model.user_save.any(id=id)).order_by(sorting).all()
    return some


def create_obj(model, **kwargs):
    obj = model(**kwargs)
    db.session.add(obj)
    db.session.commit()
    return obj




def update_post_saved(session, Post, model2):
    User.added_post.append(Post)
    session.add(User)
    session.commit()


def check_com_editable(comment):
    current_time = datetime.now()
    delta = timedelta(minutes=15)
    return current_time - comment.timestamp < delta


def check_post_editable(post):
    current_time = datetime.now()
    delta = timedelta(hours=1)
    return current_time - post.published_at < delta


def update_rows(obj, **kwargs):
    for el in kwargs:
        print(type(el))
    obj.update(kwargs)
    db.session.commit()


def create_saved_list(saved_list, obj, added_obj):
    for o in obj:
        if o in added_obj:
           saved_list.append(o)
    return saved_list


def create_dict_like(dict_like, model, likes):
    for m in model:
        if m in likes:
            dict_like[m.id] = 1
    return(dict_like)


def add_post_to_saved(user, post):
    user.added_post.append(post)
    db.session.add(user)
    db.session.commit()


def add_product_to_saved(user, product):
    user.added_product.append(product)
    db.session.add(user)
    db.session.commit()


def delete_product_from_saved(user, product):
    user.added_product.remove(product)
    db.session.add(user)
    db.session.commit()


def delete_post_from_saved(user, post):
    user.added_post.remove(post)
    db.session.add(user)
    db.session.commit()
