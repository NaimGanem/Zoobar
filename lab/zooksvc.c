#include "http.h"
#include <err.h>
#include <regex.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netdb.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <sys/param.h>
#include <sys/types.h>
#include <sys/socket.h>


int main(int argc, char **argv)
{
    int my_socket;
    if (argc < 2)
        errx(1, "Wrong arguments");
    printf("✅ service zooksvc is running --Uid:%d Gid:%d --\n", getuid(), getgid());

    my_socket = atoi(argv[1]);
    if (my_socket <= 0)
        errx(1, "Invalid socket values: my_socket=%d", my_socket);
    for (;;) {
    char envp[4000];
    int socket_continue_conversation = -1;
    const char *errmsg;
    memset(envp,'\0', sizeof(envp));


    // receive socket and envp from zookd 
    ssize_t temp = recvfd(my_socket, envp, sizeof(envp), &socket_continue_conversation);
    if (temp <= 0 || socket_continue_conversation < 0)
        err(1, "recv_fd");

    switch (fork()) {
        case -1: // error 
            err(1, "fork");
        case 0: // child 
            // set envp 
            env_deserialize(envp, sizeof(envp));
            // get all headers 
            if ((errmsg = http_request_headers(socket_continue_conversation))) {
                http_err(socket_continue_conversation, 500, "http_request_headers: %s", errmsg);
            } else {
               http_serve(socket_continue_conversation, getenv("REQUEST_URI"));
            }
           return 0;
        default: // parent 
            close(socket_continue_conversation);
            break;
        }
    }
    return 0;
}