import os
from collections import OrderedDict
from datetime import datetime, timedelta
import json
from werkzeug import secure_filename
from werkzeug.exceptions import abort

# from .extentions import db
from application  import UPLOAD_FOLDER, app, db, cache
from .models import Dialog, User, Post, Comment, CommentProduct, Product,\
    PostReaction, FavouritePost, FavouriteProduct, ProductImage, Tag, Notification, Message

from social.apps.flask_app.default.models  import UserSocialAuth

from sqlalchemy import event, update

def check_is_social(user):
    return db.session.query(UserSocialAuth).filter_by(user_id =user.id).first()

import re






def count_user_rating(user):
    rating =0
    posts = Post.query.filter_by(user_id=user.id).all()
    comments = Comment.query.filter_by(user_id=user.id).all()
    for p in posts:
        rating_by_post = p.like_count + p.funny_count*2 - p.unlike_count
        rating=rating+rating_by_post
    for c in comments:
        rating_by_post = c.like_count + c.funny_count * 2 - c.unlike_count
        rating = rating + rating_by_post
    print(rating, "rating")
    return rating

def get_last_tags():
    tag =  Tag.query[:7]
    print(tag)
    return tag

def get_posts_by_tagname(name):
    posts = Post.query.filter(Post.tags.any(name=name)).all()
    return posts

@cache.memoize(timeout=500)
def get_tags_all():
    result = db.session.query(Tag).all()
    return result

def filter_tags(tags, query):
    tags_list = []
    for tag in tags:
        if (re.match(query, tag.name)):
            tags_list.append(tag)
    print(tags_list, "llllllllllllllllllllllllllllllliist")
    return tags_list





def get_posts_search(query):
    posts1 = db.session.query(Post).filter(Post.title.contains(query)).all()
    posts2 = db.session.query(Post).filter(Post.body.contains(query)).all()
    tag = get_one_obj(Tag, name=query)
    if tag:
        post3 = Post.query.filter(Post.tags.any(name=query)).all()
        return set(posts1 + posts2 + post3)

    return set(posts1 + posts2)


# create dict of comment tree
def create_dict(d, child, parent=0):
    if parent == 0:
        d[child] = OrderedDict()
        return
    if type(d)==type(OrderedDict()):
        for k in d:
            if k == parent:
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
    # create dict with sorting
    else:
        if sort == "data":
            comments_ordering = get_ordered_list(model, model.timestamp.desc(), **kwargs)
        else:
            comments_ordering = get_ordered_list(model, model.like_count.desc(), **kwargs)

        for comment in comments_ordering:
            if comment.parent == 0:
                create_dict(comment_dict, comment.id, comment.parent)
        for comment in comments:
            if comment.parent != 0:
                create_dict(comment_dict, comment.id, comment.parent)
        return comment_dict



def get_or_create(model, **kwargs):
    instance = model.query.filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance, True


# increase or decrease rection counters
def type_of_count(obj, type, integer):
    if type == "like":
        new_count = obj.like_count + integer
        obj.like_count=new_count

    elif type == "unlike":
        new_count = obj.unlike_count + integer
        obj.unlike_count=new_count
    elif type == "angry":
        new_count = obj.angry_count + integer
        obj.angry_count = new_count

    elif type == "funny":
        new_count = obj.funny_count + integer
        obj.funny_count=new_count
    db.session.add(obj)
    db.session.commit()
    return


def increase_count(base_model, reaction_model, react_type, **kwargs):
    like = reaction_model.query.filter_by(**kwargs).first()

    # if reaction object exists
    if like is not None:

        # if reaction object exists with the same type
        if like.type == react_type:
            return {"like": base_model.like_count, "unlike": base_model.unlike_count,
                    "funny": base_model.funny_count, "angry": base_model.angry_count}

        else:
            # if reaction object exists with different type
            prev_type = like.type
            type_of_count(base_model, prev_type, -1)
            type_of_count(base_model, react_type, 1)
            reaction_model.query.filter_by(**kwargs).update(dict(type=react_type))
            db.session.commit()
    # if reaction object doesn't exist - create new reaction object
    else:
        like=reaction_model(**kwargs)
        like.type = react_type  # creating of new like
        db.session.add(like)
        db.session.commit()
        type_of_count(base_model, react_type, 1)

    return {"like": base_model.like_count, "unlike": base_model.unlike_count,
            "funny": base_model.funny_count, "angry": base_model.angry_count}




