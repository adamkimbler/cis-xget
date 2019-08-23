#!/usr/bin/env python
import os
import json
import sys
import argparse
import re
import xnat

#config_file = sys.argv[1]
#project = sys.argv[2]
#ref = sys.argv[3]

def xget_file(config_file=None, project=None, regex=None, work_dir=None):
    xnat_list = {}

    dicom_dir = work_dir + '/' + project + '/'
    os.makedirs(dicom_dir, exist_ok=True)
    subjs_json = dicom_dir + 'downloaded_subjs.json'
    with open(config_file) as f:
        config = json.load(f)
    if os.path.isfile(subjs_json):
        with open(subjs_json, 'r') as f:
            xnat_list = json.load(f)
    else:
        xnat_list = {}
    session = xnat.connect(config['server'],
                           user=config['user'],
                           password=config['password'])
    for subject in session.projects[project].subjects:
        if not re.search(regex, session.projects[project].subjects[subject].label):
            continue
        subject = session.projects[project].subjects[subject].label
        if subject not in xnat_list.keys():
            xnat_list[subject] = []
        for exp in session.projects[project].subjects[subject].experiments:
            exp = session.projects[project].subjects[subject].experiments[exp].label
            if exp not in xnat_list[subject]:
                xnat_list[subject].append(exp)
                session.projects[project].subjects[subject].experiments[exp].download(dicom_dir + exp + '.tar')
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
