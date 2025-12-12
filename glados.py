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
    # glados账号cookie
    cookies = os.environ.get("GLADOS_COOKIE", []).split("&")
    
    if not cookies or cookies[0] == "":
        print('未获取到COOKIE变量') 
        exit(0)

    url = "https://glados.rocks/api/user/checkin"
    url2 = "https://glados.rocks/api/user/status"
    referer = 'https://glados.rocks/console/checkin'
    origin = "https://glados.rocks"
    useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    payload = {'token': 'glados.one'}

    for index, cookie in enumerate(cookies):
        try:
            # 1. 执行签到
            checkin = requests.post(
                url,
                headers={
                    'cookie': cookie,
                    'referer': referer,
                    'origin': origin,
                    'user-agent': useragent,
                    'content-type': 'application/json;charset=UTF-8'
                },
                data=json.dumps(payload)
            )
            
            # 2. 获取状态 (这是报错的地方，增加了判断)
            state = requests.get(
                url2,
                headers={
                    'cookie': cookie,
                    'referer': referer,
                    'origin': origin,
                    'user-agent': useragent
                }
            )
            
            # 解析 JSON
            res = state.json()
            checkin_res = checkin.json()
            
            # --------------------------------------------------------------------------------------------------------#  
            # 关键修复：先判断 code 是否为 0 (0 代表成功获取到了数据)
            if res.get('code') == 0:
                time_str = res['data']['leftDays']
                # 处理天数为字符串或浮点数的情况
                time_str = str(time_str).split('.')[0]
                email = res['data']['email']
                
                mess = checkin_res.get('message', '无返回消息')
                
                log_info = f"{email} ---- 结果: {mess} ---- 剩余({time_str})天"
                print(log_info)
                sendContent += log_info + '\n'
            
            else:
                # 如果 code 不是 0，说明 cookie 失效或者接口报错
                error_msg = res.get('message', '未知错误')
                print(f"账号{index+1} Cookie失效或异常: {error_msg}")
                sendContent += f"账号{index+1}: Cookie失效，请更新! ({error_msg})\n"
            
            # --------------------------------------------------------------------------------------------------------#   
            
        except Exception as e:
            print(f"账号{index+1} 运行出错: {e}")
            sendContent += f"账号{index+1} 脚本运行出错: {e}\n"

    # 发送推送
    if sckey != "" and sendContent:
        try:
            requests.get('http://www.pushplus.plus/send?token=' + sckey + '&title=GLaDOS签到通知&content=' + sendContent)
        except Exception as e:
            print(f"推送发送失败: {e}")
