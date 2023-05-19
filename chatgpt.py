#!/usr/bin/env python3
# coding=utf-8
"""
ChatGPT对话
"""
import json
import os
import random
from time import sleep

import requests
from config import OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_PROXY, OPENAI_PROXY_ENABLE, ADMIN_USER, SAVE_CHAT_HISTORY, \
    ERROR_MESSAGE, LLM_TEMPERATURE, LLM_MODEL, LLM_MAX_TOKENS, LLM_SYSTEM_PROMPT
from log import logger



class GPT(object):
    def __init__(self, api_key=OPENAI_API_KEY, api_base=OPENAI_API_BASE, proxies=OPENAI_PROXY,
                 proxy_enabled=OPENAI_PROXY_ENABLE):
        self.api_key = api_key
        self.api_base = api_base
        self.s = requests.session()
        if proxies and proxy_enabled:
            self.s.proxies = proxies
        self.s.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        })

    def chat(self, messages, model=LLM_MODEL, max_tokens=LLM_MAX_TOKENS, temperature=LLM_TEMPERATURE):
        """

        :param message:
        :param model: gpt-3.5-turbo
        :param max_tokens:
        :param history_messages:
        :return:
        """
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        url = self.api_base + '/chat/completions'
        try:
            r = self.s.post(url=url, json=data)
            logger.info(f"chat completion, url: {url}, data: {data}, response: {r.status_code}:{r.text}")
            if 'error' in r.json():
                error = r.json()['error']['message']
                logger.error(f"get chatgpt reply error: {error}")
                if error.find("This model's maximum context length") >= 0:
                    data['messages'] = messages[int(len(messages) / 2):]
                    if messages[0].get('role', '') == 'system':
                        data['messages'].insert(0, messages[0])
                    r = self.s.post(url=url, json=data)
                    logger.info(f"chat completion, url: {url}, data: {data}, response: {r.status_code}:{r.text}")
                elif error.find("Invalid request") >= 0:
                    r = self.s.post(url=url, json=data)
                    logger.info(f"chat completion, url: {url}, data: {data}, response: {r.status_code}:{r.text}")
            content = r.json()["choices"][0]["message"]["content"]
            token_used = r.json()['usage']['total_tokens']
        except Exception as e:
            logger.error(f"get chatgpt reply error: {e}")
            token_used = 0
            content = ERROR_MESSAGE
        return content, token_used


class WECOMCHAT(object):
    def __init__(self, system_prompt=LLM_SYSTEM_PROMPT):
        self.gpt = GPT()
        self.messages = []
        if system_prompt:
            self.messages.append({
                "role": "system",
                "content": system_prompt
            })

    def chat(self, message, temperature=LLM_TEMPERATURE, save_history=SAVE_CHAT_HISTORY):
        self.messages.append({"role": "user", "content": message})
        reply, token_used = self.gpt.chat(self.messages, temperature=temperature)
        if save_history:
            self.messages.append({"role": "assistant", "content": reply})
        else:
            self.messages.pop()
        return reply

    def append_messages(self, message):
        self.messages.append(
            {
                "role": "user",
                "content": message
            }
        )


if __name__ == '__main__':
    # wecomgpt = WECOMCHAT('ZhuXiuLong', gpt, system_prompt="You are a code expert and product expert.")
    # gpt = GPT(api_key=chatgpt_api_key, api_base=chatgpt_api_base)
    wecomgpt = WECOMCHAT()
    # print(wecomgpt.chat(f"您好，{random.randint(1, 100)}"))
    # print(wecomgpt.chat("我刚才说了什么?"))
    ocr_text = """让你炫耀\n昨天一同学新买了苹果X,总是在群里炫耀,说新手机如何如何好,
    同学们实在看不下去了,于是几个同学就商量了下,在群里发语音,但是录音都不说话这样发了几十条语音,里面都是
    没有声音的,没过多久,就看到那悲催的同学慌慌张张地和老师请假去售后了!"""
    print(wecomgpt.chat(f"假设你是一个精通写作语文老师,根据作文草稿重写一篇100分(满分100)的作文，要求主题突出、内容充实、条理清晰、层次分明、有文采、用词丰富。并为作文起一个最好的标题。作文草稿为：{ocr_text}"))
    print(wecomgpt.chat(f"对改写前后的作文打分(0-100分)并做出详细评价，给出写作改进意见。"))
    # print(wecomgpt.chat("假设你是一个语文老师，精通写作。根据OCR识别内容写一篇优秀获奖满分作文,对两篇作文打分并做出详细评价，给出写作改进意见。"))
    # print(wecomgpt.chat("假设你是一个语文老师，精通写作。OCR识别内容为一篇小学生写的作文草稿，将上面的作文改写为获奖满分作文,对改写前后的作文打分并做出详细评价，给出写作改进意见。"))
