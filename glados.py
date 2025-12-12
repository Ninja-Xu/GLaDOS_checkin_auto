import requests
import json
import os

# -------------------------------------------------------------------------------------------
# github workflows
# -------------------------------------------------------------------------------------------
if __name__ == '__main__':
    # pushplus秘钥 申请地址 http://www.pushplus.plus
    sckey = os.environ.get("PUSHPLUS_TOKEN", "")
    # 推送内容
    sendContent = ''
    
    # 获取环境变量
    # 1. Cookies: 对应 curl 命令 -b 后的值
    cookies = os.environ.get("GLADOS_COOKIE", []).split("&")
    # 2. Authorization: 对应 curl 命令 -H 'authorization: ...' 后的值 (新增)
    #    如果是多个账号，请同样用 & 符号分隔，顺序要和 Cookie 一致
    auth_tokens = os.environ.get("GLADOS_AUTHORIZATION", "").split("&")
    
    if not cookies or cookies[0] == "":
        print('未获取到 GLADOS_COOKIE 变量')
        exit(0)

    # 填充 auth_tokens 列表，防止长度不一致导致报错
    if len(auth_tokens) < len(cookies):
        # 如果没有提供足够的 auth token，就用空字符串填充，防止索引越界
        auth_tokens.extend([""] * (len(cookies) - len(auth_tokens)))

    url = "https://glados.rocks/api/user/checkin"
    url2 = "https://glados.rocks/api/user/status"
    referer = 'https://glados.rocks/console/checkin'
    origin = "https://glados.rocks"
    # 更新 User-Agent 与你的 curl 保持一致，以防被反爬
    useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
    payload = {'token': 'glados.one'}

    for index, cookie in enumerate(cookies):
        # 获取对应的 authorization，如果为空则不发送该头或发送空值(视API宽容度而定)
        current_auth = auth_tokens[index] if index < len(auth_tokens) else ""
        
        # 构造请求头
        headers = {
            'cookie': cookie,
            'referer': referer,
            'origin': origin,
            'user-agent': useragent,
            'content-type': 'application/json;charset=UTF-8',
            # 新增 authorization 头
            'authorization': current_auth
        }

        try:
            # 1. 执行签到
            checkin = requests.post(url, headers=headers, data=json.dumps(payload))
            
            # 2. 获取状态
            state = requests.get(url2, headers=headers)
            
            res = state.json()
            checkin_res = checkin.json()
            
            # 调试打印 (GitHub Actions 日志中可见)
            # print(f"账号{index+1} 状态响应: {res}") 

            if res.get('code') == 0:
                time_str = str(res['data']['leftDays']).split('.')[0]
                email = res['data']['email']
                mess = checkin_res.get('message', '无返回消息')
                
                log_info = f"{email} ---- 结果: {mess} ---- 剩余({time_str})天"
                print(log_info)
                sendContent += log_info + '\n'
            else:
                error_msg = res.get('message', '未知错误')
                print(f"账号{index+1} 失败 (Code: {res.get('code')}): {error_msg}")
                sendContent += f"账号{index+1}: 签到失败，请检查 Cookie 和 Authorization! ({error_msg})\n"
        
        except Exception as e:
            print(f"账号{index+1} 脚本异常: {e}")
            sendContent += f"账号{index+1} 异常: {e}\n"

    # 推送
    if sckey != "" and sendContent:
        try:
            requests.get('http://www.pushplus.plus/send?token=' + sckey + '&title=GLaDOS签到通知&content=' + sendContent)
        except Exception as e:
            print(f"推送失败: {e}")
