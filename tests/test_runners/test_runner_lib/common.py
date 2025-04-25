import importlib
import pathlib
import sys

from unittest import TestCase

#Shared constants:
file_path_obj = pathlib.Path(__file__).resolve()
project_base_dir = file_path_obj.parent.parent.parent.parent
scripts_dir = project_base_dir / "python"
test_dir = project_base_dir / "tests"
test_file_dir = test_dir / "test_files"
test_helper_dir = test_file_dir / "test-helper-dir"
third_party_dir = project_base_dir / "third_party"
pybuildtoolstr = "python-useful-build-sys-tools"
development_shell_helper_str = "development_shell_helper"

#Shared functions:
def die(message: str):
    print(message, file=sys.stderr)
    exit(1)

def die_missing_dependency(dependency: str):
    die(f"Missing dependency: {dependency}")

def die_missing_directory(directory: str):
    die_missing_dependency(f"Directory: {directory}")

def get_proj_component_relative_path_str(abs_path: pathlib.Path):
    return abs_path.relative_to(project_base_dir).__str__()

if not scripts_dir.exists():
    die_missing_directory(get_proj_component_relative_path_str(scripts_dir))
sys.path.append(scripts_dir.__str__())

#Common state initialization:
pyusefulbuildtools = None
if not third_party_dir.exists():
    die_missing_directory(get_proj_component_relative_path_str(third_party_dir))

sys.path.append(third_party_dir.__str__())

pybuildtools = third_party_dir / pybuildtoolstr
if not pybuildtools.exists():
    die_missing_directory(get_proj_component_relative_path_str(pybuildtools))

sys.path.append(pybuildtools)
pyusefulbuildtools = importlib.import_module(pybuildtoolstr)

if not pyusefulbuildtools is None:
    pyusefulbuildtools.initialize()


#Hack to make it easy to track inheritance.
class TestCaseWrapper(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_breakpoint = False

    def setUp(self):
        super().setUp()
