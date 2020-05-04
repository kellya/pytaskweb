#!/usr/bin/env python3

import subprocess
import json
from flask import Flask, render_template


class Task:
    """An object to hold task data obtained from the task command"""
    task_cmd = 'task'
    search_filter = 'status:pending'
    projoutput = subprocess.run([task_cmd, search_filter, 'export'],
                                stdout=subprocess.PIPE)
    alltasks = json.loads(projoutput.stdout)

    def get_all_projects(self):
        """Return a list of unique projects"""
        allprojects = []
        iter = 0
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

    @app.route('/projects')
    def projects():
        projects = sorted(myprojects.get_all_projects(), key=lambda s: s.lower())
        return render_template('projects.html', projects=projects)

    @app.route('/project_tasks/<name>')
    def project_tasks(name):
        return render_template('tasks.html', tasks=myprojects.get_tasks(name))

    @app.route('/task/<uuid>')
    def task_detail(uuid):
        return render_template('task_detail.html',
                               task=myprojects.get_task_detail(uuid))
    app.run(debug=True)


if __name__ == '__main__':
    main()
