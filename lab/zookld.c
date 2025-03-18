//zookld.c
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <sys/prctl.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <signal.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <err.h>

#define NUM_PROCESSES 6 // Define the number of processes to create
#define MAX_PROGRAM_NAME 75 //program path+name 
#define MAX_PROGRAM_REAL_NAME 25 //program file name

#define ZOOKD_SERV 0
#define ZOOKSVC_SERV 1
#define AUTH_SERV 2
#define BANK_SERV 3
#define FIREWALL_SERV 4
#define LOGER_SERV 5

char* http_server_port = "8080";

typedef struct {
    pid_t pid;          // Process ID
    uid_t uid;          // User ID (UID)
    gid_t target_gid;    // Target Group ID
    int socket_fd;      // Socket file descriptor
    int serv_type;
    char program[MAX_PROGRAM_NAME]; // Path to the program
    char program_name[MAX_PROGRAM_REAL_NAME]; // Path to the program
} ProcessInfo;

ProcessInfo processes[NUM_PROCESSES]; // Array to hold process info
int sockets[NUM_PROCESSES][2];        // Array to hold socket pairs

void start_process(ProcessInfo *process) {
    process->pid = fork();
    if (process->pid == 0) {
        // Child process
        char fd_str[10];
        sprintf(fd_str, "%d", process->socket_fd);

        // Perform chroot to the current directory
        if (chdir(".") < 0) {
            perror("chdir after chroot failed");
            exit(EXIT_FAILURE);
        }
        if (chroot(".") < 0) {
            perror("chroot failed");
            exit(EXIT_FAILURE);
        }
        
        if (setgid(process->target_gid) < 0) {
            perror("setgid failed");
            exit(EXIT_FAILURE);
        }
        if (setuid(process->uid) < 0) {
            perror("setuid failed");
            exit(EXIT_FAILURE);
        }

        char *python_path = "/usr/bin/python3";
        switch(process->serv_type)
        {
            case ZOOKD_SERV:
                char ZOOKSVC_SERV_fd_str[10];
                sprintf(ZOOKSVC_SERV_fd_str, "%d",sockets[ZOOKSVC_SERV][1]);//sending to zooksvc socket
                printf("start: %s %s %s %s UID:%d GID:%d \n",process->program ,fd_str, http_server_port, ZOOKSVC_SERV_fd_str, getuid(), getgid());

                if (execl(process->program, process->program_name, fd_str, http_server_port, ZOOKSVC_SERV_fd_str, NULL) == -1) {
                    perror("execl failed");
                    exit(EXIT_FAILURE);
                }
                break;
            case ZOOKSVC_SERV:
                printf("start: %s %s UID:%d GID:%d\n",process->program,fd_str, getuid(), getgid());

                if(execl(process->program, process->program_name, fd_str, NULL) == -1)
                {
                    perror("execl failed");
                    exit(EXIT_FAILURE);
                }
                break;
            case AUTH_SERV:
                char *arg1_auth = "dummy_fd";
                char *arg2_auth = "/tmp/authsvc.sock";

                printf("start: python3 %s %s %s UID:%d GID:%d \n",process->program,arg1_auth,arg2_auth, getuid(), getgid());
                if (execl(python_path, python_path, process->program, arg1_auth, arg2_auth, (char *)NULL) == -1) {
                    perror("execl failed");
                    exit(EXIT_FAILURE);
                }
                break;
            case BANK_SERV:
                char *arg1_bank = "dummy_fd";
                char *arg2_bank = "/tmp/banksvc.sock";

                printf("start: python3 %s %s %s UID:%d GID:%d\n",process->program,arg1_bank,arg2_bank, getuid(), getgid());
                if (execl(python_path, python_path, process->program, arg1_bank, arg2_bank, (char *)NULL) == -1) {
                    perror("execl failed");
                    exit(EXIT_FAILURE);
                }
                break;
            case FIREWALL_SERV:
                printf("start: python3 %s UID:%d GID:%d\n",process->program, getuid(), getgid());
                // Execute the Python script using execl
                if (execl(python_path, python_path, process->program, (char *)NULL) == -1) {
                    perror("execl failed");
                    exit(EXIT_FAILURE);
                }
                break;
            case LOGER_SERV:
                printf("start: python3 %s UID:%d GID:%d\n",process->program, getuid(), getgid());
                // Execute the Python script using execl
                if (execl(python_path, python_path, process->program, (char *)NULL) == -1) {
                    perror("execl failed");
                    exit(EXIT_FAILURE);
                }
                break;
            default:
                fprintf(stderr, "Unknown service type: %d\n", process->serv_type);
                exit(EXIT_FAILURE);
                break;
        }
        
        perror("execl failed");
        exit(EXIT_FAILURE);
    } else if (process->pid < 0) {
        perror("fork failed");
        exit(EXIT_FAILURE);
    }
}

