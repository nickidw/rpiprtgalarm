/bin/date >> /var/log/checkwifilog
/bin/ping -c4 192.168.103.1 >> /var/log/checkwifilog
if [ $? != 0 ]
then
  /sbin/shutdown -r now
fi

