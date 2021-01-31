# -*- coding:utf-8 -*-  
import os
import requests,time
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import multiprocessing
import uuid,json
import base64

def parse_har(har_file_name):
    file = open(har_file_name,'r')
    content = file.read()
    my_har_origin = json.loads(content)
    m3u8 = None
    IV = None
    for req in my_har_origin['log']['entries']:
        #req_json = json.loads(req)
        if 'request' in req:
            if 'url' in req['request']:
                if "src/get?id=" in req['request']['url']:
                    m3u8 = req['response']['content']['text']
                if "authorize?id=" in req['request']['url']:
                    if req['response']['content']['mimeType'] == 'text/plain':
                        #IV = base64.b64encode(bytes(req['response']['content']['text'].encode('utf-8'))).decode('utf-8')
                        raise Exception("Key error, no solution for the moment")
                    else: 
                        IV = req['response']['content']['text']
    file.close()
    return m3u8,IV

def read_m3u8(m3u8,key,filename):
    all_content = base64.b64decode(m3u8).decode('utf-8')
    key  = base64.b64decode(key)
    cryptor = AES.new(key, AES.MODE_CBC, key) 
    if "#EXTM3U" not in all_content:
        print("not found video in " + filename)
        return 
    file_line = all_content.split("\n")
    time_str = time.strftime('%d-%H%M%S', time.localtime(time.time()))
    ts_name = "download/{}-{}.ts".format(time_str,filename)
    writer = open(ts_name, 'wb')
    for index, line in enumerate(file_line): # 第二层 
        if "EXTINF" in line: # 找ts地址并下载
            pd_url = file_line[index + 1] # 拼出ts片段的URL
            try:
                res = requests.get(pd_url)
                print(filename,pd_url)
            except Exception as e:
                print(e)
                print("请求出错，需要重新下载")
                writer.close()
                os.system("rm -f" + ts_name)
                return 
            writer.write(cryptor.decrypt(res.content))
    print("{} finish download".format(filename))
    writer.close()
    os.system("mv '{}' 'download/{}.ts'".format(ts_name,filename))
    os.system("rm -f " + '"har/' + har + '"')
    return 0

if __name__ == '__main__': 
    har_list = os.listdir('har/')
    os.system("mkdir download")
    print(har_list)
    pool = multiprocessing.Pool(processes = 3)
    for har in har_list:
        file_without_suffix = har.rsplit('.')[0]
        print(file_without_suffix)
        try:
            m3u8,key = parse_har('har/'+har)
        except Exception as e:
            print("【 {} 】 parse error :{}".format(har,e))
        else:
            pool.apply_async(read_m3u8,(m3u8,key,file_without_suffix))
    pool.close()
    pool.join()
            