def check_decrease_count(base_model, react_model, **kwargs):
    like = react_model.query.filter_by(**kwargs).first()

    # if reaction object doesn't exist
    if not like:
        return {"like": base_model.like_count, "unlike": base_model.unlike_count,
                "funny": base_model.funny_count, "angry": base_model.angry_count}
    # if exixst
    else:
        type_of_count(base_model, like.type, -1)
        db.session.delete(like)
        db.session.commit()
    return {"like": base_model.like_count, "unlike": base_model.unlike_count,
            "funny": base_model.funny_count, "angry": base_model.angry_count}


def create_filename(data, default=None):
    if  data != None:
        f = data
        filename = secure_filename(f.filename)
        f.save(os.path.join(UPLOAD_FOLDER, filename))
    else:
        filename = default
    return filename


# functions return dict with key - object id and value - type of reaction
def posts_dict_react(posts, user, dict_like):
    if user.is_authenticated:
        for p in posts:
            for react in user.post_react:
                if p.id == react.post_id:
                    dict_like[p.id]["reactions"] = react.type
    return(dict_like)


def product_dict_react(products, user, dict_like):
    if user.is_authenticated:
        for p in products:
            for react in user.product_react:
                if p.id == react.product_id:
                    dict_like[p.id]["reactions"] = react.type
    return(dict_like)


def post_comment_dict_react(comments, user, dict_like={}):
    if user.is_authenticated:
        for c in comments:
            for react in user.post_com_react:
                if c.id == react.comment_id:
                    dict_like[c.id]["reactions"] = react.type
    return(dict_like)



def prod_comment_dict_react(comments, user, dict_like={}):
    if user.is_authenticated:
        for c in comments:
            for react in user.prod_com_react:
                if c.id == react.comment_id:
                    dict_like[c.id]["reactions"] = react.type
    return(dict_like)




def get_favourite(id, model, sorting=None):
    some = model.query.filter(model.favourites.any(user_id=id)).order_by(sorting).all()
    return some


def check_com_editable(comment):
    current_time = datetime.now()
    delta = timedelta(minutes=15)
    return current_time - comment.timestamp < delta


def check_post_editable(post):
    current_time = datetime.now()
    delta = timedelta(hours=1)
    return current_time - post.published_at < delta



#@cache.memoize(500)
# #@cache.cached(timeout=500, key_prefix='all_comments')
def get_all_obj(model, **kwargs):
    return model.query.filter_by(**kwargs).all()


def dict_with_favourite_posts(posts, user, favourites_dict):
    if user.is_authenticated:
        user_favorites = get_all_obj(FavouritePost, user_id=user.id)
        for p in posts:
            for u in user_favorites:
                if p.id == u.post_id:
                    favourites_dict[p.id]["if_favourite"] = True
    return favourites_dict



def dict_with_favourite_products(products, user, dict_with_davourites):
    if user.is_authenticated:
        user_favorites = get_all_obj(FavouriteProduct, user_id=user.id)
        for p in products:
            for u in user_favorites:
                if p.id == u.product_id:
                    dict_with_davourites[p.id]["if_favourite"] = True
    return dict_with_davourites



def add_post_fav(user, post):
    get_or_create(FavouritePost, user_id = user.id, post_id = post.id)

def add_prod_fav(user, product):
    get_or_create(FavouriteProduct, user_id = user.id, product_id = product.id)


def delete_prod_fav(user, product):
    product = get_one_obj(FavouriteProduct, user_id = user.id, product_id = product.id)
    db.session.delete(product)
    db.session.commit()




def delete_post_fav(user, post):
    post =  get_one_obj(FavouritePost, user_id = user.id, post_id = post.id)
    db.session.delete(post)
    db.session.commit()


def get_post_reaction(**kwargs):
    return PostReaction.query.filter_by(**kwargs).all()

@cache.memoize(500)
def get_products_ordering(order, page, post_per_page, user_id = None):
    begin = (page-1) * post_per_page
    if user_id:
        products = Product.query.filter_by(user_id=user_id).filter_by(deleted=False).order_by(order)[begin: begin + post_per_page]
    else:
        products = Product.query.order_by(order).filter_by(deleted=False)[begin: begin + post_per_page]
    return products


