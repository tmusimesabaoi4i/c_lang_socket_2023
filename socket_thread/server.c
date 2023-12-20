#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <pthread.h>
#include <sndfile.h>

#define PORT 8080
#define BUFFER_SIZE 4096

SNDFILE* open_sound_file(char* filename, SF_INFO* sfinfo) {
    SNDFILE *sndfile = sf_open(filename, SFM_READ, sfinfo);
    if (sndfile == NULL) {
        fprintf(stderr, "サウンドファイルを開けません: %s\n", sf_strerror(NULL));
        exit(EXIT_FAILURE);
    }
    return sndfile;
}

void error(char *message) {
    fprintf(stderr, "エラー: %s (%d: %s)\n", message, errno, strerror(errno));
    exit(EXIT_FAILURE);
}

void* handle_client(void* arg) {
    int client_socket = *((int**)arg)[0];
    char* filename = ((char**)arg)[1];

    struct sockaddr_in client_address;
    socklen_t client_address_len = sizeof(client_address);
    if (getpeername(client_socket, (struct sockaddr*)&client_address, &client_address_len) == -1)
        error("クライアントの情報を取得できません");
    printf("クライアント %s が接続しました\n", inet_ntoa(client_address.sin_addr));

    SF_INFO sfinfo;
    SNDFILE* sndfile = open_sound_file(filename, &sfinfo);
    int frames_read;
    char buffer[BUFFER_SIZE];
    while ((frames_read = sf_read_float(sndfile, (float *)buffer, BUFFER_SIZE/4)) > 0) {
        int bytes_sent = 0;
        while (bytes_sent < frames_read * 4) {
            int result = send(client_socket, buffer + bytes_sent, frames_read * 4 - bytes_sent, 0);
            if (result == -1)
                error("オーディオデータを送信できません");
            bytes_sent += result;
        }
    }

    sf_close(sndfile);
    close(client_socket);
    return NULL;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "使い方: %s <ファイル名>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    int server_fd, new_socket;
    struct sockaddr_in address;
    int addrlen = sizeof(address);

    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == -1)
        error("ソケットを作成できません");

    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt)) == -1)
        error("ソケットオプションを設定できません");

    memset(&address, 0, sizeof(address));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) == -1)
        error("ソケットをバインドできません");

    if (listen(server_fd, 3) == -1)
        error("接続のリッスンができません");

    pthread_t threads[10];
    int num_threads = 0;
    while (1) {
        if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) == -1)
            error("接続要求を受け入れられません");

        if (num_threads >= 10) {
            fprintf(stderr, "クライアントの最大数を超えました\n");
            close(new_socket);
        } else {
            void** args = malloc(2 * sizeof(void*));
            args[0] = malloc(sizeof(int));
            *((int*)args[0]) = new_socket;
            args[1] = argv[1];
            if (pthread_create(&threads[num_threads], NULL, handle_client, args) != 0)
                error("スレッドを作成できません");
            num_threads++;
        }
    }

    close(server_fd);
    return 0;
}
