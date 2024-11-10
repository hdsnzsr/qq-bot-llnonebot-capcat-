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