void restart_process(ProcessInfo *process) {
    if (process->pid > 0) {
        kill(process->pid, SIGKILL);
        waitpid(process->pid, NULL, 0);
    }
    start_process(process);
}

void handle_child_exit(int sig) {
    int status;
    pid_t terminated_pid = waitpid(-1, &status, WNOHANG);

    for (int i = 0; i < NUM_PROCESSES; i++) {
        if (terminated_pid == processes[i].pid) {
            printf("Process '%s' terminated (PID: %d), restarting...\n", processes[i].program, processes[i].pid);
            restart_process(&processes[i]);
            break;
        }
    }
}
int main(int argc, char **argv) {
    if (argc < 2)
        errx(1, "Wrong arguments");

    // Ensure running as root
    if (getuid() != 0) {
        fprintf(stderr, "Must run as root\n");
    }
    http_server_port = argv[1];
    for (int i = 0; i < NUM_PROCESSES; i++) {
        if (i != 2 && i!=3 && i!=4 && i!=5 && (socketpair(AF_UNIX, SOCK_STREAM, 0, sockets[i]) < 0)) {
            perror("socketpair failed");
            exit(EXIT_FAILURE);
        }

        processes[i].socket_fd = sockets[i][0]; // Assign one end of the socket pair

        switch (i) {
            case ZOOKD_SERV:
                strncpy(processes[ZOOKD_SERV].program, "./zookd", MAX_PROGRAM_NAME);
                strncpy(processes[ZOOKD_SERV].program_name, "zookd", MAX_PROGRAM_REAL_NAME);
                processes[ZOOKD_SERV].uid = 5002;
                processes[ZOOKD_SERV].target_gid = 22221;
                processes[ZOOKD_SERV].serv_type = ZOOKD_SERV;
                break;
            case ZOOKSVC_SERV:
                strncpy(processes[ZOOKSVC_SERV].program, "./zooksvc", MAX_PROGRAM_NAME);
                strncpy(processes[ZOOKSVC_SERV].program_name, "zooksvc", MAX_PROGRAM_REAL_NAME);
                processes[ZOOKSVC_SERV].uid = 5003;
                processes[ZOOKSVC_SERV].target_gid = 11111;
                processes[ZOOKSVC_SERV].serv_type = ZOOKSVC_SERV;
                break;
            case AUTH_SERV:
                strncpy(processes[AUTH_SERV].program, "./zoobar/auth-server.py", MAX_PROGRAM_NAME);
                strncpy(processes[AUTH_SERV].program_name, "auth-server", MAX_PROGRAM_REAL_NAME);
                processes[AUTH_SERV].uid = 5006;
                processes[AUTH_SERV].target_gid = 11111;
                processes[AUTH_SERV].serv_type = AUTH_SERV;
                break;
            case BANK_SERV:
                strncpy(processes[BANK_SERV].program, "./zoobar/bank-server.py", MAX_PROGRAM_NAME);
                strncpy(processes[BANK_SERV].program_name, "bank-server", MAX_PROGRAM_REAL_NAME);
                processes[BANK_SERV].uid = 5005;
                processes[BANK_SERV].target_gid = 11111;
                processes[BANK_SERV].serv_type = BANK_SERV;
                break;
            case FIREWALL_SERV:
                strncpy(processes[FIREWALL_SERV].program, "./zoobar/firewall.py", MAX_PROGRAM_NAME);
                strncpy(processes[FIREWALL_SERV].program_name, "firewall", MAX_PROGRAM_REAL_NAME);
                processes[FIREWALL_SERV].uid = 5004;
                processes[FIREWALL_SERV].target_gid = 22221;
                processes[FIREWALL_SERV].serv_type = FIREWALL_SERV;
                break;
            case LOGER_SERV:
                strncpy(processes[LOGER_SERV].program, "./zoobar/loger.py", MAX_PROGRAM_NAME);
                strncpy(processes[LOGER_SERV].program_name, "loger", MAX_PROGRAM_REAL_NAME);
                processes[LOGER_SERV].uid = 5007;
                processes[LOGER_SERV].target_gid = 33333;
                processes[LOGER_SERV].serv_type = LOGER_SERV;
                break;
            default:
                fprintf(stderr, "Unexpected process index: %d\n", i);
                exit(1);
        }
    }

    // Handle child termination signals
    signal(SIGCHLD, handle_child_exit);

    // Start both processes
     for (int i = 0; i < NUM_PROCESSES; i++) {
        start_process(&processes[i]);
    }

    // Loader keeps running to monitor processes
    while (1) {
        pause(); // Wait for signals
    }

    return 0;
}
