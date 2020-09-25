# -*- coding:utf-8 -*-  
import os
import requests
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import uuid
import shutil

### 以下引用仅为了打包exe设置
import queue

### end

def read_m3u8(filename,uuid_str):
    m3u8_file = open(filename,"r")
    all_content = m3u8_file.read();
    if "#EXTM3U" not in all_content:
        raise BaseException("非M3U8的链接")
       
    file_line = all_content.split("\n")
    key = ""
    ## name 作为缺省值，可设置可不设置
    name = "new" 
    for index, line in enumerate(file_line): # 第二层
        if "#NAME" in line:
            name = line.split('=')[1]
            print("文件名是：",name)
        if "#EXT-X-KEY" in line:  # 找解密Key
            method_pos = line.find("METHOD")
            comma_pos = line.find(",")
            method = line[method_pos:comma_pos].split('=')[1]
            print("Decode Method：", method)
            
            uri_pos = line.find("URI")
            quotation_mark_pos = line.rfind('"')
            key_path = line[uri_pos:quotation_mark_pos].split('"')[1]
            
            key_url = key_path # 拼出key解密密钥URL
            res = requests.get(key_url)
            key = res.content
            print("key_url：",key_url)
            print("key:",key)
            if(len(key)==0):
                print("秘钥解析异常")
                #raise BaseException("解密秘钥请求异常")
        if os.path.exists(uuid_str) == False:
            os.mkdir(uuid_str)
        if "EXTINF" in line: # 找ts地址并下载
            pd_url = file_line[index + 1] # 拼出ts片段的URL
            #print(pd_url)
            try:
                res = requests.get(pd_url)
            except Exception as e:
                print(e)
                print("开始回退操作，此过程将会清除已下载的视频流，请重新添加下载")
                delete_file(uuid_str)
                return
            c_fule_name = file_line[index + 1].rsplit("/", 1)[-1]
            ts_name = uuid_str+"/"+c_fule_name + ".tmp"
            print(ts_name)
            if len(key): # AES 解密
                cryptor = AES.new(key, AES.MODE_CBC, key)  
                with open(ts_name, 'ab') as f:
                    f.write(cryptor.decrypt(res.content))
            else:
                with open(c_fule_name, 'ab') as f:
                    f.write(res.content)
                    f.flush()
        if "#EXT-X-ENDLIST" in line:
            merge_file(name,uuid_str)
            name = "new"

def delete_file(uuid_str):
    # 下载失败时，删除已经下载的文件
    #os.chdir("./"+uuid_str)
    print("当前位于 %s" % (os.getcwd()) )
    shutil.rmtree(uuid_str,True)
    if os.path.exists(uuid_str):
        os.rmdir(uuid_str)
    print("删除完成")

def merge_file(file_name,uuid_str):
    if file_name == "new":
        file_name = uuid_str
    os.chdir("./"+uuid_str)
    #print("进入到 %s" % (os.getcwd()) )
    copy_cmd = 'copy /b *.tmp "'+ file_name + '.ts"'
    print(copy_cmd)
    os.system(copy_cmd)
    mv_cmd = 'move "' + file_name + '".ts ../'
    os.system(mv_cmd)    
    #os.rename("new.tmp", file_name+".ts")
    print(file_name,"完成")
    os.chdir("../")
    delete_file(uuid_str)

if __name__ == '__main__': 
    print("将m3u8信息放入video.txt中")
    os.system("notepad video.txt")
    # uuid 作为该任务唯一的标识符
    uuid_str = str(uuid.uuid4()).split("-")[-1]
    print(uuid_str)
    read_m3u8("video.txt",uuid_str)
    #delete_file("cbc07bcebfa2")
    #merge_file()