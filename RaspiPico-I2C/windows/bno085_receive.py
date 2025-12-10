
import serial
import time

import serial
import time
import sys

PORT = "COM11"
BAUDRATE = 115200

def debug_quaternion(data):
    try:
        parts = data.split()
        if len(parts) == 4:
            i, j, k, r = map(float, parts)
            print(f"[DEBUG] Quaternion -> i: {i}, j: {j}, k: {k}, r: {r}")
        else:
            print(f"[DEBUG] Raw data: {data}")
    except Exception as e:
        print(f"[DEBUG] Parse error: {e}, data: {data}")

print(f"[INFO] Trying to open serial port {PORT} at {BAUDRATE} baud...")
try:
    ser = serial.Serial(PORT, BAUDRATE, timeout=1)
    print(f"[INFO] Serial port opened successfully.")
except Exception as e:
    print(f"[ERROR] Could not open {PORT}: {e}")
    sys.exit(1)

print("[INFO] Start receiving loop. Waiting for data...")
try:
    while True:
        try:
            data = ser.readline().decode(errors="ignore").strip()
            if data:
                print(f"[INFO] Received: {data}")
                debug_quaternion(data)
        except Exception as e:
            print(f"[ERROR] Exception while reading serial: {e}")
except KeyboardInterrupt:
    print("[INFO] Exiting...")
except Exception as e:
    print(f"[ERROR] Exception in receive loop: {e}")
finally:
    ser.close()
    print("[INFO] Serial port closed.")
