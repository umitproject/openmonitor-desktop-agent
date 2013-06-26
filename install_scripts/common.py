"""
Common values that may be needed by the generic setup, windows setup and the
macosx setup.
"""
import os

ICM_AGENT_ROOT = ''
BIN_DIRNAME = os.path.join(ICM_AGENT_ROOT,'bin')
ICM_AGENT_MAIN = os.path.join(BIN_DIRNAME, 'icm-agent')


CONFIG_DIR = os.path.join(ICM_AGENT_ROOT,'conf')
DOCS_DIR = os.path.join(ICM_AGENT_ROOT,'docs')
LOG_DIR = os.path.join(ICM_AGENT_ROOT,'log')
LOCALES_DIR = os.path.join(ICM_AGENT_ROOT,'share', 'locales')
IMAGES_DIR = os.path.join(ICM_AGENT_ROOT,'share', 'images')
ICONS_DIR = os.path.join(ICM_AGENT_ROOT,'share', 'icons')
DB_DIR = os.path.join(ICM_AGENT_ROOT,'share', 'db')
TMP_DIR = os.path.join(ICM_AGENT_ROOT,'tmp')
TOOLS_DIR = os.path.join(ICM_AGENT_ROOT,'tools')
UMITLIB_DIR = os.path.join(ICM_AGENT_ROOT,'umit')



