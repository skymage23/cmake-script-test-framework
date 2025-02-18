import pathlib
file_path_obj = pathlib.Path(__file__).resolve()
project_base_dir = file_path_obj.parent.parent.parent.parent
scripts_dir = project_base_dir / "python"
test_dir = project_base_dir / "tests"
test_file_dir = test_dir / "test_files" 