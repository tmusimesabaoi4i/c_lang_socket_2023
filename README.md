#
- python : python通信プログラム
- python_time : 時間計測(python)
- socket_thread : c通信プログラム
- socket_thread_buffre
- socket_thread_time : 時間計測(c)

#
- 192.168.50.100
- 192.168.50.102
- 192.168.50.104
- 192.168.50.108

#
```
sudo rm -rf /var/lib/apt/lists/*
```

```
sudo apt update
```

#
```
pi
```

```
wilwilwil
```

#
```
sudo apt install autoconf autogen automake build-essential libasound2 libasound2-dev \
  libflac-dev libogg-dev libtool libvorbis-dev libopus-dev libmp3lame-dev \
  libmpg123-dev pkg-config \
  libasound2-dev libsndfile1-dev pulseaudio alsa-utils 
```

```
alsamixer 
```

```
aplay -l
```

#
```
gcc client.c -o client -lsndfile -lm -lasound -pthread
```

```
gcc server.c -o server -lsndfile -lm -lasound -pthread
```

#
```
upower -i /org/freedesktop/UPower/devices/battery_BAT0
```
