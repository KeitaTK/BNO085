import serial
import numpy as np

import serial
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial.transform import Rotation as R
import threading
import queue
import time

PORT = "COM11"
BAUDRATE = 115200

# 受信データを格納するキュー
quat_queue = queue.Queue()

# シリアル受信スレッド
def serial_thread():
    ser = serial.Serial(PORT, BAUDRATE, timeout=1)
    while True:
        data = ser.readline().decode(errors="ignore").strip()
        try:
            parts = [float(x) for x in data.split()]
            if len(parts) == 4:
                quat_queue.put(parts)
        except:
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


# キャリブレーション用クォータニオン
current_quat = [0,0,0,1]
calib_quat = None



def on_key(event):
    global calib_quat
    if event.key == 'r':
        calib_quat = current_quat.copy()
        print(f"[INFO] Calibration! New origin quat: {calib_quat}")

fig.canvas.mpl_connect('key_press_event', on_key)

def update(frame):
    global current_quat, calib_quat
    while not quat_queue.empty():
        current_quat = quat_queue.get()
    # キャリブレーション原点があれば相対回転
    if calib_quat is not None:
        r_calib = R.from_quat(calib_quat)
        r_current = R.from_quat(current_quat)
        r_rel = r_calib.inv() * r_current
        rot_cube = r_rel.apply(cube)
    else:
        r = R.from_quat(current_quat)
        rot_cube = r.apply(cube)
    # Y軸の正負を逆転
    rot_cube[:,1] *= -1
    # pitch（X軸回転）も逆転
    rot_cube[:,0] *= -1
    new_faces = [rot_cube[face] for face in faces]
    poly.set_verts(new_faces)
    ax.set_xlim(-2,2)
    ax.set_ylim(-2,2)
    ax.set_zlim(-2,2)
    return [poly]

# シリアル受信スレッド開始
threading.Thread(target=serial_thread, daemon=True).start()

# アニメーション開始
from matplotlib.animation import FuncAnimation
ani = FuncAnimation(fig, update, interval=50, blit=False, cache_frame_data=False)
plt.show()
