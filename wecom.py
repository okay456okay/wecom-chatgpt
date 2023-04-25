#!/usr/bin/env python3
# coding=utf-8
import requests
from log import logger


class WECOM_APP(object):
    def __init__(self, corp_id, agent_id, agent_secret):
        self.corp_id = corp_id
        self.agent_id = agent_id
        self.agent_secret = agent_secret
        self.s = requests.session()
        self.access_token = None
        self.get_token()

    def get_token(self):
        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corp_id}&corpsecret={self.agent_secret}"
        r = self.s.get(url=url)
        logger.info(f"get access_token, url: {url}, response: {r.status_code}:{r.text}")
        self.access_token = r.json()['access_token']

    def txt_send2user(self, userid, text):
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.access_token}"
        data = {
            "touser": userid,
            "msgtype": "text",
            "agentid": self.agent_id,
            "text": {
                "content": text,
            },
            "safe": "0"
        }
        r = self.s.post(url=url, json=data)
        logger.info(f"send message to user, url: {url}, data: {data}, response: {r.status_code}:{r.text}")
        if r.json().get('errcode', 0) == 42001:
            self.get_token()
            url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.access_token}"
            r = self.s.post(url=url, json=data)
            logger.info(f"send message to user, url: {url}, data: {data}, response: {r.status_code}:{r.text}")
