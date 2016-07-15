#include <sys/un.h>
#include <stdlib.h>
#include <stdio.h>
#include <netdb.h>
#include <errno.h>
#include <time.h>
#include <stdarg.h>
#include <poll.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <getopt.h>

#include <string>
#include <vector>
#include <algorithm>
#include <boost/algorithm/string/classification.hpp>
#include <boost/algorithm/string/split.hpp>

const int MAX_PENDING = 5;

const char* LOG_FILENAME = "/var/log/clearwater-socket-factory.log";
FILE* LOG_FILE = NULL;
const char *nsstring = NULL;

void write_timestamp_namespace(FILE* stream)
{
  time_t t;
  time(&t);
  struct tm* time_info = localtime(&t);

  char buffer[80];
  size_t bytes = strftime(buffer, sizeof(buffer), "%Y:%m:%d %H:%M:%S: ", time_info);
  if (nsstring != NULL)
  {
    sprintf(buffer + bytes, "[%s] ", nsstring);
  }
  fputs(buffer, stream);
}


void logmsg(const char* format, ...)
{
  write_timestamp_namespace(LOG_FILE);

  va_list args;
  va_start(args, format);
  vfprintf(LOG_FILE, format, args);
  va_end(args);

  fputs("\n", LOG_FILE);
  fflush(LOG_FILE);
}


void logerrno(const char* format, ...)
{
  write_timestamp_namespace(LOG_FILE);

  va_list args;
  va_start(args, format);
  vfprintf(LOG_FILE, format, args);
  va_end(args);

  fprintf(LOG_FILE, ": %d %s\n", errno, strerror(errno));
  fflush(LOG_FILE);
}


struct options
{
  std::vector<std::string> allowed_hosts;
  std::string              ns;
};


enum OptionTokens
{
  OPT_ALLOWED_HOSTS = 256,
  OPT_NAMESPACE
};


const static struct option long_opt[] =
{
  {"allowed-hosts", required_argument, NULL, OPT_ALLOWED_HOSTS},
  {"namespace",     required_argument, NULL, OPT_NAMESPACE},
  {"help",          no_argument,       NULL, 'h'},
  {NULL,            0,                 NULL, 0},
};


void usage(void)
{
  puts("Options:\n"
       "\n"
       " --allowed-hosts <hosts>       A comma separated list of whitelisted hosts in\n"
       "                               the namespace for this instance of the factory.\n"
       " --namespace <namespace>       The namespace being handled by this instance of\n"
       "                               the factory\n"
       " -h, --help                    Show this help screen\n");
}


int init_options(int argc, char**argv, struct options& options)
{
  int opt;
  int long_opt_ind;

  std::string tmp;
  while ((opt = getopt_long(argc, argv, "h", long_opt, &long_opt_ind)) != -1)
  {
    switch (opt)
    {
    case OPT_ALLOWED_HOSTS:
      logmsg("Whitelist: %s", optarg);
      tmp = std::string(optarg);
      boost::split(options.allowed_hosts,
                   tmp,
                   boost::is_any_of(","),
                   boost::token_compress_on);
      break;

    case OPT_NAMESPACE:
      logmsg("Namespace: %s", optarg);
      options.ns = std::string(optarg);
      nsstring = options.ns.c_str();
      break;

    case 'h':
      usage();
      return -1;

    default:
      logerrno("Unknown option: %d.  Run with --help for options.\n", opt);
      return -1;
    }
  }

  return 0;
}


int get_shared_socket(char* target,
                      const std::vector<std::string>& allowed_hosts)
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
    freeaddrinfo(addrs);
    return rc;
  }

  *sep = 0;
  char* host = target;
  char* port = sep + 1;

  if (std::find(allowed_hosts.begin(),
                allowed_hosts.end(),
                host) == allowed_hosts.end())
  {
    logmsg("Requested host (%s) is not permitted in this namespace. Exiting",
           host);
    exit(2);
  }

  memset(&hints, 0, sizeof hints);
  hints.ai_family = AF_INET;
  hints.ai_socktype = SOCK_STREAM;

  if (getaddrinfo(host, port, &hints, &addrs) != 0)
  {
    logerrno("Could not resolve %s", host);
    rc = -2;
    freeaddrinfo(addrs);
    return rc;
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
      freeaddrinfo(addrs);
      return rc;
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
      freeaddrinfo(addrs);
      return rc;
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
  }
  else
  {
    logmsg("Shared socket connected");
  }

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


void process_one_request(int listen_socket,
                         std::vector<std::string>& allowed_hosts)
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

  /*
   * Read the target address.  We want to NUL terminate this so tell `recv` to
   * read at most one less byte than available in the buffer.
   */
  char buf[1024];
  size_t len = recv(client_sock, buf, sizeof(buf) - 1, 0);

  if (len <= 0)
  {
    logerrno("Could not read target address");
    close(client_sock);
    return;
  }

  buf[len] = 0;
  logmsg("Asked to connect to %s", buf);

  int shared_sock = get_shared_socket(buf, allowed_hosts);

  if (shared_sock < 0)
  {
    close(client_sock);
    return;
  }

  send_file_descriptor(client_sock, shared_sock);

  close(shared_sock);
  close(client_sock);
}


int create_unix_domain_socket(const char* socket_path)
{
  struct sockaddr_un addr;
  int fd;

  if ((fd = socket(AF_LOCAL, SOCK_STREAM, 0)) < 0)
  {
    logerrno("Failed to create server UNIX socket");
    return fd;
  }

  memset(&addr, 0, sizeof(addr));

  addr.sun_family = AF_LOCAL;
  strcpy(addr.sun_path, socket_path);

  unlink(socket_path);

  if (bind(fd,
           (struct sockaddr *) &(addr),
           sizeof(addr)) < 0)
  {
    logerrno("Failed to bind server UNIX socket");
    return -1;
  }

  /* Allow other processes to connect to the socket */
  chmod(socket_path, 0777);

  if (listen(fd, MAX_PENDING) < 0)
  {
    logerrno("Failed to listen on server UNIX socket");
    return -1;
  }

  logmsg("Listening for requests");

  return fd;
}


int create_server(struct options& options)
{
  struct pollfd fd;

  logmsg("Starting server");

  /*
   * Determine the socket path from the namespace
   */
  std::string socket_path =  "/tmp/clearwater_" + options.ns + "_namespace_socket";

  fd.fd = create_unix_domain_socket(socket_path.c_str());
  fd.events = POLLIN;

  /*
   * Poll the file descriptor. Set timeout to -1 so that we block until the file
   * descriptor has become ready
   */
  for (;;)
  {
    int ret = poll(&fd, 1, -1);

    if (ret > 0)
    {
      if (fd.revents & POLLIN)
      {
        process_one_request(fd.fd, options.allowed_hosts);
      }
    }
  }

  close(fd.fd);

  return 0;
}

int main(int argc, char** argv)
{
  LOG_FILE = fopen(LOG_FILENAME, "a");
  if (LOG_FILE == NULL)
  {
    fprintf(stderr, "Could not open %s for writing", LOG_FILENAME);
    return -1;
  }

  struct options options;
  if (init_options(argc, argv, options) != 0)
  {
    return 1;
  }

  return create_server(options);
}
