# Made by Kim.Seung.Hwan / ksana1215@interminds.ai
# -*- coding: utf-8 -*-
import serial
import redis
import json
import requests
import datetime
import logging
import config
import urllib3
import request_main

cf_path = config.path['path']
cf_company_id = config.refrigerators['companyId']
cf_store_id = config.refrigerators['storeId']
cf_device_id = config.refrigerators['deviceId']
cf_scanner_port = config.refrigerators['scanner']
rd = redis.StrictRedis(host='localhost', port=6379, db=0)
Scanner = serial.Serial(port=cf_scanner_port, baudrate=9600, timeout=1)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.basicConfig(filename=cf_path + 'kiosk_status.log', level=logging.DEBUG)
logger = logging.getLogger('QRC_LOG')

# phase_storeId = 'is00000002'
# phase_storeId = 's_00001'

def auth_phase(auth_type, page):
    data = {'companyId': cf_company_id, 'storeId': cf_store_id, 'orderId': auth_time, 'type': auth_type,
            'barcode': barcode}
    # data = {'companyId': '0001', 'storeId': 'PTY_0001', 'orderId': auth_time, 'type': auth_type,
    #         'barcode': barcode}
    res = requests.post('http://phasecommu.synology.me:3535/api/adult', json=data, verify=False, timeout=30)
    if json.loads(res.text)["resultCode"] == "200":
        logger.info(f'[{log_time} | Adult Auth Success]' + '\n' + str(res.text))
        if page == b'start':
            request_main.check_status(1)
        elif page == b'auth_adult':
            rd.set('door', 'open')
            rd.set('msg', 'shopping')
    elif json.loads(res.text)["resultCode"] == "-403":
        rd.set('msg', 'auth_first')
        logger.info(f'[{log_time} | Adult Auth Fail]' + '\n' + str(res.text))
    elif json.loads(res.text)["resultCode"] == "-405":
        rd.set('msg', 'auth_fail_1')
        logger.info(f'[{log_time} | Adult Auth Fail]' + '\n' + str(res.text))
    else:
        rd.set('msg', 'auth_fail')
        logger.info(f'[{log_time} | Adult Auth Fail]' + '\n' + str(res.text))


while True:
    t_time = datetime.datetime.now()
    log_time = t_time.strftime("%Y-%m-%d-%H:%M:%S")
    auth_time = t_time.strftime("%Y%m%d%H%M%S")
    try:
        page = rd.get('nowPage')
        barcode = Scanner.readline()
        barcode = barcode.decode('utf-8').rstrip()
        # 관리자 바코드
        if len(barcode) > 0 and page == b'start' and barcode == 'pnuts1234':
            rd.set('msg', 'admin')
            rd.set('door', 'admin')
        elif len(barcode) > 0 and page == b'auth_adult':
            auth_phase('1', page)
        elif len(barcode) > 0 and page == b'start':
            rd.set('msg', 'loading')
            auth_phase('1', page)

    except Exception as err:
        rd.set('err_type', 'except')
        rd.set('msg', 'device_err')
        request_main.device_err()
        logger.info(f'[{log_time} | SCANNER FAIL]' + '\n' + str(err))
        break
