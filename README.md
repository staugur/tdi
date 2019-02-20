# Tdi
花瓣网、堆糖网下载油猴脚本的远程下载服务

此程序相当于`https://open.sainitc.com/CrawlHuaban即中心端`的成员，用户选择远端下载后会由中心端选择一个成员提供给用户，减少中心端压力。

流程是：

    1. 成员端启动程序，到中心端页面`https://open.sainitc.com/CrawlHuaban/Register`注册成员端URL。
    2. 中心端校验成员端规则<ping>，没问题注册到mysql(缓存到redis)。
    3. 中心端定时检测成员端状态<state>，查询其可用性、磁盘、负载、内存。
    4. 用户请求时，中心端根据成员端状态计算是否可用(资源充足)，然后从可用列表中随机分配。


Nginx配置参考：
```
server {
    listen 80;
    server_name 域名;
    charset utf-8;
    #防止在IE9、Chrome和Safari中的MIME类型混淆攻击
    add_header X-Content-Type-Options nosniff;
    #处理静态资源:
    location ~ ^\/static\/.*$ {
        #tdi是程序目录
        root /tdi/src/;
        access_log off;
    }
    location /downloads {
        #下载程序目录
        alias /tdi/src/downloads/;
        default_type application/octet-stream;
        autoindex on;
        autoindex_format html;
        autoindex_exact_size on;
        autoindex_localtime on; 
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