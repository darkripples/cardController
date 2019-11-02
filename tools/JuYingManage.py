# coding:utf8

import socket, time
import struct


def main():
    data = "FE040000000125C5"
    Modbus_16 = ""
    for x in range(0, len(data), 2):
        Modbus_16 += chr(int(data[x:x + 2], 16))

    s = socket.socket()
    s.connect(("192.168.1.232", 10000))
    while 1:
        try:
            s.send(Modbus_16)
            reply_16 = s.recv(100)
        except:
            reply_16 = ""
            s.close()
            s = socket.socket()
            s.connect(("192.168.1.232", 10000))
        reply_temp = ""
        for i in reply_16:
            reply_temp += "0x%02x" % ord(i)
        reply_temp = reply_temp[2:]
        mb = ""
        while reply_temp:
            mb += reply_temp[0:2]
            reply_temp = reply_temp[4:]
        temp = int(mb[6:10], 16) * 0.01
        print(temp)
        time.sleep(1)


def open(num):
    # 设备地址
    device_addr = 254

    buf = struct.pack("B" * 6, 254,
                      5,
                      0, num - 1,
                      255, 0  # 255,0：开启指令； 0,0：关闭指令
                      )

    # 校验位置
    check_byte = crc16_1(buf.decode("unicode-escape"), True)
    b1 = struct.pack("B" * 2,
                     int(check_byte[:2], 16), int(check_byte[-2:], 16))
    b1 = buf + b1

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    s.connect(("192.168.1.232", 10000))
    print('connect...')
    s.send(b1)
    print('send:' + str(b1))
    resp = s.recv(1024)
    print(resp)

    s.close()


def crc16_1(x: str, invert: bool):
    a = 0xFFFF
    b = 0xA001
    for byte in x:
        a ^= ord(byte)
        for i in range(8):
            last = a % 2
            a >>= 1
            if last == 1:
                a ^= b
    s = hex(a).upper()

    return s[4:6] + s[2:4] if invert == True else s[2:4] + s[4:6]


def testBuf():
    data = "FE050001FF00C9F5"

    num = 2
    # 设备地址
    device_addr = 254

    buf = struct.pack("B" * 6, device_addr,
                      5,
                      0, num - 1,
                      255, 0  # 255,0：开启指令； 0,0：关闭指令
                      )
    print("buf0:", buf)
    buf1 = hex(device_addr) + hex(5) + hex(0) + hex(num - 1) + hex(255) + hex(0)
    # print('buf1:', buf1)
    x = [hex(device_addr), hex(5), hex(0), hex(num - 1), hex(255), hex(0)]
    # print('x:', x)
    # print('buf2:', buf1.replace("0x", "\\x"))
    buf3 = str(buf)[1:]
    print('buf3:', buf3)
    print('buf4:', buf.decode("unicode-escape"))
    # 校验位置
    print('check:', '\xfe\x05\x00\x01\xff\x00')

    # check_byte = crc16_1('\xfe\x05\x00\x01\xff\x00', True)
    check_byte = crc16_1(buf3, True)
    b1 = struct.pack("B" * 2,
                     int(check_byte[:2], 16), int(check_byte[-2:], 16))
    b1 = buf + b1
    print('final:', b1)


if __name__ == "__main__":
    open(2)
    #testBuf()
