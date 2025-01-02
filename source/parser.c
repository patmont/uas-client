
#include <stdint.h>
#include "opendroneid.h"
#include "database.h"

uint8_t* extract_payload(const uint8_t *packet) {
    const size_t header_len = 122;
    const uint8_t *payload = packet + header_len;

    return (uint8_t *)payload;
}

void parse_packet(const unsigned char *packet) {
    ODID_UAS_Data uasData;
    uint8_t *payload = extract_payload(packet);
    ODID_messagetype_t msgType = decodeOpenDroneID(&uasData, payload);

    if (msgType != ODID_MESSAGETYPE_INVALID) {
        insert_data(&uasData);
    }
}