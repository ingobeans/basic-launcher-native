import struct

# following notes of https://github.com/Skizzium/binary-vdf-parser

class Types:
    NULL=0
    STRING=1
    INT=2
    ENDMAP=8

def parse_string(vdf:bytearray)->str:
    text = ""
    while True:
        byte = vdf.pop(0)
        if byte == Types.NULL:
            break
        text += chr(byte)
    return text

def parse_int(vdf:bytearray)->int:
    d = bytearray([vdf.pop(0) for _ in range(4)])
    return struct.unpack("I",d)[0]

def parse_vdf(vdf:bytearray)->dict:
    data = {}
    while True:
        data_type = vdf.pop(0)
        if data_type == Types.ENDMAP:
            break
        key = ""
        while True:
            byte = vdf.pop(0)
            if byte == Types.NULL:
                break
            key += chr(byte)
            
        match data_type:
            case Types.NULL:
                value = parse_vdf(vdf)
            case Types.STRING:
                value = parse_string(vdf)
            case Types.INT:
                value = parse_int(vdf)
            case _:
                print(data_type)
        data[key]=value
    return data