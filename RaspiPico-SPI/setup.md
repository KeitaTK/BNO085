# BNO085 SPI通信セットアップガイド (Raspberry Pi Pico W)

## 概要
このガイドでは、Raspberry Pi Pico WとBNO085 IMUセンサーをSPI通信で接続し、姿勢データを取得・可視化するための環境構築手順を説明します。

## 必要なハードウェア

### 部品リスト
1. **Raspberry Pi Pico W** (または Raspberry Pi Pico)
2. **BNO085 IMUセンサー** (Hillcrest Laboratories製)
3. **ブレッドボードとジャンパーワイヤ**
4. **USB Type-Cケーブル** (Pico接続用)

## 配線図

以下の配線で接続してください:

| BNO085ピン | Pico W GPIO | 説明 |
|-----------|-------------|------|
| Vin | 3.3V | 電源 |
| GND | GND | グランド |
| SCL | GP18 | SPI Clock |
| SDA | GP16 | MISO (Master In Slave Out) |
| DI | GP19 | MOSI (Master Out Slave In) |
| CS | GP17 | Chip Select (チップセレクト) |
| INT | GP20 | 割り込み |
| RST | GP21 | リセット |
| PO/P1 | 3.3V | **SPI モード選択** (重要!) |

### 重要な注意点
- **PO/P1ピンを3.3Vに接続することで、BNO085がSPIモードで動作します**
- PO/P1をGNDに接続するとI2Cモードになります
- SDA/SCLのピン名はI2C用ですが、SPIモードではMISO/SCKとして機能します

## Raspberry Pi Pico W 側のセットアップ

### 1. CircuitPythonのインストール

