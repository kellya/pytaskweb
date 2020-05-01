#!/usr/bin/env python3

import subprocess
from flask import Flask, render_template


class Task:
    def get_projects(self):
        projoutput = subprocess.run(['task', '_projects'],
                                    stdout=subprocess.PIPE)
        projects = projoutput.stdout.splitlines()
        returnprojects = []
        for project in projects:
            returnprojects.append(project.decode())
        return returnprojects


def main():
    myprojects = Task()
    app = Flask(__name__)

    projects = sorted(myprojects.get_projects())
    @app.route('/')
    def home():
        return render_template('index.html', projects=projects)
    app.run()


if __name__ == '__main__':
    main()
