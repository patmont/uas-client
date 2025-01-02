#ifndef PARSER_H
#define PARSER_H

#include <stdint.h>
#include "opendroneid.h"

uint8_t* extract_payload(const uint8_t *packet);
void parse_packet(const unsigned char *packet);

#endif
