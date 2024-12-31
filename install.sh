#!/bin/bash

# Constants
CHANNEL=6
PCAP_FILE="/var/log/tcpdump.pcap"
MONITOR_SERVICE="monitor_mode.service"
TCPDUMP_SERVICE="tcpdump_mgt.service"

# Install any required dependencies
check_dependencies() {
    local dependencies=("airmon-ng" "tcpdump" "iw")
    local missing=()

    echo "Checking dependencies..."
    for cmd in "${dependencies[@]}"; do
        if ! command -v $cmd &>/dev/null; then
            missing+=("$cmd")
        fi
    done

    if [[ ${#missing[@]} -ne 0 ]]; then
        echo "Installing missing dependencies: ${missing[*]}"
        apt update && apt install -y "${missing[@]}"
    else
        echo "All dependencies are already installed."
    fi
}

# Function to detect wireless interfaces
detect_interfaces() {
    iw dev | grep Interface | awk '{print $2}'
}

# Function to create systemd service files
create_service_files() {
    local wlan="$1"
    local mon_if="${wlan}mon"

    # Create monitor mode service
    cat <<EOL > /etc/systemd/system/$MONITOR_SERVICE
[Unit]
Description=Enable Monitor Mode on $wlan
Before=$TCPDUMP_SERVICE

[Service]
ExecStart=/usr/sbin/airmon-ng start $wlan $CHANNEL
ExecStop=/usr/sbin/airmon-ng stop $mon_if
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOL

    # Create TCPDump service
    cat <<EOL > /etc/systemd/system/$TCPDUMP_SERVICE
[Unit]
Description=TCPDump Management Frame Logger
After=$MONITOR_SERVICE
Requires=$MONITOR_SERVICE

[Service]
ExecStart=/usr/bin/tcpdump -i $mon_if -W 2 -C 100 -w $PCAP_FILE 'type mgt' -Z root
Restart=always

[Install]
WantedBy=multi-user.target
EOL
}
    # Write variables to yaml
create_config_file() {
cat <<EOL > ./scripts/config.yaml
vars:
    iface: "${wlan}mon"
    channel: $CHANNEL
    pcap_file: "$PCAP_FILE"
EOL
}

# Function to reload and restart services
reload_and_restart_services() {
    systemctl daemon-reload
    systemctl enable $MONITOR_SERVICE $TCPDUMP_SERVICE
    systemctl restart $MONITOR_SERVICE
    systemctl restart $TCPDUMP_SERVICE
}

# Main script logic
main() {
    # Check for root privileges
    if [[ $EUID -ne 0 ]]; then
        echo "This script must be run as root."
        exit 1
    fi

    # Detect wireless interfaces
    local interfaces
    interfaces=$(detect_interfaces)
    if [[ -z $interfaces ]]; then
        echo "No wireless interfaces found. Exiting."
        exit 1
    fi

    # Prompt user to select an interface
    echo "Available wireless interfaces:"
    select wlan in $interfaces; do
        if [[ -n $wlan ]]; then
            echo "Selected interface: $wlan"
            break
        else
            echo "Invalid selection. Try again."
        fi
    done

    # Create and manage services
    create_service_files "$wlan"
    create_config_file "$wlan"
    reload_and_restart_services
}

main "$@"
