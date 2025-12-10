import board
import busio
import time

print("=" * 50)
print("BNO085 接続テスト開始")
print("=" * 50)

# I2Cピンの設定（配線に合わせて変更してください）
SCL_PIN = board.GP5  # SCLピン
SDA_PIN = board.GP4  # SDAピン

print(f"\n[1] I2Cピン設定:")
print(f"  SCL: GP5")
print(f"  SDA: GP4")

try:
    # I2Cバスの初期化
    print("\n[2] I2Cバスを初期化中...")
    i2c = busio.I2C(SCL_PIN, SDA_PIN, frequency=400000)
    print("  ✓ I2Cバスの初期化成功")
    
    # I2Cデバイスのスキャン
    print("\n[3] I2Cデバイスをスキャン中...")
    
    while not i2c.try_lock():
        pass
    
    try:
        devices = i2c.scan()
        print(f"  検出されたデバイス数: {len(devices)}")
        
        if len(devices) == 0:
            print("\n  ✗ I2Cデバイスが検出されませんでした")
            print("\n  【確認事項】")
            print("  - SDA/SCLの配線が正しいか")
            print("  - BNO085の電源（VCC, GND）が接続されているか")
            print("  - プルアップ抵抗（3.3kΩ〜10kΩ）が接続されているか")
            print("    → SDAとSCLそれぞれに、3.3Vへの抵抗が必要")
        else:
            print("\n  検出されたI2Cアドレス:")
            for device_address in devices:
                print(f"    0x{device_address:02X} ({device_address})")
            
            # BNO085のデフォルトアドレスは 0x4A または 0x4B
            if 0x4A in devices:
                print("\n  ✓ BNO085が検出されました！ (アドレス: 0x4A)")
            elif 0x4B in devices:
                print("\n  ✓ BNO085が検出されました！ (アドレス: 0x4B)")
            else:
                print("\n  ⚠ BNO085のアドレス (0x4A or 0x4B) が見つかりません")
                print("  別のI2Cデバイスが接続されているか、")
                print("  BNO085のアドレス設定を確認してください")
                
    finally:
        i2c.unlock()
    
    print("\n" + "=" * 50)
    print("テスト完了")
    print("=" * 50)
    
except ValueError as e:
    print(f"\n  ✗ エラー: {e}")
    print("\n  【考えられる原因】")
    print("  - プルアップ抵抗が接続されていない")
    print("  - SDA/SCLピンの指定が間違っている")
    
except Exception as e:
    print(f"\n  ✗ 予期しないエラー: {e}")
    print(f"  エラータイプ: {type(e).__name__}")
