import bluetooth.ble 
import bluetooth._bluetooth as bluez
import struct
import binascii

import sys
import subprocess
import threading
import datetime
import time
import logging
import argparse


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('2jcie_ble_sample')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='sample.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Bluetooth adaptor
BT_DEV_ID = 0

# BLE scan types.
BLE_SCAN_PASSIVE = 0x00
BLE_SCAN_ACTIVE = 0x01

# BLE address types.
BLE_PUBLIC_ADDRESS = 0x00
BLE_RANDOM_ADDRESS = 0x01

# BLE filter policies.
BLE_FILTER_ALLOW_ALL = 0x00
BLE_FILTER_WHITELIST_ONLY = 0x01
BLE_FILTER_DUPLICATES_OFF = 0x00
BLE_FILTER_DUPLICATES_ON = 0x01

# BLE OpCode group field for the LE related OpCodes.
OGF_LE_CTL = 0x08

# OMRON company ID.
COMPANY_ID = 'd502'

# BLE OpCode Commands.
OCF_BLE_SET_SCAN_PARAMETERS = 0x000B
OCF_BLE_SET_SCAN_ENABLE = 0x000C

# both sensor advertize packet detection mode.
MODE_BOTH = 'both'
# 2JCIE-BL advertize packet detection mode.
MODE_BL = 'bag'
# 2JCIE-BU advertize packet detection mode.
MODE_BU = 'usb'

# Global variables
sensor_list = []


def reset_hci():
    # resetting bluetooth dongle
    cmd = "sudo hciconfig hci0 down"
    subprocess.call(cmd, shell=True)
    cmd = "sudo hciconfig hci0 up"
    subprocess.call(cmd, shell=True)


def hci_le_set_scan_parameters(sock, scan_type=BLE_SCAN_ACTIVE, interval=0x10,
                               window=0x10, own_bdaddr_type=BLE_RANDOM_ADDRESS,
                               filter_type=BLE_FILTER_ALLOW_ALL):
    # setting up scan
    # interval and window are uint_16, so we pad them with 0x0
    cmd_pkt = struct.pack("<BBBBBBB", scan_type, 0x0, interval, 0x0, window,
                          own_bdaddr_type, filter_type)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_BLE_SET_SCAN_PARAMETERS, cmd_pkt)
    # sent scan parameters command


def hci_le_enable_scan(sock):
    hci_le_toggle_scan(sock, 0x01)


def hci_le_disable_scan(sock):
    hci_le_toggle_scan(sock, 0x00)


def hci_le_toggle_scan(sock, enable):
    # toggle scan
    cmd_pkt = struct.pack("<BB", enable, 0x00)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_BLE_SET_SCAN_ENABLE, cmd_pkt)
    # sent toggle command"


def print_bu(packet):
    company_id = str(format(packet[19],'x')+format(packet[20],'x').zfill(2))
    temperature = str(int(hex(packet[24])+format(packet[23],'x'), 16)/100)
    relative_humidity = str(int(hex(packet[26])+format(packet[25],'x'),16)/100)
    ambient_light = str(int(hex(packet[28])+format(packet[27],'x'),16))
    barometric_pressure = str(int(hex(packet[32])+format(packet[31],'x')+format(packet[30],'x')+format(packet[29],'x'),16)/1000)
    sound_noise = str(int(hex(packet[34])+format(packet[33],'x'),16)/100)
    etvoc = str(int(hex(packet[36])+format(packet[35],'x'),16))
    eco2 = str(int(hex(packet[38])+format(packet[37],'x'),16))
    logger.info("= 2JCIE-BU =================")
    logger.info("Company ID : " + company_id)
    logger.info("Temperature : " + temperature)
    logger.info("Relative humidity : " + relative_humidity)
    logger.info("Ambient light : " + ambient_light)
    logger.info("Barometric pressure : " + barometric_pressure)
    logger.info("Sound noise : " + sound_noise)
    logger.info("eTVOC : " + etvoc)
    logger.info("eCO2 : " + eco2)
    logger.info("============================\n")


