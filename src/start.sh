#!/bin/sh
python  -u C:/Users/kwon/Desktop/KIOSK/KIOSK_PNUTS/src/taskkill.py
python  -u C:/Users/kwon/Desktop/KIOSK/KIOSK_PNUTS/src/auth_main.py &
python  -u C:/Users/kwon/Desktop/KIOSK/KIOSK_PNUTS/src/door_main.py &
python  -u C:/Users/kwon/Desktop/KIOSK/KIOSK_PNUTS/src/adult_app_main.py &



