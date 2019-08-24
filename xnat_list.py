#!/usr/bin/env python
import os
import json
import argparse
import re
import xnat

def json_load(filename):
    '''
    Quick function to load json from file in one line
    '''
    with open(filename, 'r') as read_json:
        data = json.load(read_json)
    return data

def xget_file(config_file=None,
              project=None,
              regex=None,
              work_dir=None):
    xnat_list = {}
    dicom_dir = os.path.join(work_dir, project)
    os.makedirs(dicom_dir, exist_ok=True)
    subjs_json = dicom_dir + 'downloaded_subjects.json'
    print(subjs_json)
    config = json_load(config_file)
    xnat_list = {}
    if os.path.isfile(subjs_json):
        xnat_list = json_load(subjs_json)
    session = xnat.connect(config['server'],
                           user=config['user'],
                           password=config['password'])
    project_data = session.projects[project]
    for subject in project_data.subjects:
        subject_data = session.projects[project].subjects[subject]
        if not re.search(regex, subject_data.label):
            continue
        if subject_data.label not in xnat_list.keys():
            xnat_list[subject] = []
        for exp in subject_data.experiments:
            exp_data = subject_data.experiments[exp]
            if exp_data.label not in xnat_list[subject]:
                xnat_list[subject].append(exp_data.label)
                print(exp_data.label)
                exp_data.download_dir(dicom_dir)
            #subses_label = session.subjects[subject].experiments[exp].label
    with open(subjs_json, 'w') as dump_file:
        json.dump(xnat_list, dump_file, indent=4)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Arguments required to pull files')
    parser.add_argument('-c', '--config', dest='config_file', required=True)
    parser.add_argument('-p', '--project', dest='project', required=True)
    parser.add_argument('-w', dest='work_dir')
    parser.add_argument('-r', '--regex', dest='regex', required=True)
    args = parser.parse_args()
    xget_file(args.config_file, args.project, args.regex, args.work_dir)
