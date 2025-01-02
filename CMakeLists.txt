cmake_minimum_required(VERSION 3.10)
project(UAS-Client)

set(CMAKE_C_STANDARD 99)

include_directories(libs/opendroneid-core-c/libopendroneid)

set(SOURCES
    source/main.c
    source/capture.c
    source/parser.c
    source/database.c
    libs/opendroneid-core-c/libopendroneid/opendroneid.c
)

add_executable(UAS-Client ${SOURCES})

target_link_libraries(UAS-Client pcap sqlite3)