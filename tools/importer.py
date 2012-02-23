import os
import sys

# find root directory
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
while not os.path.exists(os.path.join(ROOT_DIR, 'umit')):
    new_dir = os.path.abspath(os.path.join(ROOT_DIR, os.path.pardir))
    if ROOT_DIR == new_dir:
        raise Exception("Can't find root dir.")
    ROOT_DIR = new_dir

execfile(os.path.join(ROOT_DIR, 'deps', 'umit-common', 'utils', 'importer.py'))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'deps'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'deps', 'icm-common'))
sys.path.insert(0, os.path.join(ROOT_DIR, 'deps', 'umit-common'))