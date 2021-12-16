#/bin/bash

workdir=`pwd`
#echo $log
logdir=${workdir}/logs
if [ ! -d ${logdir}  ];then
  mkdir ${logdir}
fi

export JAVA_HOME=/usr/java/latest
HADOOP_HOME=/home/hadoop/hadoop-2.6.0/bin/hadoop
PYTHON_HOME=/home/hadoop/anaconda3/bin/python

today=$(date +%Y%m%d)
today2=$(date +%Y-%m-%d)
yesterday=$(date +%Y%m%d --date '1 days ago')
yesterday2=$(date +%Y-%m-%d --date '1 days ago')
curtime=$(date +'%Y-%m-%d %H:%M:%S')

yesterday2=$(date +%Y-%m-%d --date '1 days ago')


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


hdfs_mp3_check1="/tmp/sunjian/allmp3/"${yesterday2}"/mp3.all.check"${yesterday2}
tmp_mp3_check1="./mp3.all.check"${yesterday2}
local_mp3_check1="./mp3.all.mp3.check1"
$HADOOP_HOME fs -test -e $hdfs_mp3_check1
if [ $? -eq 0 ]; then
   echo $curtime"  hdfs_file "$hdfs_mp3_check1" is exit, process begin"
   $HADOOP_HOME fs -get ${hdfs_mp3_check1}
   if [ $? -eq 0 ]; then
       mv ${tmp_mp3_check1} ${local_mp3_check1}
   fi
else
    echo $curtime"  hdfs_file "$local_mp3_check1" is not exist, please wait again"
    exit
fi


hdfs_unmp3="/tmp/sunjian/allmp3/"${yesterday2}"/mp3.all.unmp3"${yesterday2}
tmp_unmp3="./mp3.all.unmp3"${yesterday2}
local_unmp3="./mp3.all.unmp3"
$HADOOP_HOME fs -test -e $hdfs_unmp3
if [ $? -eq 0 ]; then
   echo $curtime"  hdfs_file "$hdfs_unmp3" is exit, process begin"
   $HADOOP_HOME fs -get ${hdfs_unmp3}
   if [ $? -eq 0 ]; then
       mv ${tmp_unmp3} ${local_unmp3}
   fi
else
    echo $curtime"  hdfs_file "local_unmp3" is not exist, please wait again"
    exit
fi