#### 1.1 CircuitPythonファームウェアのダウンロード
1. [CircuitPython公式サイト](https://circuitpython.org/board/raspberry_pi_pico_w/)にアクセス
2. 最新の安定版 (.uf2ファイル) をダウンロード

#### 1.2 ファームウェアの書き込み
1. Pico WのBOOTSELボタンを押しながらUSBケーブルを接続
2. `RPI-RP2`というドライブが表示される
3. ダウンロードした`.uf2`ファイルをドラッグ&ドロップ
4. Picoが自動的に再起動し、`CIRCUITPY`ドライブが表示される

### 2. 必要なライブラリのインストール

#### 2.1 CircuitPythonライブラリバンドルのダウンロード
1. [CircuitPython Library Bundle](https://circuitpython.org/libraries)にアクセス
2. CircuitPythonのバージョンに合ったBundle (.zip) をダウンロード
3. ZIPファイルを解凍

#### 2.2 必要なライブラリをCIRCUITPYドライブにコピー
`CIRCUITPY`ドライブの`lib`フォルダに以下をコピー:

```
CIRCUITPY/
├── lib/
│   ├── adafruit_bno08x/
│   │   ├── __init__.py
│   │   ├── spi.py
│   │   └── (その他のファイル)
│   └── adafruit_bus_device/
│       ├── __init__.py
│       ├── spi_device.py
│       └── (その他のファイル)
└── (その他のファイル)
```

**必要なライブラリ:**
- `adafruit_bno08x` (BNO085ドライバ)
- `adafruit_bus_device` (SPIデバイス通信用)

### 3. Picoプログラムの配置

#### 3.1 main.pyのコピー
`RaspiPico-SPI/main.py`を`CIRCUITPY`ドライブのルートにコピーし、`code.py`にリネーム:

```
CIRCUITPY/
├── code.py  (main.pyからリネーム)
└── lib/
    └── (ライブラリ群)
```

#### 3.2 動作確認
- Picoが自動的にプログラムを実行
- シリアルコンソール (Thonny, PuTTY等) で四元数データが出力されることを確認

```
BNO085 initializing...
BNO085 initialized successfully!
Starting sensor readings...

0.123456 -0.234567 0.345678 0.901234
0.124567 -0.235678 0.346789 0.902345
...
```

## Windows側のセットアップ

### 1. Pythonのインストール
1. [Python公式サイト](https://www.python.org/downloads/)から Python 3.8以降をダウンロード
2. インストール時に「Add Python to PATH」にチェック

### 2. 必要なPythonライブラリのインストール

コマンドプロンプトまたはPowerShellで以下を実行:

```powershell
pip install pyserial numpy scipy matplotlib
```

**インストールされるライブラリ:**
- `pyserial` (シリアル通信)
- `numpy` (数値計算)
- `scipy` (回転行列計算)
- `matplotlib` (3D可視化)

### 3. COMポートの確認

#### 3.1 デバイスマネージャーで確認
1. Windows検索で「デバイスマネージャー」を開く
2. 「ポート (COMとLPT)」を展開
3. `USB Serial Device (COM4)`などの表示を確認
4. `visualize_spi.py`の`SERIAL_PORT`を該当のCOMポートに変更

```python
SERIAL_PORT = 'COM4'  # 環境に応じて変更
```

### 4. プログラムの実行

```powershell
cd C:\Users\taki\Local\local\BNO085\RaspiPico-SPI
python visualize_spi.py
```

正常に動作すると、3D立方体がBNO085の姿勢に応じて回転します。

## トラブルシューティング

### Pico側

#### 問題1: BNO085が初期化できない
**原因:**
- 配線ミス
- PO/P1ピンが3.3Vに接続されていない (I2Cモードになっている)
- ライブラリが正しくインストールされていない

**解決策:**
1. 配線を再確認 (特にPO/P1ピンを確認)
2. GP17 (CS) がHighになっているか確認
3. `lib`フォルダに`adafruit_bno08x`と`adafruit_bus_device`があるか確認

#### 問題2: データが出力されない
**原因:**
- センサーの初期化失敗
- SPIクロック周波数が高すぎる

**解決策:**
1. ボーレートを下げる: `baudrate=1000000` (1MHz)
2. リセットピンを確認
3. デバッグモードを有効化: `debug=True`

### Windows側

#### 問題1: シリアルポートが開けない
**原因:**
- COMポート番号が間違っている
- 他のアプリケーションがポートを使用中

**解決策:**
1. デバイスマネージャーでCOMポート番号を確認
2. Thonny、Arduino IDE等のシリアルモニタを閉じる
3. Picoを再接続

#### 問題2: ModuleNotFoundError
**原因:**
- 必要なライブラリがインストールされていない

**解決策:**
```powershell
pip install --upgrade pyserial numpy scipy matplotlib
```

#### 問題3: 3D表示が更新されない
**原因:**
- データのパースエラー
- Matplotlibのバックエンド問題

**解決策:**
1. シリアルコンソールで生データを確認
2. 別のバックエンドを試す:
```python
import matplotlib
matplotlib.use('TkAgg')  # またはQt5Agg
```

## 参考リンク

### 公式ドキュメント
- [CircuitPython公式](https://circuitpython.org/)
- [Adafruit BNO08x Library](https://github.com/adafruit/Adafruit_CircuitPython_BNO08x)
- [BNO085データシート](https://www.ceva-dsp.com/product/bno080-085/)

### チュートリアル
- [CircuitPython Getting Started](https://learn.adafruit.com/welcome-to-circuitpython)
- [Raspberry Pi Pico W Guide](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)

## ライセンスとクレジット

このプロジェクトは以下のライブラリを使用しています:
- **Adafruit CircuitPython BNO08x** (MIT License)
- **Adafruit Bus Device** (MIT License)

## サポート

問題が解決しない場合は、以下を確認してください:
1. CircuitPythonのバージョンとライブラリバージョンの互換性
2. BNO085のファームウェアバージョン
3. 配線の接続とはんだ付けの品質

---

**作成日:** 2025年12月8日  
**対象:** Raspberry Pi Pico W + BNO085 (SPIモード)
