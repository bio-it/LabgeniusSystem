#! /bin/bash
echo "Start Program"
pm2 start "python3 PcrHidController.py" --name "PcrHidController" --no-autorestart
pm2 start "python3 app.py" --name "API-Server" --no-autorestart
exit 0
