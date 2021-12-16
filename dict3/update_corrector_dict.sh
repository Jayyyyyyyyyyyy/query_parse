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





hdfs_custom_confusion="/tmp/sunjian/query/qcdict/"${yesterday2}"/custom_confusion.txt"${yesterday2}
tmp_custom_confusion="./custom_confusion.txt"${yesterday2}
local_custom_confusion="./custom_confusion.txt"
$HADOOP_HOME fs -test -e $hdfs_custom_confusion
if [ $? -eq 0 ]; then
   echo $curtime"  hdfs_file "$hdfs_custom_confusion" is exit, process begin"
   $HADOOP_HOME fs -get ${hdfs_custom_confusion}
   if [ $? -eq 0 ]; then
       mv ${tmp_custom_confusion} ${local_custom_confusion}
   fi
else
    echo $curtime"  hdfs_file "$hdfs_custom_confusion" is not exist, please wait again"
    exit
fi

hdfs_plus_custom_confusion="/tmp/sunjian/query/qcdict/"${yesterday2}"/plus_custom_confusion.txt"${yesterday2}
tmp_plus_custom_confusion="./plus_custom_confusion.txt"${yesterday2}
local_plus_custom_confusion="./plus_custom_confusion.txt"
$HADOOP_HOME fs -test -e $hdfs_plus_custom_confusion
if [ $? -eq 0 ]; then
   echo $curtime"  hdfs_file "$hdfs_plus_custom_confusion" is exit, process begin"
   $HADOOP_HOME fs -get ${hdfs_plus_custom_confusion}
   if [ $? -eq 0 ]; then
       mv ${tmp_plus_custom_confusion} ${local_plus_custom_confusion}
   fi
else
    echo $curtime"  hdfs_file "$local_plus_custom_confusion" is not exist, please wait again"
    exit
fi




hdfs_sj_custom_confusion="/tmp/sunjian/query/qcdict/"${yesterday2}"/sj_custom_confusion.txt"${yesterday2}
tmp_sj_custom_confusion="./sj_custom_confusion.txt"${yesterday2}
local_sj_custom_confusion="./sj_custom_confusion.txt"
$HADOOP_HOME fs -test -e $hdfs_sj_custom_confusion
if [ $? -eq 0 ]; then
   echo $curtime"  hdfs_file "$hdfs_sj_custom_confusion" is exit, process begin"
   $HADOOP_HOME fs -get ${hdfs_sj_custom_confusion}
   if [ $? -eq 0 ]; then
       mv ${tmp_sj_custom_confusion} ${local_sj_custom_confusion}
   fi
else
    echo $curtime"  hdfs_file "$local_sj_custom_confusion" is not exist, please wait again"
    exit
fi


hdfs_syn="/tmp/sunjian/query/qcdict/"${yesterday2}"/syn.txt"${yesterday2}
tmp_syn="./syn.txt"${yesterday2}
local_syn="./syn.txt"
$HADOOP_HOME fs -test -e $hdfs_syn
if [ $? -eq 0 ]; then
   echo $curtime"  hdfs_file "$hdfs_syn" is exit, process begin"
   $HADOOP_HOME fs -get ${hdfs_syn}
   if [ $? -eq 0 ]; then
       mv ${tmp_syn} ${local_syn}
   fi
else
    echo $curtime"  hdfs_file "$local_syn" is not exist, please wait again"
    exit
fi