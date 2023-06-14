#! /bin/bash
echio "Restart Program"
pm2 restart "PcrHidController" --no-autorestart
pm2 restart "API-Server" --no-autorestart
exit 0
