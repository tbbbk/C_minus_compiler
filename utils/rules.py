from dataclasses import dataclass


@dataclass(frozen=True)
class KeyWord():
    R_IF: str = r"\bif\b"
    R_ELSE: str = r"\belse\b"
    R_INT: str = r"\bint\b"
    R_RETURN: str = r"\breturn\b"
    R_VOID: str = r"\bvoid\b"
    R_WHILE: str = r"\bwhile\b"

    S_LMARK: str = r"\/\*"
    S_RMARK: str = r"\*\/"
    
    S_ADD: str = r"\+"
    S_SUB: str = r"\-"
    S_MUL: str = r"\*"
    S_DIV: str = r"\/"
    S_LT: str = r"\<"
    S_LE: str = r"\<="
    S_GT: str = r"\>"
    S_GE: str = r"\>="
    S_EQ: str = r"=="
    S_NE: str = r"!="
    S_ASSIGN: str = r"="
    S_SEMICOLON: str = r";"
    S_COMMA: str = r","
    S_LPAREN: str = r"\("
    S_RPAREN: str = r"\)"
    S_LBRACKET: str = r"\{"
    S_RBRACKET: str = r"\}"
    S_LBRACE: str = r"\["
    S_RBRACE: str = r"\]"
    S_SPACE: str = r" "
    S_TAB: str = r"\t"
    S_NEWLINE: str = r"\n"

    INTEGER: str = r'\b[0-9]+\b'
    IDENTIFIER: str = r'\b[_a-zA-Z][_a-zA-Z0-9]*\b'
    
    @classmethod
    def get_ignore_tokens(self):
        return ['S_SPACE', 'S_TAB', 'S_NEWLINE']
