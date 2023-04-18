#!/usr/bin/env python3
# coding=utf-8
"""
企业微信服务
"""

from flask import Flask, request
import json
import logging
import traceback
from wxcrypt import WXBizMsgCrypt
import sys

logging.basicConfig(level=logging.DEBUG,  # 控制台打印的日志级别
                    filename='wecom_chatgpt.log',
                    filemode='a',  ##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                    # a是追加模式，默认如果不写的话，就是追加模式
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                    # 日志格式
                    )
# logging.error(traceback.print_exc())

# 存储所有用户的消息记录
messages = {}

app = Flask(__name__)


@app.route('/')
def index():
    return '<h1>Flask Receiver App is Up!</h1>', 200


@app.route('/wecom/receive/v2')
def webhook():
    token = "U6pfDj2kvxE4H9JnfxEZRr"
    encoding_aes_key = "EckrwxVr6XcMHQbwTWxWe4bQ2nRInF0PNyF9rDaXjQK"
    corp_id = "ww69bda534f8fda184"
    corp_secret = "IGJMX3Ye71PfkGA0ETOF0WjMQd7Eivx1i34uzo8dFW0"
    agent_id = 1000002
    arg = (request.args)
    msg_signature = arg["msg_signature"]
    timestamp = arg["timestamp"]
    sVerifyNonce = arg["nonce"]
    sVerifyEchoStr = arg["echostr"]
    logging.DEBUG(f"{msg_signature}, {timestamp}, {sVerifyNonce}, {sVerifyEchoStr}")
    wxcpt = WXBizMsgCrypt(token, encoding_aes_key, corp_id)
    ret, sEchoStr = wxcpt.VerifyURL(msg_signature, timestamp, sVerifyNonce, sVerifyEchoStr)
    if (ret != 0):
        print("ERR: VerifyURL ret: " + str(ret))
        sys.exit(1)
    return sEchoStr


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8088, debug=True)
