from typing import Tuple, List, Dict
from utils.constant import GRAMMAR
import pdb
from Parsing import scan


def eliminate_left_recursion(grammar: dict) -> dict:
    new_grammar = {}
    
    for non_terminal in grammar:
        """
        P  -> Pα|β
        P  -> βP'
        P' -> αP'|empty
        """
        alpha = []  # store the α
        beta = []   # store the β
        
        for production in grammar[non_terminal]:
            if production[0] == non_terminal:
                alpha.append(production[1:])
            else:
                beta.append(production)
        
        if alpha:
            new_non_terminal = non_terminal + "'"
            new_grammar[non_terminal] = []
            new_grammar[new_non_terminal] = []
            for b in beta:
                new_grammar[non_terminal].append(b + [new_non_terminal])
            for a in alpha:
                new_grammar[new_non_terminal].append(a + [new_non_terminal])
            new_grammar[new_non_terminal].append(['empty'])
        else:
            new_grammar[non_terminal] = grammar[non_terminal]
    
    return new_grammar


def build_first_set(grammar: dict) -> dict:
    first_set = {non_terminal: set() for non_terminal in grammar}
    
    def first(symbol):
        if symbol not in grammar:
            return {symbol}
        if len(first_set[symbol]) != 0:
            return first_set[symbol]

        for production in grammar[symbol]:
            for token in production:
                token_first_set = first(token)
                first_set[symbol].update(token_first_set - {'empty'})
                if 'empty' not in token_first_set:
                    break
            else:
                first_set[symbol].add('empty')
        return first_set[symbol]

    changed = True
    while changed:
        changed = False
        for non_terminal in grammar:
            original_size = len(first_set[non_terminal])
            first(non_terminal)
            if len(first_set[non_terminal]) > original_size:
                changed = True
                
    return first_set


def build_follow_set(grammar: dict, first_set: dict) -> dict:
    follow_set = {non_terminal: set() for non_terminal in grammar}

    # Add first symbol follow set '$'
    start_symbol = next(iter(grammar))  
    follow_set[start_symbol].add('$')
    
    changed = True
    while changed:
        changed = False
        for non_terminal in grammar:
            for production in grammar[non_terminal]:
                for i, symbol in enumerate(production):
                    if symbol not in grammar:
                        continue
                    if i + 1 < len(production):
                        next_symbol = production[i + 1]
                        if next_symbol in grammar:
                            original_follow = follow_set[symbol].copy()
                            follow_set[symbol].update(first_set[next_symbol] - {'empty'})
                            if 'empty' in first_set[next_symbol]:
                                follow_set[symbol].update(follow_set[non_terminal])
                            if follow_set[symbol] != original_follow:
                                changed = True
                        else:
                            original_follow = follow_set[symbol].copy()
                            follow_set[symbol].add(next_symbol)
                            if follow_set[symbol] != original_follow:
                                changed = True
                    else:
                        original_follow = follow_set[symbol].copy()
                        follow_set[symbol].update(follow_set[non_terminal])
                        if follow_set[symbol] != original_follow:
                            changed = True

    return follow_set


def build_ll1_table(grammar: dict, first_set: dict, follow_set: dict) -> dict:
    ll1_table = {non_terminal: {} for non_terminal in grammar}
    
    for non_terminal in grammar:
        for production in grammar[non_terminal]:
            first_value = [production[0]] if production[0] not in first_set else first_set[production[0]]
            if first_value != ['empty']:
                for a in first_value:
                    ll1_table[non_terminal].update({a: production})
            if first_value == ['empty'] or 'empty' in first_value:
                for a in follow_set[non_terminal]:
                    ll1_table[non_terminal].update({a: production})
    return ll1_table


def parse_ll1(tokens: List[Tuple[str, str]],
               ll1_table: Dict[str, Dict[str, Dict[str, List[str]]]], start_symbol: str) -> bool:
    pass


def syntax_analysis(tokens: Tuple[str, str]):
    grammar = GRAMMAR
    grammar = eliminate_left_recursion(grammar=grammar)
    first_set = build_first_set(grammar=grammar)
    follow_set = build_follow_set(grammar=grammar, first_set=first_set)
    analysis_table = build_ll1_table(grammar=grammar, first_set=first_set, follow_set=follow_set)
    pdb.set_trace()
    # parse_ll1(tokens, ll1_table, 'program')


def convert_tokens(tokens: List[str]) -> List[str]:
    token_map = {
        'R_IF': 'if',
        'R_ELSE': 'else',
        'R_INT': 'int', 
        'R_RETURN': 'return',
        'R_VOID': 'void',
        'R_WHILE': 'while',
        'S_ADD': '+',
        'S_SUB': '-',
        'S_MUL': '*',
        'S_DIV': '/',
        'S_LT': '<',
        'S_LE': '<=',
        'S_GT': '>',
        'S_GE': '>=',
        'S_EQ': '==',
        'S_NE': '!=',
        'S_ASSIGN': '=',
        'S_SEMICOLON': ';',
        'S_COMMA': ',',
        'S_LPAREN': '(',
        'S_RPAREN': ')',
        'S_LBRACKET': '{',
        'S_RBRACKET': '}',
        'S_LBRACE': '[',
        'S_RBRACE': ']',
        'IDENTIFIER': 'ID',
        'INTEGER': 'NUM'
    }

    return [token_map[token[0]] for token in tokens] 

if __name__ == '__main__':
    tokens = scan(file_path='src/test_tokenizer/sample_1', print=False)
    new_tokens = convert_tokens(tokens)
    syntax_analysis(tokens)