from datetime import datetime

from sqlalchemy import delete
from sqlalchemy.orm import backref

from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5

friends = db.Table('friends', db.Column('user_id', db.Integer, db.ForeignKey("user.id")),
                   db.Column('friend_id', db.Integer, db.ForeignKey("user.id")))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), nullable=False, unique=True)
    username = db.Column(db.String(128), nullable=False, unique=True)
    token = db.Column(db.String(256), nullable=False, unique=True)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    # def avatar(self, size):
    #     hash_sum = md5(self.email.lower().encode('utf-8')).hexdigest()
    #     return 'https://www.gravatar.com/avatar/{}?s={}&d=identicon'.format(hash_sum, size)

    def getGroup(self):
        return Group.query.filter_by(id=self.group_id).first_or_404().name

    def is_added_friend(self, user):
        return self.friends_added.filter(friends.c.friend_id == user.id).count() > 0

    def add_friend(self, user):
        if not self.is_added_friend(user):
            self.friends_added.append(user)

    def delete_friend(self, user):
        if self.is_added_friend(user):
            '''
            tmp = delete(friends).where(friends.c.friend_id == user.id)
            db.session.execute(tmp)
            db.session.commit()
            '''
            self.friends_added.remove(user)

    def __repr__(self):
        return 'User - {} with email {}'.format(self.username, self.email)



@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True)
    Description = db.Column(db.String(1000000))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return 'Group - {}'.format(self.name)