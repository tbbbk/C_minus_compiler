cmake_minimum_required(VERSION 3.22)
project(Cminus)

set(CMAKE_CXX_STANDARD 17)

add_executable(Cminus test.cpp Lexer.cpp Parser.cpp Parser.h)
