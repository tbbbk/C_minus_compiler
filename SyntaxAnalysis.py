from typing import Tuple
from utils.constant import GRAMMAR
import pdb


def eliminate_left_recursion(grammar: dict):
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


def build_first_set(grammar: dict):
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
            pdb.set_trace()
            if len(first_set[non_terminal]) > original_size:
                changed = True
                
    return first_set


def build_follow_set(grammar: dict):
    #TODO
    pass

def build_analysis_table(grammar: dict,
                         first_set: dict,
                         follow_set: dict):
    pass
    #TODO

def syntax_analysis(tokens: Tuple[str, str]):
    grammar = GRAMMAR
    grammar = eliminate_left_recursion(grammar=grammar)
    first_set = build_first_set(grammar=grammar)
    pdb.set_trace()
    build_follow_set()
    build_analysis_table()


if __name__ == '__main__':
    syntax_analysis(['s', 'b'])
    pass