Value FIRMWARE_NAME ([\d\.\w]+)
Value UPTIME ((\d+days\s)?(\d+hrs\s)?(\d+mins\s)?(\d+secs))

Start
  ^Firmware name:\s+${FIRMWARE_NAME}
  ^System Uptime:\s+${UPTIME}