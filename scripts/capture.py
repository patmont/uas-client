import ctypes
from ctypes import (
    Structure,
    c_uint8,
    c_char,
    c_char_p,
    c_int,
    POINTER,
    c_void_p,
    c_float,
    c_int32,
)

import sqlite3
from scapy.all import sniff, Raw

import yaml

odid = ctypes.CDLL("./build/libopendroneid.so")

# Read in config
def load_config(file_path: str) -> dict:
    """test doctring"""
    try:
        with open(file_path, 'r', encoding='UTF-8') as file:
            config = yaml.safe_load(file)
            return config.get("vars", {})
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
    return {}

class ODID_Location(Structure):
    _fields_ = [
        ("Direction", c_float),
        ("SpeedHorizontal", c_float),
        ("SpeedVertical", c_float),
        ("Latitude", c_float),
        ("Longitude", c_float),
        ("AltitudeBaro", c_float),
        ("AltitudeGeo", c_float),
        ("Height", c_float),
        ("HorizAccuracy", c_uint8),
        ("VertAccuracy", c_uint8),
        ("BaroAccuracy", c_uint8),
        ("SpeedAccuracy", c_uint8),
        ("TSAccuracy", c_uint8),
        ("TimeStamp", c_float),
    ]

class ODID_BasicID(Structure):
    _fields_ = [
        ("IDType", c_uint8),
        ("UAType", c_uint8),
        ("UASID", c_char * 20),
    ]

class ODID_Auth(Structure):
    _fields_ = [
        ("AuthType", c_uint8),
        ("DataPage", c_uint8),
        ("LastPageIndex", c_uint8),
        ("Length", c_uint8),
        ("Timestamp", c_int32),
        ("AuthData", c_char * 23),
    ]

class ODID_UAS_Data(Structure):
    _fields_ = [
        # Flags
        ("BasicIDValid", c_uint8 * 6),
        ("LocationValid", c_uint8),
        ("AuthValid", c_uint8 * 10),  # Assuming 10 auth pages
        ("SelfIDValid", c_uint8),
        ("SystemValid", c_uint8),
        ("OperatorIDValid", c_uint8),

        # Fields
        ("BasicID", ODID_BasicID * 6),  # Array of BasicID structures
        ("Location", ODID_Location),  # Single Location structure
        ("Auth", ODID_Auth * 10),  # Array of Auth structures
        # Add other fields for SelfID, System, and OperatorID
    ]

# Packet handling
def handle_packet(packet: any) -> None:
    """Parses incoming tcp captures; formats the output; stores to sqlite db
    args:
        packet: tcpdump like packet
    """
    timestamp = packet.time
    packet_data = str(packet.summary())
    cursor.execute("INSERT INTO data (timestamp, packet_data) VALUES (?, ?)",
                   (timestamp, packet_data))
    conn.commit()

    if packet.haslayer(Raw):
        raw_data = bytes(packet[Raw])
        data_buffer = (c_uint8 * len(raw_data))(*raw_data)

        uas_data = ODID_UAS_Data()
        # Call the decodeOpenDroneID function
        decoded = odid.decodeMessagePack(ctypes.byref(uas_data), ctypes.byref(data_buffer))


        # Interpret the result
        if message_type == 0:  # Replace 0 with the enum value for ODID_MESSAGETYPE_LOCATION
            print("Location message decoded")
            # Access decoded fields from uas_data here
        else:
            print(f"Message type {message_type} decoded")


# SQLite setup
conn = sqlite3.connect('../data/data.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS data (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     timestamp DATETIME,
                     packet_data TEXT)''')


if __name__ == "__main__":
    config = load_config("config.yaml")
    print("Starting packet capture...")
    sniff(iface=config["iface"], prn=handle_packet, store=False)
