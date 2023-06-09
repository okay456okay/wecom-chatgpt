#!/usr/bin/env python3
# coding=utf-8
# https://ai.baidu.com/ai-doc/OCR/7kibizyfm


from aip import AipOcr
from config import BAIDU_OCR_APP_ID,BAIDU_OCR_API_KEY,BAIDU_OCR_API_SECRET
from log import logger

client = AipOcr(BAIDU_OCR_APP_ID, BAIDU_OCR_API_KEY, BAIDU_OCR_API_SECRET)


def image2txt_ocr(image_url):
    try:
        res_url = client.basicAccurateUrl(url=image_url)
        logger.info(f"image2txt_ocr, image_url: {image_url}, res_url: {res_url}")
    except Exception as e:
        logger.error(f"image2txt_ocr error, image_url: {image_url}, error: {e}")
        return False, "OCR识别错误，请联系管理员，谢谢"
    return True, '\n'.join([i.get("words", '') for i in res_url.get("words_result", [])])


if __name__ == '__main__':
    # image_url = 'https://wework.qpic.cn/wwpic/436957_NyMsbIpPTfWU0cL_1681950970/'
    image_url = 'https://img0.baidu.com/it/u=209039708,1791441701&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=682'
    print(image2txt_ocr(image_url))
