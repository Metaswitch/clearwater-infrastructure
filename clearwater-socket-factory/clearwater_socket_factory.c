#include <sys/socket.h>
#include <sys/types.h>
#include <sys/un.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <netdb.h>
#include <errno.h>
#include <time.h>
#include <stdarg.h>

#define SOCKET_PATH "/tmp/clearwater_mgmt_namespace_socket"
#define MAX_PENDING 5

#define LOG_FILENAME "/var/log/clearwater-socket-factory.log"
FILE* LOG_FILE = NULL;

void write_timestamp(FILE* stream)
{
  time_t t;
  time(&t);
  struct tm* time_info = localtime(&t);

  char buffer[64];
  strftime(buffer, sizeof(buffer), "%Y:%m:%d %H:%M:%S: ", time_info);
  fputs(buffer, stream);
}


void logmsg(char* format, ...)
{
  write_timestamp(LOG_FILE);

  va_list args;
  va_start(args, format);
  vfprintf(LOG_FILE, format, args);
  va_end(args);

  fputs("\n", LOG_FILE);
  fflush(LOG_FILE);
}


void logerrno(char* format, ...)
{
  write_timestamp(LOG_FILE);

  va_list args;
  va_start(args, format);
  vfprintf(LOG_FILE, format, args);
  va_end(args);

  fprintf(LOG_FILE, ": %d %s\n", errno, strerror(errno));
  fflush(LOG_FILE);
}


int get_shared_socket(char* target)
{
  int rc = 0;
  struct addrinfo hints;
  struct addrinfo* addrs = NULL;
  struct addrinfo* p;

  /*
   * Parse the target string. It will be of the form `<host>:<port>`.
   *
   * Note that the socket factory currently only supports IPv4 addresses, so we
   * don't make any attempts to de-bracket an IPv6 address. Also we request IPv4
   * addresses from `getaddrinfo` below.
   */
  char* sep = strrchr(target, ':');

  if (sep == NULL)
  {
    logmsg("Bad target: %s", target);
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
    logerrno("Could not resolve %s", host);
    rc = -2;
    goto EXIT_LABEL;
  }

  logmsg("Attempting to connect");
  rc = -3;

  for (p = addrs; p != NULL; p = p->ai_next)
  {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0)
    {
      logerrno("Could not create shared socket");
      rc = -4;
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
      logerrno("Failed to set timeout on shared socket");
      rc = -5;
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
      logerrno("Could not connect to %s", str);
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
    logmsg("All connections failed");
    goto EXIT_LABEL;
  }

  logmsg("Shared socket connected");

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
  logmsg("Received new request");

  /*
   * The client should now tell us the address it wants to connect to.  Wait at
   * most 1s for this.
   */
  struct timeval timeout;
  timeout.tv_sec = 1;
  timeout.tv_usec = 0;

  if (setsockopt(client_sock, SOL_SOCKET, SO_SNDTIMEO, (char *)&timeout, sizeof(timeout)) < 0)
  {
    logerrno("Could not set timeout on client socket");
    close(client_sock);
    return;
  }

  char buf[1024];
  size_t len = recv(client_sock, buf, sizeof(buf), 0);

  if (len <= 0)
  {
    logerrno("Could not read target address");
    close(client_sock);
    return;
  }
  else if (len >= sizeof(buf))
  {
    logmsg("Target address is too long (%lu)", len);
    close(client_sock);
    return;
  }

  /* NUL terminate the target string */
  buf[len] = 0;
  logmsg("Asked to connect to %s", buf);

  int shared_sock = get_shared_socket(buf);

  if (shared_sock < 0)
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

  LOG_FILE = fopen(LOG_FILENAME, "a");
  if (LOG_FILE == NULL)
  {
    fprintf(stderr, "Could not open %s for writing", LOG_FILENAME);
    return -1;
  }

  logmsg("Starting server");

  if ((fd = socket(AF_LOCAL, SOCK_STREAM, 0)) < 0)
  {
    logerrno("Failed to create server UNIX socket");
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
    logerrno("Failed to bind server UNIX socket");
    return -1;
  }

  /* Allow other processes to connect to the socket */
  chmod(SOCKET_PATH, 0777);

  if (listen(fd, MAX_PENDING) < 0)
  {
    logerrno("Failed to listen on server UNIX socket");
    return -1;
  }

  logmsg("Listening for requests");

  for (;;)
  {
    process_one_request(fd);
  }

  return fd;
}

int main()
{
  return create_server();
}
