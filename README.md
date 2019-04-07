# rpiprtgalarm

The purpose of this utility is to activate a relay on configurable intervals with configurable pulses if any unacknowledged alarms exist in PRTG for longer than a conifgurable duration. This relay can control lights, sirens, etc.

I'm using relay https://www.netram.co.za/3817-1-channel-5v-relay-module.html with an external 12VDC power source connected to a 3-24V piezo buzzer switched by the relay.

Default configuration is to check every 60s for unacknowledged alerts.
If none found, it sleeps for 60s and rechecks.
If found, it sleeps for 300s and checks again
If still unacknowledged, the active alarming logic is executed.

This logic pulses the relay on and off 10 times with 0.1s durations, sleeps 30s, checks for unacklowledged alarms, and if still present, repeats the cycle until alarms are acknowledged in PRTG.
