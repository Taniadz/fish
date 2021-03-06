
from flask import render_template,  flash, redirect, url_for, request, g, send_from_directory, app
from application import celery, UPLOAD_FOLDER, security, cache, db, mail
from .forms import PostForm, CommentForm, UserEditForm, ProductForm, EditPostForm, ContactForm, MessageForm, ProfileSettingsForm
from werkzeug import secure_filename
from .models import PostComReaction, ProdComReaction, ProductReaction, Pagination, Tag, Message, Topic
from flask_json import jsonify
from werkzeug.datastructures import CombinedMultiDict
from urllib.request import urlopen
from flask_security import login_required, current_user
from flask_mail import Message as FlaskMessage
import facebook
POSTS_PER_PAGE = 6
import flask
import sys
from smtplib import SMTPException

from .helpers import *
from PIL import Image, ImageDraw


sys.path.append(flask)
@celery.task
def send_async_notification(subject, sender, recipients, text_body, html_body):
    """Background task to send an email with Flask-Mail."""
    msg = FlaskMessage(subject,
                  sender=sender,
                  recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    try:
        mail.send(msg)
    except SMTPException as e:
        with open('/var/log/mail/mail.log', 'a') as the_file:
            the_file.write(str(e) + "sender:" +sender + "recipientd:" +recipients + "text_body:"+text_body)

    return True

def send_mail_notification(notification):
    receiver = get_or_abort_user(User, id = notification.user_id)
    if receiver.allow_mail_notification:
        text_body = render_template("mails/notification_mail.txt", receiver=receiver, notification=notification,
                                    info=notification.get_data())
        html_body = render_template("mails/notification_mail.html", receiver=receiver,
                                    notification=notification, info=notification.get_data())

        send_async_notification.delay("Уведомление aqua.name", sender="contact.me@aqua.name",
                                    recipients=[receiver.email],
                                    text_body=text_body,
                                    html_body=html_body
                                      )

    return True


@app.route('/dialogs/<int:user_id>', methods = ['POST', 'GET'])
@login_required
def dialogs(user_id):
    dialogs = get_dialogs_by_user_id(current_user.id)
    users_dict  = get_users_for_dialog(dialogs, current_user)
    return render_template("dialogs.html", dialogs = dialogs, users_dict=users_dict)

@app.route('/send_message', methods = ['POST'])
@login_required
def send_message():
    form = MessageForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        print("validates")
        dialog = get_or_create_dialog(form.receiver_id.data, current_user.id)
        filename = create_filename(form.file.data)
        message = create_obj(Message, sender_id = current_user.id, receiver_id = form.receiver_id.data, participants=dialog.participants, file = filename, text = form.text.data, dialog_id = dialog.id)
        notification = create_notification(form.receiver_id.data, "message", {"message_id": message.id, "sender_name": current_user.username} )
        send_mail_notification(notification)
        update_dialog(dialog, short_text=message.text[:30], last_receiver = message.receiver_id, last_massage_date = message.sent_at, readed = False)

        return jsonify({"user_id" : current_user.id})



@app.route('/messages_box/', methods = ['POST', "GET"])
@login_required
def messages_box():
    page = request.args.get("page")
    if not page:
        page = 1
    else:
        page =  int(page) + 1

    form = MessageForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'GET':


        close_message_notification(current_user.id)
        messages = get_paginated_mesages(request.args.get("dialog_id"), page)
        message_was_read(messages.items, current_user)

        dialog = get_one_obj(Dialog, id = request.args.get("dialog_id"))
        dialog_was_read(dialog, current_user.id)

        form.receiver_id.data = get_other_participant(dialog, current_user.id)

        data = {'messages': render_template('messages_box.html', page = page,
                                            form=form, messages=messages, dialog_id = request.args.get("dialog_id")),
                "page": page,
                "dialog_id": dialog.id}

    if request.method == 'POST' and form.validate_on_submit():
        dialog = get_or_create_dialog(form.receiver_id.data, current_user.id)

        filename = create_filename(form.file.data)
        message = create_obj(Message, sender_id = current_user.id, receiver_id = form.receiver_id.data, participants=dialog.participants, file = filename, text = form.text.data, dialog_id = dialog.id)
        notification = create_notification(form.receiver_id.data, "message", {"message":message.id, "sender_name":current_user.username} )
        send_mail_notification(notification)
        updated_dialog = update_dialog(dialog, short_text=message.text[:30], last_receiver = message.receiver_id, last_massage_date = message.sent_at, readed=False)
        messages = get_paginated_mesages(dialog.id, page)

        data = {'messages': render_template('messages_box.html',
                                        form=form, messages=messages, page =1, dialog_id = dialog.id),
            "dialog_text" : updated_dialog.short_text,
                "dialog_id" : updated_dialog.id}

    return jsonify(data)



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)



