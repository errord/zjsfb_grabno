#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: error.d
# Date  : 2018-02-24
# Create by: error.d<error.d@gmail.com>
#

import re
import requests
from lxml import etree
from config import *

am_str = u'\xe4\xb8\x8a\xe5\x8d\x88' # 上午
pm_str = u'\xe4\xb8\x8b\xe5\x8d\x88' # 下午

estr = etree._ElementStringResult
eunicode = etree._ElementUnicodeResult
estrtypes = [str, unicode, estr, eunicode]

def is_login(html):
    for key in config['is_login_keys']:
        if html.find(key) >= 0:
            if debug:
                print "login failed: %s" % key
            return False
    return True

def get_cookies():
    return "%s=%s" % (config['session_key'], config['session_value'])

def get_headers():
    headers = {"Host": "zjsfbwx.zwjk.com",
               "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
               "Accept-Language": "zh-cn",
               "Accept-Encoding": "gzip, deflate",
               "Cookie": get_cookies(),
               "Referer":"http://zjsfbwx.zwjk.com/common/login/appointdepartmentlist.htm?action=appointordinarydepartmentlist",
               "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_5 like Mac OS X) AppleWebKit/604.5.6 (KHTML, like Gecko) Mobile/15D60 MicroMessenger/6.6.3 NetType/WIFI Language/zh_CN"
               }
    return headers

def work_time_div_idx(work_time):
    pass

def create_worktime_table(html):
    selector = etree.HTML(html)
    elements =  selector.xpath("//*[@class=\"datelist\"]")
    if debug:
        print elements, len(elements)
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
    doctor_blocks = filter(lambda x: doctor in x, blocks)
    if len(doctor_blocks) == 0:
        return None
    return doctor_blocks[0]

def onclick_parse(onclick):
    onclick = onclick.replace("'", "")
    m = re.search(r"test\((.+?)\)", onclick)
    assert len(m.groups()) == 1, "onclick failed"
    action = map(lambda x: x.encode('utf8'), m.group(1).split(","))
    action = {"id": action[0], # a
              "ampm": action[1], # b
              "date": action[2], # c
              "week": action[3], # d
              "regfee": action[4], # e
              "deptType": action[5], # f
              }
    return action
    
def create_doctor_table(html, doctor):
    doctor_table = {'am': {}, 'pm': {}}
    block_html = find_doctor_block(html, doctor)
    if block_html is None:
        print "没有'%s'医生的信息" % doctor
        return None
    print block_html, type(block_html)
    selector = etree.HTML(block_html)
    elements = [t for t in selector.xpath("//div[@class=\"datelist-am-pm\"]")]
    element_texts = [t.text for t in elements]
    if debug:
        print "element texts: %s" % element_texts
    state = 0
    idx = 0
    for eidx, text in enumerate(element_texts):
        if text == am_str: # 上午
            state = 'am'
            idx = 1
            continue
        if text == pm_str: # 下午
            state = 'pm'
            idx = 1
            continue
        if state == 0 or text == ' ':
            continue
        text = text.strip()
        action = None
        if text.isdigit():
            onclick = elements[eidx].attrib['onclick']
            action = onclick_parse(onclick)
        doctor_table[state][idx] = {"count": text, "action": action}
        idx += 1
    return doctor_table

def doctor_gatecard(html, doctor):
    html = re.sub(r"\s+", " ", html)
    worktime_table = create_worktime_table(html)
    print_text(day_work_time(worktime_table))
    print_text(last_work_time(worktime_table))

    doctor_table = create_doctor_table(html, doctor)
    if doctor_table is None:
        return None

    if debug:
        print "worktime_table: %s" % worktime_table
        print "doctor_table: %s" % doctor_table

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

def print_text(texts):
    for text in texts:
        if type(text) in estrtypes:
            print text
        else:
            print text.text

def print_str(s):
    if type(s) is str:
        print s
    elif type(s) is unicode:
        print s.encode('utf8')
    print s

def run():
    action = "action_chankezhuanjia"
    headers = get_headers()
    request = requests.get(config['action_url_map'][action], headers=headers)
    cookies = request.cookies
    html = request.content
    if debug:
        print "request headers: %s" % request.request.headers
        print "response headers: %s" % request.headers
    if not request.ok or not is_login(html):
        print "request action:%s failed.." % action
        return
    gatecard = doctor_gatecard(html, config['doctor_name'])

    print gatecard
    print gatecard[5]
    
if __name__ == '__main__':
    run()
