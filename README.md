# Tdi
花瓣网、堆糖网下载油猴脚本的远程下载服务(Tdi for Python).

此程序相当于`CrawlHuaban`(中心端)的成员，用户选择远端下载后会由中心端选择一个成员提供给用户，减少中心端压力。

PHP版本的仓库地址是：https://github.com/staugur/tdi-php

Node.js版本的仓库地址是：https://github.com/staugur/tdi-node


## 部署：

1. 要求： Python2.7、Python3.5+和Redis
2. 下载： `git clone https://github.com/staugur/tdi && cd tdi/src`
3. 依赖： `pip install -r requirements.txt`
4. 配置： 即config.py，可以从环境变量中读取配置信息，可以编写`online_preboot.sh`进行额外设置，比如export环境变量
5. 启动： sh online_rq.sh start && sh online_gunicorn.sh start  # 若需前台启动，将start换成run即可

> 部署图
> ![](misc/deploy.gif)


## 更多文档：

[点击查看文档](https://docs.saintic.com/tdi/ "点击查看部署及使用文档")，关于普通部署、Docker部署、使用手册、注意事项等问题。

若上述地址异常，备用地址是：[https://saintic-docs.readthedocs.io/tdi/](https://saintic-docs.readthedocs.io/tdi/)


## Nginx参考：
```
server {
    listen 80;
    server_name 域名;
    charset utf-8;
    client_max_body_size 10M;
    client_body_buffer_size 128k;
    location /downloads {
        #下载程序目录
        alias /path/to/tdi/src/downloads/;
        default_type application/octet-stream;
        proxy_max_temp_file_size 0;
        if ($request_filename ~* ^.*?\.(zip|tgz)$){
            add_header Content-Disposition 'attachment;';
        }
    }
    location / {
       #13145是默认端口
       proxy_pass http://127.0.0.1:13145;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-Proto $scheme;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```