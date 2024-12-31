cmake_minimum_required(VERSION 3.10)
project(opendroneid-core C)

# Build only the `opendroneid` source file as a shared library
add_library(opendroneid SHARED libs/opendroneid-core-c/libopendroneid/opendroneid.c)
