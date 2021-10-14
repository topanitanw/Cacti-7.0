import glob
import os
import yaml
import glob
import logging as log


def load_yaml(filepath):
    assert os.path.isfile(filepath), \
        "%s does not exit" % filepath

    with open(filepath, 'r') as fopen:
        data = yaml.load(fopen, Loader=yaml.FullLoader)
    return data


def write_yaml(filepath, yaml_content):
    filedir = os.path.dirname(filepath)
    assert os.path.exists(filedir), \
        "%s does not exit" % filedir

    with open(filepath, 'w') as fopen:
        data = yaml.dump(yaml_content, fopen, sort_keys=True)

    log.info("write yaml file: %s", filepath)
    return data


def mkdir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def ls(filepath):
    files = []
    # filepath can be "./*.txt" to load all text files in the current directory
    for afile in glob.glob(filepath):
        files.append(afile)

    return files


def write_file(filepath, file_content):
    log.info("writing %s", filepath)
    with open(filepath, "w") as fopen:
        fopen.write(file_content)
