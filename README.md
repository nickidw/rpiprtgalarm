# rpiprtgalarm

The purpose of this utility is to activate a buzzer on configurable intervals with configurable pulses if any unacknowledged alarms exist in PRTG for longer than a conifgurable duration. 

Default configuration is to check every 60s for unacknowledged alerts.
If none found, it sleeps for 60s and rechecks.
If found, it sleeps for 300s and checks again
If still unacknowledged, the active alarming logic is executed.

This logic pulses the buzzer on and off for 1 second with 0.1s durations, sleeps 30s, checks for unacklowledged alarms, and if still present, repeats the cycle until alarms are acknowledged in PRTG. Every 30 seconds the buzzer duration is increased by 2 seconds, i.e. 1s, 3s, 5s, 7s, 9s, etc.
