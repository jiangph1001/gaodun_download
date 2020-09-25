



# 运行

```
python3 download.py
```

执行后会自动通过记事本打开`video.txt`文件，此时手动将m3u8信息写入video.txt即可（覆盖已有的就行）

**目前仅支持windows下运行**

m3u8信息目前需要手动获取，通过chrome的开发者模式找到，样例如`video.txt`



# 原理

下载多个ts视频流，下载完成后统一执行合并，默认视频都是AES-128加密的，所以还需要解密

