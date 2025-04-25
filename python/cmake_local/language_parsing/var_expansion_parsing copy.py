  #Retval tuples: (start_ind, token, end_ind)
import enum

import development
import development.exceptions

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
# This class does not implement illegal CMake character
# checking. That should not be a problem for now because
# the encompassing program uses CMake itself as a linter.
#

class VarParser:
    def __init__(self, context):
        self.context = context
        self.token_list = None
        self.reset()

    class VarParseTokenType(enum.Enum):
        VAR_BEGIN = enum.auto()
        VAR_ENV = enum.auto()
        VAR_OPEN_BRACE = enum.auto()
        VAR_CLOSE_BRACE = enum.auto()
        VAR_CHAR_STRING = enum.auto()
    
    class Token:
        def __init__(
                self,
                token_list_ind,
                token_type: 'VarParser.VarParseTokenType',
                token_string
        ):
            self.token_list_ind = token_list_ind
            self.token_type = token_type
            self.token_string = token_string
            self.consumed = False

        def __str__(self):
            return f"Token(token_list_ind={self.token_list_ind}, token_type={self.token_type}, token_string={self.token_string})"

        def consume(self, parser):
            if self.consumed:
                return

            self.consumed = True
            self.evaluate_next_token(parser)

        def evaluate_next_token(self, parser):
            parser.counter += 1
            if parser.counter < len(parser.token_list):
                parser.token_list[parser.counter].handle(parser)

        def handle_internal(self, parser):
            raise development.exceptions.DevelopmentError("This method should be overridden by subclasses")

        def handle(self, parser):
            if self.consumed:
                self.evaluate_next_token(parser)
                return
            self.handle_internal(parser)
        
        def __str__(self):
            return f"Token(token_list_ind={self.token_list_ind}, token_type={self.token_type}, token_string={self.token_string})"

    #Anything in the line that is not a reserved character or is not
    #an instance of said character in a syntactically correct orientation.
    class VarCharStringToken(Token):
        def __init__(self, token_list_ind, char_string):
            super().__init__(token_list_ind, VarParser.VarParseTokenType.VAR_CHAR_STRING, char_string)

        def handle_internal(self, parser):
            if self.consumed:
                return

            if parser.counter > 0:
                #Merge with char tokens to the left and right:
                start_ind = self.token_list_ind - 1
                end_ind = self.token_list_ind + 1
                temp_string = ""
                while start_ind >= 0 and \
                    parser.token_list[start_ind].token_type == VarParser.VarParseTokenType.VAR_CHAR_STRING:
                    start_ind -= 1
                start_ind += 1
                
                while end_ind < len(parser.token_list) and \
                    parser.token_list[end_ind].token_type == VarParser.VarParseTokenType.VAR_CHAR_STRING:
                    parser.token_list[end_ind].consumed = True
                    end_ind += 1

                for i in range(start_ind, end_ind):
                    temp_string += parser.token_list[i].token_string

                #This is easier than moving than having to move tokens down the list:
                if end_ind < len(parser.token_list):
                    parser.token_list = parser.token_list[:start_ind] + [VarParser.VarCharStringToken(start_ind, temp_string)] \
                                        + parser.token_list[end_ind:]
                else:
                    parser.token_list = parser.token_list[:start_ind] + [VarParser.VarCharStringToken(start_ind, temp_string)]

                self.consumed = True
                parser.counter = start_ind
                parser.token_list[start_ind].handle(parser)
                return
            
            self.consume(parser)

    #Language character: '$'
    class VarBeginToken(Token):
        def __init__(self, token_list_ind):
            super().__init__(token_list_ind, VarParser.VarParseTokenType.VAR_BEGIN, '$')

        def handle_internal(self, parser):
            if self.token_list_ind + 1 == len(parser.token_list) or \
               not (parser.token_list[self.token_list_ind + 1].token_type == VarParser.VarParseTokenType.VAR_ENV or\
                    parser.token_list[self.token_list_ind + 1].token_type == VarParser.VarParseTokenType.VAR_OPEN_BRACE
            ):
                if (self.token_list_ind + 2 < len(parser.token_list)) and \
                   (parser.token_list[self.token_list_ind + 2].token_type == VarParser.VarParseTokenType.VAR_OPEN_BRACE):
                    raise VarParseError("Only ENV is allowed between '$' and '{'")

                else:
                    parser.token_list[self.token_list_ind] = VarParser.VarCharStringToken(
                        self.token_list_ind,
                        self.token_string
                    )
                    parser.token_list[self.token_list_ind].handle(parser)
                    return
            self.consume(parser)
    #Language character: '{'        
    class VarOpenBraceToken(Token):
        def __init__(self, token_list_ind):
            super().__init__(token_list_ind, VarParser.VarParseTokenType.VAR_OPEN_BRACE, '{')
            self.env_var = False

        def handle_internal(self, parser):
            close_brace_found = False
            #Look for associated close brace:
            if parser.counter == 0 or \
               not (parser.token_list[parser.counter - 1].token_type == VarParser.VarParseTokenType.VAR_BEGIN or\
                    parser.token_list[parser.counter - 1].token_type == VarParser.VarParseTokenType.VAR_ENV
            ):
                parser.token_list[self.token_list_ind] = VarParser.VarCharStringToken(
                    self.token_list_ind,
                    self.token_string
                )
                parser.token_list[self.token_list_ind].handle(parser)
                return

           # Error is here:
            open_brace_stack_counter = 0
            for i in range(self.token_list_ind + 1, len(parser.token_list)):
                token = parser.token_list[i]
                if token.token_type == VarParser.VarParseTokenType.VAR_OPEN_BRACE and \
                   parser.token_list[i - 1].token_type == VarParser.VarParseTokenType.VAR_BEGIN:
                      #Hello:
                      open_brace_stack_counter += 1 
                if token.token_type == VarParser.VarParseTokenType.VAR_CLOSE_BRACE:
                   if open_brace_stack_counter > 0:
                       open_brace_stack_counter -= 1
                   else:
                       token.open_brace_ind = self.token_list_ind
                       token.env_var = self.env_var
                       close_brace_found = True
                       break
            
            if not close_brace_found:
                raise VarParseError("Unterminated variable expansion: An '{' is missing its '}'")

            self.consume(parser)

    #Language reserved character string: "ENV" 
    class VarEnvToken(Token):
        def __init__(self, token_list_ind):
            super().__init__(token_list_ind, VarParser.VarParseTokenType.VAR_ENV, "ENV")
        
        def handle_internal(self, parser): 
            if parser.counter == 0 or \
               parser.token_list[parser.counter - 1].token_type != VarParser.VarParseTokenType.VAR_BEGIN or\
               parser.counter + 1 == len(parser.token_list) or\
               parser.token_list[parser.counter + 1].token_type != VarParser.VarParseTokenType.VAR_OPEN_BRACE:
                
                
                parser.token_list[self.token_list_ind] = VarParser.VarCharStringToken(
                    self.token_list_ind,
                    self.token_string
                )
                self.consumed = True
                parser.token_list[self.token_list_ind].handle(parser)
                return
            
            parser.token_list[parser.counter + 1].env_var= True
            self.consume(parser)

    #Language character: '}' 
    class VarCloseBraceToken(Token):
        def __init__(self, token_list_ind):
            super().__init__(token_list_ind, VarParser.VarParseTokenType.VAR_CLOSE_BRACE, '}')
            self.env_var = False
            self.open_brace_ind = None
            self.spent = False


        def handle_internal(self, parser):
            temp_token = None
            temp_ind = None
            var_name = None
            var_retval = None
            #This handles all cases where this token was not preceded by an open brace:
            breakpoint()
            if self.open_brace_ind is None:
                parser.token_list[self.token_list_ind] = VarParser.VarCharStringToken(
                    self.token_list_ind,
                    self.token_string
                )
                parser.token_list[self.token_list_ind].handle(parser)
                return
            
            var_name = ''
            temp_ind = self.open_brace_ind + 1
            temp_token = parser.token_list[temp_ind]
            if temp_token.token_type != VarParser.VarParseTokenType.VAR_CLOSE_BRACE:
                var_name = temp_token.token_string

            var_retval = parser.resolve_var(var_name, self.env_var)
            
            #Add the resolved var to the token list:
            temp_ind -= 2
            if self.env_var:
                temp_ind -= 1
            parser.token_list[temp_ind] = VarParser.VarCharStringToken(
                temp_ind,
                var_retval
            )
            parser.counter = temp_ind
            self.consumed = True
            return parser.token_list[temp_ind].handle(parser)

    def resolve_var(self, var_name, is_env=False):
        return self.context.resolve_var(var_name, is_env)
    
    def reset(self):
        if not self.token_list is None:
            self.token_list.clear()
            self.token_list = None
        self.resolved_string = None
        self.counter = 0



   # def var_parse_peek(self, string, start_ind, count):
   #     retval=[]
   #     if count < 0:
   #         raise ValueError("\"count\" cannot be negative")
   #     for i in range(start_ind, start_ind + count):
   #         retval.append(string[i])
   #     return "".join(retval)

    def get_token_stack(self, string):
        retval_tokens = []
        temp_arr=[]
        counter = 0
        token_list_ind = 0
        while counter < len(string):
            match(string[counter]):
                case '$':
                    if len(temp_arr) > 0:
                        retval_tokens.append(VarParser.VarCharStringToken(token_list_ind, "".join(temp_arr)))
                        temp_arr.clear()
                        token_list_ind += 1
                    retval_tokens.append(VarParser.VarBeginToken(token_list_ind))
                    token_list_ind += 1
                
                case '{':
                    if len(temp_arr) > 0:
                        retval_tokens.append(VarParser.VarCharStringToken(token_list_ind, "".join(temp_arr)))
                        temp_arr.clear()
                        token_list_ind += 1
                    retval_tokens.append(VarParser.VarOpenBraceToken(token_list_ind))
                    token_list_ind += 1
                
                case '}':                   
                    if len(temp_arr) > 0:
                        retval_tokens.append(VarParser.VarCharStringToken(token_list_ind, "".join(temp_arr)))
                        temp_arr.clear()
                        token_list_ind += 1
                    retval_tokens.append(VarParser.VarCloseBraceToken(token_list_ind))
                    token_list_ind += 1
                case 'E':
                    if(string[counter : counter + 3] == 'ENV'):
                        if len(temp_arr) > 0:
                            retval_tokens.append(VarParser.VarCharStringToken(token_list_ind, "".join(temp_arr)))
                            temp_arr.clear()
                            token_list_ind += 1
                        retval_tokens.append(VarParser.VarEnvToken(token_list_ind))
                        counter += 2
                        token_list_ind += 1
                    else: 
                        temp_arr.append('E')
                case _:
                    temp_arr.append(string[counter])
            counter += 1

        if len(temp_arr) > 0:
            retval_tokens.append(VarParser.VarCharStringToken(token_list_ind, "".join(temp_arr)))
            temp_arr.clear()
        return retval_tokens


    def resolve_all_vars(self, string):
        retval_arr = None
        if string is None or len(string) == 0:
            return None

        #[(start_ind, end_ind, token_type, token_string)]
        self.token_list = self.get_token_stack(string)
        self.counter = 0


        self.token_list[self.counter].handle(self)
        retval_arr = []
        for elem in self.token_list:
            if not elem.consumed:
                raise development.exceptions.DevelopmentError(f"""
We have an unspent token in the token list after parsing {elem.token_string}""")
            
            if elem.token_type == VarParser.VarParseTokenType.VAR_CHAR_STRING:
                retval_arr.append(elem.token_string)
        return "".join(retval_arr)