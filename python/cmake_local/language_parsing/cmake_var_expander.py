import os

import development.exceptions
from .. import cmake_helper
from . import var_expansion_parsing
from . import var_expansion_tokens
from . import var_expansion_ast

def pretty_print_ast(ast: var_expansion_ast.CMakeVarExpansionAST):
    tree_str, longest_line_length = ast.pretty_stringify()
    separator_line = "#" * longest_line_length
    print() 
    print()
    print(separator_line)
    print(tree_str)
    print(separator_line)
    print() 
    print()


def resolve_var(context, varname, is_env_var = False):

    retval = None
    if not is_env_var:
        retval = context.resolve_if_builtin_var(varname)
    else:
        retval = os.environ.get(varname)

    if retval is None:
        raise ValueError("\"{}\" is not a variable we are capable of resolving.".format(varname))

    return retval

#We need to set some expectations for the AST:
#1. Leaf nodes are always VAR_CHAR_STRING tokens.
#2. The root node has no parent.
#3. The root node has no siblings.

def merge_stack_string_elements(
        stack: list[tuple[var_expansion_tokens.VarParseTokenType, str]],
        start: int,
        end: int    
    ) -> str:
    merged_stack = []
    for i in range(start, end):
        merged_stack.append(stack[i])
    
    #Pop unneeded elements from the stack.
    for i in range(start + 1, end):
        stack.pop(start)
    merged_stack.reverse()
    stack[-1] = "".join(merged_stack)

def execute_ast(ast: var_expansion_ast.CMakeVarExpansionAST, context) -> str:
    """
    Expands variables in the AST using the given context.
    The parser has already validated the syntax, so we can trust the token sequences.
    """
    is_env_var = False
    param_stack = []
    nesting_level = 0
    back_check = 0
    token_stack = [node for node in ast.get_bottom_right_to_upper_left_iterator()]

    if len(token_stack) == 0:
        raise development.exceptions.DevelopmentError("AST is empty")
    
    for i in range(0, len(token_stack)):
        token = token_stack[i]
        match token[0]:
            case var_expansion_tokens.VarParseTokenType.VAR_EXPANSION:
                if len(param_stack) == 0:
                    development.exceptions.DevelopmentError("No parameter found for var expansion")
                back_check = i - (3 if not is_env_var else 4)
                if len(param_stack) > 1 and token_stack[back_check][0] != var_expansion_tokens.VarParseTokenType.VAR_CLOSE_BRACE:
                    merge_stack_string_elements(param_stack, 0, len(param_stack))
                param_stack.append(resolve_var(context, param_stack.pop(), is_env_var))
                nesting_level -= 1
                is_env_var = False
            case var_expansion_tokens.VarParseTokenType.VAR_ENV:
                is_env_var = True
            case var_expansion_tokens.VarParseTokenType.VAR_CHAR_STRING:
                param_stack.append(token[1])
            case var_expansion_tokens.VarParseTokenType.VAR_CLOSE_BRACE:
                nesting_level += 1

    param_stack.reverse()
    return "".join(param_stack)
   


def resolve_vars(input: str, context, no_fail = False) -> str:
    """
    Resolves variables in the input string using the given variable resolver.

    Args:
        input: The input string to resolve variables in.
        context: The context to resolve variables in.
        no_fail: If True, do not raise an error if a variable is not found.
                 As an aside, I'd rather not have this parameter,
                 but for now, it is necessary if we don't want to
                 add CMake "set" syntax to the language.

    Returns:
        The input string with variables resolved.
    """
    retval = None
    try:
        parser = var_expansion_parsing.VarExpansionParser(input)
        ast = parser.parse(input)
        retval = execute_ast(ast, context)
    except ValueError as e:
        if not no_fail:
            raise e
        else:
            return input
    return retval