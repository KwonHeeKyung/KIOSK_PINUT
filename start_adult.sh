#!/bin/sh
python  -u C:/Users/kwon/Desktop/KIOSK/KIOSK_PINUT/src/taskkill.py
python  -u C:/Users/kwon/Desktop/KIOSK/KIOSK_PINUT/src/auth_main.py &
python  -u C:/Users/kwon/Desktop/KIOSK/KIOSK_PINUT/src/door_main.py &
python  -u C:/Users/kwon/Desktop/KIOSK/KIOSK_PINUT/src/adult_app_main.py &



