#!/bin/sh


SERVICE_ROOT=`pwd`
SERVICE_NAME=NODE_DAEMON
SERVICE_HOME=$SERVICE_ROOT
SERVICE_VENV=$SERVICE_ROOT/DaemonVENV

PYTHONPATH=$SERVICE_HOME:$PYTHONPATH
export PYTHONPATH

if [ ! -d log ]
then
   mkdir log
fi

Log=log/daemon_service.log
DATE=`date`

echo "####################################################" >> $Log
echo "$SERVICE_NAME startup..." >> $Log

Cnt=`ps -ef | grep $SERVICE_NAME | grep -v grep | wc -l`
PROCESS=`ps -ef | grep $SERVICE_NAME | grep -v grep | awk '{print $2}'`

if [ $Cnt -ne 0 ]
then
   echo "$DATE : $SERVICE_NAME(PID : $PROCESS) is already running" >> $Log
   echo "$DATE : $SERVICE_NAME(PID : $PROCESS) is already running"
else

   nohup `$SERVICE_VENV/bin/python3 $SERVICE_HOME/NodeDaemon.py start` 1>/dev/null 2>&1 &

   echo "$DATE : $SERVICE_NAME startup" >> $Log
   echo "$DATE : $SERVICE_NAME startup"
fi

echo "###################################################" >> $Log
echo "" >> $Log
 

