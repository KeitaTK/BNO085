import serial
import time
import numpy as np
from scipy.spatial.transform import Rotation as R
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
import matplotlib.pyplot as plt

# シリアル通信の設定
ser = serial.Serial('COM4', 115200)

# データを格納するリスト
time_data = []

# 3Dプロットの初期化
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# 立方体の面を定義
faces = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4],
         [2, 3, 7, 6], [0, 3, 7, 4], [1, 2, 6, 5]]

while True:
    val_RaspberryPi = ser.readline()
    decoded_val = val_RaspberryPi.decode()

    try:
        quat_i, quat_j, quat_k, quat_real = map(float, decoded_val.split())
        time_data.append(time.time())

        # クォータニオンの順序を整理
        quat = [quat_i, quat_j, quat_k,quat_real]

        # Rotationオブジェクトを作成
        r = R.from_quat(quat)

        # 回転行列を取得
        rotation_matrix = r.as_matrix()
        # print(rotation_matrix)

        points = np.array([[-2, -1, -0.5],
                   [2, -1, -0.5 ],
                   [2, 1, -0.5],
                   [-2, 1, -0.5],
                   [-2, -1, 0.5],
                   [2, -1, 0.5],
                   [2, 1, 0.5],
                   [-2, 1, 0.5]])
        
        V = points
        V = V * 10

        rotated_vertices = np.dot(V,rotation_matrix.T)

        # 元の頂点と回転後の頂点を表示
        # print("元の頂点:\n", V)
        # print("回転後の頂点:\n", rotated_vertices)

         # プロットをクリア
        ax.clear()

        # 回転後の立方体を描画
        ax.add_collection3d(Poly3DCollection([rotated_vertices[face] for face in faces], facecolors='cyan', linewidths=1, edgecolors='r', alpha=1))

        # 軸の範囲を設定
        ax.set_xlim([-20, 20])
        ax.set_ylim([-20, 20])
        ax.set_zlim([-20, 20])

        # プロットを更新
        plt.pause(0.000001)

    except ValueError:
        print("", decoded_val)

ser.close()
