#!flask/bin/python

from .import db

friends = db.Table('friends',
                   db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                   db.Column('friend_id', db.Integer,
                             db.ForeignKey('users.id')))


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), default="None", nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    bestfriend_id = db.Column(db.Integer,
                              db.ForeignKey('users.id', ondelete='SET NULL'),
                              nullable=True)
    is_bestfriend = db.relationship('Users', uselist=False, remote_side=[id],
                                    post_update=True)
    is_friend = db.relationship('Users',  # defining the relationship
                                secondary=friends,
                                primaryjoin=(friends.c.user_id == id),
                                secondaryjoin=(friends.c.friend_id == id),
                                backref=db.backref('friends', lazy='dynamic'),
                                lazy='dynamic')

    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.name)

    @staticmethod
    def make_unique_name(name):
            if Users.query.filter_by(name=name).first() is None:
                return name
            version = 2
            while True:
                new_name = name + str(version)
                if Users.query.filter_by(name=new_name).first() is None:
                    break
                version += 1
            return new_name

    def are_friends(self, user):
        return self.is_friend.filter(friends.c.friend_id == user.id).\
            count() > 0

    # funcitons for friend management
    def be_friend(self, user):
            if not self.are_friends(user):
                    self.is_friend.append(user)
                    user.is_friend.append(self)
            return self

    # funcitons for unfriend management
    def unfriend(self, user):
        if self.are_friends(user):
            self.is_friend.remove(user)
            user.is_friend.remove(self)
            return self

    # funcitons for bestfriend management
    def are_bestfriends(self, user):
        return self.is_bestfriend == user

    # best friends management
    def be_bestfriend(self, user):
            if not self.are_bestfriends(user):
                self.is_bestfriend = user
                user.is_bestfriend = self
            return self
