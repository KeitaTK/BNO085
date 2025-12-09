"""
Windows側プログラム: Raspberry Pi Pico WからBNO085のデータを受信して3D表示
Pico側からシリアル経由で四元数データを受信し、3D立方体で姿勢を可視化
"""

import serial
import time
import numpy as np
from scipy.spatial.transform import Rotation as R
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt

# シリアルポートの設定 (環境に応じて変更してください)
SERIAL_PORT = 'COM11'  # Windows: 'COM4', Linux/Mac: '/dev/ttyACM0'
BAUDRATE = 115200

# シリアル通信の初期化
try:
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    print(f"シリアルポート {SERIAL_PORT} を {BAUDRATE}bps で開きました")
    time.sleep(2)  # Picoの起動待ち
except Exception as e:
    print(f"シリアルポート接続エラー: {e}")
    print("COMポート番号を確認してください")
    exit()

# データを格納するリスト
time_data = []

# 3Dプロットの初期化
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
plt.ion()  # インタラクティブモード

# 立方体の頂点を定義 (Pico基板を模擬)
points = np.array([
    [-2, -1, -0.5],  # 0
    [2, -1, -0.5],   # 1
    [2, 1, -0.5],    # 2
    [-2, 1, -0.5],   # 3
    [-2, -1, 0.5],   # 4
    [2, -1, 0.5],    # 5
    [2, 1, 0.5],     # 6
    [-2, 1, 0.5]     # 7
]) * 10

# 立方体の面を定義
faces = [
    [0, 1, 2, 3],  # 底面
    [4, 5, 6, 7],  # 上面
    [0, 1, 5, 4],  # 前面
    [2, 3, 7, 6],  # 後面
    [0, 3, 7, 4],  # 左面
    [1, 2, 6, 5]   # 右面
]

print("データ受信中... (Ctrl+Cで終了)")

try:
    while True:
        # シリアルからデータを読み取り
        if ser.in_waiting > 0:
            val_RaspberryPi = ser.readline()
            
            try:
                decoded_val = val_RaspberryPi.decode('utf-8').strip()
                
                # 四元数データをパース (i, j, k, real の順)
                quat_i, quat_j, quat_k, quat_real = map(float, decoded_val.split())
                
                # タイムスタンプ保存
                time_data.append(time.time())
                
                # 四元数を [x, y, z, w] の順に整理 (scipyの形式)
                quat = [quat_i, quat_j, quat_k, quat_real]
                
                # Rotationオブジェクトを作成
                r = R.from_quat(quat)
                
                # 回転行列を取得
                rotation_matrix = r.as_matrix()
                
                # 立方体の頂点を回転
                rotated_vertices = np.dot(points, rotation_matrix.T)
                
                # プロットをクリア
                ax.clear()
                
                # 回転後の立方体を描画
                ax.add_collection3d(
                    Poly3DCollection(
                        [rotated_vertices[face] for face in faces],
                        facecolors='cyan',
                        linewidths=1,
                        edgecolors='r',
                        alpha=0.7
                    )
                )
                
                # 座標軸を描画
                ax.quiver(0, 0, 0, 20, 0, 0, color='red', arrow_length_ratio=0.1, label='X')
                ax.quiver(0, 0, 0, 0, 20, 0, color='green', arrow_length_ratio=0.1, label='Y')
                ax.quiver(0, 0, 0, 0, 0, 20, color='blue', arrow_length_ratio=0.1, label='Z')
                
                # 軸の範囲を設定
                ax.set_xlim([-30, 30])
                ax.set_ylim([-30, 30])
                ax.set_zlim([-30, 30])
                
                # ラベルとタイトル
                ax.set_xlabel('X')
                ax.set_ylabel('Y')
                ax.set_zlabel('Z')
                ax.set_title('BNO085 姿勢表示 (SPI通信)')
                
                # プロットを更新
                plt.draw()
                plt.pause(0.001)
                
            except ValueError as ve:
                # パース失敗時（初期化メッセージなど）
                print(f"データ: {decoded_val}")
            except Exception as e:
                print(f"処理エラー: {e}")
        
except KeyboardInterrupt:
    print("\n終了します")
finally:
    ser.close()
    plt.close()
    print("シリアルポートを閉じました")
