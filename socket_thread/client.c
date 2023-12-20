#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <alsa/asoundlib.h>

#define PORT 8080
#define BUFFER_SIZE 4096

// gcc client.c -o client -lasound
// ./client <server IP address>

// エラー処理用の関数
void error(char *message) {
    fprintf(stderr, "エラー: %s (%d: %s)\n", message, errno, strerror(errno));
    exit(EXIT_FAILURE);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "使い方: %s <サーバーIPアドレス>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    int sock;
    struct sockaddr_in serv_addr;
    char buffer[BUFFER_SIZE];

    // ソケットファイルディスクリプタを作成する
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) == -1)
        error("ソケットを作成できません");

    // サーバーアドレスを設定する
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);
    if (inet_pton(AF_INET, argv[1], &serv_addr.sin_addr) <= 0)
        error("無効なIPアドレスです");

    // サーバーに接続する
    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) == -1)
        error("サーバーに接続できません");

    // ALSAオーディオ出力を設定する
    snd_pcm_t *handle;
    snd_pcm_hw_params_t *params;
    unsigned int sample_rate = 44100;
    int channels = 1;
    snd_pcm_uframes_t buffer_frames = 512;
    int dir;

    if (snd_pcm_open(&handle, "default", SND_PCM_STREAM_PLAYBACK, 0) < 0)
        error("ALSAオーディオデバイスを開けません");

    if (snd_pcm_hw_params_malloc(&params) < 0)
        error("ALSAハードウェアパラメータを割り当てられません");

    if (snd_pcm_hw_params_any(handle, params) < 0)
        error("ALSAハードウェアパラメータを初期化できません");

    if (snd_pcm_hw_params_set_access(handle, params, SND_PCM_ACCESS_RW_INTERLEAVED) < 0)
        error("ALSAアクセスタイプを設定できません");

    if (snd_pcm_hw_params_set_format(handle, params, SND_PCM_FORMAT_FLOAT_LE) < 0)
        error("ALSAサンプルフォーマットを設定できません");

    if (snd_pcm_hw_params_set_channels(handle, params, channels) < 0)
        error("ALSAチャンネル数を設定できません");

    if (snd_pcm_hw_params_set_rate_near(handle, params, &sample_rate, &dir) < 0 )
     error("ALSAサンプルレートを設定できません");

    if (snd_pcm_hw_params_set_buffer_size_near(handle, params, &buffer_frames) < 0)
        error("ALSAバッファサイズを設定できません");

    if (snd_pcm_hw_params(handle, params) < 0)
        error("ALSAハードウェアパラメータを設定できません");

    snd_pcm_hw_params_free(params);

    if (snd_pcm_prepare(handle) < 0)
        error("ALSAオーディオデバイスを準備できません");

    // オーディオデータを受信して出力する
    int bytes_received;
    while ((bytes_received = recv(sock, buffer, BUFFER_SIZE, 0)) > 0) {
        snd_pcm_sframes_t frames_written = snd_pcm_writei(handle, buffer, bytes_received / 4);
        if (frames_written < 0)
            frames_written = snd_pcm_recover(handle, frames_written, 0);
        if (frames_written < 0)
            error("ALSAデバイスにオーディオデータを書き込めません");
        if (frames_written < bytes_received / 4)
            printf("警告: 短い書き込み (予期したフレーム数: %d、書き込んだフレーム数: %ld)\n", bytes_received / 4, frames_written);
    }

    // クリーンアップ
    snd_pcm_drain(handle);
    snd_pcm_close(handle);
    close(sock);
    return 0;
}
