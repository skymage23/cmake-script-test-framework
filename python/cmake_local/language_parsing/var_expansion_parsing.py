#Standard library imports:
import enum
import re

#Project imports:
import development
import development.exceptions
from .var_expansion_ast import CMakeVarExpansionAST
from .var_expansion_token_list import VarExpansionTokenList
from .var_expansion_tokens import VarParseTokenType, validate_token
class VarParseError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Var expansion parse error: {message}")

#
# This class parses one line of input at a time.
# It looks for CMake-style variable expansions,
# including ENV support, but not CACHE support
# (yet). It supports nested variables as well.
#
# Consider this sample CMake snippet:
#
# include(${CMAKE_CURRENT_LIST_$ENV{INPUT_MECHANISM}})
# 
# The parser operates from left to right, and from
# innermost varible to outermost. 
# "$ENV{INPUT_MECHANISM}" gets expanded first
# and its value is appended to the "CMAKE_CURRENT_LIST"
# string. Finally, the outermost variable is evaluated
# using the newly calculated variable name.
#
# This class does not yet handle multi-line variable
# expansions.
#




 
class VarExpansionParser:
    def __init__(self, context):
        self.context = context
        self.reset()
    
    def reset(self):
        self.var_expansion_nest_stack = []
        self.token_list = None 
        self.ast = CMakeVarExpansionAST()
        self.parse_state_token_stack = []


        
    #Parser-specific list operations:
    def consume_token(self):
        token = self.token_list.get_current_token()
        validate_token(token)
        self.parse_state_token_stack.append(token)
        self.token_list.consume_token()

    def peek_until(self, token_type: VarParseTokenType):
        retval = None
        if self.token_list.is_token_list_fully_iterated():
            raise development.exceptions.DevelopmentError(
                "Token list is fully iterated. Why are we still trying to parse?"
            )

        for token in self.token_list.iterate_from_current_node():
            if token[0]== token_type:
                retval = token
                break
    
        if retval is None:
            return None
        
        validate_token(retval)
        return retval

    #Parser main logic:
    def parse_string(self):
        if self.token_list.is_token_list_fully_iterated():
            raise development.exceptions.DevelopmentError(
                "Token list is fully iterated. Why are we still trying to parse?"
            )
        
        token = self.token_list.get_current_token()
        validate_token(token, token_type=VarParseTokenType.VAR_CHAR_STRING)
        
        # Try to merge with current node if it's a string
        if not self.ast.merge_adjacent_tokens(
            lambda existing_token, new_token: [existing_token[0], existing_token[1] + new_token[1]],
            token
        ):
            # Add as new child if merge failed
            self.ast.shift_to_child_by_index(
                self.ast.add_child_to_current_node(token)[0]
            )
        
        self.consume_token()

    def parse_open_brace(self):
        token = None
        if self.token_list.is_token_list_fully_iterated():
            raise development.exceptions.DevelopmentError(
                "Token list is fully iterated. Why are we still trying to parse?"
            )

        token = self.token_list.get_current_token()
        validate_token(token, token_type=VarParseTokenType.VAR_OPEN_BRACE)
        
        if self.parse_state_token_stack is None:
            raise development.exceptions.DevelopmentError(
                "Parse state token stack was not initialized."
                "It should have been initialized by the parser"
                "before starting parsing."
            )
        
        # Check if this is part of a valid variable expansion
        is_valid_expansion = False
        if len(self.parse_state_token_stack) > 0:
            prev_token = self.parse_state_token_stack[-1]
            if prev_token[0] in [VarParseTokenType.VAR_EXPANSION, VarParseTokenType.VAR_ENV]:
                is_valid_expansion = True
        
        if not is_valid_expansion:
            # If we're inside a variable expansion (nest stack not empty), this is a syntax error
            if len(self.var_expansion_nest_stack) > 0:
                raise VarParseError("Open brace must be preceded by '$' or '$ENV' within variable expansion")
            
            # Otherwise treat as a literal { character
            token[0] = VarParseTokenType.VAR_CHAR_STRING
            self.parse_string()
            return
        
        child_index, node_id = self.ast.add_child_to_current_node(token)
        self.var_expansion_nest_stack.append(node_id)
        self.ast.shift_to_child_by_index(child_index)
        self.consume_token()

    def parse_close_brace(self):
        token = None
        if self.token_list.is_token_list_fully_iterated():
            raise development.exceptions.DevelopmentError(
                "Token list is fully iterated. Why are we still trying to parse?"
            )

        token = self.token_list.get_current_token()
        validate_token(token, token_type=VarParseTokenType.VAR_CLOSE_BRACE)

        # If we have no open brace in the stack, treat this as a literal }
        if len(self.var_expansion_nest_stack) == 0:
            token[0] = VarParseTokenType.VAR_CHAR_STRING
            self.parse_string()
            return
        
        # Create the close brace node and mark it for skipping
       # close_brace_node = VarParser.CMakeVarExpansionASTNode(token)
       # close_brace_node.skip_node = True
       # 
       # # Append this close brace to its corresponding open brace
       # open_brace_node = self.var_expansion_nest_stack[-1]
       # open_brace_node.children.append(close_brace_node)

        #open_brace_token_id = self.var_expansion_nest_stack.pop()
        #self.ast.add_sibling_by_token_ref(open_brace_token_id, token)
        #self.consume_token()

        self.var_expansion_nest_stack.pop() #to TRY not to break the parser further until we test the new execution logic.
        self.ast.shift_to_child_by_index(
            self.ast.add_child_to_current_node(token)[0]
        )
        

    def parse_env(self):
        token = None
        prev_token = None
        next_token = None

        if self.token_list.is_token_list_fully_iterated():
            raise development.exceptions.DevelopmentError(
                "Token list is fully iterated. Why are we still trying to parse?"
            )

        token = self.token_list.get_current_token()
        validate_token(token, token_type=VarParseTokenType.VAR_ENV)
       
        next_token = self.token_list.peek_token(1) 
        validate_token(next_token)

        # Validate that ENV is followed by an open brace
        if next_token[0] != VarParseTokenType.VAR_OPEN_BRACE:
            token[0] = VarParseTokenType.VAR_CHAR_STRING
            self.parse_string()
            return
        
        if not self.parse_state_token_stack:
            raise development.exceptions.DevelopmentError(
                "Parse state token stack was not initialized."
                "It should have been initialized by the parser"
                "before starting parsing."
            )

        # Validate that ENV is preceded by $
        prev_token = self.parse_state_token_stack[-1]
        validate_token(prev_token)

        if prev_token[0] != VarParseTokenType.VAR_EXPANSION:
            token[0] = VarParseTokenType.VAR_CHAR_STRING
            self.parse_string()
            return

        child_index, _ = self.ast.add_child_to_current_node(token)
        self.ast.shift_to_child_by_index(child_index)
        self.consume_token()
         
    def parse_var_expansion(self):
        token = None
        next_token = None

        if self.token_list.is_token_list_fully_iterated():
            raise development.exceptions.DevelopmentError(
                "Token list is fully iterated. Why are we still trying to parse?"
            )

        token = self.token_list.get_current_token()
        validate_token(token, token_type=VarParseTokenType.VAR_EXPANSION)
         
        next_token = self.token_list.peek_token(1)
        validate_token(next_token)
        
        if next_token[0] != VarParseTokenType.VAR_OPEN_BRACE and \
           next_token[0] != VarParseTokenType.VAR_ENV:
            token[0] = VarParseTokenType.VAR_CHAR_STRING
            self.parse_string()
            return
        
        child_index, _ = self.ast.add_child_to_current_node(token)
        self.ast.shift_to_child_by_index(child_index)
        self.consume_token()
        return


    #Mod to handle handling token children:
    #Dispatch has access to previous state.
    def build_ast(self):
        while not self.token_list.is_token_list_fully_iterated():
            token = self.token_list.get_current_token()
            if token[0] == VarParseTokenType.VAR_ENV:
                self.parse_env()
            elif token[0] == VarParseTokenType.VAR_EXPANSION:
                self.parse_var_expansion()
            elif token[0] == VarParseTokenType.VAR_OPEN_BRACE:
                self.parse_open_brace()
            elif token[0] == VarParseTokenType.VAR_CLOSE_BRACE:
                self.parse_close_brace()
            elif token[0] == VarParseTokenType.VAR_CHAR_STRING:
                self.parse_string()
            else:
                raise development.exceptions.DevelopmentError(f"Unimplemented token type: {token[0]}")

    def parse(self, string):
        retval = None
        if string is None or len(string) == 0:
            raise development.exceptions.DevelopmentError("Input string cannot be None or empty")

        #Get in known clean state:
        self.reset()

        #[(start_ind, end_ind, token_type, token_string)]
        self.token_list = VarExpansionTokenList(string)
        #breakpoint()
        self.build_ast()
        # Optimize the AST by merging adjacent string tokens
        retval = self.ast
        #Leave in known clean state:
        self.reset()
        return retval