#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: error.d
# Date  : 2020-05-12
# Create by: error.d<error.d@gmail.com>
#

debug = False

config = {
    "is_login_keys": ["parent.parent.window.location.href='/common/login/weixin.htm",
                     "请求参数有误",
                      "获取不到微信号了呢，试试点击重新授权",
                      "api key验证失败"],
    "doctor_block_tag": "<p class=\"deptname-title\">",    
    "session_key": "JSESSIONID",
    "session_value": "xxx",
    "oppointment_fail_action": 1, # 1 = continue, 2 = close
    "gatecard_idx": 7,
    "oppointment_time": "3.05",
    "visit_time": 'am',
    "use_thread": True,
    "numid_list_real": True, # True from access schedule page, False is iteration count
    "doctor_name": "xxx",
    "action_url_map" : { "action_chankezhuanjia" : {"method": "GET",
                                                    "url": "https://zjsfbwxs.zwjk.com/common/login/appointdepartmentlist.htm?action=appointdepartmentschedulelist&deptType=20803&dept_name=%E4%BA%A7%E7%A7%91%E8%B5%84%E6%B7%B1%E4%B8%93%E5%AE%B6&depttype=2&orderType=1",
                                                    "referer":"https://zjsfbwxs.zwjk.com/common/login/appointdepartmentlist.htm?action=appointordinarydepartmentlist"},
                         "action_schedule": {"method": "GET",
                                             "url": "https://zjsfbwxs.zwjk.com/common/login/appointdepartmentlist.htm?action=appointdepartmentscheduledetail&",
                                             "params": {"id": None,
                                                        "ampm": None}
                                             },
                         "action_oppointment" : {"method": "POST",
                                                 "url": "http://zjsfbwx.zwjk.com/common/login/appointdepartmentlist.htm?action=appointdepartment",
                                                 "params": {"name": 'xxx',
                                                            "patient_id": 'xxx',
                                                            "id_card": 'xxx',
                                                            "phone": 'xxx',
                                                            "numid": None, # 240919-7
                                                            "id": None, # 240919
                                                            "deptType": None,
                                                            "orderType": None
                                                            }
                                                 }
                        }
    }
