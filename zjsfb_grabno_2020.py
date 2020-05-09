#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: error.d
# Date   : 2018-02-24
# Update : 2020-05-02
# Create by: error.d<error.d@gmail.com>
#

import re
import time
import json
import requests
import threading
import ipdb
from lxml import etree
#from ying import *
from ding import *

"""
todolist:
  * 退出机制完善
"""

'''
estr = etree._ElementStringResult
eunicode = etree._ElementUnicodeResult
estrtypes = [str, unicode, estr, eunicode]
'''

done = False
full_exit = False
cur_oppointment_time = ""

def is_login(html):
    for key in config['is_login_keys']:
        if html.find(key) >= 0:
            print("login failed: %s" % key)
            return False
    print("login success")
    return True

def get_cookies():
    return "%s=%s" % (config['session_key'], config['session_value'])

def get_headers(update_headers):
    headers = {"Host": "zjsfbwxs.zwjk.com",
               "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               "Accept-Language": "zh-cn",
               "Accept-Encoding": "gzip, deflate",
               "Cookie": get_cookies(),
               "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_5 like Mac OS X) AppleWebKit/604.5.6 (KHTML, like Gecko) Mobile/15D60 MicroMessenger/6.6.3 NetType/WIFI Language/zh_CN"
               }
    headers.update(update_headers)
    return headers

def work_time_div_idx(work_time):
    pass

def create_worktime_table(html):
    selector = etree.HTML(html.encode('utf-8'))
    elements =  selector.xpath("//*[@class=\"baseli dateli\"]")
    if debug:
        print("create_worktime_table: ", elements, len(elements))
    worktime_table = {}
    for idx, element in enumerate(elements):
        if idx is 0:
            continue
        worktime_table[idx] = [s.replace("\r\n", "").replace(" ", "")
                              for s in element.itertext()]
    return worktime_table

def day_work_time(worktime_table):
    # idx is relative to today
    return worktime_table[1]

def last_work_time(worktime_table):
    return worktime_table[7]

def find_doctor_block(html, doctor):
    blocks = map(lambda x: config["doctor_block_tag"] + x,
                 html.split(config["doctor_block_tag"]))
    doctor_blocks = list(filter(lambda x: doctor in x, blocks))
    if len(doctor_blocks) == 0:
        return None
    return doctor_blocks[0]

def onclick_parse(onclick):
    onclick = onclick.replace("'", "")
    m = re.search(r"test\((.+?)\)", onclick)
    assert len(m.groups()) == 1, "onclick failed"
    action = list(map(lambda x: x.encode('utf8'), m.group(1).split(",")))
    return action
    
def create_doctor_table(html, doctor):
    doctor_table = {'am': {}, 'pm': {}}
    block_html = find_doctor_block(html, doctor)
    if block_html is None:
        print("没有'%s'医生的信息" % doctor)
        return None
    elif debug:
        print("find_doctor_block: %s" % block_html)
    selector = etree.HTML(block_html)
    elements = [t for t in selector.xpath("//div[@class=\"baseli orderli\"]")]
    element_texts = [''.join([t.text for t in element]) for element in elements]
    if debug:
        print("element texts: %s" % element_texts)
    state = 0
    idx = 0
    for eidx, text in enumerate(element_texts):
        if eidx == 0: # 上午
            state = 'am'
            idx = 1
            continue
        if eidx == 8: # 下午
            state = 'pm'
            idx = 1
            continue
        if state == 0 or text == ' ':
            continue
        text = text.strip()
        action = None
        if text.isdigit():
            onclick = elements[eidx].attrib['onclick']
            action_list = onclick_parse(onclick)
            action = {"id": action_list[0], # a
                      "ampm": action_list[1], # b
                      "date": action_list[2], # c
                      "week": action_list[3], # d
                      "regfee": action_list[4], # e
                      "deptType": action_list[5], # f
                      "orderType": action_list[6], # g
                      # dept_name = dept_name
                      }

        doctor_table[state][idx] = {"count": text, "action": action}
        idx += 1
    return doctor_table

def doctor_gatecard(html, doctor):
    if debug:
        print("html: %s doctor: %s" % (html, doctor))
    html = re.sub(r"\s+", " ", html)
    worktime_table = create_worktime_table(html)
    doctor_table = create_doctor_table(html, doctor)
    
    if doctor_table is None:
        return None

    if debug:
        print("worktime_table: %s" % worktime_table)
        print("doctor_table: %s" % doctor_table)

    gatecard = {}
    assert len(worktime_table) == 7 and \
           len(doctor_table['am']) == 7 and \
           len(doctor_table['pm']) == 7, "格式错误"
    for time in worktime_table:
        gatecard[time] = {
            "time": worktime_table[time],
            "work": {"am": doctor_table['am'][time], "pm": doctor_table['pm'][time]}
            }
    return gatecard

