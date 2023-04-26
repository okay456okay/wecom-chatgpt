#!/usr/bin/env python3
# coding=utf-8
"""
企业微信服务
"""
from time import sleep

from flask import Flask, request, abort
import logging
from wxcrypt import WXBizMsgCrypt
import xmltodict
from config import corp_id, agent_id, agent_secret, token, encoding_aes_key
from chatgpt import GPT, WECOMCHAT
from ocr import image2txt_ocr
from wecom import WECOM_APP
from log import logger

# 存储所有用户的消息记录
messages = {}

app = Flask(__name__)

gpt_instances = {}
msg_ids = []
wecom_app = WECOM_APP(corp_id, agent_id, agent_secret)


@app.route('/')
def index():
    return '<h1>Flask Receiver App is Up!</h1>', 200


@app.route('/wecom/receive/v2', methods=['POST', 'GET'])
def webhook():
    wxcpt = WXBizMsgCrypt(token, encoding_aes_key, corp_id)
    arg = (request.args)
    msg_signature = arg["msg_signature"]
    timestamp = arg["timestamp"]
    nonce = arg["nonce"]
    logger.info(f"{arg}")
    # URL验证
    if request.method == "GET":
        echostr = arg["echostr"]
        ret, echostr_decrypted = wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
        logger.info(f"verify url, ret: {ret}, echostr: {echostr}, echostr_decrypted: {echostr_decrypted}")
        if (ret != 0):
            error_message = f"ERR: VerifyURL ret: {ret}"
            logging.error(error_message)
            abort(403, error_message)
        return echostr_decrypted, 200
    elif request.method == "POST":
        ret, message = wxcpt.DecryptMsg(request.data, msg_signature, timestamp, nonce)
        message_dict = xmltodict.parse(message.decode())['xml']
        logger.info(f"接收到的企业微信消息内容：{message_dict}")
        userid = message_dict.get('FromUserName')
        if userid not in gpt_instances:
            gpt = GPT()
            wecomgpt = WECOMCHAT('ZhuXiuLong', gpt)
            gpt_instances[userid] = wecomgpt
        else:
            wecomgpt = gpt_instances[userid]
        if ret != 0:
            abort(403, "消息解密失败")
            return
        reply = "收到，思考中..."
        ret, replay_encrypted = wxcpt.EncryptMsg(reply, nonce, timestamp)
        msg_type = message_dict.get('MsgType', '')
        # 消息去重处理
        if msg_type in ['image', 'text']:
            msg_id = message_dict.get('MsgId', '')
            if msg_id in msg_ids:
                return '重复消息', 200
            else:
                msg_ids.append(msg_id)
        if msg_type == 'image':
            image_url = message_dict.get('PicUrl')
            ocr_text = image2txt_ocr(image_url)
            wecomgpt.append_messages(f"OCR识别内容: {ocr_text}")
            wecom_app.txt_send2user(userid, f"OCR识别内容为： {ocr_text}")
        if msg_type == 'text':
            # 回复消息
            content = message_dict.get('Content')
            if content.find('批改作文') >= 0 or content.find('作文批改') >= 0:
                # gpt_reply = wecomgpt.chat(
                    # "假设你是一个优秀语文老师，精通写作。请对以上作文草稿打分并做出评价，给出改进意见。作文草稿内容为上面OCR识别内容。")
                gpt_reply = wecomgpt.chat(f"假设你是一个精通写作的优秀语文老师,根据作文草稿重写一篇100分的优秀满分作文，要求主题突出、内容充实、条理清晰、层次分明、有文采、用词丰富。并为作文起一个最好的标题。作文草稿为上面OCR识别内容。")
                wecom_app.txt_send2user(userid, gpt_reply)
                sleep(3)
                # gpt_reply = wecomgpt.chat(
                #     "请将上面的文章改写为优秀获奖高分作文。并指出改写前后的差异。")
                gpt_reply = wecomgpt.chat(f"对改写前后的作文打分(0-100分)并做出详细评价，给出写作改进意见。")
                wecom_app.txt_send2user(userid, gpt_reply)
            else:
                gpt_reply = wecomgpt.chat(content)
                wecom_app.txt_send2user(userid, gpt_reply)
        return replay_encrypted, 200
    else:
        logging.warning(f"Not support method: {request.method}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8088, debug=True)
