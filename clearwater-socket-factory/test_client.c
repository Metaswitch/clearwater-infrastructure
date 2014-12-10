#include <sys/socket.h>
#include <sys/types.h>
#include <sys/un.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

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
    return res;

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

  return -1;
}

int get_magic_socket()
{
  struct sockaddr_un addr;
  int fd;

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

  int magic_sock = recv_file_descriptor(fd);

  return magic_sock;
}

int main(int argc, char** argv)
{
  int port;
  char* host;

  if (argc < 3) {
    fprintf(stderr, "Usage is: %s host port\n", argv[0]);
    return -1;
  }

  port = atoi(argv[2]);

  if ((port <= 0) || (port > 0xffff)) {
    fprintf(stderr, "Invalid port: %s", argv[1]);
    return -2;
  }

  host = argv[1];
  printf("Connect to %s:%d\n", host, port);

  int sock = get_magic_socket();

  struct sockaddr_in servaddr;
  bzero(&servaddr, sizeof(servaddr));
  servaddr.sin_family = AF_INET;
  servaddr.sin_port = htons(port);
  inet_pton(AF_INET, host, &(servaddr.sin_addr));

  if (connect(sock, (struct sockaddr*)&servaddr, sizeof(servaddr)) < 0) {
    perror("Could not connect to TCP server");
    return -3;
  }

  char* msg = "Hello there";
  printf("Connected. Sending message\n");
  send(sock, msg, strlen(msg), 0);

  close(sock);

  return 0;
}
