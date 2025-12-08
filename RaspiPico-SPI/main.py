"""
BNO085 SPI Communication for Raspberry Pi Pico W
配線:
  BNO085 -> Pico W
  Vin    -> 3.3V
  GND    -> GND
  SCL    -> GP18 (SPI Clock)
  SDA    -> GP16 (MISO)
  DI     -> GP19 (MOSI)
  CS     -> GP17 (Chip Select)
  INT    -> GP20 (Interrupt)
  RST    -> GP21 (Reset)
  PO/P1  -> 3.3V (SPI Mode)
"""

import time
import board
import busio
import digitalio
from adafruit_bno08x import (
    BNO_REPORT_ACCELEROMETER,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR,
)
from adafruit_bno08x.spi import BNO08X_SPI

# SPI設定 (GPIO18=SCK, GPIO19=MOSI, GPIO16=MISO)
spi = busio.SPI(board.GP18, MOSI=board.GP19, MISO=board.GP16)

# チップセレクトピン (GP17)
cs = digitalio.DigitalInOut(board.GP17)
cs.direction = digitalio.Direction.OUTPUT
cs.value = True

# 割り込みピン (GP20)
int_pin = digitalio.DigitalInOut(board.GP20)
int_pin.direction = digitalio.Direction.INPUT

# リセットピン (GP21)
reset_pin = digitalio.DigitalInOut(board.GP21)
reset_pin.direction = digitalio.Direction.OUTPUT
reset_pin.value = True

# BNO085初期化 (SPIモード、ボーレート3MHz推奨)
print("BNO085 initializing...")
bno = BNO08X_SPI(spi, cs, int_pin, reset_pin, baudrate=3000000, debug=False)

# センサー機能を有効化
bno.enable_feature(BNO_REPORT_ACCELEROMETER)
bno.enable_feature(BNO_REPORT_GYROSCOPE)
bno.enable_feature(BNO_REPORT_MAGNETOMETER)
bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

print("BNO085 initialized successfully!")
print("Starting sensor readings...")
print()

# メインループ
while True:
    try:
        # 加速度
        accel_x, accel_y, accel_z = bno.acceleration
        
        # ジャイロ
        gyro_x, gyro_y, gyro_z = bno.gyro
        
        # 磁力計
        mag_x, mag_y, mag_z = bno.magnetic
        
        # 四元数 (回転ベクトル)
        quat_i, quat_j, quat_k, quat_real = bno.quaternion
        
        # シリアル出力 (Windows側で受信)
        print(f"{quat_i:.6f} {quat_j:.6f} {quat_k:.6f} {quat_real:.6f}")
        
        # デバッグ用詳細出力 (コメントアウト可)
        # print(f"Accel: X={accel_x:.3f} Y={accel_y:.3f} Z={accel_z:.3f} m/s^2")
        # print(f"Gyro:  X={gyro_x:.3f} Y={gyro_y:.3f} Z={gyro_z:.3f} rad/s")
        # print(f"Mag:   X={mag_x:.3f} Y={mag_y:.3f} Z={mag_z:.3f} uT")
        # print(f"Quat:  i={quat_i:.6f} j={quat_j:.6f} k={quat_k:.6f} real={quat_real:.6f}")
        # print()
        
        time.sleep(0.01)  # 100Hz更新
        
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(1)
