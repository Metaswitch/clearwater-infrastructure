# We want the node type to be displayed as a hyphen-separated list of all the 
# flavours of Clearwater services installed on this node.
type=$(. /etc/clearwater/config
       {
         # Different operating systems use their own package management systems. 
         # We assume that if yum is installed we are running on CentOS and 
         # working with RPMs, and otherwise we are running on Ubuntu and 
         # working with .deb packages.
         if which yum > /dev/null 2>&1 ; then
           # rpm returns an unsorted list and as the version numbers are 
           # stripped off we also need to filter out duplicates.
           rpm -qa --qf '%{NAME}\n' | sort | uniq
         else
           dpkg-query -W -f='${Package}\n'
         fi
       } |
       # Filter out the packages we care about
       # Use sprout-base instead of sprout to catch all cases of sprout being
       # installed
       egrep '^(bono|clearwater-sip-stress|ellis|homer|homestead|sprout-base|stats-engine|ralf|chronos|cassandra|astaire)$' |
       # Shorten the constructed name and replace product names containing
       # hyphens.
       sed -e 's/clearwater-sip-stress/sipp/g' |
       sed -e 's/sprout-base/sprout/g' |
       sed -e 's/stats-engine/mvse/g' |
       tr "\\n" "-" |

       # Strip any trailing dashes
       # Sprout and Ralf (pre split-storage) contains astaire and chronos
       # Sprout may also contain cassandra if memento is installed
       # Homestead (pre split-storage) uses Cassandra
       # Dime consists of homstead and ralf
       # Vellum contains the storage services
       # The all in one (aio) node contains everything
       sed -e 's/-$//g
               s/^astaire-bono-cassandra-chronos-ellis-homer-homestead-sprout$/cw-aio/g
               s/^astaire-chronos-ralf$/ralf/g
               s/^astaire-chronos-sprout$/sprout/g
               s/^astaire-cassandra-chronos-sprout$/sprout/g
               s/^cassandra-homestead$/homestead/g
               s/^homestead-ralf$/dime/g
               s/^astaire-cassandra-chronos$/vellum/g')

# We should only set the node-index if it is configured in the underlying
# config.
node_idx=$(. /etc/clearwater/config
           if [ -n "$node_idx" ]
           then
             echo -$node_idx
           fi)

# The node type and index should be present in the command prompt.
if [ "$TERM" = xterm-color ]; then
    PS1='\[\e]0;['$type$node_idx']\u@\h: \w\a\]${debian_chroot:+($debian_chroot)}['$type$node_idx']\u@\h:\w\$ '
else
    PS1='${debian_chroot:+($debian_chroot)}['$type$node_idx']\u@\h:\w\$ '
fi
unset type node_idx
