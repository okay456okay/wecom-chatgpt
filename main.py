#!/usr/bin/env python3
# coding=utf-8
"""
企业微信服务
"""

from flask import Flask, request, abort
import json
import logging
import traceback
from wxcrypt import WXBizMsgCrypt
import requests

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


@app.route('/wecom/receive/v2', methods=['POST', 'GET'])
def webhook():
    token = "U6pfDj2kvxE4H9JnfxEZRr"
    encoding_aes_key = "EckrwxVr6XcMHQbwTWxWe4bQ2nRInF0PNyF9rDaXjQK"
    corp_id = "ww69bda534f8fda184"
    corp_secret = "IGJMX3Ye71PfkGA0ETOF0WjMQd7Eivx1i34uzo8dFW0"
    agent_id = 1000002
    wxcpt = WXBizMsgCrypt(token, encoding_aes_key, corp_id)
    arg = (request.args)
    msg_signature = arg["msg_signature"]
    timestamp = arg["timestamp"]
    nonce = arg["nonce"]
    # URL验证
    if request.method == "GET":
        echostr = arg["echostr"]
        # logging.DEBUG(f"{msg_signature}, {timestamp}, {sVerifyNonce}, {sVerifyEchoStr}")
        ret, echostr_decrypted = wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
        if (ret != 0):
            error_message = f"ERR: VerifyURL ret: {ret}"
            logging.error(error_message)
            abort(403, error_message)
        return echostr_decrypted, 200
    elif request.method == "POST":
        ret, message = wxcpt.DecryptMsg(request.data, msg_signature, timestamp, nonce)
        if ret != 0:
            abort(403, "消息解密失败")
        else:
            reply = "收到，思考中..."
            ret, replay_encrypted = wxcpt.EncryptMsg(reply, nonce, timestamp)
            url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={}&corpsecret={}".format(corp_id, corp_secret)
            r = requests.get(url=url)
            access_token = r.json()['access_token']
            # 回复消息
            url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={}".format(access_token)
            data = {
                "touser": 'ZhuXiuLong',
                "msgtype": "text",
                "agentid": agent_id,
                "text": {
                    "content": "来自于ChatGPT的回复，待实现"
                },
                "safe": "0"
            }
            r = requests.post(url=url, data=json.dumps(data), verify=False)
            print(r.json())

            return replay_encrypted, 200
    else:
        logging.warning(f"Not support method: {request.method}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8088, debug=True)
