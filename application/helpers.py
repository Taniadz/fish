from models import User, Post, Comment, CommentProduct, Product
import collections

def create_dict(d, parent, child):
    if parent == 0:
         d[child] = {}
         return
    if type(d)==type(dict()):
        for k in d:
            if k == parent:
                d[parent][child] = {}
                return
            create_dict(d[k], parent, child)


def get_comment_dict(post_id):
    comment_dict = {}
    comments = Comment.query.filter_by(post_id = post_id )
    for comment in comments:
        create_dict(comment_dict, comment.parent, comment.id)


    return comment_dict


def get_prod_comment_dict(product_id):
    comment_dict = {}
    comments = CommentProduct.query.filter_by(product_id = product_id )
    for comment in comments:
        create_dict(comment_dict, comment.parent, comment.id)
    return comment_dict


def get_comments_by_post_id(post_id):
    comments = Comment.query.filter_by(post_id = post_id )
    return comments


def get_comments_by_product_id(product_id):
    comments = CommentProduct.query.filter_by(product_id = product_id )
    return comments


def get_comment_by_id(id):
    comment = Comment.query.filter_by(id=id).first()
    return comment


def get_post_by_id(id):
    post = Post.query.filter_by(id=id).first()
    return post

def get_product_by_id(id):
    product = Product.query.filter_by(id=id).first()
    return product

def get_or_create(session, model, defaults=None, **kwargs):
    instance = model.query.filter_by(**kwargs).first()
    if instance:
        return False
    else:

        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance, True