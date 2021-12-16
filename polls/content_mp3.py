# -*- coding: utf-8 -*-
# @Author    : Sunjian
# @Time      : 2020/04/23 3:19 PM
# @File      : content_mp3.py
# @Software  : PyCharm
# @Company   : Xiao Tang

import re
import time
import datetime
import threading
import json

class Extracter(object):
    def __init__(self):
        self.name = 'Dictor'

        self.mp3_all_path = './hdfs_dict/mp3.all'
        self.mp3check_path = './hdfs_dict/mp3.all.mp3.check1'
        self.myload_mp3_dict()
        self.t2 = threading.Thread(target=self.load_hdfs_mp3_dict, args=())
        self.t2.start()
        file3 = "./dict/content_dance_pair.csv"
        file4 = "./dict/new_category_dict.txt"

        self.dancelist = self.read_dance(file3, file4)




    def myload_mp3_dict(self):
        self.video_mp3_name_dict_for_match2 = {}
        self.unmp3_dict = set()
        tmp_qcmp3 = {}
        mp3_alllist = []
        with open(self.mp3_all_path, 'r', encoding='utf-8') as r:
            tmp = []

            for line in r:
                line = line[:-1].split('\t')
                if len(line)<5:
                    #print(line)
                    continue
                line[2] = int(line[2])
                line[4] = int(line[4])
                tmp.append(line)
                mp3 = line[0]
                qcmp3 = line[1]
                if line[4] == 0:
                    if qcmp3 not in tmp_qcmp3:
                        tmp_qcmp3[qcmp3] = int(line[2])
                    else:
                        if int(line[2])> tmp_qcmp3[qcmp3]:
                            tmp_qcmp3[qcmp3] = int(line[2])
                    mp3_alllist.append(line)
                else:
                    self.unmp3_dict.add(mp3)

        #对所有的MP3 qcmp3 放入字典里
        for tokens in mp3_alllist:
            mp3 = tokens[0]
            qcmp3 = tokens[1]

            if qcmp3 in tmp_qcmp3:
                if qcmp3 not in self.video_mp3_name_dict_for_match2 and qcmp3 not in self.unmp3_dict and int(tokens[2])>0:
                    self.video_mp3_name_dict_for_match2[qcmp3] = [qcmp3, int(tmp_qcmp3[qcmp3])]
            if mp3 not in self.video_mp3_name_dict_for_match2 and int(tokens[2])>0:
                self.video_mp3_name_dict_for_match2[mp3] = [qcmp3, int(tokens[2])]

        self.mp3check = {}
        with open(self.mp3check_path, "r") as f0:
            for line in f0:
                line = line.strip()
                tokens = line.split("\t")
                mp3 = tokens[0]
                if len(tokens) < 8: continue

                allcount = int(tokens[2])
                ratio = float(tokens[6])
                detail = tokens[7]
                tokens2 = detail.split("_")
                flag = 0
                for tt in tokens2:
                    tt_token = tt.split(":")
                    if len(tt_token) != 2: continue

                    restype = tt_token[0]
                    rescount = tt_token[1]
                    ratio22 = float(rescount) / allcount
                    if int(restype) == 22 and (ratio < 0.65 or ratio22 >= 0.1):
                        flag += 1

                if mp3 not in self.mp3check and flag > 0:
                    self.mp3check[mp3] = tokens


    def load_hdfs_mp3_dict(self):
        while True:
            ts = time.time()
            time.sleep(1)
            c = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            if c == "10:05:00":
                self.myload_mp3_dict()

    def read_dance(self, file1, file2):
        mlist = []
        with open(file1, "r")  as f0:
            for line in f0:
                line = line.strip()
                if line.startswith("\"label\""): continue
                tokens = line.split(",")
                for word in tokens:
                    if word.strip() != "":
                        mlist.append(word.strip())
        with open(file2, "r") as f1:
            for line in f1:
                line = line.strip()
                tokens = line.split(' ')
                if tokens[0].strip() != '':
                    mlist.append(tokens[0].strip())
        mlist.append("广场舞")
        mlist.append("舞蹈")
        mlist.append("视频")
        mlist.append("编舞")
        mlist.append("扇子舞")
        mlist.append("团队")
        mlist.append("舞蹈队")
        mlist.append("舞队")
        mlist.append("dj")
        mlist.append("长扇舞")
        mlist.append("扇舞")
        mlist.extend(
            ["正面教学", "正反面演示", "附背面演示", "正反面教学", "正面教学", "背面教学", "正面演示", "演示版", "教学版", "附教学", "正反面", "正背面", "正面", "背面", "示范",
             "演示", "口令", "正反", "教程", "大赛"])
        mlist.extend(["水兵舞","水兵","单人水兵舞","单人水兵"])

        dancelist = sorted(list(set(mlist)), key=len, reverse=True)
        # print("dancelist:num", len(dancelist))
        # for dance in dancelist:
        #     print(dance, type(dance))

        return dancelist
    # for video profile
    # def my_main(self, vid, title, uname, video_mp3_name, queryflag=0):
    #     # asynchronous function start for updating mp3 dict from hdfs
    #     content_mp3, cand_content_mp3list,restype = self.content_mp3_center_vsj(title, uname, video_mp3_name, queryflag)
    #     # result = {}
    #     # result['id'] = vid
    #     # result['profileinfo'] = {}
    #     # result['profileinfo']['content_mp3'] = content_mp3
    #     # final_res = json.dumps({'tag': result}, ensure_ascii=False)
    #     return content_mp3
    # for query parse
    def my_main(self, vid, title, uname, video_mp3_name, queryflag=0):
        # asynchronous function start for updating mp3 dict from hdfs
        content_mp3, cand_content_mp3list,restype = self.content_mp3_center_vsj(title, uname, video_mp3_name, queryflag)
        result = {}
        result['id'] = vid
        result['profileinfo'] = {}
        result['profileinfo']['content_mp3'] = content_mp3
        final_res = json.dumps({'tag': result}, ensure_ascii=False)
        return final_res


    '''
        返回content_mp3 和候选所有的content_mp3
    '''

    def content_mp3_center_vsj(self, title, uname, video_mp3_name, queryflag=0):
        content_mp3 = {}
        mp3name = ""
        restype = 0
        cand_content_mp3list = []
        cand_content_mp3set = set()

        title = title.strip()
        if len(title) == 0:
            restype = 1
            return content_mp3, cand_content_mp3list, restype

        #预处理标题
        name_index = title.find(uname)
        if name_index != -1:
            # remove user_name if possible
            title = title.replace(uname, '')
        title = title.lower()
        if '.mp3' in title:
            title = title.replace('.mp3', "")
        if '.mp4' in title:
            title = title.replace('.mp4', "")
        if '原创' in title:
            title = title.replace('原创', "")

        # 预处理标题 end

        mp3names, left_indices, right_indices = self.symbol_extract_mp3(title)

        num = len(mp3names)

        booname_flag = 0
        subtitle = ""
        subtitle_list = []
        if num ==0:
            if '(' in title or '（' in title:
                mp3names_y, _, _ = self.symbol_extract_mp3_v2(title)

                if len(mp3names_y) == 1:
                    subtitle = mp3names_y[-1]
                if len(mp3names_y)>=2:
                    subtitle_list = mp3names_y
        elif num==1:
            subtitle = mp3names[0]
            booname_flag +=1
        else:
            #多个
            subtitle_list = mp3names
            booname_flag +=len(mp3names)
        if queryflag==1:
            subtitle = ""


        mp3name= ""

        video_mp3_name2 = ""
        cand_content_mp3set.add(video_mp3_name)
        if len(video_mp3_name) != 0 and '》' not in video_mp3_name and video_mp3_name not in self.unmp3_dict:
            if video_mp3_name in self.video_mp3_name_dict_for_match2:
                video_mp3_name2 = self.video_mp3_name_dict_for_match2[video_mp3_name][0]
            else:
                # 新mp3
                video_mp3_name2 = video_mp3_name
        cand_content_mp3set.add(video_mp3_name2)

        #多个《》情况提取
        restype = 0
        if len(subtitle_list)>0:
            term_mp3list = []
            for term in subtitle_list:
                term2 = self.preprocess(term)
                if term2 in self.video_mp3_name_dict_for_match2:
                    term_mp3 = self.video_mp3_name_dict_for_match2[term2][0]
                    term_mp3list.append(term_mp3)
                cand_content_mp3set.add(term2)
            term_mp3list2 = sorted(term_mp3list, key=len)
            if len(term_mp3list2)>0:
                mp3name = term_mp3list2[-1]
                restype = 1
            # else:
            #     mp3name = ""
            #     restype = 0
        else:
            pass
        #restype = 10

        if (subtitle=="" or subtitle==video_mp3_name or subtitle==video_mp3_name2) and video_mp3_name2!="":
            mp3name = video_mp3_name2
            mp3name = self.preprocess(mp3name)
            mp3name = mp3name.strip("+")
            restype = 11

        if restype==0:
            # 从title 中提取在字典中所有的 候选的mp3
            # 《》或()里面的预处理
            subtitle2 = self.preprocess(subtitle)

            # 《》或()之外的预处理
            lefttitle = title.replace(subtitle, "")
            lefttitle2 = self.preprocess(lefttitle)

            cand_content_mp3set.add(subtitle2)

            subtitle3 = subtitle2.replace("+", "")

            # 《》在曲库里

            if subtitle in self.video_mp3_name_dict_for_match2:
                mp3name = self.video_mp3_name_dict_for_match2[subtitle][0]
                restype = 12
            # 归一化+号后处理 在曲库里
            if restype == 0:
                if subtitle2 in self.video_mp3_name_dict_for_match2:
                    mp3name = self.video_mp3_name_dict_for_match2[subtitle2][0]
                    restype = 13

            # 去掉+号存在曲库里
            if restype == 0:
                if subtitle3 != subtitle2:
                    if subtitle3 in self.video_mp3_name_dict_for_match2:
                        mp3name = self.video_mp3_name_dict_for_match2[subtitle3][0]
                        restype = 14
            if restype == 0:

                # 二次预处理，替换关键词

                # subtitle 替换关键词=>+
                subtitle2_tmp = subtitle2
                plusflag = 0
                if subtitle2.find("+") >= 0:
                    plusflag += 1
                if (plusflag == 0 or len(subtitle2) >= 9) and len(subtitle2)>0:
                    for term in self.dancelist:
                        subtitle2_tmp = subtitle2_tmp.replace(term, "+")
                    subtitle2 = subtitle2_tmp
                    if subtitle2.find("+") >= 0:
                        plusflag += 1
                subtitle2 = subtitle2.strip("+")

                # lefttitle 替换关键词=>+
                lefttitle2_tmp = lefttitle2
                leftplusflag = 0
                if lefttitle2_tmp.find("+")>=0:
                    leftplusflag +=1
                if subtitle == "":
                    for term in self.dancelist:
                        lefttitle2_tmp = lefttitle2_tmp.replace(term, "+")
                    lefttitle2 = lefttitle2_tmp
                lefttitle3 = lefttitle2.strip("+")

                subtitle_list = subtitle2.split("+")

                subtitle_list2 = []
                if len(subtitle_list) > 0:
                    subtitle_list2 = sorted(subtitle_list, key=len, reverse=True)

                subtitle2_v2 = "+" + subtitle2 + "+"
                subtitle2_set = set(subtitle_list)

                #cand_content_mp3set.add(subtitle2)

                #二次预处理end

                # 提取《》里面的所有的可能的mp3,《》之外的所有的可能的mp3, 并按长度排序

                mp3name_list, leftmp3name_list, candmatchs_mp3set = self.mp3_match2(subtitle2, lefttitle2)
                cand_content_mp3set = cand_content_mp3set.union(candmatchs_mp3set)

                mp3name_list2 = mp3name_list[::-1]
                leftmp3name_list2 = leftmp3name_list[::-1]

                # step1 <=3
                # step2 for mp3name_list 查找每个mp3 是否满足，满足就返回
                # step3  video_mp3_name 比较置信 情况下的提取
                # step4 没有满足情况下 for leftmp3name_list
                # step5 兜底返回结果

                # step1
                if len(subtitle2) <= 3 and subtitle2 not in self.video_mp3_name_dict_for_match2 and booname_flag>0:
                    mp3name = ""
                    restype = 20
                # step2
                # 根据+ split  结果，完全匹配的情况
                if restype == 0:
                    if plusflag > 0:
                        for term in subtitle_list2:
                            if term in self.video_mp3_name_dict_for_match2 and len(
                                    term) >= 3 and not term.isdigit():
                                cand_content_mp3set.add(term)
                                mp3name = self.video_mp3_name_dict_for_match2[term][0]
                                restype = 15
                                break

                # 根据+ 前缀，后缀情况
                if restype == 0:
                    if plusflag > 0:
                        for i, term in enumerate(mp3name_list2):
                            if (term in subtitle2_set or term + "+" in subtitle2_v2 or "+" + term in subtitle2_v2) and len(term)>=3:
                                mp3name = term
                                restype = 16
                                break

                if restype == 0:
                    # 没有+分段情况下，判断
                    if plusflag == 0:
                        for term in mp3name_list2:
                            if (subtitle2.startswith(term) or subtitle2.endswith(term)) and len(term)>=3:
                                mp3name = term
                                restype = 17
                                break

                # step3 video_mp3_name
                # video_mp3_name2 比较置信
                if restype == 0:
                    if video_mp3_name2!="":
                        mp3name = video_mp3_name2
                        restype = 18

                # step5
                if restype == 0 or restype == 20 or mp3name in self.unmp3_dict:
                    mp3name = ""

                    cand_alllist = []
                    for term in cand_content_mp3set:
                        if term in self.video_mp3_name_dict_for_match2:
                            qcmp3_name, count = self.video_mp3_name_dict_for_match2[term]
                            cand_alllist.append([term,len(term), int(count)])

                    last_candlist = sorted(cand_alllist, key=lambda k: (k[1], k[2]), reverse=True)

                    #last_candlist = sorted(list(candmatchs_mp3set), key=len, reverse=True)

                    for i, termlist in enumerate(last_candlist):
                        term = termlist[0]
                        tmpfound = 0
                        tmpfound2 = 0
                        if term not in self.unmp3_dict:
                            if len(term)>=5 or term==lefttitle3:
                                tmpfound +=1
                            elif len(term)>=3:
                                if booname_flag>0:
                                    pass
                                    if term in subtitle2:
                                        pass
                                    else:
                                        #有书名号 term在lefttitle 中
                                        if ("+"+term in lefttitle3 or term+"+" in lefttitle3):
                                            tmpfound +=1
                                # 没有书名号 或者+term+
                                elif "+"+term+"+" in lefttitle2 or \
                                        lefttitle2.startswith("+"+term) or lefttitle2.startswith(term+"+") or \
                                        lefttitle2.endswith("+"+term) or lefttitle2.endswith(term+"+"):
                                    tmpfound +=1
                                #没有书名号，前缀，后缀，
                                elif lefttitle2.startswith(term) or lefttitle2.endswith(term):
                                    if len(term)>=5:
                                        tmpfound += 1
                                    else:
                                        if term not in self.mp3check:
                                            tmpfound2 +=1
                                        #tmpfound2 +=1

                            if queryflag==1:
                                if len(term)>=3:
                                    if lefttitle3.startswith(term) or lefttitle3.endswith(term) or "+" + term + "+" in lefttitle2_tmp:
                                        tmpfound += 1
                                        pass
                                elif len(term)==2:
                                    if "+"+term in lefttitle2_tmp or term+"+" in lefttitle2_tmp or term==lefttitle2_tmp or term==lefttitle2:
                                        pass
                                        tmpfound += 1
                                elif len(term)==1:
                                    if "+"+term+"+" in lefttitle2_tmp or term==lefttitle2 or term==lefttitle2_tmp:
                                        tmpfound += 1
                                # if term in lefttitle:
                                #     tmpfound +=1
                        if tmpfound>0:
                            mp3name = term
                            restype = 19
                            break
                        if tmpfound2>0:
                            mp3name = term
                            restype = 22
                            break


                    #考虑两个字的mp3 只有subtitle2_tmp 中含有+"mp3"+ 情况下 并且df >=500
                    if restype == 0 or restype == 20 or mp3name in self.unmp3_dict:
                        mp3name = ""
                        mp3_2word_dict = {}
                        for term in subtitle_list2:
                            if term !="" and "+"+term+"+" in subtitle2_tmp \
                                and term in self.video_mp3_name_dict_for_match2 \
                                    and self.video_mp3_name_dict_for_match2[term][1]>=500:
                                mp3_2word_dict[term] = self.video_mp3_name_dict_for_match2[term][1]
                        if len(mp3_2word_dict)>0:
                            sorted_mp3_2word_dict = sorted(mp3_2word_dict.items(), key=lambda k:k[1], reverse=True)
                            mp3name = sorted_mp3_2word_dict[0][0]
                            restype = 21


        # end
        resmp3 = self.mp3_postprocess2(mp3name)
        cand_content_mp3set.add(mp3name)
        for term in cand_content_mp3set:
            if term!="":
                cand_content_mp3list.append(term)

        return resmp3,cand_content_mp3list,restype

    '''
       只有在《》完整匹配不到的情况下再去所有的mp3 匹配
    '''
    def mp3_match2(self, subtitle2, lefttitle2):

        blacklist = ["编舞","水兵舞","恰恰舞","组合","相册","健身操"]
        blackset = set(["2018", "2017", "2016", "2015", "2014","2019年", "练习", "圈圈舞"])

        mp3_name_list = []
        cand_mp3nameset = set()
        mp3_name_set = set()

        left_mp3_name_list = []
        left_mp3_name_set = set()

        for mp3_name in self.video_mp3_name_dict_for_match2:
            qcmp3_name, count = self.video_mp3_name_dict_for_match2[mp3_name]
            if mp3_name in subtitle2:
                if qcmp3_name!=mp3_name:
                    mp3_name = qcmp3_name
                else:
                    if count>=5:
                        mp3_name = mp3_name
                    else:
                        cand_mp3nameset.add(mp3_name)
                        mp3_name = "-1"
                mp3_name = mp3_name.strip("+")
                black_flag = 0
                for blackterm in blacklist:
                    if blackterm in mp3_name:
                        black_flag +=1
                if (len(mp3_name) <= 2 and mp3_name!=subtitle2 and mp3_name!=subtitle2.strip("+")) or mp3_name.isdigit() or mp3_name in self.unmp3_dict or mp3_name in blackset or black_flag>0:
                    continue

                if mp3_name not in mp3_name_set:
                    mp3_name_set.add(mp3_name)
                    mp3_name_list.append([mp3_name, len(mp3_name), count])
                    cand_mp3nameset.add(mp3_name)
            #mp3 在left title 出现
            elif mp3_name in lefttitle2:
                if qcmp3_name!=mp3_name:
                    mp3_name = qcmp3_name
                else:
                    if count>=5:
                        mp3_name = mp3_name
                    else:
                        cand_mp3nameset.add(mp3_name)
                        mp3_name = "-1"
                mp3_name = mp3_name.strip("+")

                black_flag = 0
                for blackterm in blacklist:
                    if blackterm in mp3_name:
                        black_flag += 1
                if (len(mp3_name) <= 2 and mp3_name!=lefttitle2 and mp3_name!=lefttitle2.strip("+")) or mp3_name.isdigit() or mp3_name in self.unmp3_dict or mp3_name in blackset or black_flag > 0:
                    continue
                if mp3_name not in left_mp3_name_set:
                    left_mp3_name_set.add(mp3_name)
                    left_mp3_name_list.append([mp3_name, len(mp3_name), count])
                    cand_mp3nameset.add(mp3_name)
                pass

        if len(mp3_name_list) > 0:
            sorted_mp3_name_list = sorted(mp3_name_list, key=lambda k: (k[1], k[2]))
            mp3_name_list = [k[0] for k in sorted_mp3_name_list ]
            #mp3_name_list.sort(key=len)
        if len(left_mp3_name_list) > 0:

            sorted_left_mp3_name_list = sorted(left_mp3_name_list, key=lambda k: (k[1], k[2]))
            left_mp3_name_list = [k[0] for k in sorted_left_mp3_name_list ]
            #left_mp3_name_list.sort(key=len)
        return mp3_name_list, left_mp3_name_list, cand_mp3nameset

    def symbol_extract_mp3(self, title):
        left_symbol =  ["《", "<", "〈", "【", "巜", "［", "{", "〖","﹝"]
        right_symbol = ["》", ">", "〉", "】", "］", "}", '〗', "﹞", "﹞"]
        left_indices = []
        right_indices = []
        for sym in left_symbol:
            left_indices.extend([i for i,d in enumerate(title) if d==sym])
        for sym in right_symbol:
            right_indices.extend([i for i,d in enumerate(title) if d==sym])
        left_indices =  [ ("l", e) for e in list(set(left_indices))]
        right_indices = [ ("r", e) for e in list(set(right_indices))]
        all_indices = left_indices + right_indices
        all_indices.sort(key=lambda tup: tup[1])
        candidate =[ num for num in range(len(all_indices)-1) if all_indices[num][0]!=all_indices[num+1][0] and all_indices[num][0]=='l']
        mp3s=[]
        if candidate != []:
            for num in candidate:
                left = all_indices[num][1]
                right = all_indices[num+1][1]
                mp3 = title[left+1:right]
                mp3s.append(mp3)
        return (mp3s, left_indices, right_indices)

    def symbol_extract_mp3_v2(self, title):
        left_symbol =  ["（", "("]
        right_symbol = ["）", ")"]
        left_indices = []
        right_indices = []
        for sym in left_symbol:
            left_indices.extend([i for i,d in enumerate(title) if d==sym])
        for sym in right_symbol:
            right_indices.extend([i for i,d in enumerate(title) if d==sym])
        left_indices =  [ ("l", e) for e in list(set(left_indices))]
        right_indices = [ ("r", e) for e in list(set(right_indices))]
        all_indices = left_indices + right_indices
        all_indices.sort(key=lambda tup: tup[1])
        candidate =[ num for num in range(len(all_indices)-1) if all_indices[num][0]!=all_indices[num+1][0] and all_indices[num][0]=='l']
        mp3s=[]
        if candidate != []:
            for num in candidate:
                left = all_indices[num][1]
                right = all_indices[num+1][1]
                mp3 = title[left+1:right]
                mp3s.append(mp3)
        return (mp3s, left_indices, right_indices)

    def mp3_postprocess2(self, mp3name):

        tmp = {}
        if mp3name in ["-1", "", "恰恰伴舞", "背景素材", "0"]:
            mp3name = ""
        mp3name = self.preprocess(mp3name)
        mp3name2 = mp3name.replace("+", "")
        res = mp3name
        if mp3name in self.video_mp3_name_dict_for_match2:
            res= self.video_mp3_name_dict_for_match2[mp3name][0]
        elif mp3name2 in self.video_mp3_name_dict_for_match2:
            res= self.video_mp3_name_dict_for_match2[mp3name2][0]
        else:
            secres_list = mp3name.split("+")
            for oneterm in secres_list:
                if oneterm in self.video_mp3_name_dict_for_match2:
                    res = self.video_mp3_name_dict_for_match2[oneterm][0]
                    break
        if res == '背景素材' or res == '0':
            tmp = {}
        if res!="":
            tmp = {"tagid": 0, "tagvalue": 1.0, "tagname": res}
        return tmp

    #### 功能性方法，处理MP3_name
    def DBC2SBC(sefl, ustring):
        #' 全角转半角 "
        rstring = ""
        for uchar in ustring:
            inside_code = ord(uchar)
            if inside_code == 0x3000:
                inside_code = 0x0020
            else:
                inside_code -= 0xfee0
            if not (0x0021 <= inside_code and inside_code <= 0x7e):
                rstring += uchar
                continue
            rstring += chr(inside_code)
        return rstring

    def preprocess(self,content):

        content1 = content.lower()
        # 全角转半角
        # eg:ｄｊ爱就要大声说出来==>dj爱就要大声说出来, ｃ哩ｃ哩==>c哩c哩
        content2 = self.DBC2SBC(content1)
        # 非中文及英文数字 统一成+字符
        content3 = re.sub("[^a-zA-Z0-9\u4e00-\u9fa5+]+", "+", content2)

        content4 = content3.strip("+")

        content5 = self.trimdj(content4)

        #content6 = content5.strip("+")

        return content5

    def trimdj(self, word):
        res_word = word
        dj_set = set(["dj的歌", "dj"])
        if res_word in dj_set:
            res_word = word
        else:
            if res_word.startswith("dj版"):
                res_word = res_word[len(str("dj版")):]
            if res_word.endswith("dj版"):
                res_word = res_word[:-len(str("dj版"))]
            if res_word.startswith("dj"):
                res_word = res_word[len(str("dj")):]
            if res_word.endswith("dj"):
                res_word = res_word[:-len(str("dj"))]
        return res_word


if __name__ == "__main__":
    pass

    # mp3_extracter = Extracter()
    #
    # vid = '23424'
    # title = '美丽秋霜广场舞《给我一匹白色的马》新歌好听原创附教学'
    # uname = '杨丽萍'
    # video_mp3_name = ''
    #
    # res, candlist, restype = mp3_extracter.my_main(vid, title, uname, video_mp3_name,1) # query need the last para '1'
    # print(res)
    # print(candlist)










