#
- 192.168.50.100
- 192.168.50.102
- 192.168.50.104
- 192.168.50.108

#
```
pi
```

```
wilwilwil
```

#
```
sudo apt install libasound2-dev
```

#
```
sudo apt install libsndfile1-dev
```

#
```
sudo apt install autoconf autogen automake build-essential libasound2 libasound2-dev \
  libflac-dev libogg-dev libtool libvorbis-dev libopus-dev libmp3lame-dev \
  libmpg123-dev pkg-config python \
  libsndfile1-dev
```

#
```
gcc client.c -o client -lsndfile -lm -lasound -pthread
```


#
```
gcc server.c -o server -lsndfile -lm -lasound -pthread
```

#
```
upower -i /org/freedesktop/UPower/devices/battery_BAT0
```
