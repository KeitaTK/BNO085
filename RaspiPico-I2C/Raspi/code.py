
import time

import time
import board
import busio
from adafruit_bno08x.i2c import BNO08X_I2C

print("[DEBUG] Starting BNO085 USB sender.")
try:
    print("[DEBUG] Initializing I2C...")
    i2c = busio.I2C(board.SCL, board.SDA)
    print("[DEBUG] Initializing BNO085 sensor...")
    sensor = BNO08X_I2C(i2c)
    print("[INFO] BNO085 sensor initialized.")
except Exception as e:
    print(f"[ERROR] I2C/BNO085 init error: {e}")
    while True:
        time.sleep(1)

while True:
    try:
        quat = sensor.quaternion
        print(f"[DEBUG] Quaternion: {quat}")
        send_str = " ".join([str(q) for q in quat])
        print(f"[INFO] Sending: {send_str}")
        print(send_str)  # USB経由でPCに送信
        time.sleep(0.1)
    except Exception as e:
        print(f"[ERROR] Data read/send error: {e}")
        time.sleep(1)

print("[INFO] BNO085 USB sender started.")

while True:
    try:
        quat = sensor.quaternion
        send_str = " ".join([str(q) for q in quat])
        print(send_str)  # USB経由でPCに送信
        time.sleep(0.1)
    except Exception as e:
        print(f"[ERROR] {e}")
        time.sleep(1)
