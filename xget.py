#!/usr/bin/env python
"""Runtime for cis-xget."""
import os
import json
import argparse
import re
import shutil
import subprocess as sp
import xnat


def _json_load(filename):
    """Load json from file in one line."""
    with open(filename, 'r') as read_json:
        data = json.load(read_json)
    return data


def _add_to_tar(tar_path, input_item):
    sp.Popen(['tar', '-czf', tar_path, input_item]).wait()


def _get_parser():
    # New set of command line arguments --config is the credentials file
    parser = argparse.ArgumentParser('Arguments required to pull files')
    parser.add_argument(
        '-c', '--credentials', dest='credentials', required=True,
        help='Path to credentials file for logging in to XNAT')
    parser.add_argument(
        '-p', '--project', dest='project', required=True,
        help='Name of project on XNAT')
    parser.add_argument(
        '-d', dest='dicom_dir', required=True,
        help='location of main directory for storing dicoms')
    parser.add_argument(
        '-f', '--filter', dest='filter')


def xget(credentials=None,
         project=None,
         dicom_dir=None,
         filter=None):
    """Pull and Compress data from a given XNAT project.

    Keyword arguments:
    credentials -- path to file containing XNAT login information.
    project -- name of project as it appears on XNAT (e.g. McMakin_EMU).
    dicom_dir -- path to local directory to store pulled dicoms.
    _filter -- regex to filter out certain subjects.
    """
    if not filter:
        filter = r'([\w\W]+)'  # Grab any file from project
    previous_subjs = {}
    os.makedirs(dicom_dir, exist_ok=True)
    subjs_json = dicom_dir + '/downloaded_subjects.json'
    credentials = _json_load(credentials)
    previous_subjs = {}
    if os.path.isfile(subjs_json):
        previous_subjs = _json_load(subjs_json)

    # Creates XNAT session and looks for scans not already grabbed from XNAT,
    # then ends session once completed
    session = xnat.connect(credentials['server'],
                           user=credentials['user'],
                           password=credentials['password'])
    project_data = session.projects[project]
    for subject in project_data.subjects:
        subject_data = session.projects[project].subjects[subject]
        if not re.search(filter, subject_data.label):
            continue
        if subject_data.label not in previous_subjs.keys():
            previous_subjs[subject_data.label] = []
        for exp in subject_data.experiments:
            exp_data = subject_data.experiments[exp]
            if exp_data.label not in previous_subjs[subject_data.label]:
                previous_subjs[subject_data.label].append(exp_data.label)
                print(exp_data.label)
                exp_data.download_dir(dicom_dir)
                _add_to_tar(dicom_dir + '/' + exp_data.label + '.tar.gz',
                            dicom_dir + '/' + exp_data.label + '/scans/')
                shutil.rmtree(dicom_dir + '/' + exp_data.label)
    session.disconnect()

    # Dumps json with any newly scans grabbed and tarred from XNAT
    with open(subjs_json, 'w') as dump_file:
        json.dump(previous_subjs, dump_file, indent=4)


if __name__ == '__main__':
    args = _get_parser.parse_args()
    xget(**args)
