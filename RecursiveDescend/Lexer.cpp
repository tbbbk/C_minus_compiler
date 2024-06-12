#include "Lexer.h"
#include <algorithm>
#include <cctype>

// 关键字列表
const std::vector<std::string> keywords = {
        "if", "else", "int", "return", "void", "while"
};

// 符号映射表
const std::unordered_map<std::string, TokenType> symbols = {
        {"+", SYMBOL}, {"-", SYMBOL}, {"*", SYMBOL}, {"/", SYMBOL}, {"<", SYMBOL}, {"<=", SYMBOL},
        {">", SYMBOL}, {">=", SYMBOL}, {"==", SYMBOL}, {"!=", SYMBOL}, {"=", SYMBOL},
        {";", SYMBOL}, {",", SYMBOL}, {"(", SYMBOL}, {")", SYMBOL}, {"[", SYMBOL}, {"]", SYMBOL},
        {"{", SYMBOL}, {"}", SYMBOL}, {"/*", COMMENT}, {"*/", COMMENT}
};


bool isLetter(char c) {
    return std::isalpha(c);
}

bool isDigit(char c) {
    return std::isdigit(c);
}

bool isKeyword(const std::string& str) {
    return std::find(keywords.begin(), keywords.end(), str) != keywords.end();
}

// 词法分析器
std::vector<Token> lexer(const std::string& input) {
    std::vector<Token> tokens;
    size_t i = 0;
    int currentLine = 1;

    while (i < input.length()) {
        if (std::isspace(input[i])) {
            if (input[i] == '\n') {
                currentLine++;
            }
            i++; // 跳过空格
            continue;
        }

        if (isLetter(input[i])) {
            size_t start = i;
            while (i < input.length() && (isLetter(input[i]) || isDigit(input[i]))) {
                i++;
            }
            std::string value = input.substr(start, i - start);
            if (isKeyword(value)) {
                tokens.emplace_back(KEYWORD, value, currentLine);
            } else {
                tokens.emplace_back(ID, value, currentLine);
            }
        }
        else if (isDigit(input[i])) {
            size_t start = i;
            while (i < input.length() && isDigit(input[i])) {
                i++;
            }
            tokens.emplace_back(NUM, input.substr(start, i - start), currentLine);
        }
        else if (input[i] == '/' && i + 1 < input.length() && input[i + 1] == '*') {
            i += 2; // 跳过 /* 注释开始
            while (i + 1 < input.length() && !(input[i] == '*' && input[i + 1] == '/')) {
                if (input[i] == '\n') {
                    currentLine++;
                }
                i++;
            }
            i += 2; // 跳过 */ 注释结束
        }
        else {
            bool matched = false;
            for (const auto& sym : symbols) {
                size_t len = sym.first.length();
                if (input.substr(i, len) == sym.first) {
                    tokens.emplace_back(sym.second, sym.first, currentLine);
                    i += len;
                    matched = true;
                    break;
                }
            }
            if (!matched) {
                tokens.emplace_back(UNKNOWN, std::string(1, input[i]), currentLine);
                i++;
            }
        }
    }

    return tokens;
}

// 打印 Token
void printTokens(const std::vector<Token>& tokens) {
    for (const auto& token : tokens) {
        std::string type;
        switch (token.type) {
            case KEYWORD: type = "KEYWORD"; break;
            case SYMBOL: type = "SYMBOL"; break;
            case ID: type = "ID"; break;
            case NUM: type = "NUM"; break;
            case COMMENT: type = "COMMENT"; break;
            case WHITESPACE: type = "WHITESPACE"; break;
            default: type = "UNKNOWN"; break;
        }
        std::cout << "Token("<<"Line: "<<token.lineNumber<<", "<<"Type: " << type << ", Value: \"" << token.value << "\")\n";
    }
}
