#!/usr/bin/env python
import json
import xnat
import sys
import argparse
import re
#config_file = sys.argv[1]
#project = sys.argv[2]
#ref = sys.argv[3]

def xget_file(config_file=None, project=None, regex=None, work_dir=None):
    xnat_list = {}
    subjs_json = work_dir + '/' + project + '.json'
    with open(config_file) as f:
        config = json.load(f)
    with open(subjs_json, 'r') as f:
        xnat_list = json.load(f)
    session = xnat.connect(config['server'],
                           user=config['user'],
                           password=config['password'])
    for subject in session.projects[project].subjects:
        if not re.search(regex, session.projects[project].subjects[subject].label):
            continue
        subject = session.projects[project].subjects[subject].label
        if subject not in xnat_list.keys():
            xnat_list[subject] = []
        for exp in session.subjects[subject].experiments:
            exp = session.subjects[subject].experiments[exp].label
            if exp not in xnat_list[subject]:
                xnat_list[subject].append(exp)
            #subses_label = session.subjects[subject].experiments[exp].label
    with open(subjs_json, 'w') as df:
        json.dump(xnat_list, df, indent=4)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Arguments required to pull files')
    parser.add_argument('-c', '--config', dest='config_file', required=True)
    parser.add_argument('-p', '--project', dest='project', required=True)
    parser.add_argument('-w', dest='work_dir')
    parser.add_argument('-r', '--regex', dest='regex', required=True)
    args = parser.parse_args()
    xget_file(args.config_file, args.project, args.regex, args.work_dir)
