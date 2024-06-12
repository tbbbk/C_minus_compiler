#include "Parser.h"

Parser::Parser(const std::vector<Token>& tokens) : tokens(tokens), currentTokenIndex(0) {}

bool Parser::match(TokenType type, const std::string& value) {
    if (currentTokenIndex < tokens.size() && tokens[currentTokenIndex].type == type &&
        (value.empty() || tokens[currentTokenIndex].value == value)) {
        return true;
    }
    return false;
}

const Token& Parser::consume() {
    return tokens[currentTokenIndex++];
}

const Token& Parser::peek() const {
    return tokens[currentTokenIndex];
}

std::unique_ptr<ASTNode> Parser::parse() {
    return program();
}

std::unique_ptr<ASTNode> Parser::program() {
    auto node = std::make_unique<ASTNode>("program");
    node->children.push_back(declarationList());
    return node;
}

std::unique_ptr<ASTNode> Parser::declarationList() {
    auto node = std::make_unique<ASTNode>("declaration-list");
    while (match(KEYWORD, "int") || match(KEYWORD, "void")) {
        node->children.push_back(declaration());
    }
    if (tokens[currentTokenIndex-1].lineNumber != tokens.back().lineNumber){
        std::cerr << "Error in "<< tokens[currentTokenIndex].lineNumber << std::endl;
        return nullptr;
    }
    return node;
}

std::unique_ptr<ASTNode> Parser::declaration() {
    if (match(KEYWORD, "int") || match(KEYWORD, "void")) {
        auto type = typeSpecifier();
        if (match(ID)) {
            auto id = std::make_unique<ASTNode>(consume().value);
            if (match(SYMBOL, "(")) {
                return funDeclaration(std::move(type), std::move(id));
            } else {
                return varDeclaration(std::move(type), std::move(id));
            }
        }
    }
    std::cerr << "Error in "<< peek().lineNumber << std::endl;
    return nullptr; // Error
}

std::unique_ptr<ASTNode> Parser::varDeclaration(std::unique_ptr<ASTNode> type, std::unique_ptr<ASTNode> id) {
    if (match(SYMBOL, "[")) {
        consume(); // consume [
        if (match(NUM)) {
            auto num = std::make_unique<ASTNode>(consume().value);
            if (match(SYMBOL, "]")) {
                consume(); // consume ]
                if (match(SYMBOL, ";")) {
                    consume(); // consume ;
                    auto node = std::make_unique<ASTNode>("var-declaration");
                    node->children.push_back(std::move(type));
                    node->children.push_back(std::move(id));
                    node->children.push_back(std::move(num));
                    return node;
                }
            }
        }
    } else if (match(SYMBOL, ";")) {
        consume(); // consume ;
        auto node = std::make_unique<ASTNode>("var-declaration");
        node->children.push_back(std::move(type));
        node->children.push_back(std::move(id));
        return node;
    }
    std::cerr << "Error in "<< peek().lineNumber << std::endl;
    return nullptr; // Error
}

std::unique_ptr<ASTNode> Parser::typeSpecifier() {
    if (match(KEYWORD, "int") || match(KEYWORD, "void")) {
        return std::make_unique<ASTNode>(consume().value);
    }
    std::cerr << "Error in "<< peek().lineNumber << std::endl;
    return nullptr; // Error
}

std::unique_ptr<ASTNode> Parser::funDeclaration(std::unique_ptr<ASTNode> type, std::unique_ptr<ASTNode> id) {
    if (match(SYMBOL, "(")) {
        consume(); // consume (
        auto paramsNode = params();
        if (match(SYMBOL, ")")) {
            consume(); // consume )
            auto compoundStmtNode = compoundStmt();
            auto node = std::make_unique<ASTNode>("fun-declaration");
            node->children.push_back(std::move(type));
            node->children.push_back(std::move(id));
            node->children.push_back(std::move(paramsNode));
            node->children.push_back(std::move(compoundStmtNode));
            return node;
        }
    }
    std::cerr << "Error in "<< peek().lineNumber << std::endl;
    return nullptr; // Error
}

std::unique_ptr<ASTNode> Parser::params() {
    if (match(KEYWORD, "void")) {
        consume(); // consume void
        return std::make_unique<ASTNode>("params");
    } else {
        return paramList();
    }
}

std::unique_ptr<ASTNode> Parser::paramList() {
    auto node = std::make_unique<ASTNode>("param-list");
    node->children.push_back(param());
    while (match(SYMBOL, ",")) {
        consume(); // consume ,
        node->children.push_back(param());
    }
    return node;
}

