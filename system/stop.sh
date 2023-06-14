#! /bin/bash
echo "Stop Program"
pm2 stop "API-Server"
pm2 stop "PcrHidController"
exit 0
