#!/user/bin/env python
import os
from flask.ext.migrate import Migrate, MigrateCommand
from app import create_app
from flask.ext.script import Manager
from app import db


app = create_app(os.environ.get('FLASK_CONFIG', 'default'))
magrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def init_db():
    db.drop_all()
    db.create_all()


@manager.command
def test():
    from subprocess import call
    call(['nosetests', '-v',
          '--with-coverage', '--cover-package=app', '--cover-branches',
          '--cover-erase', '--cover-html', '--cover-html-dir=cover'])

if __name__ == '__main__':
    manager.run()
