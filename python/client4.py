import sys
import queue
import argparse
import threading

import socket

import pickle
import numpy as np

import sounddevice as sd

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
    '-d', '--device', type=int_or_str,
    help='output device (numeric ID or substring)')
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

q = queue.Queue(maxsize=args.buffersize)
event = threading.Event()

def callback(outdata, frames, time, status):
    assert frames == args.blocksize
    if status.output_underflow:
        print('Output underflow: increase blocksize?', file=sys.stderr)
        raise sd.CallbackAbort
    assert not status
    try:
        data = q.get_nowait()
    except queue.Empty as e:
        print('Buffer is empty: increase buffersize?', file=sys.stderr)
        raise sd.CallbackAbort from e
    if len(data) < len(outdata):
        outdata[:len(data)] = data
        outdata[len(data):].fill(0)
        raise sd.CallbackStop
    else:
        outdata[:] = data

if __name__ == "__main__":
    # HOST, PORT = "localhost", 9999
    # HOST, PORT = "133.10.104.56", 9999
    # HOST, PORT = "192.168.103.2", 9999
    HOST, PORT = "192.168.50.200", 9999

    timeout = args.blocksize * args.buffersize / args.samplerate

    zerodata = np.zeros((args.blocksize,args.channels), dtype=np.float32)
    for _ in range(args.buffersize):# Pre-fill queue
        q.put_nowait(zerodata)

    stream = sd.OutputStream(
            samplerate=args.samplerate,
            blocksize=args.blocksize,
            device=args.device,
            channels=args.channels,
            dtype='float32',
            latency='high',
            # extra_settings=None,
            callback=callback,
            finished_callback=event.set,
            # clip_off=None,
            # dither_off=None,
            # never_drop_input=None,
            # prime_output_buffers_using_stream_callback=None
            )

    try:                                                                        # 例外を処理する
        with stream:
            while True:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:    # ソケット通信を開始する
                    s.settimeout(10)                                            # コネクションの待ち時間を設定する
                    try:
                        s.connect((HOST, PORT))                                 # サーバとの接続
                    except:
                        sys.exit(0)                                             # プログラムの終了
                    s.sendall(pickle.dumps('ok4'))                              # サーバへのメッセージの送信
                    data_r = bytes(0)
                    while True:
                        data = s.recv(2**10)                                    # サーバからのメッセージの受信
                        if not data: sys.exit(0)                                # データが取得できない場合は終了
                        else: data_r = data_r + data
                        if data_r[-10:-1] == b'\x00\x00\x00"@\x94t\x94b':       # pickle.dumps(np.ones(10)*9)
                            break
                    data_r = pickle.loads(data_r)                               # データを読み込む
                data_r = data_r.reshape(-1, args.channels)                      # データを正しい形にする
                q.put(data_r, timeout=timeout)
            event.wait()                                                        # Wait until playback is finished
    except BaseException as e:
        print(type(e).__name__ + ': ' + str(e))