@celery.task
def publish_async_facebook(text, image):
    photo = open(os.path.join(UPLOAD_FOLDER, image), "rb")
    graph = facebook.GraphAPI("")
    if image:
        graph.put_photo(message=text, image=photo, link="https://aqua.name/")
    else:
        graph.put_object("", "feed", message=text, link="https://aqua.name/")
    return True




@celery.task
def close_async_notification(user_id):
    """Background task to make user's notifications closed."""
    close_not_message_notification(user_id)
    return True

@celery.task
def send_async_email(title, message):
    """Background task to send an email with Flask-Mail."""
    msg = FlaskMessage(title,
                  sender="contact.me@aqua.name",
                  recipients=["contact.me@aqua.name"])
    msg.body = message
    mail.send(msg)
    return True



@app.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    form = ContactForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        send_async_email.delay(form.email.data, form.message.data)
        flash("Ваше сообщение было отправлено")
        return redirect(url_for('index'))
    if current_user.is_authenticated:
        if current_user.email:
            form.email.data = current_user.email
    return render_template("contact_us.html", form=form)





@app.before_request
def before_request():
    if current_user.is_authenticated:
        if current_user.last_seen:
            current_time = datetime.utcnow()
            if current_time - current_user.last_seen > timedelta(minutes=10):
                current_user.last_seen = datetime.utcnow() # update user.last_seen every 10 minutes
                db.session.add(current_user)
                db.session.commit()
        else:
                current_user.last_seen = datetime.utcnow()
                db.session.add(current_user)
                db.session.commit()

        notifications = get_open_notifications(current_user.id) #cashed notification
        for n in notifications:
            if n.name == "message":
                g.have_message = True  #check if user has new messages
            else:
                g.new_notification = True




