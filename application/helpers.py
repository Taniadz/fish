import os
from collections import OrderedDict
from datetime import datetime, timedelta

from werkzeug import secure_filename
from werkzeug.exceptions import abort

from __init__ import UPLOAD_FOLDER
from application import UPLOAD_FOLDER, db
from models import User, Post, Comment, CommentProduct, Product, PostReaction


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
    print comments, "com from help"
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

def get_or_create(model, **kwargs):
    instance = model.query.filter_by(**kwargs)
    if instance:
        return instance, False
    else:

        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance, True



def type_of_count(obj, type, integer):
    if type == "like":
        new_count = obj[0].like_count + integer
        update_rows(obj, like_count=new_count)

    elif type == "unlike":
        new_count = obj[0].unlike_count + integer
        update_rows(obj, unlike_count=new_count)

    elif type == "angry":
        new_count = obj[0].angry_count + integer
        update_rows(obj, angry_count=new_count)

    elif type == "funny":
        new_count = obj[0].funny_count + integer
        update_rows(obj, funny_count=new_count)
    return


def increase_count(base_model, reaction_model, react_type, **kwargs):
    like = reaction_model.query.filter_by(**kwargs).first()
    print like
    if like is not None:
        if like.type == react_type:

            return {"like": base_model[0].like_count, "unlike": base_model[0].unlike_count,
                    "funny": base_model[0].funny_count, "angry": base_model[0].angry_count}

        else:
            prev_type = like.type

            type_of_count(base_model, prev_type, -1)
            type_of_count(base_model, react_type, 1)
            reaction_model.query.filter_by(**kwargs).update(dict(type=react_type))
            db.session.commit()
    else:
        like=reaction_model(**kwargs)

        like.type = react_type  # creating of new like
        db.session.add(like)
        db.session.commit()
        type_of_count(base_model, react_type, 1)

    return {"like": base_model[0].like_count, "unlike": base_model[0].unlike_count,
            "funny": base_model[0].funny_count, "angry": base_model[0].angry_count}




def check_decrease_count(base_model, react_model, **kwargs):
    like = react_model.query.filter_by(**kwargs).first()
    if not like:
        return {"like": base_model[0].like_count, "unlike": base_model[0].unlike_count,
                "funny": base_model[0].funny_count, "angry": base_model[0].angry_count}
    else:
        type_of_count(base_model, like.type, -1)
        db.session.delete(like)
        db.session.commit()
    return {"like": base_model[0].like_count, "unlike": base_model[0].unlike_count,
            "funny": base_model[0].funny_count, "angry": base_model[0].angry_count}



def create_filename(data, default=None):
    if  data != None:
        f = data
        filename = secure_filename(f.filename)
        f.save(os.path.join(UPLOAD_FOLDER, filename))
    else:
        filename = default
    return filename


# functions return dict with key - object id and value - type of reaction
def post_dict_like(dict_like, model, likes):
    for m in model:
        for l in likes:
            if m.id == l.post_id:
                dict_like[m.id] = l.type
    return(dict_like)


def product_dict_like(dict_like, model, likes):
    for m in model:
        for l in likes:
            if m.id == l.product_id:
                dict_like[m.id] = l.type
    return(dict_like)


def comment_dict_like(dict_like, model, likes):
    for m in model:
        for l in likes:
            if m.id == l.comment_id:
                dict_like[m.id] = l.type
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


def get_favourite(id, model, sorting=None):
    some = model.query.filter(model.favourite.any(id=id)).order_by(sorting).all()
    return some


def create_obj(model, **kwargs):
    obj = model(**kwargs)
    db.session.add(obj)
    db.session.commit()
    return obj




def update_post_saved(session, Post, model2):
    User.favourite_post.append(Post)
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

    obj.update(kwargs)
    db.session.commit()
    print "updated"
    return


def create_list_of_favourite(saved_list, obj, added_obj):
    for o in obj:
        if o in added_obj:
           saved_list.append(o)
    return saved_list


def create_dict_like(dict_like, model, likes):
    for m in model:
        for l in likes:
            if m.id == l.post_id:
                dict_like[m.id] = 1
    return(dict_like)


def add_post_fav(user, post):
    user.favourite_post.append(post)
    db.session.add(user)
    db.session.commit()


def add_prod_fav(user, product):
    user.favourite_product.append(product)
    db.session.add(user)
    db.session.commit()


def delete_prod_fav(user, product):
    user.favourite_product.remove(product)
    db.session.add(user)
    db.session.commit()


def delete_post_fav(user, post):
    user.favourite_post.remove(post)
    db.session.add(user)
    db.session.commit()


def get_post_reaction(**kwargs):
    return PostReaction.query.filter_by(**kwargs).all()

def get_one_like(model, **kwargs):
    return model.query.filter_by(**kwargs).first()



def get_or_abort(model, code=404,**kwargs):
    result = model.query.filter_by(**kwargs)
    if result is None:
        abort(code)
    return result