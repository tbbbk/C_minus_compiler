from typing import Tuple, List, Dict
from utils.constant import GRAMMAR
import pdb
from Parsing import scan


def eliminate_left_recursion_and_factor(grammar: dict) -> dict:
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
    
    new_grammar = {}
    for non_terminal in grammar:
        """
        eliminate the left factors
        """
        left_factor = []
        for factor in zip(*grammar[non_terminal]):
            if len(set(factor)) == 1:
                left_factor.append(factor[0])
            else:
                break
        if len(left_factor) == 0 or len(grammar[non_terminal]) <= 1:
            new_grammar[non_terminal] = grammar[non_terminal]
        else:
            print(left_factor)
            new_non_terminal = non_terminal + "*"
            new_grammar[non_terminal] = [[left_factor] + [new_non_terminal]]
            new_production = []
            for production in grammar[non_terminal]:
                if len(left_factor) != len(production):
                    new_production.append(production[len(left_factor):])
            new_production.append(['empty'])
            new_grammar[new_non_terminal] = new_production

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


def build_follow_set(grammar: dict, first_set: dict, start_symbol: str) -> dict:
    follow_set = {non_terminal: set() for non_terminal in grammar}
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
                ll1_table: Dict[str, Dict[str, List]],
                grammar: dict,
                start_symbol: str) -> bool:
    stack = ['$', start_symbol]
    for token in tokens:
        while True:
            if token == stack[-1] and token == '$':
                print("Parse Successfully!!!")
                return True
            elif token == stack[-1] and token != '$':
                stack.pop()
                print(f'[Match] {token}')
                break
            elif token != stack[-1] and stack[-1] in grammar:
                if token in ll1_table[stack[-1]].keys():
                    print(f'[Predict] {stack[-1]} -> {ll1_table[stack[-1]][token]}')
                    stack_top = stack.pop()
                    stack += reversed(ll1_table[stack_top][token])
                    print('-[stack]', stack, '[token]', token)
                else:
                    print('[stack]', stack, '[token]', token)
                    print(f"[Failed] Undefined ll1_table key: {token}")
                    return False
            elif token != stack[-1] and stack[-1] not in grammar:
                print('-[stack]', stack, '[token]', token)
                print(f"[Failed] token is '{token}', but stack top is '{stack[-1]}'")
                return False


def syntax_analysis(tokens: Tuple[str, str]):
    grammar = GRAMMAR
    start_symbol = 'program'
    new_tokens = convert_tokens(tokens)
    grammar = eliminate_left_recursion_and_factor(grammar=grammar)
    # first_set = build_first_set(grammar=grammar)
    # follow_set = build_follow_set(grammar=grammar, 
    #                               first_set=first_set, 
    #                               start_symbol=start_symbol)
    # ll1_table = build_ll1_table(grammar=grammar, 
    #                             first_set=first_set, 
    #                             follow_set=follow_set)
    import json
    with open('grammar.json', 'w') as f:
        json.dump(grammar, f, indent=4)
    # with open('ll1_table.json', 'w') as f:
    #     json.dump(ll1_table, f, indent=4)
    # pdb.set_trace()
    # parse_ll1(tokens=new_tokens,
    #           ll1_table=ll1_table,
    #           grammar=grammar,
    #           start_symbol=start_symbol)


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

    return [token_map[token[0]] for token in tokens] + ['$']

if __name__ == '__main__':
    tokens = scan(file_path='src/test_tokenizer/sample_1', print=False)
    syntax_analysis(tokens)