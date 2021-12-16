#!/usr/bin/env bash
#/bin/bash



export JAVA_HOME=/usr/java/latest

workdir=`pwd`
#echo $log
logdir=${workdir}/logs
if [ ! -d ${logdir}  ];then
  mkdir ${logdir}
fi

source ~/.bashrc

HADOOP_HOME=/home/hadoop/hadoop-2.6.0/bin/hadoop
PYTHON_HOME=/home/hadoop/anaconda3/bin/python

today=$(date +%Y%m%d)
today2=$(date +%Y-%m-%d)
yesterday=$(date +%Y%m%d --date '1 days ago')
yesterday2=$(date +%Y-%m-%d --date '1 days ago')
curtime=$(date +'%Y-%m-%d %H:%M:%S')

yesterday2=$(date +%Y-%m-%d --date '1 days ago')


hdfs_mp3_all="/tmp/sunjian/allmp3/"${yesterday2}"/custom_confusion.txt_"${yesterday}
tmp_mp3_all="./custom_confusion.txt_"${yesterday}
local_mp3_all="./custom_confusion.txt"
$HADOOP_HOME fs -test -e $hdfs_mp3_all
if [ $? -eq 0 ]; then
   echo $curtime"  hdfs_file "$hdfs_mp3_all" is exit, process begin"
   $HADOOP_HOME fs -get ${hdfs_mp3_all}
   if [ $? -eq 0 ]; then
       mv ${tmp_mp3_all} ${local_mp3_all} 
   fi 
else
    echo $curtime"  hdfs_file "$hdfs_mp3_all" is not exist, please wait again"
    exit
fi

hdfs_mp3_all="/tmp/sunjian/allmp3/"${yesterday2}"/mp3.all"${yesterday2}
tmp_mp3_all="./mp3.all"${yesterday2}
local_mp3_all="./mp3.all"
$HADOOP_HOME fs -test -e $hdfs_mp3_all
if [ $? -eq 0 ]; then
   echo $curtime"  hdfs_file "$hdfs_mp3_all" is exit, process begin"
   $HADOOP_HOME fs -get ${hdfs_mp3_all}
   if [ $? -eq 0 ]; then
       mv ${tmp_mp3_all} ${local_mp3_all}
   fi
else
    echo $curtime"  hdfs_file "$hdfs_mp3_all" is not exist, please wait again"
    exit
fi


hdfs_mp3_hour="/tmp/sunjian/allmp3/"${yesterday2}"/hourlymp3"
tmp_mp3_hour="./hourlymp3"
local_mp3_hour="./hourlymp3_local"
$HADOOP_HOME fs -test -e $hdfs_mp3_hour
if [ $? -eq 0 ]; then
   echo $curtime"  hdfs_file "$hdfs_mp3_hour" is exit, process begin"
   $HADOOP_HOME fs -get ${hdfs_mp3_hour}
   if [ $? -eq 0 ]; then
       mv ${tmp_mp3_hour} ${local_mp3_hour}
   fi
else
    echo $curtime"  hdfs_file "$hdfs_mp3_hour" is not exist, please wait again"
    exit
fi
