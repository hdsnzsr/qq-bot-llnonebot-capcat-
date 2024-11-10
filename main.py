from datetime import date
import uvicorn
import requests
import random
import reportlab
import json
from fastapi import FastAPI, Request
import psutil
import subprocess
import yaml
import os
import qianfan
import http.client
import urllib3
import time
import redis
from txt_load import t
import sys
#这里需要的库：uvicrom，requests,random,json,psutil,yaml,os,qianfan(ai的),http.client
output_file = "date.txt"

with open ('./config.yml','r',encoding= 'UTF-8') as f :
    result = yaml.load(f.read(),Loader=yaml.FullLoader)
#api = result['api']

# 信息发送
URL = "http://localhost:3000"


app = FastAPI()
def q(key):
    print(f'key:{key}')

def get_value(key, data):
    return data.get(key, "Key not found")

def a(value): 
    print(f'Value: {value}')
def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

data = load_json('x.json') 
for key, value in data.items():
    q(key)   # 将键传递给函数 q
    a(value) # 将值传递给函数 a
# 读取问题和答案
    
def extract_after_keyword(input_string, keyword="[CQ:at,qq=430262007] "):
        # 查找关键字
        index = input_string.find(keyword)
        
        if index != -1:  # 如果找到了关键字
            # 提取关键字后面的所有字符
            result = input_string[index + len(keyword):]
            return result  # 去除首尾空格
        else:
            return None  # 如果未找到关键字，返回None
        


# 获取菜单名
def get_name():

    with open("yang.json",mode='r',encoding='utf-8') as get_names:
        js = json.loads(get_names.read()) # 将内容转换为json数据格式
        return js['菜单名']

# 获取时间
#换算月日天分钟
def get_time(number): # number : 分钟

    # 时间计算
    ji = int(number) / 60

    if ji > 34560:
        mo = int (int(ji)/34560)
        d=int((int(ji)-mo*34560)/1440)
        h=int((int(ji)-mo*34560-d*1440)/60)
        m=int((int(ji)-mo*34560-d*1440-h*60))
        return str(mo) + f"月{d}天{h}小时{m}分钟"
    elif ji == 34560:
        return "1月0天0小时0分钟"
    elif ji > 1440 :
        d = int(int(ji)/1440)
        h = int((int(ji)-d*1440)/60)
        m = int(int(ji)-h*60-d*1440)
        return "0月"+str(d)+ f"天 {h}小时 {m}分钟"
    elif ji == 1440:
        return "0月1天0小时0分钟"

    elif ji > 60 :
        h = int(int(ji)/60)
        m = int(int(ji)-h*60)
        return "0月0天"+str(h) + f"小时 {m}分钟" 
    elif ji == 60:
        return "0月0天1小时0分钟"
    else:
        m = int(ji)
        return "0月0天 0小时"+str(m) + "分钟"
    
