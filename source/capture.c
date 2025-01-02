#include <pcap.h>
#include <stdio.h>
#include "parser.h"


void packet_handler(unsigned char *user, const struct pcap_pkthdr *header, const unsigned char *packet) {
    // Pass packet to parser
    parse_packet(packet);
}

void start_capture() {
    char errbuf[PCAP_ERRBUF_SIZE];
    pcap_t *handle = pcap_open_live("wlan0mon", BUFSIZ, 1, 1000, errbuf);
    
    if (!handle) {
        fprintf(stderr, "Error: %s\n", errbuf);
        return;
    }

    // Filter for 802.11 management frames
    struct bpf_program fp;
    char filter_exp[] = "wlan type mgt"; // BPF syntax
    if (pcap_compile(handle, &fp, filter_exp, 0, PCAP_NETMASK_UNKNOWN) == -1) {
        fprintf(stderr, "Could not parse filter: %s\n", pcap_geterr(handle));
        return;
    }
    if (pcap_setfilter(handle, &fp) == -1) {
        fprintf(stderr, "Could not apply filter: %s\n", pcap_geterr(handle));
        return;
    }

    pcap_loop(handle, -1, packet_handler, NULL);
    pcap_close(handle);
}