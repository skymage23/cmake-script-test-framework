
import development.exceptions
from . import var_expansion_tokens
class VarExpansionTokenList:
    class TokenListIterator:
        def __init__(self, token_list, index = 0):
            self.token_list = token_list
            self.index = index

        def __next__(self):
            if self.index >= len(self.token_list):
                raise StopIteration
            token = self.token_list[self.index]
            self.index += 1
            return token

        def __iter__(self):
            return self
        
    def __init__(self, string):
        self.token_list_ind = 0
        self.token_list_end = False
        self.var_expansion_nest_stack = []
        self.token_list = self.get_token_list(string)

    def get_token_list(self,string):
        if not isinstance(string, str):
            raise development.exceptions.DevelopmentError("Input string must be a string")
        
        if string is None:
            raise development.exceptions.DevelopmentError("Input string cannot be None")
        
        retval_tokens = []
        temp_arr=[]
        counter = 0
        token_list_ind = 0
        while counter < len(string):
            match(string[counter]):
                case '$':
                    if len(temp_arr) > 0:
                        retval_tokens.append([var_expansion_tokens.VarParseTokenType.VAR_CHAR_STRING, "".join(temp_arr)])
                        temp_arr.clear()
                        token_list_ind += 1
                    retval_tokens.append([var_expansion_tokens.VarParseTokenType.VAR_EXPANSION, '$'])
                    token_list_ind += 1
                
                case '{':
                    if len(temp_arr) > 0:
                        retval_tokens.append([var_expansion_tokens.VarParseTokenType.VAR_CHAR_STRING, "".join(temp_arr)])
                        temp_arr.clear()
                        token_list_ind += 1
                    retval_tokens.append([var_expansion_tokens.VarParseTokenType.VAR_OPEN_BRACE, '{'])
                    token_list_ind += 1
                
                case '}':                   
                    if len(temp_arr) > 0:
                        retval_tokens.append([var_expansion_tokens.VarParseTokenType.VAR_CHAR_STRING, "".join(temp_arr)])
                        temp_arr.clear()
                        token_list_ind += 1
                    retval_tokens.append([var_expansion_tokens.VarParseTokenType.VAR_CLOSE_BRACE,'}'])
                    token_list_ind += 1
                case 'E':
                    if(string[counter : counter + 3] == 'ENV'):
                        if len(temp_arr) > 0:
                            retval_tokens.append([var_expansion_tokens.VarParseTokenType.VAR_CHAR_STRING, "".join(temp_arr)])
                            temp_arr.clear()
                            token_list_ind += 1
                        retval_tokens.append([var_expansion_tokens.VarParseTokenType.VAR_ENV, 'ENV'])
                        counter += 2
                        token_list_ind += 1
                    else: 
                        temp_arr.append('E')
                case _:
                    temp_arr.append(string[counter])
            counter += 1

        if len(temp_arr) > 0:
            retval_tokens.append([var_expansion_tokens.VarParseTokenType.VAR_CHAR_STRING, "".join(temp_arr)])
            temp_arr.clear() 
        return retval_tokens

    def __iter__(self):
        return self.TokenListIterator(self.token_list)    

    def iterate_from_current_node(self):
        return self.TokenListIterator(self.token_list, self.token_list_ind)

    def get_current_token(self):
        retval = None
        if self.token_list_ind < 0:
            raise development.exceptions.DevelopmentError(
                "Token list index is negative. It should NEVER be negative."
            )
    
        if self.token_list_ind >= len(self.token_list):
            raise development.exceptions.DevelopmentError(
                "Tried to retrieve token past the end of the token list"
            )
        
        retval = self.token_list[self.token_list_ind]
        var_expansion_tokens.validate_token(retval)
        return retval
    
    def consume_token(self):
        if self.token_list_ind < 0:
            raise development.exceptions.DevelopmentError(
                "Token list index is negative. It should NEVER be negative."
            )

        self.token_list_ind += 1
        if self.token_list_ind >= len(self.token_list):
            self.token_list_end = True
    
    def peek_token(self, lookahead_count):
        if self.is_token_list_fully_iterated():
            raise development.exceptions.DevelopmentError(
                "Token list is fully iterated. Why are we still trying to parse?"
            )

        if (lookahead_count < 0):
            raise development.exceptions.DevelopmentError(
                "Lookahead count cannot be negative"
            )
    
        if self.token_list_ind + lookahead_count >= len(self.token_list):
            raise development.exceptions.DevelopmentError(
                "Peeked past the end of the token list"
            )
       
        token = self.get_token(self.token_list_ind + lookahead_count)
        var_expansion_tokens.validate_token(token)
        
        return token
        
    
    def get_token(self, index):
        if self.is_token_list_fully_iterated():
            raise development.exceptions.DevelopmentError(
                "Token list is fully iterated. Why are we still trying to parse?"
            )
        
        if index < 0:
            raise development.exceptions.DevelopmentError(
                "Index is negative. It should NEVER be negative."
            )
        
        if index >= len(self.token_list):
            raise development.exceptions.DevelopmentError(
                "Index is greater than the length of the token list"
            )
    
        token = self.token_list[index]
        var_expansion_tokens.validate_token(token)
        return token
         
    def get_index_by_token_ref(self, token_ref):
        #Throw an error if the token reference is not a valid token:
        var_expansion_tokens.validate_token(token_ref)
        
        for index, token in enumerate(self.token_list):
            if token == token_ref:
                return index
        return -1
        
         
    def is_token_list_fully_iterated(self):
        return self.token_list_end  