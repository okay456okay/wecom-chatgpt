#!/usr/bin/env python3
# coding=utf-8
"""
ChatGPT对话
"""
import json
import os
import random

import requests
from config import chatgpt_api_key, chatgpt_api_base
from log import logger

messages_file = 'messages.json'


class GPT(object):
    def __init__(self, api_key, api_base='https://api.openai.com', proxies=None):
        self.api_key = api_key
        self.api_base = api_base
        self.s = requests.session()
        if proxies:
            self.s.proxies = proxies
        self.s.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        })

    def chat(self, message, model='gpt-3.5-turbo', max_tokens=2000, history_messages=[]):
        full_messages = history_messages
        full_messages.append({"role": "user", "content": message})
        data = {
            "model": model,
            "messages": full_messages,
            "temperature": 0.7,
            "max_tokens": max_tokens,
        }
        url = self.api_base + '/v1/chat/completions'
        try:
            r = self.s.post(url=url, json=data)
            logger.info(f"chat completion, url: {url}, data: {data}, response: {r.status_code}:{r.text}")
            if 'error' in r.json():
                error = r.json()['error']['message']
                logger.error(f"get chatgpt reply error: {error}")
                if error.find("This model's maximum context length") >= 0:
                    data['messages'] = full_messages[int(len(full_messages)/2):]
                    r = self.s.post(url=url, json=data)
            content = r.json()["choices"][0]["message"]["content"]
            token_used = r.json()['usage']['total_tokens']
        except Exception as e:
            logger.error(f"get chatgpt reply error: {e}")
            token_used = 0
            content = "网络错误，请联系管理员处理，谢谢"
        return content, token_used


class WECOMCHAT(object):
    def __init__(self, userid, gpt, system_prompt="", messages_file=messages_file):
        self.gpt = gpt
        self.messages_user = []
        if os.path.exists(messages_file):
            with open(messages_file, 'r') as f:
                messages = json.load(f)
                if userid in messages:
                    self.messages_user = messages[userid]
        else:
            if system_prompt:
                self.messages_user.append({
                    "role": "system",
                    "content": system_prompt
                })

    def chat(self, message):
        reply, token_used = self.gpt.chat(message, history_messages=self.messages_user)
        self.messages_user.append({"role": "assistant", "content": reply})
        return reply

    def append_messages(self, message):
        self.messages_user.append(
            {
                "role": "user",
                "content": message
            }
        )


if __name__ == '__main__':
    # proxies = {
    #     'http': 'http://127.0.0.1:1087',
    #     'https': 'http://127.0.0.1:1087'
    # }
    # gpt = GPT(api_key="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", proxies=proxies)
    # wecomgpt = WECOMCHAT('ZhuXiuLong', gpt, system_prompt="You are a code expert and product expert.")
    gpt = GPT(api_key=chatgpt_api_key, api_base=chatgpt_api_base)
    wecomgpt = WECOMCHAT('ZhuXiuLong', gpt)
    print(wecomgpt.chat(f"您好，{random.randint(1, 100)}"))
    print(wecomgpt.chat("我刚才说了什么?"))
