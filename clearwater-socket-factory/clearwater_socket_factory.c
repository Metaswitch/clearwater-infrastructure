#include <sys/socket.h>
#include <sys/types.h>
#include <sys/un.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <netdb.h>
#include <errno.h>

#define SOCKET_PATH "/tmp/clearwater_mgmt_namespace_socket"
#define MAX_PENDING 5

int get_shared_socket(char* target)
{
  int rc = 0;
  struct addrinfo hints;
  struct addrinfo* addrs = NULL;
  struct addrinfo* p;

  char* sep = strrchr(target, ':');

  if (sep == NULL)
  {
    fprintf(stderr, "  Bad target: %s\n", target);
    rc = -1;
    goto EXIT_LABEL;
  }

  *sep = 0;
  char* host = target;
  char* port = sep + 1;

  memset(&hints, 0, sizeof hints);
  hints.ai_family = AF_INET;
  hints.ai_socktype = SOCK_STREAM;

  if (getaddrinfo(host, port, &hints, &addrs) != 0)
  {
    fprintf(stderr, "  Could not resolve %s: %s\n", host, strerror(errno));
    rc = -2;
    goto EXIT_LABEL;
  }

  printf("  Attempting to connect\n");
  rc = -3;

  for (p = addrs; p != NULL; p = p->ai_next)
  {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0)
    {
      perror("Could not create shared socket");
      rc = -3;
      goto EXIT_LABEL;
    }

    /* Wait 30s for the connection to come up */
    struct timeval timeout;
    timeout.tv_sec = 30;
    timeout.tv_usec = 0;

    if (setsockopt(sock,
                   SOL_SOCKET,
                   SO_SNDTIMEO,
                   (char *)&timeout,
                   sizeof(timeout)) < 0)
    {
      perror("  Failed to set timeout on shared socket");
      rc = -4;
      close(sock);
      goto EXIT_LABEL;
    }

    if (connect(sock, p->ai_addr, p->ai_addrlen) < 0)
    {
      char str[INET_ADDRSTRLEN];
      inet_ntop(AF_INET,
                &(((struct sockaddr_in*)(p->ai_addr))->sin_addr),
                str,
                sizeof(str));
      fprintf(stderr, "    Could not connect to %s: %s\n", str, strerror(errno));
      close(sock);
    }
    else
    {
      /* Connection successful.*/
      rc = sock;
      break;
    }
  }

  if (rc < 0)
  {
    fprintf(stderr, "  All connections failed\n");
    goto EXIT_LABEL;
  }

  printf("  Shared socket connected\n");

EXIT_LABEL:

  freeaddrinfo(addrs);
  return rc;
}

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


void process_one_request(int listen_socket)
{
  int client_sock = accept(listen_socket, NULL, NULL);
  printf("Received new request\n");

  /*
   * The client should now tell us the address it wants to connect to in the
   * form `<host>:<port>`
   *
   * Wait at most 1s for this.
   */
  struct timeval timeout;
  timeout.tv_sec = 1;
  timeout.tv_usec = 0;

  if (setsockopt(client_sock, SOL_SOCKET, SO_SNDTIMEO, (char *)&timeout, sizeof(timeout)) < 0)
  {
    perror("  Could not set timeout on client socket");
    close(client_sock);
    return;
  }

  char buf[1024];
  size_t len = recv(client_sock, buf, sizeof(buf), 0);

  if (len <= 0)
  {
    perror("  Could not read target address");
    close(client_sock);
    return;
  }
  else if (len >= sizeof(buf))
  {
    fprintf(stderr, "  Target address is too long (%lu)\n", len);
    close(client_sock);
    return;
  }

  /* NUL temrinate the target string */
  buf[len] = 0;
  printf("  Asked to connect to %s\n", buf);

  int shared_sock = get_shared_socket(buf);

  if(shared_sock < 0)
  {
    close(client_sock);
    return;
  }

  send_file_descriptor(client_sock, shared_sock);

  close(shared_sock);
  close(client_sock);
}


int create_server()
{
  struct sockaddr_un addr;
  int fd;

  printf("Starting server\n");

  if ((fd = socket(AF_LOCAL, SOCK_STREAM, 0)) < 0)
  {
    perror("Failed to create server unix socket");
    return fd;
  }

  memset(&addr, 0, sizeof(addr));

  addr.sun_family = AF_LOCAL;
  strcpy(addr.sun_path, SOCKET_PATH);

  unlink(SOCKET_PATH);

  if (bind(fd,
           (struct sockaddr *) &(addr),
           sizeof(addr)) < 0)
  {
    perror("Failed to bind server unix socket");
    return -1;
  }

  /* chmod the socket so that any process can connect to it */
  chmod(SOCKET_PATH, 0777);

  if (listen(fd, MAX_PENDING) < 0)
  {
    perror("Failed to listen on server unix socket");
    return -1;
  }

  printf("Listening for requests\n");

  for (;;)
  {
    process_one_request(fd);
  }

  return fd;
}

int main()
{
  create_server();
  return;
}