@cache.memoize(500)
def get_posts_ordering(order, page, post_per_page, user_id = None):
    begin = (page - 1) * post_per_page
    if user_id:
        posts = Post.query.filter_by(user_id=user_id).filter_by(deleted=False).order_by(order)[begin: begin + post_per_page]
    else:
        posts = Post.query.order_by(order).filter_by(deleted=False)[begin: begin + post_per_page]
    return posts


def get_post_comments_by_user_id(order, user_id, page, comments_per_page):
    begin = (page - 1) * comments_per_page
    comments = Comment.query.filter_by(user_id = user_id).order_by(order)[begin: begin + comments_per_page]
    return comments


def get_product_comments_by_user_id(order, user_id,  page, comments_per_page):
    begin = (page - 1) * comments_per_page
    comments = CommentProduct.query.filter_by(user_id = user_id).order_by(order)[begin: begin + comments_per_page]
    return comments




def create_obj(model, **kwargs):
    obj = model(**kwargs)
    db.session.add(obj)
    db.session.commit()
    return obj

def get_one_obj(model, **kwargs):
    return model.query.filter_by(**kwargs).first()

def get_or_abort(model, code=404, **kwargs):
    result = model.query.filter_by(**kwargs)
    if result is None:
        abort(code)
    return result

@cache.memoize(timeout=50)
def get_or_abort_post(model, code=404, **kwargs):
    result = model.query.filter_by(**kwargs).first()
    if result is None:
        abort(code)
    return result

@cache.memoize(timeout=500)
def get_or_abort_product(model, code=404, **kwargs):
    result = model.query.filter_by(**kwargs).first()
    if result is None:
        abort(code)
    return result

@cache.memoize(timeout=500)
def get_or_abort_user(model, code=404, **kwargs):
    result = model.query.filter_by(**kwargs).first()
    if result is None:
        abort(code)
    return result

def get_for_update(model, **kwargs):
    result = model.query.filter_by(**kwargs)
    return result


def update_rows(obj, **kwargs):
    obj.update(kwargs)
    db.session.commit()
    return


def update_post_rows(post, body, title, image):

    post.body = body
    post.title = title
    post.image = image
    db.session.add(post)
    db.session.commit()
    return


def update_comments_row(comment, text, image):
    comment.text = text
    comment.image = image

    db.session.add(comment)
    db.session.commit()
    return



def update_product_rows(product, description, title, price):
    product.description = description
    product.title = title
    product.price = price
    db.session.add(product)
    db.session.commit()
    return


def update_user_rows(user, avatar, username, social=None, avatar_min=None, about_me=None):
    user.about_me = about_me
    user.avatar = avatar
    user.username = username
    if social:
        user.social = True
    db.session.add(user)
    db.session.commit()
    return

def delete_object(instance):
    instance.deleted = True
    db.session.add(instance)
    db.session.commit()
    return





def check_if_post_favourite(user, post):
    if user.is_authenticated:
        favourite = get_one_obj(FavouritePost, post_id = post.id, user_id = user.id)
        if favourite:
            return True
    else:
        return False



def check_if_product_favourite(user, product):
    if user.is_authenticated:
        favourite = get_one_obj(FavouriteProduct, product_id = product.id, user_id = user.id)
        if favourite:
            return True
    else:
        return False

def get_post_for_comments(comments, posts_dict):
    posts_id = []
    posts_objects = []
    for c in comments:
        posts_id.append(c.post_id)
    uniq_set_id = set(posts_id)
    for id in uniq_set_id:
        posts_objects.append(get_one_obj(Post, id=id))

    for c in comments:
        for p in posts_objects:
            if c.post_id == p.id:
                posts_dict[c.id]['post'] = p
    return posts_dict



def get_notifications_sources(user_id, rel_dict):
    posts_set_id=set()
    posts_instances = []
    comments_instances = []
    notifications = Notification.query.filter(Notification.source_model != "mesage").all()
    for notification in notifications:
        if notification.source_model == "post":
            posts_set_id.add(notification.source_id)
        if notification.source_model == "post_comment":
            comments_instances.append(notification.source_id)
    for id in posts_set_id:
        posts_instances.append(get_one_obj(Post, id=id))

    for notification in notifications:
        for post in posts_instances:
            if notification.source_id == post.id and notification.source_model == "post":
                rel_dict[notification.id]['post'] = post
        for comment in comments_instances:
            if notification.source_id == comment.id and notification.source_model == "post_comment":
                rel_dict[notification.id]['comment'] = comment

    print(rel_dict)
    return rel_dict





