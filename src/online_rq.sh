#!/bin/bash
#
#启动rq异步任务队列进程
#启动rqscheduler定时任务调度队列进程
#

dir=$(cd $(dirname $0); pwd)
cd $dir

#准备环境
if [ -r online_preboot.sh ]; then
    source ./online_preboot.sh
fi

pidfile1=${dir}/logs/rq.pid
logfile1=${dir}/logs/rq.log
[ -d ${dir}/logs ] || mkdir -p ${dir}/logs

case "$1" in
start)
    if [ -f $pidfile1 ]; then
        echo "$pidfile1 exists, process is already running or crashed"
    else
        echo "Starting rq server..."
        python -O rq_worker.py &>> $logfile1 &
        pid=$!
        echo $pid > $pidfile1
    fi
    ;;

run)
    # 前台运行
    python -O rq_worker.py
    ;;

autostart)
    #可用于监控进程，异常时自动启动服务
    if [ -f $pidfile1 ]; then
        PID1=$(cat $pidfile1)
        PIDNUM=$(ps aux|grep -v grep|grep ${PID1}|wc -l)
        if [ "${PIDNUM}" = "0" ]; then
            bash $0 stop
            bash $0 start
        fi
    else
        bash $0 start
    fi
    ;;

stop)
    if [ ! -f $pidfile1 ]; then
        echo "$pidfile1 does not exist, process is not running"
    else
        echo "Stopping rq server..."
        pid=$(cat $pidfile1)
        kill $pid
        while [ -x /proc/${pid} ]
        do
            echo "Waiting for rq to shutdown ..."
            kill $pid ; sleep 1
        done
        echo "rq stopped"
        rm -f $pidfile1
    fi
    ;;

status)
    if [ -f $pidfile1 ]; then
        PID1=$(cat $pidfile1)
        if [ ! -x /proc/${PID1} ]
        then
            echo 'rq is not running'
        else
            echo "rq is running ($PID1)"
        fi
    else
        echo "$pidfile1 is not exist"
    fi
    ;;

restart)
    bash $0 stop
    bash $0 start
    ;;

*)
    echo "Usage: $0 start|autostart|stop|restart|status"
    ;;
esac
