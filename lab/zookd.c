/* dispatch daemon */

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
#include <arpa/inet.h>
#include <sys/un.h>  

static void process_client(int);
static int run_server(const char *portstr);
static int start_server(const char *portstr);

int my_socket;
int svc_socket;
char* sttp_port;

int check_ip_with_service(const char *client_ip) {
    pid_t pid;
    int status;
    pid = fork();
    if (pid < 0) {
        perror("Fork failed");
        return 1;
    }
    if (pid == 0) { 
        char *python_path = "/usr/bin/python3";
        execl(python_path, python_path, "/zoobar/firewall_C.py", client_ip, (char *)NULL);
        perror("execl failed");
        exit(1);
    } else { 
        waitpid(pid, &status, 0);
        if (WIFEXITED(status)) {
            int exit_code = WEXITSTATUS(status);
            if (exit_code == 1) {
                return 1;
            } else {
                return 0;
            }
        } else {
            printf("Python script did not terminate normally\n");
            return 1;
        }
    }
    return 1;
}

int main(int argc, char **argv)
{
    if (argc < 4)
        errx(1, "Wrong arguments");
    my_socket = atoi(argv[1]);
    svc_socket = atoi(argv[3]);
    if (my_socket <= 0 || svc_socket <= 0)
        errx(1, "Invalid socket values: my_socket=%d, svc_socket=%d", my_socket, svc_socket);
    sttp_port = argv[2];
    run_server(sttp_port);
}

/* socket-bind-listen idiom */

static int start_server(const char *portstr)
{
    struct addrinfo hints = {0}, *res;
    int sockfd;
    int e, opt = 1;
    printf("✅ service zookd is running --Uid:%d Gid:%d --\n", getuid(), getgid());
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE;

    if ((e = getaddrinfo(NULL, portstr, &hints, &res)))
        errx(1, "getaddrinfo: %s", gai_strerror(e));
    if ((sockfd = socket(res->ai_family, res->ai_socktype, res->ai_protocol)) < 0)
        err(1, "socket");
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)))
        err(1, "setsockopt");
    if (fcntl(sockfd, F_SETFD, FD_CLOEXEC) < 0)
        err(1, "fcntl");
    if (bind(sockfd, res->ai_addr, res->ai_addrlen))
        err(1, "bind");
    if (listen(sockfd, 5))
        err(1, "listen");
    freeaddrinfo(res);

    return sockfd;
}

static int run_server(const char *port) {
    int sockfd = start_server(port);
    for (;;)
    {
    struct sockaddr_storage client_addr;
    socklen_t client_len = sizeof(client_addr);
    int cltfd = accept(sockfd, (struct sockaddr *)&client_addr, &client_len);
	int pid;
	int status;

	if (cltfd < 0)
	    err(1, "accept");

	/* fork a new process for each client process, because the process
	 * builds up state specific for a client (e.g. cookie and other
	 * enviroment variables that are set by request). We want to get rid off
	 * that state when we have processed the request and start the next
	 * request in a pristine state.
         */
	switch ((pid = fork()))
	{
	case -1:
	    err(1, "fork");

	case 0:
        char client_ip[INET6_ADDRSTRLEN]; 
        if (client_addr.ss_family == AF_INET) {
            struct sockaddr_in *s = (struct sockaddr_in *)&client_addr;
            inet_ntop(AF_INET, &s->sin_addr, client_ip, sizeof(client_ip));
        } else if (client_addr.ss_family == AF_INET6) {
            struct sockaddr_in6 *s = (struct sockaddr_in6 *)&client_addr;
            inet_ntop(AF_INET6, &s->sin6_addr, client_ip, sizeof(client_ip));
        }
        if (!check_ip_with_service(client_ip)) {
            printf("zookd - this IP is blocked -  %s \n", client_ip);
            you_are_blocked(cltfd);
            close(cltfd);
            continue;  
        }
	    process_client(cltfd);
	    exit(0);
	    break;

	default:
	    close(cltfd);
	    pid = wait(&status);
	    if (WIFSIGNALED(status)) {
		printf("Child process %d terminated incorrectly, receiving signal %d\n",
		       pid, WTERMSIG(status));
	    }
	    break;
	}
    }
}

static void process_client(int fd)//dispacher
{
    static char env[4000];  /* static variables are not on the stack */
    static size_t env_len = 3999;
    char reqpath[4096];
    const char *errmsg;
    memset(env,'\0', sizeof(env));
    /* get the request line */
    if ((errmsg = http_request_line(fd, reqpath, env, &env_len)))
        return http_err(fd, 500, "http_request_line: %s", errmsg);
    
    int temp=sendfd(svc_socket, env, sizeof(env), fd);
    if(temp<0)
    {
        http_err(fd, 500, "Failed to send data");
    }
    close(fd);
} 

