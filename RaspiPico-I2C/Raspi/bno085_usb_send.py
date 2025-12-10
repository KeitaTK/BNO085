import time
import board
import busio
from adafruit_bno08x.i2c import BNO08X_I2C
from adafruit_bno08x import BNO_REPORT_ROTATION_VECTOR

print("[DEBUG] Starting BNO085 USB sender (Pico)")

try:
    print("[DEBUG] Initializing I2C on GP5(SCL), GP4(SDA) ...")
    i2c = busio.I2C(board.GP5, board.GP4, frequency=400000)
    print("[DEBUG] Initializing BNO085 sensor...")
    sensor = BNO08X_I2C(i2c)
    try:
        sensor.enable_feature(BNO_REPORT_ROTATION_VECTOR)
        print("[DEBUG] Enabled rotation vector report")
    except Exception as e:
        print(f"[WARN] Could not enable rotation vector: {e}")
    time.sleep(0.5)
    print("[INFO] BNO085 sensor initialized.")
except Exception as e:
    print(f"[ERROR] I2C/BNO085 init error: {e}")
    while True:
        time.sleep(1)

try:
    while True:
        try:
            quat = sensor.quaternion
            if quat is None:
                time.sleep(0.05)
                continue
            send_str = " ".join([str(q) for q in quat])
            print(send_str)
            time.sleep(0.1)
        except Exception as e:
            print(f"[ERROR] Data read/send error: {e}")
            time.sleep(1)
except KeyboardInterrupt:
    print("[INFO] Stopped by user (KeyboardInterrupt)")
except Exception as e:
    print(f"[FATAL] Unexpected error: {e}")
finally:
    print("[INFO] Exiting sender")
