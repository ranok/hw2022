import serial
from typing import Dict, Union, Optional

DEVICE = '/dev/ttyUSB0'

def read_message(sd : serial.Serial) -> Dict[str, Union[int, bytearray]]:
    '''Reads an incoming ANT+ message from the serial device'''
    msg = {}
    msg['msg_sync'] = sd.read(1)
    if msg['msg_sync'] is None:
        return {}
    msg['length'] = int(sd.read(1).hex(), base=16)
    msg['type'] = sd.read(1)
    msg['msg'] = sd.read(msg['length'])
    msg['chksum'] = sd.read(1)
    return msg

def send_hexstring(sd : serial.Serial, hexstring : str) -> None:
    '''Sends the passed hexstring to the serial device'''
    sd.write(bytes.fromhex(hexstring))
    sd.flush()

def enable_rx_scan_mode(sd : serial.Serial) -> None:
    '''Configures the serial ANT+ device to listen for messages'''
    send_hexstring(sd, 'a4014a30df')
    send_hexstring(sd, 'a4014a30df')
    send_hexstring(sd, 'a4094600b9a521fbbd72c34564')
    send_hexstring(sd, 'a40342004000a5')
    send_hexstring(sd, 'a405510000000000f0')
    send_hexstring(sd, 'a402450039da')
    send_hexstring(sd, 'a402660001c1')
    send_hexstring(sd, 'a4026e00e028')
    send_hexstring(sd, 'a4015b00fe')

def parse_msg_to_hr(msg : Dict) -> Optional[int]:
    if msg['type'].hex() == '4e':
        return int(msg['msg'][8])
    return None

def main(dev : str = DEVICE) -> None:
    sd = serial.Serial(dev, 115200)
    enable_rx_scan_mode(sd)
    while True:
        hr = parse_msg_to_hr(read_message(sd))
        if hr != None:
            print('Got HR: ' + str(hr))

