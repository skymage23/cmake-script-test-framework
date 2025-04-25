import enum
import development.exceptions

class VarParseTokenType(enum.Enum):
    VAR_EXPANSION = enum.auto()
    VAR_ENV = enum.auto()
    VAR_OPEN_BRACE = enum.auto()
    VAR_CLOSE_BRACE = enum.auto()
    VAR_CHAR_STRING = enum.auto()
    VAR_STATEMENT_END = enum.auto()

    def __str__(self):
        match self:
            case VarParseTokenType.VAR_EXPANSION:
                return "$"
            case VarParseTokenType.VAR_ENV:
                return "ENV"
            case VarParseTokenType.VAR_OPEN_BRACE:
                return r"{"
            case VarParseTokenType.VAR_CLOSE_BRACE:
                return r"}"
            case VarParseTokenType.VAR_CHAR_STRING:
                return "CHAR_STRING"
            case _:
                raise development.exceptions.DevelopmentError(f"Unimplemented token type: {self}")
            

#Token Utility Functions:
def validate_token(token, token_type=None, string_value = None):
    """Validates basic token structure and types.
    
    Args:
        token: The token to validate
        index: Optional index for error messages
        
    Raises:
        DevelopmentError if token structure is invalid
    """
    if not isinstance(token, list):
        raise development.exceptions.DevelopmentError(
            f"Token {token} is not a tuple. "
            f"Expected {type(list)}, got {type(token)}"
        )
    
    if len(token) != 2:
        raise development.exceptions.DevelopmentError(
            f"Token {token} has wrong length. "
            f"Expected 2 elements, got {len(token)}"
        )
    
    if token[0] not in VarParseTokenType:
        raise development.exceptions.DevelopmentError(
            f"Token {token} has invalid type. "
            f"{token[0]} is not in {VarParseTokenType}"
        )
    
    if not isinstance(token[1], str):
        raise development.exceptions.DevelopmentError(
            f"Token {token} has invalid value type. "
            f"Expected {type(str)}, got {type(token[1])}"
        )
    
    if token_type is not None and token[0] != token_type:
        raise development.exceptions.DevelopmentError(
            f"Token {token} has wrong type. "
            f"Expected {token_type}, got {token[0]}"
        )
    if string_value is None and \
        token_type is not None and \
        token_type != VarParseTokenType.VAR_CHAR_STRING:
        string_value = str(token_type)
            
    if string_value is not None and \
        token_type != VarParseTokenType.VAR_CHAR_STRING and \
        token[1] != string_value:
        raise development.exceptions.DevelopmentError(
            f"Token {token} has wrong value. "
            f"Expected {string_value}, got {token[1]}"
        )