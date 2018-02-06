import os
from collections import OrderedDict
from datetime import datetime, timedelta

from werkzeug import secure_filename
from werkzeug.exceptions import abort

# from .extentions import db
from application  import UPLOAD_FOLDER, app, db
from .models import User, Post, Comment, CommentProduct, Product, PostReaction





def create_dict(d, child, parent=0):
    if parent == 0:
        print("par 0")
        d[child] = OrderedDict()
        return

    if type(d)==type(OrderedDict()):
        print(1)

        for k in d:
            print(2)
            if k == parent:
                print(3)
                d[parent][child] = OrderedDict()
                return
            create_dict(d[k], child, parent)


def get_comment_dict(comments, model=None, sort=None, **kwargs):
    comment_dict = OrderedDict()

    # create dict without sorting
    if sort == None:
        for comment in comments:
            create_dict(comment_dict, comment.id, comment.parent)
        return comment_dict

    else:
        if sort == "date":
            comments_ordering = get_ordered_list(model, model.timestamp.desc(), **kwargs)
        else:
            comments_ordering = get_ordered_list(model, model.like_count.desc(), **kwargs)

        for comment in comments_ordering:
            if comment.parent == 0:
                create_dict(comment_dict, comment.id, comment.parent)
        for comment in comments:
            if comment.parent != 0:
                create_dict(comment_dict, comment.id, comment.parent)
        print(comment_dict)
        return comment_dict


def get_ordered_list(model, sorting, **kwargs):
    list = model.query.filter_by(**kwargs).order_by(sorting).all()
    return list


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
        print(f.filename)
        filename = secure_filename(f.filename)

        f.save(os.path.join(UPLOAD_FOLDER, filename))
    else:
        filename = default
    return filename


# functions return dict with key - object id and value - type of reaction
def post_dict_react(posts, user):
    dict_like={}
    if user.is_authenticated:
        for p in posts:
            for react in user.post_react:
                if p.id == react.post_id:
                    dict_like[p.id] = react.type
    return(dict_like)


def product_dict_react(products, user):
    dict_like={}

    if user.is_authenticated:
        for p in products:
            print(p.id, "product")
            for react in user.product_react:

                if p.id == react.product_id:
                    dict_like[p.id] = react.type
    return(dict_like)


def post_comment_dict_react(comments, user):
    dict_like={}
    if user.is_authenticated:
        for c in comments:
            for react in user.post_com_react:
                if c.id == react.comment_id:
                    dict_like[c.id] = react.type
    return(dict_like)

def prod_comment_dict_react(comments, user):
    dict_like={}
    if user.is_authenticated:
        for c in comments:
            for react in user.prod_com_react:
                if c.id == react.comment_id:
                    dict_like[c.id] = react.type
    return(dict_like)

def get_posts_ordering(order, limit=None):
    posts = Post.query.order_by(order).limit(limit)
    return posts


def get_products_ordering(order, limit=None):
    products = Product.query.order_by(order).limit(limit)
    return products



def get_favourite(id, model, sorting=None):
    some = model.query.filter(model.favourite.any(id=id)).order_by(sorting).all()
    return some


def create_obj(model, **kwargs):
    obj = model(**kwargs)
    db.session.add(obj)
    db.session.commit()
    return obj



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
    return


def create_list_of_favourite_posts(posts, user):
    saved_list = []
    if user.is_authenticated:
        for p in posts:
            if p in user.favourite_post:
                saved_list.append(p)
    return saved_list

def create_list_of_favourite_products(products, user):
    saved_list = []
    if user.is_authenticated:
        for p in products:
            if p in user.favourite_product:
                saved_list.append(p)
    return saved_list



def add_post_fav(user, post):
    user.favourite_post.append(post)
    db.session.add(user)
    db.session.commit()


def add_prod_fav(user, product):
    user.favourite_product.append(product)
    db.session.add(user)
    db.session.commit()


def delete_prod_fav(user, product):
    if product in user.favourite_product:
        user.favourite_product.remove(product)
        db.session.add(user)
        db.session.commit()


def delete_post_fav(user, post):
    user.favourite_post.remove(post)
    db.session.add(user)
    db.session.commit()


def get_post_reaction(**kwargs):
    return PostReaction.query.filter_by(**kwargs).all()


def get_one_obj(model, **kwargs):
    return model.query.filter_by(**kwargs).first()


def get_all_obj(model, **kwargs):
    return model.query.filter_by(**kwargs).all()


def get_or_abort(model, code=404, **kwargs):
    result = model.query.filter_by(**kwargs)
    print(result.first())
    if result.first() is None:
        abort(code)
    return result


def check_if_favourite(user, checked):
    if user.is_authenticated:
        if user in checked.favourite:
            return True
    else:
        return False
