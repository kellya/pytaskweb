#!/usr/bin/env python3
import subprocess
import json
import random, string
from flask import Flask, render_template, request
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask_sqlalchemy import SQLAlchemy


class Task:
    """An object to hold task data obtained from the task command"""
    task_cmd = 'task'
    search_filter = 'status:pending'

    def load_task_data(self):
        """Pull task data from json data exported from the task command"""
        projoutput = subprocess.run([self.task_cmd, self.search_filter, 'export'],
                                    stdout=subprocess.PIPE)
        self.alltasks = json.loads(projoutput.stdout)

    def get_all_projects(self):
        """Return a list of unique projects"""
        allprojects = []
        iter = 0
        self.load_task_data()
        maxiter = len(self.alltasks)
        while iter < maxiter:
            try:
                if '.' in self.alltasks[iter]['project']:
                    parentproj = self.alltasks[iter]['project'].split('.')[0]
                    if parentproj not in allprojects:
                        allprojects.append(parentproj)
                if self.alltasks[iter]['project'] not in allprojects:
                    allprojects.append(self.alltasks[iter]['project'])
            except KeyError:
                pass
            iter += 1
        return allprojects

    def get_tasks(self, project):
        """return a list of all tasks within the given {project}"""
        iter = 0
        self.load_task_data()
        maxiter = len(self.alltasks)
        projecttasks = []
        while iter < maxiter:
            try:
                if project in self.alltasks[iter]['project']:
                    projecttasks.append(self.alltasks[iter])
            except KeyError:
                pass
            iter += 1
        return projecttasks

    def get_task_detail(self, uuid):
        """Return a dictionary of task details"""
        iter = 0
        maxiter = len(self.alltasks)
        while iter < maxiter:
            try:
                if self.alltasks[iter]['uuid'] == uuid:
                    return self.alltasks[iter]
            except KeyError:
                pass
            iter += 1


def main():
    myprojects = Task()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'super-secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
    letters = string.ascii_lowercase
    app.config['SECURITY_PASSWORD_SALT'] = 'ewnieyxnzyjhcc'
    db = SQLAlchemy(app)
    roles_users = db.Table('roles_users',
                           db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                           db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

    class Role(db.Model, RoleMixin):
        id = db.Column(db.Integer(), primary_key=True)
        name = db.Column(db.String(80), unique=True)
        description = db.Column(db.String(255))

    class User(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(255), unique=True)
        password = db.Column(db.String(255))
        active = db.Column(db.Boolean())
        confirmed_at = db.Column(db.DateTime())
        roles = db.relationship('Role', secondary=roles_users,
                                backref=db.backref('users', lazy='dynamic'))

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    @app.route('/')
    @login_required
    def home():
        return render_template('index.html')

    @app.route('/projects', methods=['get', 'post'])
    def projects():
        project = sorted(myprojects.get_all_projects(), key=lambda s: s.lower())
        return render_template('projects.html', projects=project)

    @app.route('/project_tasks/<name>', methods=['get', 'post'])
    def project_tasks(name):
        return render_template('tasks.html', tasks=myprojects.get_tasks(name))

    @app.route('/task/<uuid>', methods=['get', 'post'])
    def task_detail(uuid):
        return render_template('task_detail.html',
                               task=myprojects.get_task_detail(uuid))

    @app.route('/complete/<uuid>', methods=['post'])
    def task_complete(uuid):
        result = request.form.to_dict()
        print(str(result))
        if result['submit'] == 'complete':
            return render_template('complete.html', result=result)
        elif result['submit'] == 'edit':
            return render_template('edit.html', result=result)

    @app.route('/task_add', methods=['get', 'post'])
    def task_add():
        project = request.args.get("project")
        return render_template('task_add.html', project=project)

    app.run(debug=True)


if __name__ == '__main__':
    main()
