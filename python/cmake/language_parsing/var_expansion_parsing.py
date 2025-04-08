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
                start_ind,
                end_ind,
                token_list_ind,
                token_type: 'VarParser.VarParseTokenType',
                token_string
        ):
            self.start_ind = start_ind
            self.end_ind = end_ind
            self.token_list_ind = token_list_ind
            self.token_type = token_type
            self.token_string = token_string

        def consume(self, parser):
            parser.counter += 1
            if parser.counter < len(parser.token_list):
                parser.token_list[parser.counter].handle(parser)

    #Anything in the line that is not a reserved character or is not
    #an instance of said character in a syntactically correct orientation.
    class VarCharStringToken(Token):
        def __init__(self, start_ind, end_ind, token_list_ind, char_string):
            super().__init__(start_ind, end_ind, token_list_ind, VarParser.VarParseTokenType.VAR_CHAR_STRING, char_string)

        def handle(self, parser):
            self.consume(parser)

    #Language character: '$'
    class VarBeginToken(Token):
        def __init__(self, start_ind, end_ind, token_list_ind):
            super().__init__(start_ind, end_ind, token_list_ind, VarParser.VarParseTokenType.VAR_BEGIN, '$')

        def handle(self, parser):
            have_open_brace = False
            if parser.counter + 1 == len(parser.token_list) or \
               not (parser.token_list[parser.counter + 1].token_type == VarParser.VarParseTokenType.VAR_ENV or\
                    parser.token_list[parser.counter + 1].token_type == VarParser.VarParseTokenType.VAR_OPEN_BRACE
            ):
                
                
                for i in range(self.end_ind + 1, len(parser.token_list)):
                    if parser.token_list[i].token_type == VarParser.VarParseTokenType.VAR_OPEN_BRACE:
                        have_open_brace
                        break

                if have_open_brace:
                    #throw syntax error:
                    raise VarParseError("Only ENV is allowed between '$' and '{'")

                else:
                    parser.token_list[self.token_list_ind] = VarParser.VarCharStringToken(
                        self.start_ind,
                        self.end_ind,
                        self.token_list_ind,
                        self.token_string
                    )
                    parser.token_list[self.token_list_ind].handle(parser)
                    return
            self.consume(parser)
    #Language character: '{'        
    class VarOpenBraceToken(Token):
        def __init__(self, start_ind, end_ind, token_list_ind):
            super().__init__(start_ind, end_ind, token_list_ind, VarParser.VarParseTokenType.VAR_OPEN_BRACE, '{')
            self.env_var = False

        def handle(self, parser):
            close_brace_found = False
            #Look for associated close brace:
            if parser.counter == 0 or \
               not (parser.token_list[parser.counter - 1].token_type == VarParser.VarParseTokenType.VAR_BEGIN or\
                    parser.token_list[parser.counter - 1].token_type == VarParser.VarParseTokenType.VAR_ENV
            ):
                parser.token_list[self.token_list_ind] = VarParser.VarCharStringToken(
                    self.start_ind,
                    self.end_ind,
                    self.token_list_ind,
                    self.token_string
                )
                parser.token_list[self.token_list_ind].handle(parser)
                return

           #Bug: Does not handle nested vars: 
            open_brace_stack_counter= []
            for i in range(self.end_ind + 1, len(parser.token_list)):
                token = parser.token_list[i]
                if token.token_type == VarParser.VarParseTokenType.VAR_OPEN_BRACE and \
                   parser.token_list[i - 1].token_type == VarParser.VarParseTokenType.VAR_BEGIN:
                      #Hello:
                      open_brace_stack_counter += 1 
                if token.token_type == VarParser.VarParseTokenType.VAR_CLOSE_BRACE:
                   
                   if open_brace_stack_counter > 0:
                       pass 
                   else:
                       token.open_brace_ind = self.start_ind
                       token.env_var = self.env_var
                       close_brace_found = True
            
            if not close_brace_found:
                raise VarParseError("Unterminated variable expansion: An '{' is missing its '}'")

            self.consume(parser)

    #Language reserved character string: "ENV" 
    class VarEnvToken(Token):
        def __init__(self, start_ind, end_ind, token_list_ind):
            super().__init__(start_ind, end_ind, token_list_ind, VarParser.VarParseTokenType.VAR_ENV, "ENV")
        
        def handle(self, parser):
            token = parser.token_list[parser.counter]
            if token.token_type != VarParser.VarParseTokenType.VAR_ENV:
                return False
        
            if parser.counter == 0 or \
               parser.token_list[parser.counter - 1].token_type != VarParser.VarParseTokenType.VAR_BEGIN or\
               parser.counter + 1 == len(parser.token_list) or\
               parser.token_list[parser.counter + 1].token_type != VarParser.VarParseTokenType.VAR_OPEN_BRACE:
                #Convert to char string:
                parser.token_list[self.token_list_ind] = VarParser.VarCharStringToken(
                    self.start_ind, self.end_ind, self.token_list_ind, self.token_string) 
                parser.token_list[self.token_list_ind].handle(parser)
                return
            
            parser.token_list[self.counter + 1].env_var= True
            self.consume(parser)

    #Language character: '}' 
    class VarCloseBraceToken(Token):
        def __init__(self, start_ind, end_ind, token_list_ind):
            super().__init__(start_ind, end_ind, token_list_ind, VarParser.VarParseTokenType.VAR_CLOSE_BRACE, '}')
            self.env_var = False
            self.open_brace_ind = None
            self.spent = False

        def handle(self, parser):
            if self.spent:
                return self.consume(parser)
            temp_token = None
            temp_ind = None
            var_name = None
            var_retval = None
            #This handles all cases where this token was not preceded by an open brace:
            if self.open_brace_ind is None:
                parser.token_list[self.token_list_ind] = VarParser.VarCharStringToken(
                    self.start_ind,
                    self.end_ind,
                    self.token_list_ind,
                    self.token_string
                )
                parser.token_list[self.token_list_ind].handle(parser)
                return
            
            #Hello:
            var_name = ''
            temp_ind = parser.counter - 1
            temp_token = parser.token_list[temp_ind]

            while temp_token.token_type != VarParser.VarParseTokenType.VAR_CHAR_STRING:
                if temp_token.token_type != VarParser.VarParseTokenType.VAR_CLOSE_BRACE and \
                   not temp_token.spent:
                   raise VarParseError("Encountered unprocessed close bracket while resolving this one.")
                temp_ind = -1
                temp_token = parser.token_list[temp_ind]

            var_retval = parser.resolve_var(var_name, self.env_var)
            
            #Trace back to VAR_BEGIN:
            temp_ind = self.open_brace_ind - 1

            parser.token_list[temp_ind] = VarParser.VarCharStringToken(
                temp_token.start_ind,
                temp_token.end_ind + len(var_retval),
                temp_token.token_list_ind,
                var_retval
            )
            parser.counter = temp_ind
            self.spent = True
            return parser.token_list[temp_ind].handle(parser)

    def resolve_var(self, var_name, is_env=False):
        self.context.resolve_var()
    
    def reset(self):
        self.token_list.clear()
        self.token_list = None
        self.resolved_string = None
        self.counter = 0



    def var_parse_peek(self, string, start_ind, count):
        retval=[]
        if count < 0:
            raise ValueError("\"count\" cannot be negative")
        for i in range(start_ind, start_ind + count):
            retval.append(string[i])
        return "".join(retval)

    def get_token_stack(self, string):
        retval_tokens = []
        temp_arr=[]
        temp_ind = 0
        counter = 0
        while counter < len(string):
            match(string[counter]):
                case '$':
                    if len(temp_arr) > 0:
                        retval_tokens.append(VarParser.Token(temp_ind, counter - 1, self.VarParseTokenType.VAR_CHAR_STRING, "".join(temp_arr)))
                        temp_arr.clear()
                    retval_tokens.append(VarParser.Token(counter, counter, self.VarParseTokenType.VAR_BEGIN, '$'))
                    temp_ind = counter + 1
                
                case '{':
                    if len(temp_arr) > 0:
                        retval_tokens.append(VarParser.Token(temp_ind, counter - 1, self.VarParseTokenType.VAR_CHAR_STRING, "".join(temp_arr)))
                        temp_arr.clear()
                    retval_tokens.append(VarParser.Token(counter, counter, self.VarParseTokenType.VAR_OPEN_BRACE, '{'))
                    temp_ind = counter + 1
                
                case '}':                   
                    if len(temp_arr) > 0:
                        retval_tokens.append(VarParser.Token(temp_ind, counter - 1, self.VarParseTokenType.VAR_CHAR_STRING, "".join(temp_arr)))
                        temp_arr.clear()
                    retval_tokens.append(VarParser.Token(counter, counter, self.VarParseTokenType.VAR_CLOSE_BRACE, '}'))
                    temp_ind = counter + 1
                
                case 'E': 
                    if(self.var_parse_peek(string, counter, 2) == 'ENV'):
                        if len(temp_arr) > 0:
                            retval_tokens.append(VarParser.Token(temp_ind, counter - 1, self.VarParseTokenType.VAR_CHAR_STRING, "".join(temp_arr)))
                            temp_arr.clear()
                        
                        retval_tokens.append(VarParser.Token(counter, counter + 2, self.VarParseTokenType.VAR_ENV, 'ENV'))
                        temp_ind = counter + 3
                        counter += 2
                    else: 
                        temp_arr.append('E')

                case _:
                    temp_arr.append(string[counter])
            counter += 1
        temp_arr.clear()
        retval_tokens.reverse()
        return retval_tokens


    def resolve_all_vars(self, string):
        retval_arr = None
        #[(start_ind, end_ind, token_type, token_string)]
        self.token_list = self.get_token_stack(string)
        self.counter = 0


        if not self.token_list[self.counter].handle():
            raise VarParseError(f"Unknown error occurred when parsing string: \"{string}\"")

        retval_arr = []
        for elem in self.token_list:
            if elem.token_type != VarParser.VarParseTokenType.VAR_CHAR_STRING and \
               elem.token_type != VarParser.VarParseTokenType.VAR_CLOSE_BRACE:
                raise development.exceptions.DevelopmentError("""
Somehow, we have a non char string token in the token list after parsing that is not
a spent close brace.""") 
            
            if elem.token_type == VarParser.VarParseTokenType.VAR_CLOSE_BRACE and\
               not elem.spent:
                raise development.exceptions.DevelopmentError("""We have an unspent close brace in the
token list after parsing.""")

            retval_arr.append(elem.token_string)

        return "".join(retval_arr)