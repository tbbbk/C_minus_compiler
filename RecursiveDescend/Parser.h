#ifndef CMINUS_PARSER_H
#define CMINUS_PARSER_H

#include <vector>
#include <memory>
#include <string>
#include "Lexer.h"

struct ASTNode {
    std::string value;
    std::vector<std::unique_ptr<ASTNode>> children;

    ASTNode(const std::string& value) : value(value) {}
};

class Parser {
public:
    Parser(const std::vector<Token>& tokens);
    std::unique_ptr<ASTNode> parse();

private:
    const std::vector<Token>& tokens;
    size_t currentTokenIndex;

    bool match(TokenType type, const std::string& value = "");
    const Token& consume();
    const Token& peek() const;

    std::unique_ptr<ASTNode> program();
    std::unique_ptr<ASTNode> declarationList();
    std::unique_ptr<ASTNode> declaration();
    std::unique_ptr<ASTNode> varDeclaration(std::unique_ptr<ASTNode> type, std::unique_ptr<ASTNode> id);
    std::unique_ptr<ASTNode> typeSpecifier();
    std::unique_ptr<ASTNode> funDeclaration(std::unique_ptr<ASTNode> type, std::unique_ptr<ASTNode> id);
    std::unique_ptr<ASTNode> params();
    std::unique_ptr<ASTNode> paramList();
    std::unique_ptr<ASTNode> param();
    std::unique_ptr<ASTNode> compoundStmt();
    std::unique_ptr<ASTNode> localDeclarations();
    std::unique_ptr<ASTNode> statementList();
    std::unique_ptr<ASTNode> statement();
    std::unique_ptr<ASTNode> expressionStmt();
    std::unique_ptr<ASTNode> selectionStmt();
    std::unique_ptr<ASTNode> iterationStmt();
    std::unique_ptr<ASTNode> returnStmt();
    std::unique_ptr<ASTNode> expression();
    std::unique_ptr<ASTNode> var();
    std::unique_ptr<ASTNode> simpleExpression();
    std::unique_ptr<ASTNode> additiveExpression();
    std::unique_ptr<ASTNode> term();
    std::unique_ptr<ASTNode> factor();
    std::unique_ptr<ASTNode> call();
    std::unique_ptr<ASTNode> args();
    std::unique_ptr<ASTNode> argList();
};


#endif //CMINUS_PARSER_H
