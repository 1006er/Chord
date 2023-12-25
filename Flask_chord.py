from flask import Flask
from flask import request
from flask import jsonify
import os
import redis
import json
import random
import requests

from flask_cors import CORS

local_ip = '192.168.10.1'
chord_port = '8001'


dit = {}

# 随机生成GVIP
def Creat_Gvip():
    num1 = 212 
    num2 = random.randint(0,255) 
    num3 = random.randint(2,254) 
    Gvip = "10." + str(num1) +'.'+str(num2)+'.'+str(num3)
    return Gvip
# 实例化，可视为固定格式
app = Flask(__name__)
# route()方法用于设定路由；类似spring路由配置
CORS(app, resources=r'/*')  # 注册CORS, "/*" 允许访问所有api


# 在chordnode1上进行查询操作 输入key值返回节点
def query_function(key):
    print("chord 查询"+key)
    str = "java Query " + local_ip + " " + chord_port+" "
    result = os.popen(str+key)
    context = result.read()
    for line in context.splitlines():
        start = line.find('/')
        end = line.find(':')
        ip = line[1:end]
        port = line[end+1:]
    result.close()
    dic = {}
    dic['ip'] = ip
    dic['port'] = port
    return dic
 
# 输入key值所在的节点ip 以及key值 返回查询结果（成功返回数据，失败返回str NULL）
def redis_select(key):
    print("redis 查询"+ key)
    ip = local_ip
    r = redis.Redis(host=ip,port=6379,db=0,password='000415')
    ans = r.get(key)
    if ans != None:
        return ans
    else:
        return "NULL"

# 利用redis的ip存储数据，成功返回success 失败返回false
def redis_set(key,value):
    ip = local_ip
    r = redis.Redis(host=ip,port=6379,db=0,password='000415')
    ans = r.set(key,value)
    if ans:
        return 'success'
    return 'false'



# 服务注册
@app.route('/services/register/',methods = ['post'])
def sname_register():
    data = request.get_data()
    json_data  = json.loads(data.decode("utf-8"))
    sName = json_data.get("sName")
    lSip = json_data.get("lSip")
    ans = query_function(sName)
    chord_ip = ans['ip']
    url = "http://"+chord_ip+":5000/_services/register"
    print("===============================================调用服务注册接口  服务名称: "+sName+"  服务Lsip: "+lSip)
    payload = {
        "sName": sName,
        "lSip": lSip
    }
    r = requests.post(url, data=json.dumps(payload))
    print(sName+"服务注册成功")
    return r.text


@app.route('/_services/register/',methods = ['post'])
def _sname_register():
        data = request.get_data()
        json_data  = json.loads(data.decode("utf-8"))
        sName = json_data.get("sName")
        lSip = json_data.get("lSip")
        ans = redis_select(sName)
        if ans != "NULL":
            dict = json.loads(ans)
            # 判断是否注册过
            flag = False
            service_instance_list = dict["Service_instance"]
            print(service_instance_list)
            for instance in service_instance_list:
                if instance["Lsip"] == lSip:
                    flag = True
                    break
            if flag == False:
                dict_service_instance = {'Lsip':lSip,'success_rate': 0,'latency': 0,'frequency': 0}
                dict['Service_instance'].append(dict_service_instance)
                value = json.dumps(dict, indent=2, sort_keys=True, ensure_ascii=False)
                ans = redis_set(sName,value)#成功返回字符串success失败返回false
                print("服务注册成功"+sName)
                return ans
            else:
                print("服务已经注册。无需再次注册")
                return "already register"
        else:
            #创建新的service
            print("首次注册服务")
            Gvip_temp = Creat_Gvip();
            print("生成Gvip"+Gvip_temp)
            dict_temp = {"Gvip": Gvip_temp ,"Service_instance": [{"Lsip": lSip,"frequency": 0 ,"latency": 0,"success_rate": 0}],"Sname": sName}
            value = json.dumps(dict_temp, indent=2, sort_keys=True, ensure_ascii=False)
            ans = redis_set(sName,value)#成功返回字符串success失败返回false
            print("服务注册成功"+sName)
            return ans

