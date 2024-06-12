#ifndef CMINUS_LEXER_H
#define CMINUS_LEXER_H

#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>

// TokenType 枚举类型
enum TokenType {
    KEYWORD, SYMBOL, ID, NUM, COMMENT, WHITESPACE, UNKNOWN
};

// Token 结构体
struct Token {
    TokenType type;
    std::string value;
    int lineNumber;

    Token(TokenType type, std::string value, int lineNumber) : type(type), value(value), lineNumber(lineNumber) {}
};



// 关键字列表
extern const std::vector<std::string> keywords;

// 符号映射表
extern const std::unordered_map<std::string, TokenType> symbols;

// 函数声明
bool isKeyword(const std::string& str);
bool isLetter(char ch);
bool isDigit(char ch);
std::vector<Token> lexer(const std::string& input);
void printTokens(const std::vector<Token>& tokens);

#endif //CMINUS_LEXER_H
