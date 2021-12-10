from flask import render_template, request, Blueprint
from uschat.models import User, Friend, Message
from flask_login import current_user, login_required
main = Blueprint('main', __name__)

@main.route("/home")
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    posts = Message.query.order_by(Message.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)


@main.route("/")
@main.route("/chats")
@login_required
def chats():
    page = request.args.get('page', 1, type=int)
    chat = Friend.query.filter_by(frnd_id=current_user.id).paginate(page=page, per_page=15)
    return render_template('chats.html', chats=chat)


@main.route("/about")
def about():
    return render_template('about.html', title='About')