std::unique_ptr<ASTNode> Parser::param() {
    auto type = typeSpecifier();
    if (match(ID)) {
        auto id = std::make_unique<ASTNode>(consume().value); // consume ID
        if (match(SYMBOL, "[")) {
            consume(); // consume [
            if (match(SYMBOL, "]")) {
                consume(); // consume ]
                auto node = std::make_unique<ASTNode>("param");
                node->children.push_back(std::move(type));
                node->children.push_back(std::move(id));
                return node;
            }
        } else {
            auto node = std::make_unique<ASTNode>("param");
            node->children.push_back(std::move(type));
            node->children.push_back(std::move(id));
            return node;
        }
    }
    std::cerr << "Error in "<< peek().lineNumber << std::endl;
    return nullptr; // Error
}

std::unique_ptr<ASTNode> Parser::compoundStmt() {
    if (match(SYMBOL, "{")) {
        consume(); // consume {
        auto localDeclarationsNode = localDeclarations();
        auto statementListNode = statementList();
        if (match(SYMBOL, "}")) {
            consume(); // consume }
            auto node = std::make_unique<ASTNode>("compound-stmt");
            node->children.push_back(std::move(localDeclarationsNode));
            node->children.push_back(std::move(statementListNode));
            return node;
        }
    }
    std::cerr << "Error in "<< peek().lineNumber << std::endl;
    return nullptr; // Error
}

std::unique_ptr<ASTNode> Parser::localDeclarations() {
    auto node = std::make_unique<ASTNode>("local-declarations");
    while (match(KEYWORD, "int") || match(KEYWORD, "void")) {
        auto type = typeSpecifier();
        auto id = std::make_unique<ASTNode>(consume().value);
        node->children.push_back(varDeclaration(std::move(type), std::move(id)));
    }
    return node;
}

std::unique_ptr<ASTNode> Parser::statementList() {
    auto node = std::make_unique<ASTNode>("statement-list");
    while (true) {
        auto stmt = statement();
        if (stmt) {
            node->children.push_back(std::move(stmt));
        } else {
            break;
        }
    }
    return node;
}

std::unique_ptr<ASTNode> Parser::statement() {
    if (match(SYMBOL, ";") || match(ID) || match(NUM) || match(SYMBOL, "(")) {
        return expressionStmt();
    } else if (match(SYMBOL, "{")) {
        return compoundStmt();
    } else if (match(KEYWORD, "if")) {
        return selectionStmt();
    } else if (match(KEYWORD, "while")) {
        return iterationStmt();
    } else if (match(KEYWORD, "return")) {
        return returnStmt();
    } else if (match(SYMBOL, "}")){
        return nullptr;
    }
    std::cerr << "Error in "<< peek().lineNumber << std::endl;
    return nullptr;
}

std::unique_ptr<ASTNode> Parser::expressionStmt() {
    auto node = std::make_unique<ASTNode>("expression-stmt");
    if (!match(SYMBOL, ";")) {
        node->children.push_back(expression());
    }
    if (match(SYMBOL, ";")) {
        consume(); // consume ;
        return node;
    }
    std::cerr << "Error in "<< peek().lineNumber << std::endl;
    return nullptr; // Error
}

std::unique_ptr<ASTNode> Parser::selectionStmt() {
    if (match(KEYWORD, "if")) {
        consume(); // consume if
        if (match(SYMBOL, "(")) {
            consume(); // consume (
            auto expr = expression();
            if (match(SYMBOL, ")")) {
                consume(); // consume )
                auto stmt = statement();
                auto node = std::make_unique<ASTNode>("selection-stmt");
                node->children.push_back(std::move(expr));
                node->children.push_back(std::move(stmt));
                if (match(KEYWORD, "else")) {
                    consume(); // consume else
                    node->children.push_back(statement());
                }
                return node;
            }
        }
    }
    std::cerr << "Error in "<< peek().lineNumber << std::endl;
    return nullptr; // Error
}

std::unique_ptr<ASTNode> Parser::iterationStmt() {
    if (match(KEYWORD, "while")) {
        consume(); // consume while
        if (match(SYMBOL, "(")) {
            consume(); // consume (
            auto expr = expression();
            if (match(SYMBOL, ")")) {
                consume(); // consume )
                auto stmt = statement();
                auto node = std::make_unique<ASTNode>("iteration-stmt");
                node->children.push_back(std::move(expr));
                node->children.push_back(std::move(stmt));
                return node;
            }
        }
    }
    std::cerr << "Error in "<< peek().lineNumber << std::endl;
    return nullptr; // Error
}

