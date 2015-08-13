#include <sys/socket.h>
#include <sys/types.h>
#include <sys/un.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
#include <unistd.h>

#define SOCKET_PATH "/tmp/clearwater_mgmt_namespace_socket"

static int recv_file_descriptor(int socket)
{
  int sent_fd;
  struct msghdr message;
  struct iovec iov[1];
  struct cmsghdr *control_message = NULL;
  char ctrl_buf[CMSG_SPACE(sizeof(int))];
  char data[1];
  int res;

  memset(&message, 0, sizeof(struct msghdr));
  memset(ctrl_buf, 0, CMSG_SPACE(sizeof(int)));

  /* For the dummy data */
  iov[0].iov_base = data;
  iov[0].iov_len = sizeof(data);

  message.msg_name = NULL;
  message.msg_namelen = 0;
  message.msg_control = ctrl_buf;
  message.msg_controllen = CMSG_SPACE(sizeof(int));
  message.msg_iov = iov;
  message.msg_iovlen = 1;

  if((res = recvmsg(socket, &message, 0)) <= 0)
  {
    fprintf(stderr, "recvmsg returned %d (%d %s)\n", res, errno, strerror(errno));
    return res;
  }

  /* Iterate through header to find if there is a file descriptor */
  for(control_message = CMSG_FIRSTHDR(&message);
      control_message != NULL;
      control_message = CMSG_NXTHDR(&message,
                                    control_message))
  {
    if( (control_message->cmsg_level == SOL_SOCKET) &&
        (control_message->cmsg_type == SCM_RIGHTS) )
    {
      return *((int *) CMSG_DATA(control_message));
    }
  }

  fprintf(stderr, "No socket received\n");
  return -1;
}

int get_magic_socket(char* host, char* port)
{
  struct sockaddr_un addr;
  int fd;

  printf("Get socket to %s:%s\n", host, port);

  if ((fd = socket(AF_LOCAL, SOCK_STREAM, 0)) < 0)
  {
    perror("Failed to create client socket");
    return fd;
  }

  memset(&addr, 0, sizeof(addr));

  addr.sun_family = AF_LOCAL;
  strcpy(addr.sun_path, SOCKET_PATH);

  if (connect(fd,
              (struct sockaddr *) &(addr),
              sizeof(addr)) < 0) {
    perror("Failed to connect to server\n");
    return -1;
  }

  char target[1024];
  sprintf(target, "%s:%s", host, port);

  if (send(fd, target, strlen(target), 0) < 0)
  {
    fprintf(stderr, "Error sending target '%s' to server: %s", target, strerror(errno));
    return -2;
  }

  int magic_sock = recv_file_descriptor(fd);

  return magic_sock;
}

int main(int argc, char** argv)
{
  if (argc < 3)
  {
    fprintf(stderr, "Usage is: %s host port\n", argv[0]);
    return -1;
  }

  int sock = get_magic_socket(argv[1], argv[2]);

  if (sock < 0)
  {
    return -2;
  }

  const char* msg = "Hello there\n";
  printf("Connected. Sending message\n");
  send(sock, msg, strlen(msg), 0);
  close(sock);

  return 0;
}
