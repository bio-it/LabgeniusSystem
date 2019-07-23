# LabgeniusSystem
New labgenius system for Raspberry pi

# Labgenius api test(emulator)
All response will return by json format.

1. PCR Start
	- http://210.115.227.99:6009/api/pcr/start
	- The protocol list is defined, check out the PCR Status API.
	- When the PCR is already started, error returned.

2. PCR Stop
	- http://210.115.227.99:6009/api/pcr/stop
	- The PCR is not running, error returned.

3. PCR Status
	- http://210.115.227.99:6009/api/pcr/status
	- return all information for displaying the PCR status on GUI.
	- Currently, the error information is not contained.


