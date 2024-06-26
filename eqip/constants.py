from pathlib import Path


def read_author_from_metadata(metadata_file: Path) -> str:
    with open(metadata_file) as f:
        for l in f.readlines():
            if "author=" in l:
                return l.split("=")[-1].strip()
    raise Exception(f"Did not find version in {metadata_file=}")


def read_project_name_from_metadata(metadata_file: Path) -> str:
    with open(metadata_file) as f:
        for l in f.readlines():
            if "name=" in l:
                return l.split("=")[-1].strip()
    raise Exception(f"Did not find version in {metadata_file=}")


def read_version_from_metadata(metadata_file: Path) -> str:
    with open(metadata_file) as f:
        for l in f.readlines():
            if "version=" in l:
                return l.split("=")[-1].strip()
    raise Exception(f"Did not find version in {metadata_file=}")


PLUGIN_DIR = Path(__file__).parent
METADATA_FILE = PLUGIN_DIR / "metadata.txt"

if not METADATA_FILE.exists():
    raise Exception(f"Did not find  {METADATA_FILE=}")

PROJECT_NAME = read_project_name_from_metadata(METADATA_FILE)
VERSION = read_version_from_metadata(METADATA_FILE)
PLUGIN_AUTHOR = read_author_from_metadata(METADATA_FILE)

MANUAL_REQUIREMENTS = [
    "qgis"
    # 'qgis' # not visible to pip?
]

try:
    from apppath import AppPath

    PROJECT_APP_PATH = AppPath(PROJECT_NAME, app_author=PLUGIN_AUTHOR)
except:
    PROJECT_APP_PATH = None

__version__ = VERSION
__author__ = PLUGIN_AUTHOR
