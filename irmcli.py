import argparse
import json
import os
import platform
import time

import serial

PORT_LINUX = "/dev/ttyACM0"
PORT_MACOS = "/dev/cu.usbmodem01231"
PORTS = {
    "Linux": PORT_LINUX,
    "Darwin": PORT_MACOS,
}
BAUDRATE = 9600
TIMEOUT = 1
ir_serial = serial.Serial(PORTS.get(platform.system(), None), BAUDRATE, timeout=TIMEOUT)


def capture_IR() -> None:
    """Capture IR data from IR sensor"""
    print("Capturing IR...")
    ir_serial.write(str.encode("c\r\n"))
    time.sleep(3.0)
    ret = ir_serial.readline()
    print(f"{ret=}")


def play_IR(path: str) -> None:
    """Play IR data from IR sensor

    Args:
        path (str): file_path
    """
    if path and os.path.isfile(path):
        print(f"Playing IR with {path} ...")
        with open(path, "r") as f:
            data = json.load(f)

        recNumber = len(data["data"])
        rawX = data["data"]

        ir_serial.write(str.encode(f"n,{recNumber}\r\n"))
        ir_serial.readline()

        postScale = data["postscale"]
        ir_serial.write(str.encode(f"k,{postScale}\r\n"))
        ret = ir_serial.readline()

        for n in range(recNumber):
            bank = int(n / 64)
            pos = n % 64
            if pos == 0:
                ir_serial.write(str.encode(f"b,{bank}\r\n"))
            ir_serial.write(str.encode(f"w,{pos},{rawX[n]}\n\r"))

        ir_serial.write(str.encode("p\r\n"))
        ret = ir_serial.readline()
        print(f"{ret=}")

    else:
        print("Playing IR...")
        ir_serial.write(str.encode("p\r\n"))
        time.sleep(1.0)
        ret = ir_serial.readline()
        print(f"{ret=}")


def save_IR(path: str) -> None:
    """Save IR data to file

    Args:
        path (str): file_path
    """
    print(f"Saving IR data to {path} ...")
    rawX = []
    ir_serial.write(str.encode("I,1\r\n"))
    time.sleep(1.0)
    recNumberStr = ir_serial.readline()
    recNumber = int(recNumberStr, 16)

    ir_serial.write(str.encode("I,6\r\n"))
    time.sleep(1.0)
    postScaleStr = ir_serial.readline()
    postScale = int(postScaleStr, 10)

    for n in range(recNumber):
        bank = int(n / 64)
        pos = n % 64
        if pos == 0:
            ir_serial.write(str.encode(f"b,{bank}\r\n"))

        ir_serial.write(str.encode(f"d,{pos}\n\r"))
        xStr = ir_serial.read(3).decode()
        xData = int(xStr, 16)
        rawX.append(xData)

    data = {"format": "raw", "freq": 38, "data": rawX, "postscale": postScale}

    with open(path, "w") as f:
        json.dump(data, f)
    print("Done !")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="irMagician CLI utility.")
    parser.add_argument("-c", "--capture", action="store_true", dest="cap", help="capture IR data", default=False)
    parser.add_argument("-p", "--play", action="store_true", dest="play", help="play IR data", default=False)
    parser.add_argument("-s", "--save", action="store_true", dest="save", help="save IR data", default=False)
    parser.add_argument("-f", "--file", action="store", dest="file", help="IR data file (json)", default=False)
    args = parser.parse_args()

    if args.cap:
        capture_IR()

    if args.play:
        play_IR(args.file)

    if args.save and args.file:
        save_IR(args.file)

    # release resources
    ir_serial.close()
