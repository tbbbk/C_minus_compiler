from typing import Tuple, List, Dict
from utils.constant import GRAMMAR
import pdb
from Parsing import scan


def eliminate_left_recursion(grammar: dict) -> dict:
    new_grammar = {}
    
    for non_terminal in grammar:
        alpha = []  # 存储直接左递归的产生式部分
        beta = []   # 存储非左递归的产生式部分
        
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
    # 初始化每个非终结符的FIRST集为空集
    first_set = {non_terminal: set() for non_terminal in grammar}
    
    # 计算某个符号的FIRST集
    def first(symbol):
        if symbol not in grammar:  # 如果是终结符，返回它自己
            return {symbol}
        if len(first_set[symbol]) != 0:  # 如果FIRST集已经计算过，直接返回
            return first_set[symbol]

        for production in grammar[symbol]:
            for token in production:
                # pdb.set_trace()
                token_first_set = first(token)
                first_set[symbol].update(token_first_set - {'empty'})
                if 'empty' not in token_first_set:
                    break
            else:
                first_set[symbol].add('empty')
        return first_set[symbol]

    # 迭代直到FIRST集不再变化
    changed = True
    while changed:
        changed = False
        for non_terminal in grammar:
            original_size = len(first_set[non_terminal])
            first(non_terminal)
            # pdb.set_trace()
            if len(first_set[non_terminal]) > original_size:
                changed = True
                
    return first_set


def build_follow_set(grammar: dict, first_set: dict) -> dict:
    # 初始化每个非终结符的Follow集为空集
    follow_set = {non_terminal: set() for non_terminal in grammar}
    
    # 添加开始符号的Follow集
    start_symbol = next(iter(grammar))  # 假设第一个非终结符是开始符号
    follow_set[start_symbol].add('$')
    
    # 迭代直到Follow集不再变化
    changed = True
    while changed:
        changed = False
        for non_terminal in grammar:
            for production in grammar[non_terminal]:
                # 遍历产生式中的每个位置
                for i, symbol in enumerate(production):
                    if symbol not in grammar:
                        continue  # 当前符号是终结符，跳过
                    
                    # 当前符号后面有符号
                    if i + 1 < len(production):
                        next_symbol = production[i + 1]
                        if next_symbol in grammar:
                            # 将next_symbol的FIRST集（除去'empty'）添加到symbol的FOLLOW集中
                            original_follow = follow_set[symbol].copy()
                            follow_set[symbol].update(first_set[next_symbol] - {'empty'})
                            if 'empty' in first_set[next_symbol]:
                                follow_set[symbol].update(follow_set[non_terminal])
                            if follow_set[symbol] != original_follow:
                                changed = True
                        else:
                            # 下一个符号是终结符
                            original_follow = follow_set[symbol].copy()
                            follow_set[symbol].add(next_symbol)
                            if follow_set[symbol] != original_follow:
                                changed = True
                    else:
                        # 当前符号是产生式的最后一个符号，将non_terminal的FOLLOW集添加到symbol的FOLLOW集中
                        original_follow = follow_set[symbol].copy()
                        follow_set[symbol].update(follow_set[non_terminal])
                        if follow_set[symbol] != original_follow:
                            changed = True

    return follow_set


def build_ll1_table(grammar: dict, first_set: dict, follow_set: dict) -> dict:
    # 确保所有终结符都在 first_set 中，并且它们的 FIRST 集是它们自身
    for non_terminal in grammar:
        for production in grammar[non_terminal]:
            for symbol in production:
                if symbol not in grammar and symbol not in first_set:
                    first_set[symbol] = {symbol}

    # 初始化分析表
    ll1_table = {non_terminal: {} for non_terminal in grammar}

    for non_terminal in grammar:
        for production in grammar[non_terminal]:
            # 对于每个产生式 A -> u
            first_u = set()
            
            # 计算 FIRST(u)
            for symbol in production:
                first_u.update(first_set[symbol] - {'empty'})
                if 'empty' not in first_set[symbol]:
                    break
            else:
                first_u.add('empty')

            # 对 FIRST(u) 中的每个终结符 a，设置 M[A, a] = "A -> u"
            for terminal in first_u:
                if terminal != 'empty':
                    ll1_table[non_terminal][terminal] = production

            # 如果 FIRST(u) 含有空串，则对 FOLLOW(A) 中的每个符号 a，设置 M[A, a] = "A -> u"
            if 'empty' in first_u:
                for terminal in follow_set[non_terminal]:
                    ll1_table[non_terminal][terminal] = production

    return ll1_table