def print_bl(packet):
    company_id = str(format(packet[19],'x') + format(packet[20], 'x').zfill(2))
    sequence_number = str(int(hex(packet[21]),16))
    temperature = str(int(hex(packet[23]) + format(packet[22], 'x'), 16)/100)
    relative_humidity = str(int(hex(packet[25])+format(packet[24],'x'),16)/100)
    ambient_light = str(int(hex(packet[27])+format(packet[26],'x'),16))
    uv_index = str(int(hex(packet[29])+format(packet[28],'x'),16)/100)
    pressure = str(int(hex(packet[31])+format(packet[30],'x'),16)/10)
    sound_noise = str(int(hex(packet[33])+format(packet[32],'x'),16)/100)
    discomfort_index = str(int(hex(packet[35])+format(packet[34],'x'),16)/100)
    heat_stroke = str(int(hex(packet[37])+format(packet[36],'x'),16)/100)
    battery_voltage = str(int(hex(packet[40]),16))
    logger.info("= 2JCIE-BL =================")
    logger.info("Company ID : " + company_id)
    logger.info("Sequence number : " + sequence_number)
    logger.info("Temperature : " + temperature)
    logger.info("Relative humidity : " + relative_humidity)
    logger.info("Ambient light : " + ambient_light)
    logger.info("UV index : " + uv_index)
    logger.info("Pressure : " + pressure)
    logger.info("Sound noise : " + sound_noise)
    logger.info("Discomfort index : " + discomfort_index )
    logger.info("Heat stroke : " + heat_stroke)
    logger.info("Battery voltage : " + battery_voltage)
    logger.info("============================\n")


def parse_events(sock, mode):
    global sensor_list

    pkt = sock.recv(255)

    parsed_packet = hci_le_parse_response_packet(pkt)
    packet_bin = parsed_packet["packet_bin"]
    
    if mode == MODE_BOTH:
        if(b'\xd5\x02' in packet_bin):
            if(b'EP' in packet_bin):
                print_bl(packet_bin)
            if(b'Rbt' in packet_bin):
                print_bu(packet_bin)
    elif mode == MODE_BL:
        if(b'\xd5\x02' in packet_bin and b'EP' in packet_bin):
            print_bl(packet_bin)
    elif mode == MODE_BU:
        if(b'\xd5\x02' in packet_bin and b'Rbt' in packet_bin):
            print_bu(packet_bin)


def hci_le_parse_response_packet(pkt):
    result = {}
    ptype, event, plen = struct.unpack("<BBB", pkt[:3])
    result["packet_type"] = ptype
    result["bluetooth_event_id"] = event
    result["packet_length"] = plen
    result["packet_str"] = pkt.hex()
    result["packet_bin"] = pkt
    return result


# main function
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", help="sensor select", type=str, choices=[MODE_BOTH, MODE_BL, MODE_BU], default=MODE_BOTH)
    detection_mode = parser.parse_args().mode
    print('main detection mode:%s' % detection_mode)

    try:
        flag_scanning_started = False

        # reset bluetooth functionality
        try:
            print("-- reseting bluetooth device")
            reset_hci()
            print("-- reseting bluetooth device : success")
        except Exception as e:
            print("error enabling bluetooth device")
            print(str(e))
            sys.exit(1)

        # initialize bluetooth socket
        try:
            print("-- open bluetooth device")
            sock = bluez.hci_open_dev(BT_DEV_ID)
            print("-- ble thread started")
        except Exception as e:
            print("error accessing bluetooth device: ", str(BT_DEV_ID))
            print(str(e))
            sys.exit(1)

        # set ble scan parameters
        try:
            print("-- set ble scan parameters")
            hci_le_set_scan_parameters(sock)
            print("-- set ble scan parameters : success")
        except Exception as e:
            print("failed to set scan parameter!!")
            print(str(e))
            sys.exit(1)

        # start ble scan
        try:
            print("-- enable ble scan")
            hci_le_enable_scan(sock)
            print("-- ble scan started")
        except Exception as e:
            print("failed to activate scan!!")
            print(str(e))
            sys.exit(1)
        
        flag_scanning_started = True
        print("envsensor_observer : complete initialization")
        print("")

        # preserve old filter setting
        old_filter = sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)
        # perform a device inquiry on bluetooth device #0
        # The inquiry should last 8 * 1.28 = 10.24 seconds
        # before the inquiry is performed, bluez should flush its cache of
        # previously discovered devices
        flt = bluez.hci_filter_new()
        bluez.hci_filter_all_events(flt)
        bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
        sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, flt)

        while True:
            # parse ble event
            parse_events(sock, detection_mode)
            flag_update_sensor_status = False

    except Exception as e:
        print("Exception: " + str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        if flag_scanning_started:
            # restore old filter setting
            sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, old_filter)
            hci_le_disable_scan(sock)
        print("Exit")
