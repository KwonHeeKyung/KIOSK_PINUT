# Made by Kim.Seung.Hwan / ksana1215@interminds.ai
# -*- coding: utf-8 -*-
import redis
import time
import json
import requests
import urllib3
import datetime
import config
import logging

cf_path = config.path['path']
cf_company_id = config.refrigerators['companyId']
cf_store_id = config.refrigerators['storeId']
cf_device_id = config.refrigerators['deviceId']
cf_network_server = config.network_info['server_request_url']
cf_master_server = config.network_info['raspberry_base_url']
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.basicConfig(filename=cf_path + 'kiosk_status.log', level=logging.DEBUG)
logger = logging.getLogger('API_LOG')
rd = redis.StrictRedis(host='localhost', port=6379, db=0)
msg = rd.get('msg')

# 상태조회
def check_status():
    log_time = datetime.datetime.now()
    log_time = log_time.strftime("%Y-%m-%d-%H:%M:%S")
    res = requests.post(f'{cf_master_server}check_status_sbc',
                        json={'companyId': cf_company_id, 'storeId': cf_store_id, 'deviceId': cf_device_id},
                        verify=False, timeout=30)
    json_data = json.loads(res.text)
    result_code = str(json_data['resultCode'])
    if result_code == '000':
        rd.set('msg', '000')
        logger.info(f'[{log_time} | check_status_sbc]' + '\n' + str(res.text))
    else:
        rd.set('msg', '001')
        logger.info(f'[{log_time} | check_status_sbc_fail]' + '\n' + str(res.text))

# 문열림
def door_open():
    res = requests.post(f'{cf_network_server}door_opened',
                        json={'companyId': cf_company_id, 'storeId': cf_store_id, 'deviceId': cf_device_id,
                              'barcode': '1234'}, verify=False)
# 문닫힘
def door_close():
    sender = []
    t_time = datetime.datetime.now()
    log_time = t_time.strftime("%Y-%m-%d-%H:%M:%S")
    tdr_time = t_time.strftime("%Y%m%d%H%M%S")
    res = requests.post(f'{cf_master_server}door_closed',
                        json={'storeId': cf_store_id, 'deviceId': cf_device_id, 'barcode': '1234',
                              "needSalesInfo": "true"}, verify=False)
    json_data = json.loads(res.text)
    logger.info(f'[{log_time} | LET\'s INFER]' + '\n' + str(json_data))
    # if json.loads(res.text)['resultCode'] == '000':
    #     order_list = json.loads(res.text)['data']['orderList']
    #     ln = len(order_list)
    #     if ln > 0:
    #         for i in range(0, ln):
    #             orders = order_list[i]
    #             NAME = orders['goodsName']
    #             BC = orders['goodsId']
    #             QTY = int(orders['goodsCnt'])
    #             dic = {"barcode": BC, "count": QTY}
    #             if QTY > 0: sender.append(dic)
    #         data = {"companyId": "0001", "storeId": "PTY_0001", "orderId": tdr_time, "items": sender}
    #         phase_res = requests.post('http://phasecommu.synology.me:3535/api/price', json=data, verify=False, timeout=30)
    #         logger.info(f'[{log_time} | Phase price Res]' + '\n' + str(phase_res.text))
    #         if json.loads(phase_res.text)["status"] == "200":
    #             items = json.loads(phase_res.text)["items"]
    #             rd.set('ol', json.dumps(items))
    #             rd.set('msg', 'cal')
    #             data_2 = {"companyId": "0001", "storeId": "PTY_0001", "orderId": tdr_time, "items": items}
    #             phase_res_2 = requests.post('http://phasecommu.synology.me:3535/api/order', json=data_2, verify=False, timeout=30)
    #             logger.info(f'[{log_time} | Phase order Res]' + '\n' + str(phase_res_2.text))
    #         else:
    #             rd.set('msg', '003')
    #
    #     elif ln == 0:
    #         rd.set('msg', 'end_none')
    # else:
    #     rd.set('msg', '003')
    #     logger.info(f'[{log_time} | INF FAIL]')
    #     logger.info(res.text)

# 관리자 문열림
def admin_open():
    log_time = datetime.datetime.now()
    log_time = log_time.strftime("%Y-%m-%d-%H:%M:%S")
    res = requests.post(f'{cf_master_server}manage_door', json={'deviceId': cf_device_id, 'doorStatus': 'O'},
                        verify=False)
    logger.info(f'[{log_time} | 관리자 OPEN SUCCESS]' + '\n' + str(res.text))

# 관리자 문닫힘
def admin_close():
    log_time = datetime.datetime.now()
    log_time = log_time.strftime("%Y-%m-%d-%H:%M:%S")
    res = requests.post(f'{cf_master_server}manage_door', json={'deviceId': cf_device_id, 'doorStatus': 'C'},
                        verify=False)
    logger.info(f'[{log_time} | 관리자 CLOSE SUCCESS]' + '\n' + str(res.text))
    rd.delete('door')
    json_data = json.loads(res.text)
    result_code = str(json_data['resultCode'])
    if result_code == '000':
        rd.set('msg', 'admin_close')
    else:
        rd.set('msg', '001')

# 장치 알림
def device_err():
    log_time = datetime.datetime.now()
    log_time = log_time.strftime("%Y-%m-%d-%H:%M:%S")
    err_type = rd.get('err_type')
    if err_type is None:
        pass
    elif err_type == b'except':
        rd.set('msg', 'device_err')
        text_type = '키오스크 장치 에러'
    elif err_type == b'long':
        text_type = '장시간 문열림 알림'
    elif err_type == b'payment':
        text_type = '잔액부족 결제실패'
    elif err_type == b'unknown':
        text_type = '미확인 에러 발생'
    res = requests.post(f'{cf_network_server}kakao_alarm',
                        json={'companyId': cf_company_id, 'storeId': cf_store_id, 'deviceId': cf_device_id,
                              "alarmHeader": "alarm", 'subjectHeader': "키오스크", 'alarmContext': text_type}, verify=False)
    logger.info(f'[{log_time} | DEVICE ERROR]')
    logger.info(res.text.replace('\n', ''))