def parse_ll1(tokens: List[Tuple[str, str]], ll1_table: Dict[str, Dict[str, List[str]]], start_symbol: str) -> bool:
    # 初始化栈，开始符号和结束符号
    stack = [start_symbol, '$']
    index = 0
    tokens.append(('$', '$'))  # 添加结束标志

    while len(stack) > 0:
        top = stack.pop()
        current_token, _ = tokens[index]
        pdb.set_trace()
        
        if top in ll1_table:  # 栈顶是非终结符
            if current_token in ll1_table[top]:
                production = ll1_table[top][current_token]
                if production != ['empty']:
                    stack.extend(reversed(production))
            else:
                print(f"Error: Unexpected token {current_token} for non-terminal {top}")
                return False
        elif top == current_token:  # 栈顶是终结符
            index += 1
        else:
            print(f"Error: Mismatch between stack top {top} and current token {current_token}")
            return False

    if stack:
        print("Error: Stack not empty at end of input")
        return False
    return True



def syntax_analysis(tokens: Tuple[str, str]):
    # grammar = GRAMMAR
    # grammar = eliminate_left_recursion(grammar=grammar)
    # first_set = build_first_set(grammar=grammar)
    # follow_set = build_follow_set(grammar=grammar, 
    #                               first_set=first_set)
    # analysis_table = build_ll1_table(grammar=grammar, 
    #                      first_set=first_set,
    #                      follow_set=follow_set)
    ll1_table = {
    'additive_expression': {'(': ['term', "additive_expression'"],
                            'IDENTIFIER': ['term', "additive_expression'"],
                            'INTEGER': ['term', "additive_expression'"]},
    "additive_expression'": {'!=': ['empty'],
                             ')': ['empty'],
                             '+': ['addop', 'term', "additive_expression'"],
                             ',': ['empty'],
                             '-': ['addop', 'term', "additive_expression'"],
                             ';': ['empty'],
                             '<': ['empty'],
                             '<=': ['empty'],
                             '==': ['empty'],
                             '>': ['empty'],
                             '>=': ['empty'],
                             ']': ['empty']},
    'addop': {'+': ['+'], '-': ['-']},
    'arg_list': {'(': ['expression', "arg_list'"],
                 'IDENTIFIER': ['expression', "arg_list'"],
                 'INTEGER': ['expression', "arg_list'"]},
    "arg_list'": {')': ['empty'], ',': [',', 'expression', "arg_list'"]},
    'args': {'(': ['arg_list'],
             ')': ['empty'],
             'IDENTIFIER': ['arg_list'],
             'INTEGER': ['arg_list']},
    'call': {'IDENTIFIER': ['IDENTIFIER', '(', 'args', ')']},
    'compound_stmt': {'{': ['{', 'local_declarations', 'statement_list', '}']},
    'declaration': {'R_INT': ['fun_declaration'], 'R_VOID': ['fun_declaration']},
    'declaration_list': {'R_INT': ['declaration', "declaration_list'"],
                         'R_VOID': ['declaration', "declaration_list'"]},
    "declaration_list'": {'$': ['empty'],
                          'R_INT': ['declaration', "declaration_list'"],
                          'R_VOID': ['declaration', "declaration_list'"]},
    'expression': {'(': ['simple_expression'],
                   'IDENTIFIER': ['simple_expression'],
                   'INTEGER': ['simple_expression']},
    'expression_stmt': {'(': ['expression', ';'],
                        ';': [';'],
                        'IDENTIFIER': ['expression', ';'],
                        'INTEGER': ['expression', ';']},
    'factor': {'(': ['(', 'expression', ')'], 'IDENTIFIER': ['call'], 'INTEGER': ['INTEGER']},
    'fun_declaration': {'R_INT': ['type_specifier',
                                  'IDENTIFIER',
                                  '(',
                                  'params',
                                  ')',
                                  'compound_stmt'],
                        'R_VOID': ['type_specifier',
                                   'IDENTIFIER',
                                   '(',
                                   'params',
                                   ')',
                                   'compound_stmt']},
    'iteration_stmt': {'R_WHILE': ['R_WHILE', '(', 'expression', ')', 'statement']},
    'local_declarations': {'$': ['empty', "local_declarations'"],
                           '(': ['empty', "local_declarations'"],
                           ';': ['empty', "local_declarations'"],
                           'IDENTIFIER': ['empty', "local_declarations'"],
                           'INTEGER': ['empty', "local_declarations'"],
                           'R_ELSE': ['empty', "local_declarations'"],
                           'R_IF': ['empty', "local_declarations'"],
                           'R_INT': ['empty', "local_declarations'"],
                           'R_RETURN': ['empty', "local_declarations'"],
                           'R_VOID': ['empty', "local_declarations'"],
                           'R_WHILE': ['empty', "local_declarations'"],
                           '{': ['empty', "local_declarations'"],
                           '}': ['empty', "local_declarations'"]},
    "local_declarations'": {'$': ['empty'],
                            '(': ['empty'],
                            ';': ['empty'],
                            'IDENTIFIER': ['empty'],
                            'INTEGER': ['empty'],
                            'R_ELSE': ['empty'],
                            'R_IF': ['empty'],
                            'R_INT': ['empty'],
                            'R_RETURN': ['empty'],
                            'R_VOID': ['empty'],
                            'R_WHILE': ['empty'],
                            '{': ['empty'],
                            '}': ['empty']},
    'mulop': {'*': ['*'], '/': ['/']},
    'param': {'R_INT': ['type_specifier', 'IDENTIFIER', '[', ']'],
              'R_VOID': ['type_specifier', 'IDENTIFIER', '[', ']']},
    'param_list': {'R_INT': ['param', "param_list'"],
                   'R_VOID': ['param', "param_list'"]},
    "param_list'": {')': ['empty'], ',': [',', 'param', "param_list'"]},
    'params': {'R_INT': ['param_list'], 'R_VOID': ['R_VOID']},
    'program': {'R_INT': ['declaration_list'], 'R_VOID': ['declaration_list']},
    'relop': {'!=': ['!='],
              '<': ['<'],
              '<=': ['<='],
              '==': ['=='],
              '>': ['>'],
              '>=': ['>=']},
    'return_stmt': {'R_RETURN': ['R_RETURN', 'expression', ';']},
    'selection_stmt': {'R_IF': ['R_IF',
                                '(',
                                'expression',
                                ')',
                                'statement',
                                'R_ELSE',
                                'statement']},
    'simple_expression': {'(': ['additive_expression'],
                          'IDENTIFIER': ['additive_expression'],
                          'INTEGER': ['additive_expression']},
    'statement': {'(': ['expression_stmt'],
                  ';': ['expression_stmt'],
                  'IDENTIFIER': ['expression_stmt'],
                  'INTEGER': ['expression_stmt'],
                  'R_IF': ['selection_stmt'],
                  'R_RETURN': ['return_stmt'],
                  'R_WHILE': ['iteration_stmt'],
                  '{': ['compound_stmt']},
    'statement_list': {'(': ['empty', "statement_list'"],
                       ';': ['empty', "statement_list'"],
                       'IDENTIFIER': ['empty', "statement_list'"],
                       'INTEGER': ['empty', "statement_list'"],
                       'R_IF': ['empty', "statement_list'"],
                       'R_RETURN': ['empty', "statement_list'"],
                       'R_WHILE': ['empty', "statement_list'"],
                       '{': ['empty', "statement_list'"],
                       '}': ['empty', "statement_list'"]},
    "statement_list'": {'(': ['statement', "statement_list'"],
                        ';': ['statement', "statement_list'"],
                        'IDENTIFIER': ['statement', "statement_list'"],
                        'INTEGER': ['statement', "statement_list'"],
                        'R_IF': ['statement', "statement_list'"],
                        'R_RETURN': ['statement', "statement_list'"],
                        'R_WHILE': ['statement', "statement_list'"],
                        '{': ['statement', "statement_list'"],
                        '}': ['empty']},
    'term': {'(': ['factor', "term'"],
             'IDENTIFIER': ['factor', "term'"],
             'INTEGER': ['factor', "term'"]},
    "term'": {'!=': ['empty'],
              ')': ['empty'],
              '+': ['empty'],
              ',': ['empty'],
              '-': ['empty'],
              '/': ['mulop', 'factor', "term'"],
              ';': ['empty'],
              '<': ['empty'],
              '<=': ['empty'],
              '==': ['empty'],
              '>': ['empty'],
              '>=': ['empty'],
              ']': ['empty']},
    'type_specifier': {'R_INT': ['R_INT'], 'R_VOID': ['R_VOID']},
    'var': {'IDENTIFIER': ['IDENTIFIER', '[', 'expression', ']']},
    'var_declaration': {'R_INT': ['type_specifier', 'IDENTIFIER', '[', 'INTEGER', ']', ';'],
                        'R_VOID': ['type_specifier', 'IDENTIFIER', '[', 'INTEGER', ']', ';']}
}

    parse_ll1(tokens, ll1_table, 'program')
    # pdb.set_trace()


if __name__ == '__main__':
    tokens = scan(file_path='src\\test_tokenizer\\sample_2', print=False)
    print(tokens)
    syntax_analysis(tokens)