# custom pipeline  for python social auth
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
    topics = get_all_obj(Topic)
    return render_template('home.html', user=current_user,
                           posts=posts, products=products,
                            topics = topics,
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



@app.route('/topic/<int:topic>', methods=['GET', 'POST'])
@app.route('/topic/<int:topic>/<int:page>', methods=['GET', 'POST'])
def topic(topic, page=1):
    if request.args.get("sort") == "rating":  # sort by datetime
        posts = get_posts_ordering(Post.like_count.desc(), page, POSTS_PER_PAGE, topic_id=topic)

    else:  # sort by rating
        posts = get_posts_ordering(Post.published_at.desc(), page, POSTS_PER_PAGE, topic_id=topic)
    topic = get_one_obj(Topic, id=topic)
    count = count_all_posts(topic_id=topic.id)
    pagination = Pagination(page, POSTS_PER_PAGE, count)
    posts_relationships=get_posts_relationship(posts, current_user)

    return render_template('topic.html',
                           posts=posts,
                           topic = topic,
                           posts_relationships = posts_relationships,
                           pagination=pagination,
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
        if form.topic_id.data:
            topic_id = int(form.topic_id.data)
        else:
            topic_id = 0
        post = create_obj(Post,
                          title=form.title.data.strip(),
                          body=form.body.data.strip(),
                          user_id=current_user.id,
                          image=filename,
                          topic_id = topic_id)

        for t in form.tags.data:
            tag_name = t["name"][:32]
            if tag_name:
                tag = get_or_create(Tag, name = tag_name)
                if tag[1]: # if tag created
                    post.tags.append(tag[0])
                    db.session.commit()
        if form.facebook_post.data:
            publish_async_facebook.delay(post.body, post.image)
            flash("Ваш пост был опубликован на фейбсук")

        return redirect(url_for('singlepost', postid=post.id))
    return render_template("add_post.html", form=form)






@app.route('/user/<username>')
def user(username):
    page = 1
    user = get_or_abort_user(User, username=username)
    print(user.allow_mail_notification, user.profile_settings)
    form = MessageForm(CombinedMultiDict((request.files, request.form)))
    form.receiver_id.data = user.id

    rating = count_user_rating(user)
    side_posts = get_posts_ordering(Post.published_at.desc(), page, POSTS_PER_PAGE)
    # show users posts, comments, products and saved in user profile page.
    # if user is a profile owner or user hasn't profile settings - show all containers with this content.
    # When page rendering, it show only posts container, other part rendering by ajax on click.

    # if current user is not profile owner, rendered content depends on profile settings.
    if user.profile_settings and current_user != user:
        profile_settings = json.loads(str(user.profile_settings))
        col_md = 0
        for value in profile_settings.values():
            if value:
                col_md +=1
        col_md = int(12 /col_md)

        if profile_settings["show_posts"] or current_user == user:
            POSTS_PER_USER_PAGE = count_post_by_user_id(user.id)
            posts = get_posts_ordering(Post.published_at.desc(), page, POSTS_PER_USER_PAGE, user_id=user.id)
            posts_relationships = get_posts_relationship(posts, current_user)
            return render_template('user.html', posts_relationships =posts_relationships,tags=get_last_tags(),
                                   profile_settings=profile_settings, active_container = "post",
                               user=user, user_id=user.id, posts=posts, side_posts=side_posts, rating=rating, form=form, col_md=col_md)

        elif  profile_settings["show_comments"]:
            COMMENTS_PER_PAGE = count_post_comments_by_user_id(user.id)
            comments = get_post_comments_by_user_id(Comment.timestamp.desc(), user.id, page,
                                                    COMMENTS_PER_PAGE)
            comments_relationships = get_post_comment_relationships(comments, current_user)
            return render_template('user.html', comments_relationships=comments_relationships, tags=get_last_tags(),
                                   profile_settings=profile_settings,user=user, user_id=user.id, comments=comments,
                                   side_posts=side_posts, rating=rating, form=form, col_md=col_md, active_container = "comment")

        elif profile_settings["show_products"]:
            PRODUCTS_PER_PAGE = count_product_by_user_id(user.id)
            products = get_products_ordering(Product.published_at.published_at(), page, PRODUCTS_PER_PAGE, user.id)
            products_relationships = get_products_relationship(products, current_user)
            return render_template('user.html', products_relationships=products_relationships, tags=get_last_tags(),
                                   profile_settings=profile_settings, user=user, user_id=user.id, products=products,
                                   side_posts=side_posts, rating=rating, form=form, col_md=col_md, active_container = "product")

        elif profile_settings["show_saved"]:
            posts = get_favourite(id, Post, Post.published_at.desc())
            posts_relationships=get_products_relationship(posts,current_user)
            return render_template('user.html', posts_relationships=posts_relationships, tags=get_last_tags(),
                                   profile_settings=profile_settings, user=user, user_id=user.id, posts=posts,
                                   side_posts=side_posts, rating=rating, form=form, col_md=col_md, active_container = "saved")



    POSTS_PER_USER_PAGE = count_post_by_user_id(user.id)
    posts = get_posts_ordering(Post.published_at.desc(), page, POSTS_PER_USER_PAGE, user_id=user.id)
    posts_relationships = get_posts_relationship(posts, current_user)
    return render_template('user.html', posts_relationships=posts_relationships, tags=get_last_tags(),
                         active_container="post", profile_settings =None,
                           user=user, user_id=user.id, posts=posts, side_posts=side_posts, rating=rating, form=form,
                           col_md=3)







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






















@app.route('/user_notification/<int:user_id>')
def user_notification(user_id):
    notifications = get_not_message_notifications(user_id)
    info = {}
    for n in notifications:
        info[n.id] = n.get_data()

    close_async_notification.delay(user_id)


    return render_template('users_notifications.html', notifications = notifications, info = info)
                           # notifications_relationships=notifications_relationships)

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
    user = get_for_update(User, username=username)
    if current_user == user[0]:
        if request.method == 'POST' and form.validate_on_submit():
            if form.file.data:
                filename = create_filename(form.file.data)  # create secure filename
            else:
                filename = user[0].avatar

            updated_user = update_user_rows(user[0],avatar=filename,
                               username=form.username.data,
                               about_me=form.about_me.data)
            if form.file.data is not None:
                return redirect(url_for('crop_image'))
            else:
                return redirect(url_for('user', username=updated_user.username))
        else:
            form.username.data = user[0].username
            form.about_me.data = user[0].about_me
            return render_template('user_edit.html',
                                   user=user[0],
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
        post = get_or_abort_post(Post, id=postid)

        filename = create_filename(form.file.data)
        parent = request.args.get('parent')
        if request.args.get('parent') is None:
            parent = 0

        comment = create_obj(Comment, text=form.text.data, user_id=current_user.id,
                   post_id=postid, image=filename, parent=parent)
        if post.user_id != current_user.id:  # not to notify about your own comments

            if comment.parent == 0:


                notification = create_notification(post.user_id, "comment_on_post", json_data(postid, post.title, comment.id, current_user.username)) # notification for comment on post
                send_mail_notification(notification)
            else:
                parent_comment = get_one_obj(Comment, id = parent)

                notification = create_notification(post.user_id, "comment_on_post", json_data(postid, post.title, comment.id,
                                                                               current_user.username))  # notification for comment on post
                send_mail_notification(notification)
                notification = create_notification(parent_comment.user_id, "comment_on_post_comment", json_data(postid, post.title, comment.id, current_user.username)) # notification for parent comment on comment
                send_mail_notification(notification)

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
                print(img, "filenameeeeeee")
                filename = create_filename(img)

                new_image = create_obj(ProductImage, user_id=current_user.id,
                                       filename=filename,
                                       product_id=product.id)
            if form.facebook_post.data:
                publish_async_facebook.delay(product.description, filename)
                flash("Ваш продукт был опубликован на фейбсук")
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
        post = get_one_obj(Post, id=request.args.get("id"))
        if not check_post_editable(post):
            return redirect(url_for('singlepost', postid=request.args.get("id")))
        form.body.data=post.body
        form.title.data=post.title
        return render_template("edit_post.html", form=form, id=request.args.get("id"))

    elif request.method == 'POST' and form.validate_on_submit():
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

    else:    #if use tagname search and full text search
        posts = get_posts_search(query)

    return render_template('search_results.html',
        query = query,
        posts = posts,
                        posts_relationships = get_posts_relationship(posts, current_user))


@app.route('/profile_settings/', methods=['GET', 'POST'])
@login_required
def profile_settings():

    form = ProfileSettingsForm(request.form)
    if request.method == 'GET':
        form.allow_mail_notification.data= current_user.allow_mail_notification
        if current_user.profile_settings:
            profile_settings = json.loads(str(current_user.profile_settings))
            print(profile_settings)
            form.show_comments.data =  profile_settings["show_comments"]
            form.show_posts.data = profile_settings["show_posts"]
            form.show_products.data = profile_settings["show_products"]
            form.show_saved.data = profile_settings["show_saved"]

    if request.method == 'POST' and form.validate_on_submit():
        print(form.data)
        change_settings(current_user, form.allow_mail_notification.data, {"show_comments":form.show_comments.data,
                                                                  "show_posts":form.show_posts.data,
                                                                  "show_products":form.show_products.data,
                                                                  "show_saved":form.show_saved.data} )
        flash("Настройки были сохранены")
        return redirect(url_for("user", username=current_user.username))

    return render_template("profile_settings.html", form=form)


