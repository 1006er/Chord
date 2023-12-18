# Chord环 简介及部署使用手册

## 项目简介
在原型系统中利用Chord环来实现服务注册信息的存储与各个服务实例状态信息维护的功能，服务注册信息是存储服务名称到IP的映射用于服务发现，服务实例状态信息的维护则是在服务调用时为服务实例的选择提供参考。

## 架构设计
![image](https://gitee.com/wrj1006er/pic/raw/master/pic/chord%E6%9E%B6%E6%9E%84%E5%9B%BE.png)
在结构的设计中，分为三个层。
1. 基于Python Flask框架对外提供的HTTP接口。（服务注册，服务发现，服务状态查询，服务状态上报）
2. 基于JAVA 的chord环系统。包括环的创建，节点加入，节点退出，环信息查询，key值定位。
3. 基于Redis 的K-V数据库，利用AOF日志开启持久化存储。

## 部署手册
- 虚拟机配置（ubuntu-81.0.4）
- 安装java运行环境

```shell
apt install openjdk-11-jre-headless
apt install openjdk-11-jdk-headless //java编译环境
```

- 安装python 运行环境
```shell
sudo apt install python3-pip //安装pip
pip3 install flask   //安装flask web 框架
pip3 install redis //安装redis工具
pip3 install flask_cors //安装falask_cors 组件
```

- redis 数据库安装 docker方式
```shell
sudo apt  install curl //安装curl
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun //安装docker 配置镜像地址为阿里云
sudo docker pull redis //下载 redis的镜像
mkdir -p /home/redis/myredis // 递归创建文件夹用于config 文件以及data挂载
cd /home/redis/myredis  
mkdir data
touch redis.conf
vim redis.conf //配置conf文件
docker run --restart=always --log-opt max-size=100m --log-opt max-file=2 -p 6379:6379 --name myredis -v /home/redis/myredis/myredis.conf:/etc/redis/redis.conf -v /home/redis/myredis/data:/data -d redis redis-server /etc/redis/redis.conf  --appendonly yes  --requirepass 000415 //启动redis
```

- Redis conf文件内容
```
# bind 192.168.1.100 10.0.0.1
# bind 127.0.0.1 ::1
#bind 127.0.0.1

protected-mode no
port 6379
tcp-backlog 511
requirepass 000415
timeout 0
tcp-keepalive 300
daemonize no
supervised no
pidfile /var/run/redis_6379.pid
loglevel notice
logfile ""
databases 30
always-show-logo yes
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir ./
replica-serve-stale-data yes
replica-read-only yes
repl-diskless-sync no
repl-disable-tcp-nodelay no
replica-priority 100
lazyfree-lazy-eviction no
lazyfree-lazy-expire no
lazyfree-lazy-server-del no
replica-lazy-flush no
appendonly yes
appendfilename "appendonly.aof"
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-load-truncated yes
aof-use-rdb-preamble yes
lua-time-limit 5000
slowlog-max-len 128
notify-keyspace-events ""
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
list-compress-depth 0
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
hll-sparse-max-bytes 3000
stream-node-max-bytes 4096
stream-node-max-entries 100
activerehashing yes
hz 10
dynamic-hz yes
aof-rewrite-incremental-fsync yes
rdb-save-incremental-fsync yes
```
- 清空redis
```
docker exec -it f48c0fa892ed redis-cli
auth "000415"
flushall
```

## 运行手册
运行分为两个部分第一个部分在集群中启动Chord环，第二个部分为启动Flask。
- 启动Chord环
```
# 创建Chord 环在终端中执行 参数：port是希望Chord运行的端口。
JAVA Chord port
# 加入Chord环 参数：前一组ip port是已经在Chord环中的任意一个节点的ip port，第三个参数port是设置Chord在本集群中运行Chord的端口。
JAVA Chord ip port port
```
- 启动Python Flask
```
# 在每一个Chord节点上运行。
python3 Flask_chord.py
```