"""
BNO085 USB Sender (Raspberry Pi Pico)
======================================
Reads quaternion data from BNO085 IMU sensor via I2C
and sends it to PC over USB serial with timestamp.

Hardware Setup:
- BNO085 SCL -> Pico GP5
- BNO085 SDA -> Pico GP4
- BNO085 VCC -> Pico 3.3V
- BNO085 GND -> Pico GND

Output Format:
quat_i quat_j quat_k quat_real timestamp
Example: -0.0410767 -0.0148315 -0.977966 0.204102 1904.42
"""

import time
import board
import busio
from adafruit_bno08x.i2c import BNO08X_I2C
from adafruit_bno08x import BNO_REPORT_ROTATION_VECTOR

# Initialize I2C and BNO085 sensor
i2c = busio.I2C(board.GP5, board.GP4, frequency=400000)
sensor = BNO08X_I2C(i2c)

# Enable rotation vector (quaternion) report
sensor.enable_feature(BNO_REPORT_ROTATION_VECTOR)
time.sleep(0.5)

# Main loop: read and send quaternion data with timestamp
while True:
    try:
        quat = sensor.quaternion  # (i, j, k, real)
        if quat is None:
            time.sleep(0.05)
            continue

        # Get monotonic timestamp
        timestamp = time.monotonic()
        
        # Send data: i j k real timestamp
        print(f"{quat[0]} {quat[1]} {quat[2]} {quat[3]} {timestamp}")
        
        # 50Hz sampling rate
        time.sleep(0.02)

    except Exception as e:
        print(f"[ERROR] {e}")
        time.sleep(1)
