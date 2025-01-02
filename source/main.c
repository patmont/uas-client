
#include <stdio.h>
#include "capture.c"
#include "database.c"
#include "parser.c"

void main() {
    init_db();
    start_capture();
}