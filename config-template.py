# 我的企业 最下面
CORP_ID = "ww69bd8fda184"
# 在 应用管理 - 打开应用后，可查看 secret 和 agent_id
AGENT_SECRET = "IGJMX3Ye71PfQd7Eivx1i34uzo8dFW0"
AGENT_ID = 1000002
# 接收信息处设置
TOKEN = "U6pfDj2nfxEZRr"
ENCODING_AES_KEY = "EckrwxVr6e4bQ2nRInF0PNyF9rDaXjQK"
OCR_ENABLE = True
BAIDU_OCR_APP_ID = '32553'
BAIDU_OCR_API_KEY = 'llNjpb2PPhEzaCvGAyW1'
BAIDU_OCR_API_SECRET = 'UW7W9Z6Ae1neY8oyYNFCtW'
LOG_LEVEL = 'DEBUG'  # INFO
openai_api_base = 'https://api.openai.com/v1'
openai_api_key = 'sk-toKUib5xiW3BlbkFJKx6aXIQv3NkFjhRP3rdc' # openai
# openai_proxy_enable = True
OPENAI_PROXY_ENABLE = False
OPENAI_PROXY = {
    'http': 'http://127.0.0.1:1087',
    'https': 'http://127.0.0.1:1087'
}
ADMIN_USER = '管理员'
WELCOME_MESSAGE = """欢迎使用GPT智能助手"""
ERROR_MESSAGE = f"网络错误，请联系 {ADMIN_USER} 处理，谢谢"
FLASK_PORT = 8088
LLM_MAX_TOKENS = 1024
LLM_MODEL = 'gpt-3.5-turbo'
LLM_TEMPERATURE = 0.9
LLM_SYSTEM_PROMPT = ""
SAVE_CHAT_HISTORY = True
