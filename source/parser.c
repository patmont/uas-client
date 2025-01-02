
#include <stdint.h>
#include "opendroneid.h"
#include "database.h"

void parse_packet(const unsigned char *packet) {
    ODID_UAS_Data uasData;
    uint8_t *payload = extract_payload(packet);
    ODID_messagetype_t msgType = decodeOpenDroneID(&uasData, payload);

    if (msgType != ODID_MESSAGETYPE_INVALID) {
        insert_data(&uasData);
    }
}