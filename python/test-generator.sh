#!/bin/sh
export CMAKE_TEST_FRAMEWORK_DIR="$(realpath ${PWD}/..)"

CPLUSPLUS_PROJ_BASE="${HOME}/Documents/source_cd_dirs/nvme_1tb/cplusplus-task-management"
./generate-test-file.py \
-b "${CPLUSPLUS_PROJ_BASE}/build" \
-c "${CPLUSPLUS_PROJ_BASE}" \
-p "${CPLUSPLUS_PROJ_BASE}" \
"${CPLUSPLUS_PROJ_BASE}/scripts/scripts_tests/cmake/test_get_targets_from_project_tree.cmake"
