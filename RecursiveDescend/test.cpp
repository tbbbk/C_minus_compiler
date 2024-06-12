#include "Lexer.h"
#include "Parser.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <algorithm>


void printAST(const std::unique_ptr<ASTNode>& node, int indent = 0) {
    if(node == nullptr) return;
    for (int i = 0; i < indent; ++i) {
        std::cout << "  ";
    }
    std::cout << node->value << "\n";
    for (const auto& child : node->children) {
        printAST(child, indent + 1);
    }
}

int main() {

    std::ios::sync_with_stdio(false);
    std::ifstream file("/opt/c_minus_compiler/src/test_tokenizer/sample_2");

    if (!file.is_open()) {
        std::cerr << "Failed to open the file." << std::endl;
        return 1;
    }

    std::stringstream buffer;
    buffer << file.rdbuf();
    std::string input = buffer.str();

    file.close();

    // 调用词法分析器
    std::vector<Token> tokens = lexer(input);
    printTokens(tokens);
    auto parser = Parser(tokens);

    auto ast = parser.parse();

    printAST(ast);

    return 0;
}
