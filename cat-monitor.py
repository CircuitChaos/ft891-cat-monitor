#!/usr/bin/env python3

import serial
import time

cat_port = "/dev/ttyUSB0"
cat_baud = 9600
poll_interval = .25

def cat(ser, req):
    ser.write((req + ";").encode())
    rsp = ""
    while True:
        byte = ser.read(1)
        if byte == b";":
            break
        rsp += byte.decode()
    if len(rsp) < len(req):
        raise(RuntimeError("CAT response too short"))
    if rsp[0:len(req)] != req:
        raise(RuntimeError("CAT response invalid: %s" % rsp))
    return rsp[len(req):]

ser = serial.Serial(cat_port, cat_baud, timeout=1)
model = cat(ser, "ID")
if model != "0650":
    print("Expecting FT-891 (ID0650), but got different model ID string: %s" % model)
    print("This program was never tested on radios other tha FT-891.")
    print("Refusing to continue. Comment out this check if you want to proceed.")
    ser.close()
    exit(1)

def interpolate(cal_table, raw_value):
    if raw_value < cal_table[0][0] or raw_value > cal_table[len(cal_table) - 1][0]:
        raise(RuntimeError("Invalid meter value: %u" % raw_value))

    result = []
    prev_entry = cal_table[0]
    next_entry = None
    for entry in cal_table:
        if entry[0] == raw_value:
            result.append(entry[1])
            result.append(entry[2])
            return result

        if entry[0] > raw_value:
            next_entry = entry
            break
        prev_entry = entry

    min_raw = prev_entry[0]
    max_raw = next_entry[0]
    min_calc = prev_entry[1]
    max_calc = next_entry[1]

    raw_delta = (raw_value - min_raw) / (max_raw - min_raw)
    calc_diff = max_calc - min_calc
    calc = (calc_diff * raw_delta) + min_calc

    result.append(calc)
    result.append(prev_entry[2])
    return result

def get_meter(value):
    num_on = int(value / 16)
    num_off = 16 - num_on
    return "%3u [" % value + "#" * num_on + " " * num_off + "]"

def get_sig(raw_sig):
    # Based on FT891_STR_CAL: https://github.com/Hamlib/Hamlib/blob/master/rigs/yaesu/ft891.h#L88
    cal = []
    cal.append([0,  -54, "S0"])
    cal.append([12, -48, "S1"])
    cal.append([27, -42, "S2"])
    cal.append([40, -36, "S3"])
    cal.append([55, -30, "S4"])
    cal.append([65, -24, "S5"])
    cal.append([80, -18, "S6"])
    cal.append([95, -12, "S7"])
    cal.append([112, -6, "S8"])
    cal.append([130,  0, "S9"])
    cal.append([150, 10, "S9+10"])
    cal.append([172, 20, "S9+20"])
    cal.append([190, 30, "S9+30"])
    cal.append([220, 40, "S9+40"])
    cal.append([240, 50, "S9+50"])
    cal.append([255, 60, "S9+60"])
    result = interpolate(cal, raw_sig)
    return get_meter(raw_sig) + " %s (%u dB)" % (result[1], result[0])

def get_alc(raw_alc):
    cal = []
    cal.append([0, 0, ""])
    cal.append([255, 200, ""])
    result = interpolate(cal, raw_alc)
    return get_meter(raw_alc) + " %u%%" % interpolate(cal, raw_alc)[0]

def get_pwr(raw_pwr):
    # Based on FT891_RFPOWER_METER_CAL: https://github.com/Hamlib/Hamlib/blob/master/rigs/yaesu/ft891.h#L73
    cal = []
    cal.append([0, 0.0, ""])
    cal.append([10, 0.8, ""])
    cal.append([50, 8.0, ""])
    cal.append([100, 26.0, ""])
    cal.append([150, 54.0, ""])
    cal.append([200, 92.0, ""])
    cal.append([250, 140.0, ""])
    return get_meter(raw_pwr) + " %.1f W" % interpolate(cal, raw_pwr)[0]

def get_swr(raw_swr):
    cal = []
    # Counting pixels:
    # 1 1.5 2  3  inf
    # 0 19  37 52 97
    cal.append([0, 1.0, ""])
    cal.append([19 * 255 / 97, 1.5, ""])
    cal.append([37 * 255 / 97, 2.0, ""])
    cal.append([52 * 255 / 97, 3.0, ""])
    if raw_swr > (52 * 255 / 97):
        return get_meter(raw_swr) + " too much!"
    return get_meter(raw_swr) + " %.2f" % interpolate(cal, raw_swr)[0]

def get_idd(raw_idd):
    cal = []
    cal.append([0, 0.0, ""])
    cal.append([255, 30.0, ""])
    return get_meter(raw_idd) + " %.1f A" % interpolate(cal, raw_idd)[0]

while True:
    raw_sig = int(cat(ser, "RM1"))
    # raw_cmp = int(cat(ser, "RM3"))
    raw_alc = int(cat(ser, "RM4"))
    raw_pwr = int(cat(ser, "RM5"))
    raw_swr = int(cat(ser, "RM6"))
    raw_idd = int(cat(ser, "RM7"))

    print("Sig:   %s" % get_sig(raw_sig))
    # print("Comp:  %s" % get_cmp(raw_cmp))
    print("ALC:   %s" % get_alc(raw_alc))
    print("Power: %s" % get_pwr(raw_pwr))
    print("SWR:   %s" % get_swr(raw_swr))
    print("Idd:   %s" % get_idd(raw_idd))

    print("")
    time.sleep(poll_interval)

ser.close()