def submit_oppointment(doctor_id, dept_type, numid_list, order_type):
    global done, full_exit
    
    def _start_oppointment(numid):
        global done, full_exit
        if done or full_exit:
            return
        numid = str(doctor_id) + '-' + str(nid)
        print("oppointment numid: %s dept_type: %s id: %s" % \
              (numid, dept_type, doctor_id))
        _r = http_request("action_oppointment",
                            numid=numid, deptType=dept_type, id=doctor_id, orderType=order_type)
        print("numid:%s oppointment result: %s" % (numid, _r))
        try:
            result = json.loads(_r)
        except Exception as e:
            print("submit_oppointment loads failed : %s" % e)
            return
        if result["R"] == 200:
            if 'url' in result:
                print("发现需要社保支持..")
                print("[http request] GET url:%s" % url)
                headers = get_headers({})
                request = requests.get(result['url'], headers=headers)
                if debug:
                    html = request.content.decode('utf-8')
                    print(html)                

            print("oppointment SUCCESS: %s" % result["res"])
            full_exit = True
            return
        if config["oppointment_fail_action"] == 2:
            full_exit = True
            return

    print("submit_oppointment params: doctor_id=%s dept_type=%s numid_list=%s" % \
          (doctor_id, dept_type, numid_list))

    clock = 0.05
    for nid in numid_list:
        if config["use_thread"] is True:
            threading.Thread(target=_start_oppointment, args=(nid,),
                             name='thread-' + str(nid)).start()
        else:
            _start_oppointment(nid)
        if clock > 0:
            time.sleep(clock)
            clock -= 0.01
    full_exit = True

def http_request(action, **kwargs):
    update_headers = {}
    action_info = config["action_url_map"][action]
    if "referer" in action_info:
        update_headers["Referer"] = action_info["referer"]
    headers = get_headers(update_headers)
    method = action_info["method"].upper()
    url = action_info["url"]

    params = {}
    if "params" in action_info:
        for key, value in action_info["params"].items():
            params[key] = value
        params.update(kwargs)
    assert None not in params.values(), "request need params has None"

    if method == "GET":
        if len(params) > 0:
            url += '&'.join(["{0}={1}".format(k, v) for k,v in params.items()])
        print("[http request] GET url:%s" % url)
        request = requests.get(url, headers=headers)
    elif method == "POST":
        if debug:
            print("post url:%s params:%s" % (url, params))
        print("[http request] POST url:%s" % url)
        request = requests.post(url, headers=headers, data=params)
            
    cookies = request.cookies
    html = request.content.decode('utf-8')

    if debug:
        print("request headers: %s" % request.request.headers)
        if method == "POST":
            print("request body: %s" % request.request.body)
        print("response headers: %s" % request.headers)
    if not request.ok or not is_login(html):
        print("request action:%s failed.." % action)
        if debug:
            print("response: %s" % html)
        return None
    return html

'''
def print_text(texts):
    for text in texts:
        if type(text) in estrtypes:
            print(text)
        else:
            print(text.text)

def print_str(s):
    if type(s) is str:
        print(s)
    elif type(s) is unicode:
        print(s.encode('utf8'))
    print(s)
'''

def is_availability(gatecard):
    global done
    count = gatecard['work'][config['visit_time']]['count']
    if count == '-':
        print('oppointment: no availability(-)')
        done = True
        return False
    elif count == '满':
        print('oppointment: doctor full(满)')
        done = True
        return False
    elif count == "停诊":
        print('oppointment: doctor stop(停诊)')
        done = True
        return False
    return True

def get_numid_list(doctor_id):
    ampm = 1 if config['visit_time'] == 'am' else 2
    html = http_request("action_schedule",
                        id=doctor_id, ampm=ampm)
    selector = etree.HTML(html.encode('utf-8'))
    elements =  selector.xpath("//*[@class=\"order_menu_list\"]")
    onclick_list = filter(lambda x: x != None,
                          [element.attrib.get('onclick', None) for element in elements])
    numid_list = []
    for onclick in onclick_list:
        action_list = onclick_parse(onclick)
        numid_list.append(int(action_list[1]))
    return numid_list

def oppointment(gatecard):
    if not is_availability(gatecard):
        return
    try:
        count = gatecard['work'][config['visit_time']]['count']
        dept_type = gatecard['work'][config['visit_time']]['action']['deptType']
        doctor_id = int(gatecard['work'][config['visit_time']]['action']['id'])
        order_type = gatecard['work'][config['visit_time']]['action']['orderType']
    except Exception as e:
        print("oppointment params failed: %s" % e)
        return

    if config["numid_list_real"] is True:
        numid_list = get_numid_list(doctor_id)
    else:
        numid_list = [i for i in range(1, int(count))]
    submit_oppointment(doctor_id, dept_type, numid_list, order_type)

def run():
    global cur_oppointment_time, done
    print("预约 -- 医生: %s 时间: %s-%s " %
          (config['doctor_name'], config['oppointment_time'], config['visit_time']))
    while not (done is True and cur_oppointment_time == config["oppointment_time"]) and \
              full_exit is False:
        time.sleep(0.01)
        done = False
        action = "action_chankezhuanjia"
        html = http_request(action)
        if html is None:
            continue
        gatecard = doctor_gatecard(html, config['doctor_name'])
        if gatecard is None:
            print('no doctor...')
            if config["check_doctor_name"] == False:
                return
            else:
                continue
        if debug:
            print('gatecard: %s' % gatecard)
        cur_gatecard = gatecard[config["gatecard_idx"]]
        cur_oppointment_time = cur_gatecard["time"][1]
        if cur_oppointment_time != config["oppointment_time"]:
            print("time failed cur_oppointment_time: %s config oppointment_time: %s" %
                  (cur_oppointment_time, config["oppointment_time"]))

            print("auto search time: %s" % config["oppointment_time"])
            has_time = False
            for item in gatecard.items():
                item = item[1]
                item_time = item['time']
                if item_time[1] == config["oppointment_time"]:
                    has_time = True
                    cur_oppointment_time = item_time[1]
                    print("search success %s %s" % (item_time[0], item_time[1]))
                    break
            if not has_time:
                print("search %s failed" % config["oppointment_time"])
                continue
        oppointment(cur_gatecard)
    
if __name__ == '__main__':
    run()