@app.post("/")
async def root(request: Request):
    data = await request.json()  # 获取事件数据
    with open(output_file, 'w') as f:
    # 将print的数据写入到文件中
        print(data, file=f)
    print(data)

    # 通知信息
    if data['post_type'] == 'notice' :

        # 群聊禁言
        if data['notice_type'] == 'group_ban' and data['sub_type'] == 'ban' :

            # 获取禁言时间
            ban_time = get_time(data['duration'])
            print(ban_time) 

            # 获取被执行人ID
            user_id = data['user_id']

            # 获取执行人ID
            operator_id = data['operator_id']

            # 获取群聊信息
            group_id = data['group_id']


            url = URL + "/send_group_msg"
            
            payload = {
                "group_id": group_id,
                "message": [
                    {
                        "type": "at",
                        "data": {
                            "qq": user_id  # all 表示@全体
                        }
                    },
                    {
                        "type": "text",
                        "data": {
                            "text": f"\nQQ群:{group_id} \nQQ:{user_id}\n被禁言时长{ban_time}\n执行人:{operator_id}"
                        }
                    }
                ]
            }

            repone = requests.post(url,json=payload)

   #群播报
    if data ['post_type'] == 'notice' :
        if data['group_id'] in t:
         #退群播报
            if  data ['notice_type'] == 'group_decrease' and data ['sub_type'] == 'leave':

                url = "http://localhost:3000/send_group_msg"
                #获取群号和退群人
                user_id = data ['user_id']
                group_id = data ['group_id']

                payload = json.dumps({
                    "group_id": group_id,
                    "message": [
                        {
                            "type": "text",
                            "data": {
                                "text": f'{user_id}退群了'
                            }
                        }
                    ]
                    })
                headers = {
                    'Content-Type': 'application/json'
                }

                response = requests.request("POST", url, headers=headers, data=payload)

                print(response.text) 
                with open(output_file, 'w') as f:
                    # 将print的数据写入到文件中
                    print(response.text, file=f)
            if data ['notice_type'] == 'group_increase' :
                #如果是被邀请进来的
                if data ['sub_type'] == 'invite':
                #获取邀请人的信息
                    group_id = data ['group_id']
                user_id = data ['user_id']
                operator_id = data ['operator_id']

                url = "http://localhost:3000/send_group_msg"

                payload = json.dumps({
                "group_id": group_id,

                "message": [
                    
                {
                    "type": "text",
                    "data": {
                        "text": f"{user_id}被{operator_id}邀请进了群聊\n热烈欢迎~"
                        }
                    }
                ]
                })
                headers = {
                'Content-Type': 'application/json'
                }
                
                response = requests.request("POST", url, headers=headers, data=payload)


                print(response.text)
                with open(output_file, 'w') as f:
                    # 将print的数据写入到文件中
                    print(response.text, file=f)


                #扫码进群的
            elif data ['sub_type'] == 'approve':
                group_id  = data ['group_id']
                user_id = data ['user_id']
                url = URL + "/send_group_msg"

                payload = json.dumps({
                        "group_id": group_id,
                        "message": [
                            {
                                "type": "text",
                                "data": {
                                    "text": f"{user_id}被{operator_id}邀请进了群聊\n热烈欢迎~"
                                }
                            }
                        ]
                        })
                headers = {
                        'Content-Type': 'application/json'
                        }

                response = requests.request("POST", url, headers=headers, data=payload)

                print(response.text)
                with open(output_file, 'w') as f:
                    # 将print的数据写入到文件中
                    print(response.text, file=f)
                
     #好友验证
    if data['post_type'] == 'request' and data ['request_type'] == 'friend':\
      
        url =URL + "/set_friend_add_request"
        #获取请求id和备注
        flag = data ['flag']
        remark = data ['comment']

        payload = json.dumps({

        "flag": flag,
        "approve": True,
        "remark": remark

        })
        headers = {

        'Content-Type': 'application/json'

        }

        response = requests.request("POST", url, headers=headers, data=payload)

    # 群聊信息
    if data['message_type'] == 'group' :

      if data['group_id'] in t:
      
        # 关键词
        if data["raw_message"] == '菜单' :

            # 获取发送信息的QQ群号
            group_id = data['group_id']
            user_id = data['user_id']

            url = URL + "/send_group_msg"
            
            payload = {
                "group_id": group_id,
                "message": [
                    {
                        "type": "at",
                        "data": {
                            "qq": user_id  # all 表示@全体
                        }
                    },
                    {
                        "type": "text",
                        "data": {
                            "text": "\n-----xyang bot-----\n     当前版本BATE\n   运行状态  ai对话  \n     剩下的还在写"#菜单的写入，\n是换行
                        }
                    }
                ]
            }

            repone = requests.post(url,json=payload)
        #今日老婆
        elif data ['raw_message'] == '今日老婆':
            user_id = data['user_id']
            group_id = data['group_id']
            url = URL + "/send_group_msg"
            conn = http.client.HTTPSConnection("localhost", 3000)
            payload = json.dumps({

            "group_id": group_id,
            "no_cache": True

            })
            headers = {
                'Content-Type': 'application/json'

            }
            conn.request("POST", "/get_group_member_list", payload, headers) 

            res = conn.getresponse()
            dat = res.read()

            print(data.decode("utf-8"))
            with open(output_file, 'w') as f:
                    # 将print的数据写入到文件中
                    print(data.decode("utf-8"), file=f)
            wife =random.choice(dat)



            payload = {
                    "group_id": group_id,
                    "message": [
                        {
                            "type": "at",
                            "data": {
                                "qq": user_id  # all 表示@全体
                            }
                        },
                        {
                            "type": "text",
                            "data": {
                                "text": f" 你今天的老婆是{str(wife)}" 
                            }
                        }
                    ]
                }
            repone = requests.post(url,json=payload)
            #还没写好，目前会报ssl错误，如果有会修的可以私聊我或者开个问题来告诉我
        elif data['raw_message'] == '运行状态':
            group_id = data['group_id']
            user_id = data ['user_id']
            cpu_usage = psutil.cpu_percent(interval=1)

            print("当前CPU使用率：%f%%" % cpu_usage)
            with open(output_file, 'w') as f:
                    # 将print的数据写入到文件中
                    print("当前CPU使用率：%f%%" % cpu_usage, file=f)
            print()
            url = URL + "/send_group_msg"
            payload = {
                "group_id": group_id,
                "message": [
                    {
                        "type": "at",
                        "data": {
                            "qq": user_id  # all 表示@全体
                        }
                    },
                    {
                        "type": "text",
                        "data": {
                            "text": f"  当前CPU使用率： {int(cpu_usage)}%" 
                        }
                    }
                ]
            }
            repone = requests.post(url,json=payload)

        if '[CQ:at,qq="bot的qq号"]' in data ['raw_message']:
            group_id = data ['group_id']
            user_id = data['user_id']
            sample_string = data['raw_message']
            result = extract_after_keyword(sample_string)
            dt = load_json('x.json')
            key = result 
            url = URL + "/send_group_msg"
            if  key == "问题2" or key == "问题3":
                            payload = {
                    "group_id": group_id,
                    "message": [
                        {
                            "type": "at",
                            "data": {
                                "qq": user_id  # all 表示@全体
                            }
                        },
                        {
                            "type": "text",
                            "data": {
                                "text": "答案1"
                            }
                        }
                    ]
                }
          
            elif key == "问题":
                group_id = data['group_id']
                user_id = data['user_id']
                url = URL + "/send_group_msg"
                payload = {
                    "group_id": group_id,
                    "message": [
                        {
                            "type": "at",
                            "data": {
                                "qq": user_id  # all 表示@全体
                            }
                        },
                        {
                            "type": "text",
                            "data": {
                                "text": "答案" 
                            }
                        }
                    ]
                }
                repone = requests.post(url,json=payload)
            else :
                
                
                user_id=data['user_id']
                group_id=data['group_id']
#

                os.environ["QIANFAN_AK"] = "你自己的ak"
                os.environ["QIANFAN_SK"] = "你自己的sk"

                chat_comp = qianfan.ChatCompletion(ak="你自己的ak")

                        # 指定特定模型
                resp = chat_comp.do(model="ERNIE-4.0-8K", messages=[{
                            "role": "user",
                            "content": str(result)
                        }])



                payload = {
                            "group_id": group_id,
                            "message": [
                                {
                                    "type": "at",
                                    "data": {
                                        "qq": user_id  # all 表示@全体
                                    }
                                },
                                {
                                    "type": "text",
                                    "data": {
                                        "text": " "+resp["result"] # type: ignore
                                    }
                                }
                            ]
                        }
                repone = requests.post(url,json=payload)
                                

                        

            return {}

if __name__ == "__main__":
    uvicorn.run(app, port=8080)