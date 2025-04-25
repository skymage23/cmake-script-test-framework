import development.exceptions
from .. import cmake_helper
from . import var_expansion_parsing
from . import var_expansion_tokens
from . import var_expansion_ast




#We need to set some expectations for the AST:
#1. Leaf nodes are always VAR_CHAR_STRING tokens.
#2. The root node has no parent.
#3. The root node has no siblings.

def execute_ast(ast: var_expansion_ast.CMakeVarExpansionAST, context: cmake_helper.CMakeScriptContext) -> str:
    """
    Expands variables in the AST using the given context.
    The parser has already validated the syntax, so we can trust the token sequences.
    """
    is_env_var = False
    param = None
    ast.pretty_print()
    token_stack = [node for node in ast.get_bottom_right_to_upper_left_iterator()]
    print(token_stack) 

    if len(token_stack) == 0:
        raise development.exceptions.DevelopmentError("AST is empty")
    
     
    for token in token_stack:
        match token[0]:
            case var_expansion_tokens.VarParseTokenType.VAR_EXPANSION:
                if param is None:
                    development.exceptions.DevelopmentError("No parameter found for var expansion")
                param = context.resolve_var(param, is_env_var)
                is_env_var = False
            case var_expansion_tokens.VarParseTokenType.VAR_ENV:
                is_env_var = True
            case var_expansion_tokens.VarParseTokenType.VAR_CHAR_STRING:
                if param is not None:
                    param = token[1] + param
                else:
                    param = token[1]
            case var_expansion_tokens.VarParseTokenType.VarParseTokenType.VAR_OPEN_BRACE:
                
                break

    return param
   

def resolve_vars(input: str, context: cmake_helper.CMakeScriptContext) -> str:
    """
    Resolves variables in the input string using the given variable resolver.

    Args:
        input: The input string to resolve variables in.

    Returns:
        The input string with variables resolved.
    """
    parser = var_expansion_parsing.VarExpansionParser(input)
    ast = parser.parse(input)
    return execute_ast(ast, context)