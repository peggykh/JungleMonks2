#!flask/bin/python
import unittest
import re
import threading
from flask.ext.testing import TestCase
from app import create_app, db
from app.model import Users, friends
from flask import request, url_for, g
import flask


class BaseTestCase(TestCase):
    def create_app(self):
        self.app = create_app('testing')
        return self.app

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


class LayoutTestCase(BaseTestCase):

    def test_index_page(self):
        response = self.client.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_home_page(self):
        response = self.client.get('/', follow_redirects=True)
        self.assertTrue('Welcome to the JungleMonks!', response.data)

    def test_user(self):
        # create a user
        u = Users(name='john', email='john@example.com', age=22)
        db.session.add(u)
        db.session.commit()
        assert u.is_authenticated() is True
        assert u.is_active() is True
        assert u.is_anonymous() is False
        assert u.id == int(u.get_id())

    def test_user_add(self):
        data = dict(name='admin', email='adminu@gmail.com', age=25)
        response = self.client.post(url_for('layout.new'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('User was added successfully.', response.data)

    def test_monkey_edit(self):
        u = Users(name='user1', email='user1@gmail.com', age=25)
        db.session.add(u)
        db.session.commit()
        response = self.client.post('/profile/1', follow_redirects=True)
        data = dict(name='admin', email='adminu@gmail.com', age=28)
        response = self.client.post(
            '/edit/1', data=data, follow_redirects=True)
        self.assertTrue('You have been updated the profile', response.data)

    def test_monkey_profile(self):
        u = Users(name='user1', email='user1@gmail.com', age=25)
        db.session.add(u)
        db.session.commit()
        response = self.client.get('/profile/1', follow_redirects=True)

    def test_make_unique_name(self):
        u = Users(name='john', email='john@example.com', age=25)
        db.session.add(u)
        db.session.commit()
        name = Users.make_unique_name('john')
        assert name != 'john'
        u = Users(name=name, email='susan@example.com', age=28)
        db.session.add(u)
        db.session.commit()
        name2 = Users.make_unique_name('john')
        assert name2 != 'john'
        assert name2 != name

    def test_user_page(self):
        # navigate to home page
        response = self.client.get(
            'http://127.0.0.1:5000/user/1?sort=normal&monkey=')
        self.assertTrue('Friend', response.data)

    def test_user_sortbyname(self):
        e1 = Users(name='admine1', email='admine2@gmail.com', age=25)
        e2 = Users(name='teste2', email='teste2@gmail.com', age=27)
        db.session.add_all([e1, e2])
        db.session.commit()
        response = self.client.post(
            url_for('layout.user', page='1', sort='asc'),
            follow_redirects=True)
        self.assertTrue('Monkeys sort by the name!', response.data)

    def test_user_sortbyFnum(self):
        e1 = Users(name='teste1', email='teste1@gmail.com', age=25)
        e2 = Users(name='teste2', email='teste2@gmail.com', age=27)
        e3 = Users(name='teste3', email='teste3@gmail.com', age=27)
        db.session.add_all([e1, e2, e3])
        db.session.commit()
        e1.be_friend(e2)
        e1.be_friend(e3)
        response = self.client.get(url_for(
            'layout.user', page='1', sort='friendnum'), follow_redirects=True)
        self.assertTrue('Monkeys sort by the friend number!', response.data)

    def test_user_sortbybf(self):
        e1 = Users(name='admin1', email='admin1@gmail.com', age=25)
        e2 = Users(name='test1', email='test1@gmail.com', age=27)
        db.session.add_all([e1, e2])
        db.session.commit()
        e1.be_bestfriend(e2)
        response = self.client.post(url_for(
            'layout.user', page='1', sort='bf'), follow_redirects=True)
        self.assertTrue('Monkeys sort by the bestFriend name!', response.data)

    def test_friend(self):
        u1 = Users(name='monk1', email='monk1@example.com', age=25)
        u2 = Users(name='monk2', email='monk2@example.com', age=27)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertTrue(u1.be_friend(u2))

    def test_friend_main(self):
        e1 = Users(name='admine1', email='admine2@gmail.com', age=25)
        e2 = Users(name='teste2', email='teste2@gmail.com', age=27)
        db.session.add_all([e1, e2])
        db.session.commit()
        response = self.client.post(
            '/login', data=dict(name='admine1', email='admine2@gmail.com'))
        print response.location
        response = self.client.get('home', follow_redirects=True)
        self.assertTrue('You are now Friend with !', response.data)

    def test_unfriend(self):
        u1 = Users(name='monk1', email='monk1@example.com', age=25)
        u2 = Users(name='monk2', email='monk2@example.com', age=27)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        response = self.client.post(
            '/login', data=dict(name='monk2', email='monk2@gmail.com'))
        self.assertTrue(u1.be_friend(u2))
        #self.assertEqual(u1.unfriend(u2), response.data)
        

    def test_user_delete(self):
        e1 = Users(name='admine1', email='admine2@gmail.com', age=25)
        e2 = Users(name='teste2', email='teste2@gmail.com', age=27)
        db.session.add_all([e1, e2])
        db.session.commit()
        u = Users.query.get(1)
        db.session.remove()
        db.session.delete(u)
        response = self.client.post('/delete/1',
                                    follow_redirects=True)
        self.assertTrue('admine1 is removed!', response.data)

    def test_user_delete_page(self):
        e1 = Users(name='admine4', email='admine4@gmail.com', age=25)
        e2 = Users(name='teste3', email='teste3@gmail.com', age=28)
        db.session.add_all([e1, e2])
        db.session.commit()
        u = Users.query.get(2)
        response = self.client.delete(url_for('layout.delete', id=1))

    def test_bestfriend(self):
        e1 = Users(name='admine4', email='admine4@gmail.com', age=25)
        e2 = Users(name='teste3', email='teste3@gmail.com', age=28)
        db.session.add_all([e1, e2])
        db.session.commit()
        response = self.client.post('/login', data=dict(
            name='admine4', email='admine4@gmail.com'))
        e1 = e1.be_bestfriend(e2)
        response = self.client.post(
            '/bestFriend/teste3', follow_redirects=True)
        self.assertTrue('You are now BestFriend with admine4.', response.data)
