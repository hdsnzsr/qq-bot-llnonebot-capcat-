import time



txt_tables = []
f = open("qq line.txt", "r",encoding='utf-8')
line = f.readline() # 读取第一行
while line:
                txt_data = eval(line) # 可将字符串变为元组
                txt_tables.append(txt_data) # 列表增加
                line = f.readline() # 读取下一行
f.close()
t = txt_tables

#需要自己创建qq line.txt，格式是一行一条群号，不用接分号
#目前用不到time库）
