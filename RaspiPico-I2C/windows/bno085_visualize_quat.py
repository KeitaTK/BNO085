import serial
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial.transform import Rotation as R
import threading
import queue
import time
from datetime import datetime
import csv
import os

PORT = "COM11"
BAUDRATE = 115200

# 受信データを格納するキュー（クォータニオン、タイムスタンプのペア）
quat_queue = queue.Queue()

# CSV記録用データリスト
csv_data = []

# プログラム起動時刻
start_time = datetime.now()

# シリアル受信スレッド
def serial_thread():
    global csv_data, start_time
    print("[DEBUG] Serial thread starting...")
    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
        print(f"[DEBUG] Serial port {PORT} opened successfully")
    except Exception as e:
        print(f"[ERROR] Failed to open serial port: {e}")
        return
    
    pico_start_time = None  # Picoのモノトニック時刻の初期値
    while True:
        data = ser.readline().decode(errors="ignore").strip()
        try:
            parts = [float(x) for x in data.split()]
            if len(parts) == 5:  # クォータニオン(4) + タイムスタンプ(1)
                quat = parts[:4]
                pico_timestamp = parts[4]
                
                # 最初のデータでPicoの初期時刻を記録
                if pico_start_time is None:
                    pico_start_time = pico_timestamp
                    print(f"[INFO] Pico start time: {pico_start_time}")
                    print(f"[INFO] Pico timestamp precision: {len(str(pico_timestamp).split('.')[-1])} decimal places")
                
                # Windows起動時刻 + Picoの経過時間で正確なタイムスタンプ
                elapsed = pico_timestamp - pico_start_time
                accurate_timestamp = start_time.timestamp() + elapsed
                accurate_dt = datetime.fromtimestamp(accurate_timestamp)
                
                # CSV用データを記録
                csv_data.append([accurate_dt.isoformat(), *quat])
                
                # アニメーション用キューに追加
                quat_queue.put(quat)
                
                # 定期的にタイムスタンプの詳細をログ
                if len(csv_data) % 50 == 1:
                    print(f"[INFO] Records: {len(csv_data)}, Elapsed: {elapsed:.6f}s, Timestamp: {accurate_dt.isoformat()}")
            else:
                print(f"[ERROR] Expected 5 values, got {len(parts)}: {data}")
        except Exception as e:
            if data:
                print(f"[ERROR] Parse error: {e}, data: {data}")
            pass

# 3Dアニメーション描画
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.set_xlabel('X (Forward)')
ax.set_ylabel('Y (Left)')
ax.set_zlabel('Z (Up)')

# 立方体の頂点（右手系：前X, 左Y, 上Z）
cube = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]])
faces = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[0,3,7,4],[1,2,6,5]]

# Poly3DCollectionで面描画
cube_faces = [cube[face] for face in faces]
poly = Poly3DCollection(cube_faces, facecolors='cyan', edgecolors='b', linewidths=1, alpha=0.5)
ax.add_collection3d(poly)

# アニメーション更新関数
current_quat = [0,0,0,1]
calib_quat = None
quiver_artists = []

def on_key(event):
    global calib_quat
    if event.key == 'r':
        calib_quat = current_quat.copy()
        print(f"[INFO] Calibration! New origin quat: {calib_quat}")

fig.canvas.mpl_connect('key_press_event', on_key)

def update(frame):
    global current_quat, calib_quat, quiver_artists
    while not quat_queue.empty():
        current_quat = quat_queue.get()
    # キャリブレーション原点があれば相対回転
    if calib_quat is not None:
        r_calib = R.from_quat(calib_quat)
        r_current = R.from_quat(current_quat)
        r_rel = r_calib.inv() * r_current
        rot_cube = r_rel.apply(cube)
        rot_axes = r_rel.apply(np.eye(3))
    else:
        r = R.from_quat(current_quat)
        rot_cube = r.apply(cube)
        rot_axes = r.apply(np.eye(3))
    # Y軸の正負を逆転
    rot_cube[:,1] *= -1
    rot_axes[:,1] *= -1
    # pitch（X軸回転）も逆転
    rot_cube[:,0] *= -1
    rot_axes[:,0] *= -1
    new_faces = [rot_cube[face] for face in faces]
    poly.set_verts(new_faces)
    ax.set_xlim(-2,2)
    ax.set_ylim(-2,2)
    ax.set_zlim(-2,2)
    # 軸描画（中心から各軸方向に矢印）
    origin = np.array([0,0,0])
    # 前回のquiverを消す
    for artist in quiver_artists:
        try:
            artist.remove()
        except Exception:
            pass
    quiver_artists = []
    quiver_artists.append(ax.quiver(*origin, *rot_axes[0], length=1.5, color='r', arrow_length_ratio=0.2)) # X軸
    quiver_artists.append(ax.quiver(*origin, *rot_axes[1], length=1.5, color='g', arrow_length_ratio=0.2)) # Y軸
    quiver_artists.append(ax.quiver(*origin, *rot_axes[2], length=1.5, color='b', arrow_length_ratio=0.2)) # Z軸
    return [poly] + quiver_artists

# シリアル受信スレッド開始
threading.Thread(target=serial_thread, daemon=True).start()

# アニメーション開始
from matplotlib.animation import FuncAnimation
ani = FuncAnimation(fig, update, interval=50, blit=False, cache_frame_data=False)

try:
    plt.show()
finally:
    # プログラム終了時にCSVを保存
    if csv_data:
        # ダウンロードフォルダのパスを取得
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        # ファイル名: 日時-Quaternion.csv
        filename = start_time.strftime("%Y%m%d_%H%M%S") + "-Quaternion.csv"
        filepath = os.path.join(downloads_folder, filename)
        
        # CSVに保存
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Quat_I', 'Quat_J', 'Quat_K', 'Quat_Real'])
            writer.writerows(csv_data)
        
        print(f"\n[INFO] Data saved to: {filepath}")
        print(f"[INFO] Total records: {len(csv_data)}")
        
        # 最初と最後のデータを表示してタイムスタンプを確認
        if len(csv_data) > 0:
            print(f"[INFO] First record: {csv_data[0][0]}")
            print(f"[INFO] Last record: {csv_data[-1][0]}")
            
            # タイムスタンプの精度を確認
            first_ts = csv_data[0][0]
            if '.' in first_ts:
                decimal_part = first_ts.split('.')[-1].split('+')[0].split('-')[0]
                print(f"[INFO] Timestamp precision: {len(decimal_part)} decimal places")
    else:
        print("\n[WARN] No data collected")
