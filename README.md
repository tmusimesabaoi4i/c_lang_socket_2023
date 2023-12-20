#

```
sudo apt install autoconf autogen automake build-essential libasound2 libasound2-dev \
  libflac-dev libogg-dev libtool libvorbis-dev libopus-dev libmp3lame-dev \
  libmpg123-dev pkg-config python \
  libsndfile1-dev
```

#
gcc -lsndfile -lm -lasound -pthread server.c -o server
