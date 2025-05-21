#!/bin/bash
# Script to set up the daily CSV export cron job

# Create the log file
touch /var/log/export_tasks.log
chmod 644 /var/log/export_tasks.log

# Set up the cron job to run at 2:00 AM daily
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/bin/python3 /opt/scripts/export_tasks.py >> /var/log/export_tasks.log 2>&1") | crontab -

echo "Cron job has been set up to run export_tasks.py daily at 2:00 AM"
echo "Logs will be saved to /var/log/export_tasks.log" 