def count_all_posts():
    return db.session.query(Post).count()

def count_all_products():
    return db.session.query(Product).count()

def count_post_comments_by_user_id(id):
    return db.session.query(Comment).filter(Comment.user_id==id).count()

def count_product_comments_by_user_id(id):
    return db.session.query(Comment).filter(CommentProduct.user_id==id).count()


def count_product_by_user_id(id):
    return db.session.query(Product).filter(Product.user_id==id).count()

def count_post_by_user_id(id):
    return db.session.query(Post).filter(Post.user_id==id).count()


def count_fav_post_by_user_id(id):
    return db.session.query(FavouritePost).filter(FavouritePost.user_id==id).count()

def count_fav_product_by_user_id(id):
    return db.session.query(FavouriteProduct).filter(FavouriteProduct.user_id==id).count()

def get_many_authors(checked, auth_dict):
    authors_id = []
    authors_objects=[]
    for c in checked:
        authors_id.append(c.user_id)
    uniq_set_id = set(authors_id)   #get only unique authors
    for id in uniq_set_id:
        authors_objects.append(get_one_obj(User, id = id))

    for c in checked:
        for a in authors_objects:
            if c.user_id == a.id:
                auth_dict[c.id] = {}
                auth_dict[c.id]['author'] = a
    return auth_dict


def get_many_sender(checked, auth_dict):
    authors_id = []
    authors_objects=[]
    for c in checked:
        authors_id.append(c.sender_id)
    uniq_set_id = set(authors_id)   #get only unique authors
    for id in uniq_set_id:
        authors_objects.append(get_one_obj(User, id = id))

    for c in checked:
        for a in authors_objects:
            if c.sender_id == a.id:
                auth_dict[c.id] = {}
                auth_dict[c.id]['sender'] = a
    return auth_dict



def get_prod_comment_relationships(comments, user):
    relationships={}
    get_many_authors(comments, relationships)
    prod_comment_dict_react(comments, user, relationships)
    return relationships

def get_post_comment_relationships(comments, user):
    relationships={}
    get_many_authors(comments, relationships)
    post_comment_dict_react(comments, user, relationships)
    return relationships



def get_products_relationship(products, user):
    relationships = {}
    get_many_authors(products, relationships)
    product_dict_react(products, user, relationships)
    dict_with_favourite_products(products, user, relationships)
    get_many_images(products, relationships)
    return relationships


def get_posts_relationship(posts, user):
    relationships = {}
    get_many_authors(posts, relationships)
    posts_dict_react(posts, user, relationships)
    dict_with_favourite_posts(posts, user, relationships)
    return relationships


def get_many_images(products, images_dict):
    if images_dict:   # check if not empty
        for p in products:
            images_dict[p.id]["images"] = get_all_obj(ProductImage, product_id = p.id)
    else:
        for p in products:
            images_dict[p.id]={}
            images_dict[p.id]["images"] = get_all_obj(ProductImage, product_id = p.id)
    return images_dict




def get_ordered_list(model, sorting, **kwargs):
    list = model.query.filter_by(**kwargs).order_by(sorting).all()
    return list


# @cache.memoize(500)
def get_all_comments_by_post_id(id):
    return Comment.query.filter_by(post_id = id).all()

@cache.memoize(500)
def get_last_comments_for_posts():
    return Comment.query.order_by(Comment.timestamp.desc())[:10]


@cache.memoize(500)
def get_last_comments_for_products():
    return CommentProduct.query.order_by(CommentProduct.timestamp.desc())[:10]


# @cache.memoize(500)
def get_all_comments_by_product_id(id):
    return CommentProduct.query.filter_by(product_id = id).all()

def delete_user_cache(username):

    cache.delete_memoized(get_or_abort_user, User, code=404, username=username)


def delete_post_cache(id):
    cache.delete_memoized(get_or_abort_post, Post, code=404, id = id)
    cache.delete_memoized(get_posts_ordering)

def delete_product_cache(id):
    cache.delete_memoized(get_or_abort_product, Product, code=404, id = id)
    cache.delete_memoized(get_products_ordering)

@event.listens_for(User, 'after_insert')
def after_update_user(mapper, connection, target):
    print("ussssssssssser insert")
    delete_user_cache(target.username)

@event.listens_for(User, 'after_update')
def after_update_user(mapper, connection, target):
    print("useeeeer update")
    delete_user_cache(target.username)

