import copy
import enum
import os
import pathlib
import re
#  I would MUCH rather make a lexer, but
# I also want to keep this project simple.


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
        return context.list_file
    
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

    def resolve_var(self, varname, is_env_var = False):
        retval = None
        if varname not in self.supported_builtin_vars and not is_env_var:
            raise ValueError("\"{}\" is not a variable we are capable of resolving.".format(varname))
        
        if not is_env_var:
            retval = self.supported_builtin_vars[varname](self)
        else:
            retval = os.environ.get(varname)
            if retval is None:
                raise VarEnvironExpansionError(varname)
    #What if there is more than one variable?
    # we need to change direction. We need to make tokenizer and a lexer.

    class CMakeVarRefLangSyntaxError(Exception):
        def __init__(self, message):
            super().__init__(f"CMake variable dereference language syntax error: {message}")

  
    #def resolve_vars(self, string):
    #    var_string = None
    #    resolved_var = None
    #    string = string.strip()
    #    if self.re_cmake_var_dereference.search(string) is None:
    #        return string
    #    
    #    ind_temp1 = string.index('$') + 1
    #    ind_temp2 = string.index('}')
    #    var_string = string[ind_temp1 + 1: -(len(string) - (ind_temp2))]
    
    #    #OK. Are we an environment variable or not.
    #    if self.re_cmake_env_var_dereference.search(var_string) is None:
    #        resolved_var = self.resolve_var(var_string)            
    #    else: 
    #        #Parse 
    #        var_string = string[(string.index('{') + 1):]
    #        if not var_string in os.environ:
    #            raise ValueError("\"{}\" is not an existing environment variable.".format(var_string))
    #        resolved_var =os.environ[string]
    #    
    #    retval = f"{string[0:ind_temp1 - 2]}{resolved_var}{string[ind_temp2+1:]}"   
    #    return retval
    
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