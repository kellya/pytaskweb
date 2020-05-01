#!/usr/bin/env python3

import subprocess
import json
from flask import Flask, render_template


class Task:
    projoutput = subprocess.run(['task', 'status:pending', 'export'],
                                stdout=subprocess.PIPE)
    alltasks = json.loads(projoutput.stdout)

    def get_all_projects(self):
        alltasks = self.alltasks
        allprojects = []
        iter = 0
        maxiter = len(alltasks)
        while iter < maxiter:
            try:
                print(alltasks[iter]['project'])
                if alltasks[iter]['project'] not in allprojects:
                   # if '.' in alltasks[iter]['project']:
                   #     parentproj = alltasks[iter]['projects'].split('.')[0]
                    allprojects.append(alltasks[iter]['project'])
            except KeyError:
                pass
            iter += 1
        return allprojects


def main():
    myprojects = Task()
    app = Flask(__name__)

    projects = sorted(myprojects.get_all_projects(), key=lambda s: s.lower())
    #projects = sorted(myprojects.get_all_projects())
    @app.route('/')
    def home():
        return render_template('index.html', projects=projects)
    app.run(debug=True)


if __name__ == '__main__':
    main()
