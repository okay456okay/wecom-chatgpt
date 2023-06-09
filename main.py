#!/usr/bin/env python3
# coding=utf-8
"""
企业微信服务
"""
import os.path
from time import sleep

from flask import Flask, request, abort
import logging
from wxcrypt import WXBizMsgCrypt
import xmltodict
from config import CORP_ID, AGENT_ID, AGENT_SECRET, TOKEN, ENCODING_AES_KEY, WELCOME_MESSAGE, FLASK_PORT, SAVE_CHAT_HISTORY, OCR_ENABLE
from chatgpt import WECOMCHAT
from ocr import image2txt_ocr
from wecom import WECOM_APP
from log import logger
import pickle
import signal

# 存储所有用户的消息记录
messages = {}

app = Flask(__name__)

gpt_instances = {}
msg_ids = []
wecom_app = WECOM_APP(CORP_ID, AGENT_ID, AGENT_SECRET)
gpt_session_file = 'gpt_instance.session'


@app.route('/')
def index():
    return '<h1>Flask Receiver App is Up!</h1>', 200


@app.route('/wecom/receive/v2', methods=['POST', 'GET'])
def webhook():
    wxcpt = WXBizMsgCrypt(TOKEN, ENCODING_AES_KEY, CORP_ID)
    arg = (request.args)
    msg_signature = arg["msg_signature"]
    timestamp = arg["timestamp"]
    nonce = arg["nonce"]
    logger.info(f"request.args: {arg}")
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
            wecomgpt = WECOMCHAT()
            gpt_instances[userid] = wecomgpt
        else:
            wecomgpt = gpt_instances[userid]
        if ret != 0:
            abort(403, "消息解密失败")
            return
        reply = "收到，思考中..."
        ret, replay_encrypted = wxcpt.EncryptMsg(reply, nonce, timestamp)
        msg_type = message_dict.get('MsgType', '')
        msg_event = message_dict.get('Event', '')
        # 消息去重处理
        if msg_type in ['image', 'text', 'event']:
            msg_id = message_dict.get('MsgId', '')
            if msg_id in msg_ids:
                return '重复消息', 200
            else:
                msg_ids.append(msg_id)
        if msg_type == 'image':
            if OCR_ENABLE:
                image_url = message_dict.get('PicUrl')
                ret, ocr_text = image2txt_ocr(image_url)
                if ret:
                    wecomgpt.append_messages(f"OCR识别内容: {ocr_text}")
                    wecom_app.txt_send2user(userid, f"OCR识别内容为： {ocr_text}")
                else:
                    wecomgpt.append_messages(f"OCR识别错误，报错内容: {ocr_text}")
            else:
                wecom_app.txt_send2user(userid, "目前不支持图片内容，仅支持文字发送，谢谢。")
        elif msg_type == 'event' and msg_event == 'enter_agent':
            # 进入会话
            wecom_app.txt_send2user(userid, WELCOME_MESSAGE)
        elif msg_type == 'text':
            # 回复消息
            content = message_dict.get('Content')
            if content.find('批改作文') >= 0 or content.find('作文批改') >= 0:
                # gpt_reply = wecomgpt.chat(
                # "假设你是一个优秀语文老师，精通写作。请对以上作文草稿打分并做出评价，给出改进意见。作文草稿内容为上面OCR识别内容。")
                gpt_reply = wecomgpt.chat(
                    f"假设你是一个精通写作的优秀语文老师,根据作文草稿重写一篇100分的优秀满分作文，要求主题突出、内容充实、条理清晰、层次分明、有文采、用词丰富。并为作文起一个最好的标题。作文草稿为上面OCR识别内容。")
                wecom_app.txt_send2user(userid, gpt_reply)
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


def save_gpt_session(signum, frame):
    f = open(gpt_session_file, 'wb')
    if gpt_instances:
        pickle.dump(gpt_instances, f)
        logger.info(f"成功保存gpt会话, 会话内容：{gpt_instances.keys()}")
    f.close()
    exit(0)


if __name__ == '__main__':
    if SAVE_CHAT_HISTORY:
        signal.signal(signal.SIGINT, save_gpt_session)
        signal.signal(signal.SIGHUP, save_gpt_session)
        signal.signal(signal.SIGTERM, save_gpt_session)
        # signal.signal(signal.SIGKILL, save_gpt_session)
        signal.signal(signal.SIGQUIT, save_gpt_session)
        try:
            if os.path.exists(gpt_session_file):
                f = open(gpt_session_file, 'rb')
                try:
                    gpt_instances = pickle.load(f)
                    logger.info(f"成功加载gpt会话， 内容：{gpt_instances.keys()}")
                except Exception as e:
                    pass
                finally:
                    f.close()
        except Exception as e:
            logger.error(f"加载gpt会话失败，错误内容：{e}")
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=False, use_reloader=False)
