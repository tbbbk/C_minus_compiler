from utils.constant import KEYWORD
from utils.files import read_file
from utils.rules import KeyWord
import argparse
import re
from typing import List, Tuple


def get_regex_patterns(KeyWord: KeyWord) -> str:
    """
    Get regex patterns from KeyWord class
        
    Parameters:
    KeyWord (KeyWord): KeyWord class
    
    Returns:
    complie_re (re.Pattern): Compiled regex pattern
    """
    rules = []
    for key, value in vars(KeyWord).items():
        rules.append((key, value))
    regex_patterns = '|'.join('(?P<%s>%s)' % pair for pair in rules)
    complie_re = re.compile(regex_patterns)
    return complie_re


def tokenize(code: str, regex_patterns: re.Pattern, keyword_cls: type) -> List[Tuple[str, str]]:
    """
    Tokenize the code
        
    Parameters:
    code (str): Code to be tokenized
    
    Returns:
    tokens (List[Tuple[str, str]]): List of tokens
    """
    tokens = []
    last_pos = 0
    for match in regex_patterns.finditer(code):
        if match.start() != last_pos:
            unmatched_value = repr(code[last_pos:match.start()])
            tokens.append(('ERROR', unmatched_value))
        kind = match.lastgroup
        value = match.group()
        last_pos = match.end()
        if kind in keyword_cls.get_ignore_tokens():
            continue
        tokens.append((kind, repr(value)))
    return tokens


def print_tokens(tokens: List[Tuple[str, str]]) -> None:
    """
    Print result tokens
    
    Parameters:
    tokens (List[Tuple[str, str]]): List of tokens
    
    Returns:
    None
    """
    print(f"{'TOKEN-TYPE':<12}", f"{'|':^3}", f"{'TOKEN-VALUE':<15}")
    print(f"{'-'*33:^33}")
    for type, value in tokens:
        print(f"{type:<12}", f"{'|':^3}", f"{value:<15}")


def scan(file_path: str) -> List[Tuple[str, str]]:
    """
    Scan and tokenize the file
    
    Parameters:
    file_path (str): File path to be scanned
    
    Returns:
    tokens (List[Tuple[str, str]]): List of tokens
    """
    file = read_file(file_path)
    regex_patterns = get_regex_patterns(KEYWORD)
    tokens = tokenize(file, regex_patterns, type(KEYWORD))
    print_tokens(tokens)
    return tokens


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scanner")
    parser.add_argument('--file_path', type=str, help='File to be scanned')
    scan(parser.parse_args().file_path)