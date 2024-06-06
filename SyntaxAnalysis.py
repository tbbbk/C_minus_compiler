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
            # pdb.set_trace()
            if len(first_set[non_terminal]) > original_size:
                changed = True
                
    return first_set


def build_follow_set(grammar: dict, first_set: dict):
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




def build_analysis_table(grammar: dict,
                         first_set: dict,
                         follow_set: dict):
    pass
    #TODO

def syntax_analysis(tokens: Tuple[str, str]):
    grammar = GRAMMAR
    grammar = eliminate_left_recursion(grammar=grammar)
    first_set = build_first_set(grammar=grammar)
    follow_set = build_follow_set(grammar=grammar, 
                                  first_set=first_set)
    pdb.set_trace()
    build_analysis_table()


if __name__ == '__main__':
    syntax_analysis(['s', 'b'])
    pass