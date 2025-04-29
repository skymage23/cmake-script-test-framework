import copy
import enum
import os
import pathlib
import re

from . import language_parsing

class VarEnvironExpansionError(Exception):
    def __init__(self, varname):
        super().__init__(f"Environment variable \"{varname}\" does not exist.")


class CMakeScriptContext:
    def resolve_cmake_build_dir(context):
        return context.build_dir
    
    def resolve_cmake_source_dir(context):
        return context.source_dir
    
    def resolve_project_source_dir(context):
        return context.project_source_dir.__str__()
    
    def resolve_cmake_current_list_file(context):
        return context.list_file.__str__()
    
    def resolve_cmake_current_list_dir(context):
        return context.list_file.parent.__str__()    
    
    
    def __init__(self,
        list_file: str, 
        build_dir: str,
        source_dir: str,
        project_source_dir: str           
    ):
        self.list_file = pathlib.Path(list_file)
        self.build_dir = pathlib.Path(build_dir)
        self.source_dir = pathlib.Path(source_dir)
        self.project_source_dir = pathlib.Path(project_source_dir)
        self.current_list_dir = self.list_file.parent

        self.supported_builtin_vars = {
            "CMAKE_BUILD_DIR": CMakeScriptContext.resolve_cmake_build_dir,
            "CMAKE_SOURCE_DIR": CMakeScriptContext.resolve_cmake_source_dir,
            "CMAKE_CURRENT_LIST_FILE": CMakeScriptContext.resolve_cmake_current_list_file,
            "CMAKE_CURRENT_LIST_DIR": CMakeScriptContext.resolve_cmake_current_list_dir,
            "PROJECT_SOURCE_DIR": CMakeScriptContext.resolve_project_source_dir
        }
        self.re_cmake_var_dereference = re.compile(R"^\$(?:ENV)?{.*}.?")
        self.re_cmake_env_var_dereference = re.compile(R"^\$?ENV{")

    def resolve_if_builtin_var(self, varname):
        retval_func = self.supported_builtin_vars.get(varname)
        if retval_func is None:
            return None
        return retval_func(self)

    class CMakeVarRefLangSyntaxError(Exception):
        def __init__(self, message):
            super().__init__(f"CMake variable dereference language syntax error: {message}")


    def resolve_vars(self, string):
        return language_parsing.resolve_vars(string, self)
    
    def __str__(self):
        #Hello:
        retval_buff = [
"""*
* CMakeScriptContext:                      
***********************\n"""
        ]
        retval_buff.append("List file: {}".format(self.list_file))
        retval_buff.append("Build dir: {}".format(self.build_dir))
        retval_buff.append("CMake source dir: {}".format(self.source_dir))
        retval_buff.append("Project source dir: {}".format(self.project_source_dir))
        retval_buff.append("\n")
        return "\n".join(retval_buff)