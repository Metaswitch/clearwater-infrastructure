#include <sys/socket.h>
#include <sys/types.h>
#include <sys/un.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#define SOCKET_PATH "/tmp/clearwater_mgmt_namespace_socket"
#define MAX_PENDING 5

int send_file_descriptor(int socket, int fd_to_send)
{
  struct msghdr message;
  struct iovec iov[1];
  struct cmsghdr *control_message = NULL;
  char ctrl_buf[CMSG_SPACE(sizeof(int))];
  char data[1];

  memset(&message, 0, sizeof(struct msghdr));
  memset(ctrl_buf, 0, CMSG_SPACE(sizeof(int)));

  /* We are passing at least one byte of data so that recvmsg() will not return 0 */
  data[0] = ' ';
  iov[0].iov_base = data;
  iov[0].iov_len = sizeof(data);

  message.msg_name = NULL;
  message.msg_namelen = 0;
  message.msg_iov = iov;
  message.msg_iovlen = 1;
  message.msg_controllen =  CMSG_SPACE(sizeof(int));
  message.msg_control = ctrl_buf;

  control_message = CMSG_FIRSTHDR(&message);
  control_message->cmsg_level = SOL_SOCKET;
  control_message->cmsg_type = SCM_RIGHTS;
  control_message->cmsg_len = CMSG_LEN(sizeof(int));

  *((int *) CMSG_DATA(control_message)) = fd_to_send;

  return sendmsg(socket, &message, 0);
}


int create_server()
{
  struct sockaddr_un addr;
  int fd;

  if ((fd = socket(AF_LOCAL, SOCK_STREAM, 0)) < 0)
  {
    perror("Failed to create server unix socket");
    return fd;
  }

  memset(&addr, 0, sizeof(addr));

  addr.sun_family = AF_LOCAL;
  unlink(SOCKET_PATH);
  strcpy(addr.sun_path, SOCKET_PATH);

  if (bind(fd,
           (struct sockaddr *) &(addr),
           sizeof(addr)) < 0)
  {
    perror("Failed to bind server unix socket");
    return -1;
  }

  if (listen(fd, MAX_PENDING) < 0)
  {
    perror("Failed to listen on server unix socket");
    return -1;
  }

  for (;;)
  {
    int client_sock = accept(fd, NULL, NULL);

    int shared_sock = socket(AF_INET,SOCK_STREAM,0);
    send_file_descriptor(client_sock, shared_sock);

    close(shared_sock);
    close(client_sock);
  }

  return fd;
}

int main()
{
  create_server();
  return;
}