std::unique_ptr<ASTNode> Parser::returnStmt() {
    if (match(KEYWORD, "return")) {
        consume(); // consume return
        auto node = std::make_unique<ASTNode>("return-stmt");
        if (!match(SYMBOL, ";")) {
            node->children.push_back(expression());
        }
        if (match(SYMBOL, ";")) {
            consume(); // consume ;
            return node;
        }
    }
    std::cerr << "Error in "<< peek().lineNumber << std::endl;
    return nullptr; // Error
}

std::unique_ptr<ASTNode> Parser::expression() {
    auto node = simpleExpression();

    if (match(SYMBOL, "=")) {
        auto assign = std::make_unique<ASTNode>(consume().value);
        assign->children.push_back(std::move(node));
        assign->children.push_back(expression());
        node = std::move(assign);
    }

    return node;
}


std::unique_ptr<ASTNode> Parser::var() {
    if (match(ID)) {
        auto id = std::make_unique<ASTNode>(consume().value); // consume ID
        if (match(SYMBOL, "[")) {
            consume(); // consume [
            auto expr = expression();
            if (match(SYMBOL, "]")) {
                consume(); // consume ]
                auto node = std::make_unique<ASTNode>("var");
                node->children.push_back(std::move(id));
                node->children.push_back(std::move(expr));
                return node;
            }
        } else {
            return id;
        }
    }
    std::cerr << "Error in "<< peek().lineNumber << std::endl;
    return nullptr; // Error
}

std::unique_ptr<ASTNode> Parser::simpleExpression() {
    auto node = additiveExpression();
    while (match(SYMBOL, "<=") || match(SYMBOL, "<") || match(SYMBOL, ">") ||
           match(SYMBOL, ">=") || match(SYMBOL, "==") || match(SYMBOL, "!=")) {
        auto relop = std::make_unique<ASTNode>(consume().value);
        relop->children.push_back(std::move(node));
        relop->children.push_back(additiveExpression());
        node = std::move(relop);
    }
    return node;
}

std::unique_ptr<ASTNode> Parser::additiveExpression() {
    auto node = term();
    while (match(SYMBOL, "+") || match(SYMBOL, "-")) {
        auto addop = std::make_unique<ASTNode>(consume().value); // consume addop
        addop->children.push_back(std::move(node));
        addop->children.push_back(term());
        node = std::move(addop);
    }
    return node;
}

std::unique_ptr<ASTNode> Parser::term() {
    auto node = factor();
    while (match(SYMBOL, "*") || match(SYMBOL, "/")) {
        auto mulop = std::make_unique<ASTNode>(consume().value); // consume mulop
        mulop->children.push_back(std::move(node));
        mulop->children.push_back(factor());
        node = std::move(mulop);
    }
    return node;
}

std::unique_ptr<ASTNode> Parser::factor() {
    if (match(SYMBOL, "(")) {
        consume(); // consume (
        auto expr = expression();
        if (match(SYMBOL, ")")) {
            consume(); // consume )
            return expr;
        }
    } else if (match(ID)) {
        auto id = consume(); // consume ID
        if (match(SYMBOL, "(")) {
            currentTokenIndex--; // unconsume ID
            return call();
        } else {
            currentTokenIndex--; // unconsume ID
            return var();
        }
    } else if (match(NUM)) {
        return std::make_unique<ASTNode>(consume().value); // consume NUM
    }
    std::cerr << "Error in "<< peek().lineNumber << std::endl;
    return nullptr; // Error
}

std::unique_ptr<ASTNode> Parser::call() {
    if (match(ID)) {
        auto id = std::make_unique<ASTNode>(consume().value); // consume ID
        if (match(SYMBOL, "(")) {
            consume(); // consume (
            auto argsNode = args();
            if (match(SYMBOL, ")")) {
                consume(); // consume )
                auto node = std::make_unique<ASTNode>("call");
                node->children.push_back(std::move(id));
                node->children.push_back(std::move(argsNode));
                return node;
            }
        }
    }

    std::cerr << "Error in "<< peek().lineNumber << std::endl;
    return nullptr; // Error
}

std::unique_ptr<ASTNode> Parser::args() {
    if (match(SYMBOL, ")")) {
        return std::make_unique<ASTNode>("args");
    } else {
        return argList();
    }
}

std::unique_ptr<ASTNode> Parser::argList() {
    auto node = std::make_unique<ASTNode>("arg-list");
    node->children.push_back(expression());
    while (match(SYMBOL, ",")) {
        consume(); // consume ,
        node->children.push_back(expression());
    }
    return node;
}