@event.listens_for(Post, 'after_update')
def after_update_post(mapper, connection, target):
    delete_post_cache(target.id)



@event.listens_for(Product, 'after_update')
def after_update_product(mapper, connection, target):
    delete_product_cache(target.id)


@event.listens_for(Product, 'after_insert')
def after_insert_product(mapper, connection, target):
    delete_product_cache(target.id)


@event.listens_for(Comment, 'after_update')
def after_update_comment(mapper, connection, target):
    # cache.delete_memoized(get_all_comments_by_post_id, target.post_id)
    cache.delete_memoized(get_last_comments_for_posts)


@event.listens_for(Comment, 'after_insert')
def after_insert_comment(mapper, connection, target):
    # cache.delete_memoized(get_all_comments_by_post_id, target.post_id)
    cache.delete_memoized(get_last_comments_for_posts)



@event.listens_for(CommentProduct, 'after_update')
def after_update_comment(mapper, connection, target):
    print("update")
    # cache.delete_memoized(get_all_comments_by_product_id, target.product_id)
    cache.delete_memoized(get_last_comments_for_products)


@event.listens_for(CommentProduct, 'after_insert')
def after_insert_comment(mapper, connection, target):
    print("insert")
    # cache.delete_memoized(get_all_comments_by_product_id, target.product_id)
    cache.delete_memoized(get_last_comments_for_products)


@event.listens_for(Tag, 'after_insert')
def after_insert_tag(mapper, connection, target):
    print("insert tags")
    cache.delete_memoized(get_tags_all)

def get_or_create_dialog(receiver_id, sender_id):
    dialog = Dialog.query.filter(Dialog.participants[str(receiver_id)] == "").filter(Dialog.participants[str(sender_id)] == "").first()
    string1 = str(receiver_id)
    string2 = str(sender_id)
    if not dialog:
        dialog = Dialog(participants={string1: "", string2 : ""})
        db.session.add(dialog)
        db.session.commit()
    return dialog


def get_dialogs_by_user_id(user_id):
    dialog = Dialog.query.filter(Dialog.participants[str(user_id)] == "").all()
    return dialog

def update_dialog(dialog, short_text, last_receiver, last_massage_date, readed):
    dialog.short_text = short_text
    dialog.last_receiver = last_receiver
    dialog.last_massage_date = last_massage_date
    dialog.readed = readed
    db.session.add(dialog)
    db.session.commit()
    return dialog

def get_users_for_dialog(dialogs, user):
    users_dict={}
    for dialog in dialogs:
        for participant in dialog.participants:
            if participant != str(user.id):
                users_dict[dialog.id] = get_one_obj(User, id = int(participant))
    return users_dict



# make all messeges read by current user after dialog had opened and return receiver
def message_was_read(messages, user_id):
    for m in messages:
        if m.receiver_id == user_id and not m.readed:
            m.readed = True
            db.session.add(m)
    db.session.commit()

def dialog_was_read(dialog, user):

    if user == dialog.last_receiver:
        dialog.readed = True
        db.session.add(dialog)
        db.session.commit()
    return

def get_other_participant(dialog, user_id):
    for p in dialog.participants:
        if int(p) != user_id:
            return int(p)



def get_notification(user_id):
    return get_all_obj(Notification, user_id=user_id, closed=False)


def get_all_notifications(user_id):
    return get_all_obj(Notification, user_id=user_id)


def close_notification(notifications):
    for n in notifications:
        n.closed = True
        db.session.add(n)
    db.session.commit()

def get_and_close_notification(**kwargs):
    notifications = get_all_obj(Notification, **kwargs)
    for n in notifications:
        n.closed = True
        db.session.add(n)
    db.session.commit()

def create_notification(user_id, name, data):
    n = Notification(name=name, payload_json=json.dumps(data), user_id=user_id)
    db.session.add(n)
    db.session.commit()
    return n


def json_data(post_id, post_title, comment_id, sender_name):
    return {"post_id" : post_id, "post_title":post_title, "comment_id":comment_id, "sender_name":sender_name}


def get_paginated_mesages(dialog_id, page):
    return Message.query.filter_by(dialog_id=dialog_id).order_by(Message.sent_at.desc()).paginate(page, 5, False)

def get_paginated_user(page):
    return User.query.order_by(User.registered_on.desc()).paginate(page, 10, False)