# 服务实例取消
@app.route('/services/registercancel/',methods = ['post'])
def sname_registercancel():
    data = request.get_data()
    json_data  = json.loads(data.decode("utf-8"))
    sName = json_data.get("sName")
    lSip = json_data.get("lSip")
    ans = query_function(sName)
    chord_ip = ans['ip']
    url = "http://"+chord_ip+":5000/_services/registercancel"
    print("===============================================调用服务取消注册接口  服务名称: "+sName+"  服务Lsip: "+lSip)
    payload = {
        "sName": sName,
        "lSip": lSip
    }
    r = requests.post(url, data=json.dumps(payload))
    print(sName+"服务取消注册成功")
    return r.text


@app.route('/_services/registercancel/',methods = ['post'])
def _sname_registercancel():
        data = request.get_data()
        json_data  = json.loads(data.decode("utf-8"))
        sName = json_data.get("sName")
        lSip = json_data.get("lSip")
        ans = redis_select(sName)
        if ans != "NULL":
            dict_temp = json.loads(ans)
            # 判断是否注册过
            service_instance_list = dict_temp["Service_instance"]
            print(service_instance_list)
            index = 0
            for instance in service_instance_list:
                index+=1
                if instance["Lsip"] == lSip:
                    print("index"+str(index))
                    print(dict_temp["Service_instance"])
                    print("服务实例存在，删除服务注册信息")
                    dict_temp["Service_instance"].pop(index-1)
                    print("==============================更改之后")
                    print(dict_temp)
                    value = json.dumps(dict_temp, indent=2, sort_keys=True, ensure_ascii=False)
                    ans = redis_set(sName,value)
                    return "The service instance has been deleted"
            print("服务实例不存在"+sName)
            return "The service instance does not exist"
        else:
            #创建新的service
            print("服务类型不存在")
            ans = "The service type does not exist"
            return ans

# 服务名称解析 /sname_resolution
@app.route('/services/resolution/')
def sname_resolution():
    key = request.args['sname']
    print("=============================================调用服务名称解析接口：",key)
    ans = query_function(key)
    #ans = redis_select(ans['ip'],key)
    url = "http://"+ans['ip']+':5000/_services/resolution/?sname='+key
    json_dict = {
        "gVip":"0.0.0.0",
        "msg":"Failed"
    }
    r = requests.get(url)
    ans = r.text
    if ans != "NULL":
        dict = json.loads(ans)
        json_dict["gVip"] = dict["Gvip"]
        json_dict["msg"] = "Success"
        dit[json_dict["gVip"]] = ans
    print("服务名称解析结果")
    print(jsonify(json_dict))
    return jsonify(json_dict)

@app.route('/_services/resolution/')
def  _sname_resolution():
    key = request.args['sname']
    ans = redis_select(key)
    return ans


#查询服务
@app.route('/services/servicestate')
def servicestate():
    key_1 = request.args['gvip']
    print("================================================调用服务状态查询接口  gvip:"+key_1)
    key = dit[key_1]
    print("服务状态查询结果"+key)
    return key

# 更新服务状态信息
@app.route('/service_status_storage')
def service_status_storage():
    key = request.args['sname']
    Lsip = request.args['Lsip']
    success_rate = request.args['success_rate']
    latency = request.args['latency']
    frequency = request.args['frequency']
    ans = query_function(key)
    print("=====================================调用服务状态更新接口：key"+key+"   lsip:"+Lsip)
    url = "http://"+ans['ip']+':5000/_service_status_storage?sname='+key+"&Lsip="+Lsip+'&success_rate='+success_rate+'&latency='+latency+'&frequency='+frequency
    r = requests.get(url)
    print("服务状态查询结果"+r.text)
    return r.text

@app.route('/_service_status_storage')
def _service_status_storage():
    key = request.args['sname']
    Lsip = request.args['Lsip']
    success_rate = request.args['success_rate']
    latency = request.args['latency']
    frequency = request.args['frequency']
    json_dict_str = redis_select(key)
    dict = json.loads(json_dict_str)
    for i in range(len(dict['Service_instance'])):
        if(dict['Service_instance'][i]['Lsip'] == Lsip):
            dict['Service_instance'][i]['success_rate'] = float(success_rate)
            dict['Service_instance'][i]['latency'] = float(latency)
            dict['Service_instance'][i]['frequency'] = float(frequency)

    value = json.dumps(dict, indent=2, sort_keys=True, ensure_ascii=False)
    print("----------------------------------------------------------------------------------------------------")
    ans = redis_set(key,value)
    return value


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
