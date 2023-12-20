import sys
import queue
import argparse
import threading

import socket

import pickle
import numpy as np

import sounddevice as sd
import soundfile as sf

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    'filename', metavar='FILENAME',
    help='audio file to be played back')
parser.add_argument(
    '-c', '--channels', type=int, default=1,
    help='number of channels to play sound (default: %(default)s)')
parser.add_argument(
    '-s', '--samplerate', type=int, default=44.1e3,
    help='sampling frequency (Hz) (default: %(default)s)')
parser.add_argument(
    '-b', '--blocksize', type=int, default=2048*2,
    help='block size (default: %(default)s)')
parser.add_argument(
    '-q', '--buffersize', type=int, default=20,
    help='number of blocks used for buffering (default: %(default)s)')

args = parser.parse_args(remaining)

if args.blocksize == 0:
    parser.error('blocksize must not be zero')
if args.buffersize < 1:
    parser.error('buffersize must be at least 1')

event = threading.Event()


f1 = sf.SoundFile(args.filename)
f2 = sf.SoundFile(args.filename)
f3 = sf.SoundFile(args.filename)
f4 = sf.SoundFile(args.filename)

def client_handler(conn,addr,f1,f2,f3,f4):
    """
    クライアントとの接続処理スレッド
    """
    try:                                          # 例外を処理する
        data_r = conn.recv(2**10)                 # クライアントより受信
        data_r = pickle.loads(data_r)             # データを読み込む

        if data_r == 'ok1':
            data1 = f1.read(args.blocksize)       # データの読み込み
            if not len(data1):                    # データが存在しない場合は閉じる
                f1.close()
                conn.close()                      # コネクションのクローズ
                sys.exit(0)
            else:
                data_s = pickle.dumps(data1)      # データを送信しやすい形にする
        elif data_r == 'ok2':
            data2 = f2.read(args.blocksize)       # データの読み込み
            if not len(data2):                    # データが存在しない場合は閉じる
                f2.close()
                conn.close()                      # コネクションのクローズ
                sys.exit(0)
            else:
                data_s = pickle.dumps(data2)      # データを送信しやすい形にする
        elif data_r == 'ok3':
            data3 = f3.read(args.blocksize)       # データの読み込み
            if not len(data3):                    # データが存在しない場合は閉じる
                f3.close()
                conn.close()                      # コネクションのクローズ
                sys.exit(0)
            else:
                data_s = pickle.dumps(data3)      # データを送信しやすい形にする
        elif data_r == 'ok4':
            data4 = f4.read(args.blocksize)       # データの読み込み
            if not len(data4):                    # データが存在しない場合は閉じる
                f4.close()
                conn.close()                      # コネクションのクローズ
                sys.exit(0)
            else:
                data_s = pickle.dumps(data4)      # データを送信しやすい形にする
        else: data_s = pickle.dumps(0)            # データを送信しやすい形にする

        data_s = data_s + pickle.dumps(np.ones(10)*9)       # フラグデータの作成
        conn.sendall(data_s)                                # メッセージの送信
        conn.close()                                        # コネクションのクローズ
    except BaseException as e:
        print(type(e).__name__ + ': ' + str(e))
        conn.close()                                        # コネクションのクローズ

if __name__ == "__main__":
    # HOST, PORT = "localhost", 9999
    # HOST, PORT = "133.10.104.56", 9999
    # HOST, PORT = "192.168.103.2", 9999
    HOST, PORT = "192.168.50.200", 9999

    timeout = args.blocksize * args.buffersize / args.samplerate

    try:                                                                # 例外を処理する
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:    # ソケットの作成
            s.bind((HOST, PORT))                                        # アドレスの設定
            s.listen()                                                  # 接続の待ち受け
            s.settimeout(10)                                            # コネクションの待ち時間を設定する

            while True:                                                 # 対応の繰り返し
                conn, addr = s.accept()                                 # 通信用ソケットの取得

                # スレッドの設定と起動
                p = threading.Thread(target = client_handler, args = (conn,addr,f1,f2,f3,f4))
                p.start()

    except BaseException as e:
        print(type(e).__name__ + ': ' + str(e))
