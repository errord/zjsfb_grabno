#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright: error.d
# Date  : 2018-02-24
# Create by: error.d<error.d@gmail.com>
#

debug = False

config = {
    "is_login_keys": ["parent.parent.window.location.href='/common/login/weixin.htm",
                     "请求参数有误"],
    "doctor_block_tag": "<div style=\" margin-top: 100px;",
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
                                                    "url":"http://zjsfbwx.zwjk.com/common/login/appointdepartmentlist.htm?action=appointdepartmentschedulelist&deptType=20701&dept_name=%E5%A6%87%E7%A7%91%E5%90%8D%E5%8C%BB&deptDesc=&depttype=1",
                                                    "referer":"http://zjsfbwx.zwjk.com/common/login/appointdepartmentlist.htm?action=appointordinarydepartmentlist"},
                         "action_schedule": {"method": "GET",
                                             "url": "http://zjsfbwx.zwjk.com/common/login/appointdepartmentlist.htm?action=appointdepartmentscheduledetail&",
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
                                                            "deptType": None
                                                            }
                                                 }
                        }
    }
