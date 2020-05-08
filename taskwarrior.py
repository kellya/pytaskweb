#!/usr/bin/env python3

import subprocess
import json
from flask import Flask, render_template, request


class Task:
    """An object to hold task data obtained from the task command"""
    task_cmd = 'task'
    search_filter = 'status:pending'

    def load_task_data(self):
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
                if self.alltasks[iter]['project'] not in allprojects:
                    # if '.' in alltasks[iter]['project']:
                    #     parentproj = alltasks[iter]['projects'].split('.')[0]
                    allprojects.append(self.alltasks[iter]['project'])
            except KeyError:
                pass
            iter += 1
        return allprojects

    def get_tasks(self, project):
        """return a list of all tasks within the given {project}"""
        iter = 0
        maxiter = len(self.alltasks)
        projecttasks = []
        while iter < maxiter:
            try:
                if self.alltasks[iter]['project'] == project:
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

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/projects', methods=['get', 'post'])
    def projects():
        project = sorted(myprojects.get_all_projects(), key=lambda s: s.lower())
        return render_template('projects.html', projects=project)

    @app.route('/project_tasks/<name>')
    def project_tasks(name):
        return render_template('tasks.html', tasks=myprojects.get_tasks(name))

    @app.route('/task/<uuid>')
    def task_detail(uuid):
        return render_template('task_detail.html',
                               task=myprojects.get_task_detail(uuid))

    @app.route('/complete/<uuid>', methods=['POST'])
    def task_complete(uuid):
        result = request.form.to_dict()
        print(str(result))
        if result['submit'] == 'complete':
            return render_template('complete.html', result=result)
        elif result['submit'] == 'edit':
            return render_template('edit.html', result=result)

    app.run(debug=True)


if __name__ == '__main__':
    main()
