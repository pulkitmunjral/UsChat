from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from uschat import db
from uschat.models import Message, User
from uschat.messages.forms import MsgForm
from sqlalchemy import or_, and_

messages = Blueprint('messages', __name__)


@messages.route("/message/new/<int:frnd_id>", methods=['GET', 'POST'])
@login_required
def new_message(frnd_id):
    form = MsgForm()
    if form.validate_on_submit():
        message = Message(title=form.title.data, content=form.content.data, user_id=current_user.id,receiver_id=frnd_id)
        db.session.add(message)
        db.session.commit()
        flash('Your message has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Message', form=form, legend='New Message')

@login_required
@messages.route("/messages/<int:frnd_id>", methods=['GET', 'POST'])
def msgs(frnd_id):

    page = request.args.get('page', 1, type=int)
    frnd=User.query.filter_by(id=frnd_id).first_or_404()
    # sms = Message.query.filter_by(user_id=current_user.id,receiver_id=frnd_id).order_by(Message.date_posted.desc()).paginate(page=page, per_page=5)
    sms = Message.query.filter(or_(and_(Message.receiver_id==current_user.id,Message.user_id==frnd_id),and_(Message.receiver_id==frnd_id,Message.user_id==current_user.id))).order_by(Message.date_posted.asc()).paginate(page=page)
    form = MsgForm()
    if form.validate_on_submit():
        msg = Message(title=form.content.data, content=form.content.data, user_id=current_user.id, receiver_id=frnd_id)
        db.session.add(msg)
        db.session.commit()
        # flash('Your post has been created!', 'success')
        return redirect(url_for('messages.msgs',frnd_id=frnd_id))
    return render_template('messages.html', msgs=sms, form=form,frnd=frnd)

@messages.route("/messages/<int:message_id>/update", methods=['GET', 'POST'])
@login_required
def update_message(message_id):
    message = Message.query.get_or_404(message_id)
    if message.sender != current_user:
        abort(403)
    form = MsgForm()
    if form.validate_on_submit():
        message.title = form.title.data
        message.content = form.content.data
        db.session.commit()
        flash('Your message has been updated!', 'success')
        return redirect(url_for('messages.messages', message_id=message.id))
    elif request.method == 'GET':
        form.title.data = message.title
        form.content.data = message.content
    return render_template('create_message.html', title='Update Message',
                           form=form, legend='Update Message')


@messages.route("/message/<int:message_id>/delete", methods=['POST'])
@login_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    if message.sender != current_user:
        abort(403)
    db.session.delete(message)
    db.session.commit()
    flash('Your message has been deleted!', 'success')
    return redirect(url_for('main.home'))
