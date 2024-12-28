import yaml
import sqlite3
from scapy.all import sniff

# Read in config
def load_config(file_path):
    try:
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
            return config.get("vars", {})
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
    return {}

# SQLite setup
conn = sqlite3.connect('../data/data.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS data (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     timestamp DATETIME,
                     packet_data TEXT)''')

# Packet handling
def handle_packet(packet):
    timestamp = packet.time
    packet_data = str(packet.summary())
    cursor.execute("INSERT INTO data (timestamp, packet_data) VALUES (?, ?)",
                   (timestamp, packet_data))
    conn.commit()


if __name__ == "__main__":
    vars = load_config("config.yaml")
    print("Starting packet capture...")
    sniff(iface=vars["iface"], prn=handle_packet, store=False)
