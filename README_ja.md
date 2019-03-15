# 2jciebl-bu-ble-raspberrypi
オムロン製環境センサ 2JCIE-BL 及び 2JCIE-BU から BLE インタフェース経由でセンシングデータを取得するサンプルプログラムです。  
各センサはそれぞれ以下の値を取得することができます。  

- [型2JCIE-BL 環境センサ（カバン型）](https://www.omron.co.jp/ecb/product-detail?partId=73062)  
![2JCIE-BL](2JCIE-BL.jpeg)  
    - 温度
    - 湿度
    - 照度
    - UV指数
    - 気圧
    - 騒音
    - 不快指数
    - 熱中症警戒度


- [型2JCIE-BU 環境センサ（USB型）](https://www.omron.co.jp/ecb/product-detail?partId=73063)  
![2JCIE-BU](2JCIE-BU.jpg)  
    - 温度
    - 湿度
    - 照度
    - 気圧
    - 騒音
    - 3軸加速度
    - eTVOC
    - 不快指数
    - 熱中症警戒度
    - 振動情報

## 言語
- [英語](./README.md)
- [日本語](./README_ja.md)

## 概要
- sample_2jciebl-bu-ble.py  
Bluetooth Low Energy で 環境センサの発する advertising packet をスキャンし、含まれるセンシングデータをログファイルに出力するサンプルプログラムです。  
起動時のオプションでデータ取得対象の環境センサ種別を指定します。  
※ 型2JCIE-BL 環境センサ（カバン型）を利用する場合は [事前設定](#link2) が必要です。  

    - 型2JCIE-BL 環境センサ（カバン型）  
    以下の値を出力します。
        - メーカー番号
        - 温度
        - 湿度
        - 照度
        - UV指数
        - 気圧
        - 騒音
        - eTVOC
        - eCO2

    - 型2JCIE-BU 環境センサ（USB型）
        - メーカー番号
        - シーケンス番号
        - 温度
        - 湿度
        - 照度
        - UV Index
        - 気圧
        - 騒音
        - 不快指数
        - 熱中症警戒度
        - バッテリーレベル

***デモ:***  
sample_2jciebl-bu-ble.py を実行するとコンソール上でセンシングデータを確認することができます。  
また、sample.log というログファイルが作成されデータが出力されます。

![demo_2jcie-bl.png](demo_2jcie-bl.png)

![demo_2jcie-bu.png](demo_2jcie-bu.png)

## インストール方法
1. 事前に依存関係のあるソフトウェアをインストールして下さい。  
    [依存関係](#link1)
2. ターミナルを開き、次のコマンドを実行します。  
    ```
    $ mkdir omron_sensor
    $ cd omron_sensor
    $ git clone https://github.com/omron-devhub/2jciebl-bu-ble-raspberrypi.git
    ```

## 使い方
サンプルプログラムを動作させる手順です。  
※型2JCIE-BL 環境センサ（カバン型） を利用する場合は [事前設定](#link2) が必要になります。

-  型2JCIE-BL 環境センサ（カバン型）  
ターミナルを開き、次のコマンドを実行します。  
    ```
    $ sudo python3 sample_2jciebl-bu-ble.py -m bag
    ```
    停止する際は、Ctrl + C を押します。

- 型2JCIE-BU 環境センサ（USB型）  
ターミナルを開き、次のコマンドを実行します。  
    ```
    $ sudo python3 sample_2jciebl-bu-ble.py -m usb
    ```
    停止する際は、Ctrl + C を押します。

## <a name="link1"></a>依存関係
2jciebl-bu-ble-raspberrypi には次に挙げるソフトウェアとの依存関係があります。
- [python3](https://www.python.org/)
- [pybluez](https://code.google.com/archive/p/pybluez/wikis/Documentation.wiki)

## Contributors
このリポジトリにContributeしていただいた方は[こちら](https://github.com/omron-devhub/2jciebl-bu-ble-raspberrypi/graphs/contributors)です。  
私たちはすべてのContributorに感謝します！

---

## <a name="link2">型2JCIE-BL 環境センサ（カバン型）事前設定</a>
![2JCIE-BL](2JCIE-BL.jpeg)  
### 事前準備
BLEデバイスのユーテリティアプリ "BLE Scanner" をスマートフォンにダウンロードします。
- [android版](https://play.google.com/store/apps/details?id=com.macdom.ble.blescanner&hl=ja)
- [iOS版](https://itunes.apple.com/jp/app/ble-scanner-4-0/id1221763603)

### モード変更
以下の手順で環境センサの Beacon mode を変更します。
1. Env(EnvSensor-BL01)というBLEデバイスを探して接続
1. CUSTOM SERVICE の 0C4C**3040**-7700-46F4-AA96D5E974E32A54 を開く
1. CUSTOM CHERACTERISTIC の 0C4C**3042**-7700-46F4-AA96D5E974E32A54 を開く
1. Write Value をタップし 0808A000000A0032**04**00 を書き込む
1. Read Value をタップし設定値が反映されているかを確認
1. 接続を切り、機器の名前が **EP-BL01** に変わっていることを確認 

### 計測間隔変更
以下の手順で環境センサの Measurement interval を変更します。
1. CUSTOM SERVICE の 0C4C**3010**-7700-46F4-AA96D5E974E32A54 を開く
1. CUSTOM CHERACTERISTIC の 0C4C**3011**-7700-46F4-AA96D5E974E32A54 を開く
1. Write Value をタップし 1〜3600sec の範囲で任意の値を書き込む  
例：1分の場合は 60sec なので "3C" を書き込む
1. Read Value をタップし設定値が反映されているかを確認