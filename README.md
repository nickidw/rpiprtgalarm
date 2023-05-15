# rpiprtgalarm

The purpose of this utility is to activate a buzzer on configurable intervals with configurable pulses if any unacknowledged alarms exist in PRTG for longer than a conifgurable duration. 

Default configuration is to check every 60s for unacknowledged alerts.
If none found, it sleeps for 60s and rechecks.
If found, it sleeps for 300s and checks again
If still unacknowledged, the active alarming logic is executed.

This logic pulses the buzzer on and off for 1 second with 0.1s durations, sleeps 30s, checks for unacklowledged alarms, and if still present, repeats the cycle until alarms are acknowledged in PRTG. Every 30 seconds the buzzer duration is increased by 2 seconds, i.e. 1s, 3s, 5s, 7s, 9s, etc.

## Installation
* clone the repo
* Copy rpiopsgeniealarm.service from <local cloned folder>/lib/systemd/system to /etc/systemd/system
* Create config.py in /home/pi with _geniekey="your OpsGenie key"_ as only content
* Run _systemctl start rpiopsgeniealarm.service_
* Run _systemctl enable rpiopsgeniealarm.service_
  
## Debugging
Stop the service using _systemctl stop rpiopsgeniealarm.service_ and run _python3 getopsgenie.py_ in a terminal and observe the output
  
## checkwifi
There is a checkwifi.sh script in lib/usr/local/bin that pings an address and reboots the pi if no response received. This became necessary because the wifi connection on my pi zero would disconnect and not reconnect, therefor one would have no way to reach the raspberry pi.
There is a sample crontab in lib/var/spool/cron/crontabs to schedule checkwifi.sh
There is a sample logrorate config in lib/etc/logrorate.d/checkwifi to rotate /var/log/checkwifi
  
## Prerequisites
Raspberry Pi OS Lite bullseye required no other packages to be installed
