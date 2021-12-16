#-*- coding: utf-8 -*-
'''
@Author    :  sunjian
@Time      :  2020/4/1 下午5:11
@File      :  qcorrector.py
'''
import numpy as np
import re
from .Trie import Trie
from .synonymnorm import SynonymNorm
from xpinyin import Pinyin

def DBC2SBC(ustring):
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


def SBC2DBC(ustring):
    #' 半角转全角 ”
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 0x0020:
            inside_code = 0x3000
        else:
            if not (0x0021 <= inside_code and inside_code <= 0x7e):
                rstring += uchar
                continue
        inside_code += 0xfee0
        rstring += chr(inside_code)
    return rstring


def trimdj(word):
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
        if res_word.startswith("d+j"):
            res_word = res_word[len(str("d+j")):]
        if res_word.endswith("d+j"):
            res_word = res_word[:-len(str("d+j"))]

    res_word = res_word.strip("+")

    return res_word


def preprocess2(content):

    content1 = content.lower().strip()
    # 全角转半角
    # eg:ｄｊ爱就要大声说出来==>dj爱就要大声说出来, ｃ哩ｃ哩==>c哩c哩
    content2 = DBC2SBC(content1)
    # 非中文及英文数字 统一成+字符
    content3 = re.sub("[^a-zA-Z0-9\u4e00-\u9fa5+]+", "+", content2)

    content4 = content3.strip("+")

    content5 = trimdj(content4)

    content6 = content5.strip("+")

    return content6


def edit_distance(word1, word2):
    len1 = len(word1)
    len2 = len(word2)
    dp = np.zeros((len1 + 1, len2 + 1))
    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            delta = 0 if word1[i - 1] == word2[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j - 1] + delta, min(dp[i - 1][j] + 1, dp[i][j - 1] + 1))

    return dp[len1][len2]


def cal_sim(word1, word2, prefix=""):
    newword1 = word1
    newword2 = word2
    if word1.startswith(prefix):
        newword1 = word1[len(prefix):]
    if word2.startswith(prefix):
        newword2 = word2[len(prefix):]

    edit_count = edit_distance(newword1,newword2)
    max_len = max(len(word1), len(word2))+ len(prefix)

    sim = float(max_len-edit_count)/max_len
    return sim,edit_count

'''
    逐次添加true_dict
'''


def insert_syndict(qc_word, word, true_dict):

    code = 0
    pass
    if qc_word not in true_dict:
        true_dict[qc_word] = qc_word
        if word!="" and qc_word!=word:
            o_word = word
            if o_word not in true_dict:
                true_dict[o_word] = qc_word
            else:
                if qc_word != true_dict[o_word]:
                    # error
                    #print("syn_error:", o_word + "\t" + qc_word + "\t" + true_dict[o_word])
                    code = 1
                else:
                    # 重复
                    code = 2
                    # print("syn_repeat:",o_word + "\t" + qc_word)
    else:
        if word!="" and qc_word!=word:
            o_word = word
            if o_word not in true_dict:
                # 需要补充进去
                true_dict[o_word] = qc_word
                pass
                # print("syn_supply:",o_word+"\t"+qc_word)
            else:
                pass
                # 错误或者重复
                if qc_word != true_dict[o_word]:
                    code = 1
                    # 错误
                    #print("error:" + o_word + "\t" + qc_word + "\t" + true_dict[o_word])
                else:
                    #重复
                    code = 2
    return code
'''
    逐次添加qc_dict
'''


def insert_qcdict(qc_word, word, true_dict, qc_dict):

    code = 0
    if word == qc_word:
        code = insert_syndict(qc_word, word, true_dict)
        # if code == 1:
        #     print("qc1_syn_error", word, qc_word)
    else:
        # true_dict
        if qc_word not in true_dict:
            if word not in true_dict:
                pass
                # 正常的qc 词条
                true_dict[qc_word] = qc_word
                qc_dict[word] = qc_word
            else:
                # syn&qc 交叉， word词在truedict 里, error
                code = 2
                #print("qc1_qc_error1", word, qc_word)
                pass
        else:
            qc_word_syn = true_dict[qc_word]
            if word not in true_dict:
                # 正常的qc 词条

                if qc_word_syn == qc_word:
                    pass
                    true_dict[qc_word] = qc_word
                else:
                    pass
                    true_dict[qc_word] = qc_word_syn
                    # print("qc1_qc_error2", word, qc_word, qc_word_syn)
                # qc 文件里，qc_word 保持不变
                qc_dict[word] = qc_word
            else:
                pass
                # word 在true_dict 里
                # qc_dict[word] = qc_word
                # true_dict[qc_word] = qc_word_syn
                word_true = true_dict[word]
                if qc_word != word_true:
                    if word != word_true:
                        # ok 将qc 文件里增加同义词库
                        if qc_word_syn == word_true:
                            pass
                        else:
                            code = 3
                            # true_dict[qc_word] = true_dict[word]
                            #print("qc1_qc_error3", word, true_dict[word], qc_word)
                    else:
                        pass
                        # 不应该加入进去 qc字典 交叉
                        if qc_word_syn == word_true:
                            pass
                        else:
                            code = 4
                            #print("qc1_qc_error3", word, true_dict[word], qc_word)
                else:
                    # 正常,word 在true
                    pass
    return code


class Corrector(object):

    def __init__(self, user_confusion_path, sj_user_confusion_path, plus_user_confusion_path, syn_path, mp3all_file, trie_flag):

        qc_dict, truedict = self.get_qc_syn(user_confusion_path, sj_user_confusion_path, plus_user_confusion_path, syn_path)

        mp3_song_dict, new_word2qcword = self.read_mp3all(mp3all_file, qc_dict, truedict)

        self.qc_dict = qc_dict
        self.truedict = truedict
        self.mp3_song_dict = mp3_song_dict
        self.new_word2qcword = new_word2qcword

        self.norm = SynonymNorm()

        print("qc_dict:", len(self.qc_dict))
        print("true_dict:", len(self.truedict))

        if trie_flag==1:

            self.mytrie = Trie()

            self.mytrie_reverse = Trie()

            for word,trueword in self.truedict.items():
                self.mytrie.insert(word)
                self.mytrie_reverse.insert(word[::-1])
            for word, qcword in self.qc_dict.items():
                self.mytrie.insert(word)
                self.mytrie_reverse.insert(word[::-1])
            print("trie tree construction success")

        self.py = Pinyin()
        self.pydict, self.w_pydict, self.py_truedict, self.w_py_qcdict = self.get_py_dict()
    '''
        返回纠正错误-> truth, truth dict{}
    '''

    def get_qc_syn(self, user_confusion_path, sj_user_confusion_path, plus_user_confusion_path, syn_path):
        # user_confusion_path = './dict/custom_confusion.txt_v1118'
        # sj_user_confusion_path = "./dict/sj_custom_confusion.txt_v0324"
        # plus_user_confusion_path = './dict/plus_custom_confusion.txt_v1118'
        # syn_path = "./dict/syn.txt_v0324"

        # 不包括word!=qc_word
        qc_dict = {}
        true_dict = {}

        with open(syn_path, "r") as f0:
            for line in f0:
                line = line[:-1]
                tokens = line.split("|")
                qc_word = tokens[0]
                if len(tokens) >= 2:
                    for o_word in tokens[1:]:
                        code = insert_syndict(qc_word, o_word, true_dict)
                        if code==1:
                            print("syn_error",qc_word,o_word)
                else:
                    code = insert_syndict(qc_word, "", true_dict)
                    if code == 1:
                        print("syn_error",qc_word, o_word)

        with open(user_confusion_path, "r") as f0:
            for line in f0:
                line = line.strip()
                tokens = line.split("\t")
                if len(tokens) < 8: continue
                word = tokens[0]
                qc_word = tokens[1]


                code = insert_qcdict(qc_word, word,true_dict,qc_dict)
                if code!=0:
                    print("qc1:",code, qc_word, word)

        with open(sj_user_confusion_path, "r") as f0:
            for line in f0:
                line = line.strip()
                tokens = line.split("\t")
                if len(tokens) < 8: continue
                word = tokens[0]
                qc_word = tokens[1]

                if qc_word in qc_dict and qc_word not in true_dict:
                    print("sj_error:",word,qc_word,qc_dict[qc_word])

                else:
                    # 默认qc_word 是对的
                    code = insert_qcdict(qc_word, word, true_dict, qc_dict)
                    if code != 0:
                        print("qc2:", code, qc_word, word)


        with open(plus_user_confusion_path, "r") as f0:
            for line in f0:
                line = line.strip()
                tokens = line.split("\t")
                if len(tokens) < 8: continue
                word = tokens[0]
                qc_word = tokens[1]


                code = insert_qcdict(qc_word, word, true_dict, qc_dict)
                if code != 0:
                    print("qc3:", code, qc_word, word)
        # query = "月亮湾漂在天边"
        # if query in true_dict:
        #     print("true:",query, true_dict[query])
        # if query in qc_dict:
        #     print("qc:",query, qc_dict[query])
        return qc_dict, true_dict
    '''
        根据query，segline, mp3dict 判断query 的纠正词
    '''
    def get_newquery_byseg(self, query, srcount1=None, srcount2=None, seglist=None, mp3dict=None):

        newquery = ""
        restype = 0

        #如果是truth 返回1，2
        if query in self.truedict:
            newquery = self.truedict[query]
            if newquery==query:
                restype = 1
            else:
                restype = 2
            return newquery,restype
        #纠正的返回3
        if query in self.qc_dict:
            newquery = self.qc_dict[query]
            restype = 3
            return newquery, restype

        #对于
        # query 在搜索结果中，疑似歌曲名
        res_flag = 0
        if mp3dict and query in mp3dict:
            res_flag = 1
            # 这是一个新的query
            newquery = query
            restype = 4
            return newquery, restype
        elif srcount1 and srcount1>=3 and len(query)>=4:
            newquery = query
            restype = 5
            return newquery, restype
        elif srcount2 and srcount2>=3:
            newquery = query
            restype = 6
            return newquery, restype
        else:
            #不要停用词过滤，
            # 利用分词处理,判断分词有效

            if seglist and len(seglist)>0 and ("".join(seglist)).lower()==query.lower():

                wordlen = len(seglist)

                newwordlist = []
                newworddict = {}

                proced_dict = {}
                ok_dict = {}
                # 2 3 4 5 元 分词组词，看是否是纠错字典的词
                offset = 0
                for i, w in enumerate(seglist):
                    if i + 4 < wordlen:
                        if len(seglist[i]) <= 1 or len(seglist[i + 1]) <= 1 or len(seglist[i + 2]) <= 1 or len(
                                seglist[i + 3]) <= 1 or len(seglist[i + 4]) <= 1:
                            c_word = ''.join(seglist[i:i + 5])

                            if c_word in self.truedict:
                                ok_flag = 0
                                offset_length = 0
                                for j in range(5):
                                    if j + i not in ok_dict:
                                        ok_dict[j + i] = 1
                                        ok_flag += 1
                                        offset_length += len(w)
                            elif c_word in self.qc_dict:
                                qc_word = self.qc_dict[c_word]
                                if (qc_word.find(c_word) < 0 and c_word.find(qc_word) < 0):
                                    proced_flag = 0
                                    offset_length = 0
                                    for j in range(5):
                                        if j + i not in proced_dict:
                                            proced_dict[j + i] = 1
                                            proced_flag += 1
                                            offset_length += len(w)
                                    if proced_flag > 0:
                                        # print(query + ":" + "i5:" + str(offset) + " " + c_word + "==>" + qc_word)
                                        newwordlist.append([i, 5, offset, offset_length, c_word, qc_word])
                                        newworddict[i] = [i, 5, offset, offset_length, c_word, qc_word]
                                        # newwordline = ''.join(seglist[:i])+qc_word+''.join(seglist[i+5:])
                            else:
                                pass

                            pass
                    if i + 3 < wordlen:
                        if len(seglist[i]) <= 1 or len(seglist[i + 1]) <= 1 or len(seglist[i + 2]) <= 1 or len(
                                seglist[i + 3]) <= 1:
                            c_word = ''.join(seglist[i:i + 4])

                            if c_word in self.truedict:
                                ok_flag = 0
                                offset_length = 0
                                for j in range(4):
                                    if j + i not in ok_dict:
                                        ok_dict[j + i] = 1
                                        ok_flag += 1
                                        offset_length += len(w)
                            elif c_word in self.qc_dict:
                                qc_word = self.qc_dict[c_word]
                                if (qc_word.find(c_word) < 0 and c_word.find(qc_word) < 0):
                                    proced_flag = 0
                                    offset_length = 0
                                    for j in range(4):
                                        if j + i not in proced_dict:
                                            proced_dict[j + i] = 1
                                            proced_flag += 1
                                            offset_length += len(w)
                                    if proced_flag > 0:
                                        # print(query+":"+"i4:"+str(offset)+" "+c_word+"==>"+qc_word)
                                        newwordlist.append([i, 4, offset, offset_length, c_word, qc_word])
                                        newworddict[i] = [i, 4, offset, offset_length, c_word, qc_word]
                                        # newwordline = ''.join(seglist[:i]) + qc_word + ''.join(seglist[i + 5:])
                            else:
                                pass

                            pass
                    if i + 2 < wordlen:
                        if len(seglist[i]) <= 1 or len(seglist[i + 1]) <= 1 or len(seglist[i + 2]) <= 1:
                            c_word = ''.join(seglist[i:i + 3])

                            if c_word in self.truedict:
                                ok_flag = 0
                                offset_length = 0
                                for j in range(3):
                                    if j + i not in ok_dict:
                                        ok_dict[j + i] = 1
                                        ok_flag += 1
                                        offset_length += len(w)
                            elif c_word in self.qc_dict:
                                qc_word = self.qc_dict[c_word]
                                if (qc_word.find(c_word) < 0 and c_word.find(qc_word) < 0):
                                    proced_flag = 0
                                    offset_length = 0
                                    for j in range(3):
                                        if j + i not in proced_dict:
                                            proced_dict[j + i] = 1
                                            proced_flag += 1
                                            offset_length += len(w)
                                    if proced_flag > 0:
                                        # print(query+":"+"i3:"+str(offset)+" "+c_word+"==>"+qc_word)
                                        newwordlist.append([i, 3, offset, offset_length, c_word, qc_word])
                                        newworddict[i] = [i, 3, offset, offset_length, c_word, qc_word]
                            else:
                                pass

                            pass
                    if i + 1 < wordlen:
                        if len(seglist[i]) <= 1 or len(seglist[i + 1]) <= 1:
                            c_word = ''.join(seglist[i:i + 2])

                            if c_word in self.truedict:
                                pass
                                ok_flag = 0
                                offset_length = 0
                                for j in range(3):
                                    if j + i not in ok_dict:
                                        ok_dict[j + i] = 1
                                        ok_flag += 1
                                        offset_length += len(w)
                            elif c_word in self.qc_dict:
                                qc_word = self.qc_dict[c_word]
                                if (qc_word.find(c_word) < 0 and c_word.find(qc_word) < 0):
                                    proced_flag = 0
                                    offset_length = 0
                                    for j in range(2):
                                        if j + i not in proced_dict:
                                            proced_dict[j + i] = 1
                                            proced_flag += 1
                                            offset_length += len(w)
                                    if proced_flag > 0:
                                        # print(query+":"+"i2:"+str(offset)+" "+c_word+"==>"+qc_word)
                                        newwordlist.append([i, 2, offset, offset_length, c_word, qc_word])
                                        newworddict[i] = [i, 2, offset, offset_length, c_word, qc_word]
                            else:
                                pass

                            # pass

                    c_word = ''.join(seglist[i:i + 1])
                    if c_word in self.truedict:
                        ok_flag = 0
                        offset_length = 0
                        for j in range(1):
                            if j + i not in ok_dict:
                                ok_dict[j + i] = 1
                                ok_flag += 1
                                offset_length += len(w)
                        pass
                    elif c_word in self.qc_dict:
                        qc_word = self.qc_dict[c_word]
                        if (qc_word.find(c_word) < 0 and c_word.find(qc_word) < 0):
                            proced_flag = 0
                            offset_length = 0
                            for j in range(1):
                                if j + i not in proced_dict:
                                    proced_dict[j + i] = 1
                                    proced_flag += 1
                                    offset_length += len(w)
                            if proced_flag > 0:
                                # print(query+":"+"i1:"+str(offset)+" "+c_word+"==>"+qc_word)
                                newwordlist.append([i, 1, offset, offset_length, c_word, qc_word])
                                newworddict[i] = [i, 1, offset, offset_length, c_word, qc_word]
                    else:
                        pass

                    offset += len(w)
                    pass

                tmpnewquery = ""
                tmpnewquery2 = ""
                tmpnewquery2_badflag = 0
                c_i = 0
                ok_and_new = []

                while c_i < len(seglist):
                    flag = 0
                    if c_i in newworddict:
                        term = newworddict[c_i][5]
                        tmpnewquery2 += term
                        tmpnewquery += term
                        ok_and_new.append(term)
                        c_i += int(newworddict[c_i][1])
                    else:
                        term = seglist[c_i]
                        if c_i in ok_dict:
                            ok_and_new.append(term)
                            tmpnewquery2 += term
                        else:
                            if term in self.truedict:
                                flag += 1
                            # else:
                            #     newquery, restype = getsrcdict_type_json(term, srcdict_jsondata)
                            #     if restype == 1:
                            #         flag += 1
                            if flag > 0:
                                tmpnewquery2 += term
                            else:
                                tmpnewquery2_badflag += 1

                        tmpnewquery += seglist[c_i]
                        c_i += 1
                ratio = 0.0
                if len(query)!=0:
                    ratio = float(len(''.join(ok_and_new))) / float(len(query))
                ratio2 = 0.0
                if tmpnewquery2_badflag == 0:
                    if len(query)!=0:
                        ratio2 = float(len(tmpnewquery2)) / float(len(query))
                else:
                    if tmpnewquery2.find(query) >= 0 or query.find(tmpnewquery2) >= 0:
                        if len(query)!=0:
                            ratio2 = float(len(tmpnewquery2)) / float(len(query))

                # print("query=>newquery:"+query+"==>"+newquery +"\t"+str(ratio))

                # print("query=>newquery:" + query + "==>" + tmpnewquery +":"+''.join(ok_and_new)+":"+tmpnewquery2+ "\t" + str(ratio)+"\t"+str(ratio2))

                if ratio >= 0.75:
                    newquery = tmpnewquery
                    restype = 8
                    # return newquery, restype
                elif ratio2 >= 0.8:
                    newquery = tmpnewquery2
                    restype = 16
                    # return newquery, restype
                else:

                    # query = newquery

                    pattern2 = re.search("(第.+套)|(第.+节)", tmpnewquery)
                    newquery = tmpnewquery
                    restype = 15

                    if not pattern2:

                        if tmpnewquery != query:
                            if tmpnewquery in self.truedict:
                                newquery = tmpnewquery
                                restype = 10
                            elif tmpnewquery in self.qc_dict:
                                newquery = self.qc_dict[tmpnewquery]
                                restype = 11
                            else:
                                newquery = tmpnewquery
                                restype = 12

                        else:
                            restype = 13
                    else:
                        if tmpnewquery != query:
                            restype = 14
                        else:
                            restype = 15
                return newquery, restype
            else:
                #不处理
                newquery = query
                restype = 7
                return newquery, restype
        # print("query=>newquery:" + query + "==>" + tmpnewquery + ":" + ''.join(ok_and_new) + ":" + tmpnewquery2 + "\t" + str(ratio) + "\t" + str(ratio2)+"\t"+str(restype))

    def get_newquery_byseg_norm(self, query, srcount1=None, srcount2=None, seglist=None, mp3dict=None):

        qc_query, qc_type = self.get_newquery_byseg(query,srcount1, srcount2, seglist, mp3dict)

        if qc_type not in (1,2,3,7,8,9,10,11) and seglist:
            qc_query_norm = self.norm.transform(qc_query, " ".join(seglist))
            if qc_query_norm!=qc_query:
                qc_query= qc_query_norm
                qc_type = 16

        #add pinyin
        query_py = self.py.get_pinyin(query, splitter='')
        if len(query)>=3 and ( query_py in self.py_truedict or query_py in self.w_py_qcdict ) and qc_type not in (1,2,3):
            qc_type = 21
            if query_py in self.py_truedict:
                qc_query = self.py_truedict[query_py]
                qc_type = 22
            elif query_py in self.w_py_qcdict:
                qc_query = self.w_py_qcdict[query_py]
                qc_type = 23
            else:
                pass

        return qc_query, qc_type

    '''
        check qc_dict 及truedict
    '''
    # def check_dict(self, user_confusion_path, sj_user_confusion_path, plus_user_confusion_path, syn_path):
    #     # 不包括word!=qc_word
    #     qc_dict = {}
    #     true_dict = {}
    #
    #     with open(syn_path, "r") as f0:
    #         for line in f0:
    #             line = line[:-1]
    #             tokens = line.split("|")
    #             qc_word = tokens[0]
    #             if len(tokens) >= 2:
    #                 for o_word in tokens[1:]:
    #                     true_dict[o_word] = qc_word
    #             true_dict[qc_word] = qc_word
    #             # for o_word in tokens:
    #             #     if o_word not in true_dict:
    #             #         true_dict[o_word] = {}
    #             #     true_dict[o_word][qc_word] = 1
    #             # if qc_word not in true_dict:
    #             #     true_dict[qc_word][qc_word] = 1
    #
    #     with open(user_confusion_path, "r") as f0:
    #         for line in f0:
    #             line = line.strip()
    #             tokens = line.split("\t")
    #             if len(tokens) < 8: continue
    #             word = tokens[0]
    #             qc_word = tokens[1]
    #
    #             if qc_word in true_dict:
    #                 qc_word = true_dict[qc_word]
    #             else:
    #                 if word != qc_word:
    #                     if word not in qc_dict:
    #                         qc_dict[word] = qc_word
    #                     else:
    #                         if qc_dict[word]!=qc_word:
    #                             print("1error:", word,qc_word, qc_dict[word])
    #
    #                 if qc_word in true_dict and true_dict[qc_word] != qc_word:
    #                     true_dict[qc_word] = true_dict[qc_word]
    #                 else:
    #                     true_dict[qc_word] = qc_word
    #                 if qc_word in qc_dict:
    #                     print("1:"+word+"|"+qc_word+"|"+qc_dict[qc_word])
    #                     true_dict[qc_word] = qc_dict[qc_word]
    #             # if qc_word not in true_dict:
    #             #     true_dict[qc_word] = {}
    #             # true_dict[qc_word][qc_word] = 1
    #
    #     with open(sj_user_confusion_path, "r") as f0:
    #         for line in f0:
    #             line = line.strip()
    #             tokens = line.split("\t")
    #             if len(tokens) < 8: continue
    #             word = tokens[0]
    #             qc_word = tokens[1]
    #
    #             if qc_word in true_dict:
    #                 qc_word = true_dict[qc_word]
    #             else:
    #                 if word != qc_word:
    #                     #qc_dict[word] = qc_word
    #                     if word not in qc_dict:
    #                         qc_dict[word] = qc_word
    #                     else:
    #                         if qc_dict[word]!=qc_word:
    #                             print("2error:", word,qc_word, qc_dict[word])
    #                 if qc_word in true_dict and true_dict[qc_word] != qc_word:
    #                     true_dict[qc_word] = true_dict[qc_word]
    #                 else:
    #                     true_dict[qc_word] = qc_word
    #                 if qc_word in qc_dict:
    #                     #print("2:", word,qc_word,qc_dict[qc_word])
    #                     #print("2:" + word + "|" + qc_word + "|" + qc_dict[qc_word])
    #                     true_dict[qc_word] = qc_dict[qc_word]
    #                 # if qc_word not in true_dict:
    #                 #     true_dict[qc_word] = {}
    #                 # true_dict[qc_word][qc_word] = 1
    #
    #     with open(plus_user_confusion_path, "r") as f0:
    #         for line in f0:
    #             line = line.strip()
    #             tokens = line.split("\t")
    #             if len(tokens) < 8: continue
    #             word = tokens[0]
    #             qc_word = tokens[1]
    #
    #             if qc_word in true_dict:
    #                 qc_word = true_dict[qc_word]
    #             else:
    #                 if word != qc_word:
    #                     #qc_dict[word] = qc_word
    #                     if word not in qc_dict:
    #                         qc_dict[word] = qc_word
    #                     else:
    #                         if qc_dict[word]!=qc_word:
    #                             print("3error:", word,qc_word, qc_dict[word])
    #                 if qc_word in true_dict and true_dict[qc_word] != qc_word:
    #                     true_dict[qc_word] = true_dict[qc_word]
    #                 else:
    #                     true_dict[qc_word] = qc_word
    #                 if qc_word in qc_dict:
    #                     #print("3:", word,qc_word,qc_dict[qc_word])
    #                     print("3:" + word + "|" + qc_word + "|" + qc_dict[qc_word])
    #
    #             # if qc_word not in true_dict:
    #             #     true_dict[qc_word] = {}
    #             # true_dict[qc_word][qc_word] = 1
    #
    #
    #
    #     return qc_dict, true_dict
    #     pass

    '''
        check new qc and updata
    '''
    def check_updatdict(self, qc_file):

        ss =0
        tt =0
        cc =0
        fw = open(qc_file+".tt", "w")
        with open(qc_file, "r") as f0:
            for line in f0:
                line = line.strip()
                tokens = line.split("\t")
                if len(tokens) < 8: continue
                word = tokens[0]
                qc_word = tokens[1]

                #print(line)
                if word==qc_word:
                    #syn
                    if word not in self.truedict:
                        print("syn_exit:" + word + "\t" + qc_word)
                    else:
                        print("syn_notexit:" + word + "\t" + qc_word)
                else:
                    if qc_word in self.qc_dict:
                        if self.qc_dict[qc_word] in self.truedict:
                            pass
                            ss +=1
                            #print("ss:", word, qc_word, self.qc_dict[qc_word])
                        else:
                            print("qc_error:"+ word+"\t"+qc_word+"\t"+self.qc_dict[qc_word])
                    if word not in self.qc_dict:
                        pass
                        #need insert into qc_dict

                        if word.find(qc_word)<0 and qc_word.find(word)<0:
                            fw.write(line.strip()+"\n")
                            tt += 1
                        #qc_dict[word] = qc_word
                    else:
                        if self.qc_dict[word]!=qc_word:
                            # 有冲突，no care
                            pass
                            #print("qc_error:", word, qc_word, self.qc_dict[word])
                        else:
                            pass
                            #已存在
                cc +=1

        print("cc:", cc)
        print("ss:", ss)
        print("tt:", tt)
        fw.close()

    '''
        mp3 all
    '''
    def read_mp3all(self, mp3all_file, qc_dict={}, true_dict={}):
        mp3_song_dict = {}

        # print("len_qc_dict:",len(qc_dict))
        new_word2qcword = {}
        # fw = open("./tmp4.mp3", "w")
        ss = 0
        with open(mp3all_file, "r") as f0:
            for line in f0:
                tokens = line.strip().split("\t")
                if len(tokens) < 5: continue
                token1_mp3 = preprocess2(tokens[1])
                # token0 = tokens[0]
                word = tokens[0]
                qc_word = tokens[1]

                if tokens[3] == "8" and tokens[4] != "2" and int(tokens[2]) >= 5:
                    if word not in mp3_song_dict:
                        mp3_song_dict[word] = qc_word
                    mp3_song_dict[qc_word] = qc_word
                    # else:
                    #     mp3_song_dict[token1_mp3] = tokens
                    # pass
                    # if word.find(qc_word)>=0:
                    #     continue
                    word = trimdj(word)
                    if word != qc_word:

                        if word in true_dict:
                            if word.find(qc_word) >= 0:
                                # print(word, qc_word)
                                continue
                            true_word = true_dict[word]
                            # 同义词
                            if qc_word in true_dict:
                                pass
                                # if true_dict[qc_word]!=true_word:
                                #     print(word,qc_word,true_word,true_dict[qc_word])
                                if qc_word != true_word:
                                    if true_word != true_dict[qc_word]:
                                        print("mp3error0:", word, qc_word, true_word, true_dict[qc_word], tokens[2])
                                    else:
                                        pass
                                else:
                                    true_dict[qc_word] = true_word
                            else:
                                # 这是一个新 的qc_word
                                # true_dict[qc_word] = true_word

                                print("mp3error1:", word, qc_word, true_dict[word])
                                ss += 1
                        else:
                            pass
                            if word.find(qc_word) >= 0:
                                continue
                            # 纠正词
                            if qc_word in true_dict:
                                qc_word_true = true_dict[qc_word]
                                word_trim = trimdj(word)
                                word_trim = word_trim.replace("+", "")
                                if word in qc_dict:
                                    word_true = true_dict[qc_dict[word]]
                                    if word_true != qc_word_true:
                                        print("mp3error2:", word, qc_word, word_true, qc_word_true)
                                        pass
                                    else:
                                        pass
                                        # 纠正词已经在字典了
                                        # print(word,qc_word)
                                elif word_trim in qc_dict:
                                    pass
                                    # 纠正词已经在字典了
                                    # print(word_trim+"\t"+word+"\t"+qc_word+"\t"+qc_dict[word_trim])
                                else:
                                    # word 是一个新的错误词,需要trimdj 之后放入qc字典, 需要check
                                    pass
                                    ss += 1
                                    if word_trim == qc_word:
                                        # 加入同义
                                        true_dict[word] = qc_word
                                    else:
                                        pass
                                        # print(word_trim+"\t"+word+"\t"+qc_word +"\t"+str(tokens[2]))
                                        # fw.write(qc_word + "|" + word + "\n")
                                        new_word2qcword[word] = qc_word

                                    # 387
                                    # print(word,trimdj(word),qc_word,tokens[2])
                                    # fw.write(word+"\t"+qc_word+"\n")
                            else:
                                # qc_word 是一个新的纠正词，新歌曲,需要放入qc_dict
                                pass
                                # print(word,qc_word)
                                new_word2qcword[word] = qc_word
                                # fw.write(qc_word + "|" + word + "\n")
                                # qc_dict[word] = qc_word
                        pass

                    else:
                        pass
                        # word == qc_word
                        if word in true_dict:
                            # word 已经在true字典
                            pass
                        else:
                            if word in qc_dict:
                                # 同义的 需要check
                                qc_word_true = ""
                                if qc_dict[word] in true_dict:
                                    qc_word_true = true_dict[qc_dict[word]]
                                word_true = ""
                                if word in true_dict:
                                    word_true = true_dict[word]
                                if qc_word_true != word_true:
                                    print("mp3error3:", word, qc_word, word_true, qc_word_true)
                                pass
                                # print(word, qc_word, tokens[2])
                                # fw.write(word+"\t"+qc_word+"\n")
                            else:
                                pass
                                # 新的词, 要放入true字典里
                                # print(word,qc_word, tokens[2])
                                true_dict[word] = qc_word

                            pass

                # end if
        # print("ss:", ss)
        return mp3_song_dict, new_word2qcword

    def edit_sim(self, str1, str2, prefix=""):
        return cal_sim(str1, str2, prefix)
    '''
        根据 trie 树提取相似的words
    '''
    def get_sim_wordsbyTrie(self, query):
        newquery = query
        m_len = len(newquery)
        re_sentence2 = newquery

        m_len = int(m_len / 2)
        re_sentence2 = re_sentence2[:m_len + 1]

        right_dict = {}
        right_qc_dict = {}
        right_qc_count_dict = {}
        # 折半查找
        while len(re_sentence2) > 1:

            tri_list = self.mytrie.get_start(re_sentence2)

            found_flag = 0

            for triword in tri_list:

                if triword not in right_dict:

                    sim, edit_count = cal_sim(newquery, triword, re_sentence2)

                    right_dict[triword] = sim
                    qctriword = triword
                    if triword in self.qc_dict:
                        qctriword = self.qc_dict[triword]
                    value = 1
                    if qctriword != triword:
                        value = 1.5

                    if sim >= 0.80 or (len(triword) == 4 and sim >= 0.75) or (len(triword) <= 3 and sim >= 0.65):

                        if qctriword not in right_qc_dict:
                            right_qc_dict[qctriword] = sim
                            right_qc_count_dict[qctriword] = value
                        else:
                            right_qc_dict[qctriword] = sim
                            right_qc_count_dict[qctriword] += value

                    if sim >= 0.80:
                        found_flag += 1

            if found_flag > 1:
                break
            else:
                m_len = int(m_len / 2)
                re_sentence2 = re_sentence2[:m_len + 1]

        # end 前向trie

        query_reverse = newquery[::-1]
        m_len = len(query_reverse)
        re_sentence2 = query_reverse

        m_len = int(m_len / 2)
        re_sentence2 = re_sentence2[:m_len + 1]

        # 折半查找
        while len(re_sentence2) > 1:

            tri_list = self.mytrie_reverse.get_start(re_sentence2)

            found_flag = 0

            for triword in tri_list:

                triword2 = triword[::-1]

                if triword2 not in right_dict:
                    sim, edit_count = cal_sim(newquery, triword2, "")
                    right_dict[triword2] = sim

                    qctriword = triword2
                    if triword2 in self.qc_dict:
                        qctriword = self.qc_dict[triword2]
                    value = 1
                    if qctriword != triword2:
                        value = 1.5
                    if sim >= 0.80 or (len(triword2) == 4 and sim >= 0.75) or (len(triword) <= 3 and sim >= 0.65):
                        if qctriword not in right_qc_dict:
                            right_qc_dict[qctriword] = sim
                            right_qc_count_dict[qctriword] = value
                        else:
                            right_qc_dict[qctriword] = sim
                            right_qc_count_dict[qctriword] += value
                    if sim >= 0.8:
                        found_flag += 1

            if found_flag > 1:
                break
            else:
                m_len = int(m_len / 2)
                re_sentence2 = re_sentence2[:m_len + 1]

        # end 逆向trie
        # 对搜索结果的候选者进行计算

        right_qc_dict_sorted = sorted(right_qc_dict.items(), key=lambda k:k[1], reverse=True)

        return right_qc_dict_sorted


    def get_py_dict(self):

        pydict = {}
        py_truedict = {}
        w_pydict = {}
        w_py_qcdict = {}
        for word, synword in self.truedict.items():
            word_py = self.py.get_pinyin(word, splitter='')
            synword_py = self.py.get_pinyin(synword, splitter='')

            if synword_py not in pydict:
                pydict[synword_py] = {}

            synword2 = synword
            if synword in self.truedict:
                synword2 = self.truedict[synword]

            if synword2 not in pydict[synword_py]:
                pydict[synword_py][synword2] = 1
            else:
                pydict[synword_py][synword2] += 1

            if word_py not in pydict:
                pydict[word_py] = {}

            word2 = word
            if word in self.truedict:
                word2 = self.truedict[word]

            if word2 not in pydict[word_py]:
                pydict[word_py][word2] = 1
            else:
                pydict[word_py][word2] += 1

        for word, qcword in self.qc_dict.items():
            word_py = self.py.get_pinyin(word, splitter='')
            qcword_py = self.py.get_pinyin(qcword, splitter='')

            if qcword_py not in pydict:
                pydict[qcword_py] = {}
            qcword2 = qcword
            if qcword in self.truedict:
                qcword2 = self.truedict[qcword]
            if qcword2 not in pydict[qcword_py]:
                pydict[qcword_py][qcword2] = 1
            else:
                pydict[qcword_py][qcword2] += 1

            if word != qcword and word not in self.truedict:
                if word_py not in w_pydict:
                    w_pydict[word_py] = {}
                if qcword2 not in w_pydict[word_py]:
                    w_pydict[word_py][qcword2] = 1
                else:
                    w_pydict[word_py][qcword2] += 1

        for wordpy, worddict in pydict.items():
            worddict_sorted = sorted(worddict.items(), key=lambda k:k[1], reverse=True)
            py_truedict[wordpy] = worddict_sorted[0][0]
        for wordpy, worddict in w_pydict.items():
            worddict_sorted = sorted(worddict.items(), key=lambda k: k[1], reverse=True)
            w_py_qcdict[wordpy] = worddict_sorted[0][0]
        return pydict, w_pydict, py_truedict, w_py_qcdict

if __name__ == "__main__":

    workdir = "./"
    user_confusion_path = workdir + 'dict3/custom_confusion.txt'
    sj_user_confusion_path = workdir + "dict3/sj_custom_confusion.txt"
    plus_user_confusion_path = workdir + 'dict3/plus_custom_confusion.txt'
    syn_path = workdir + "dict3/syn.txt"
    mp3all_file = workdir + "mp3/mp3.all"
    corrector = Corrector(user_confusion_path, sj_user_confusion_path, plus_user_confusion_path, syn_path, mp3all_file,1)

    query = "绍东跳跳乐快乐舞步健身操第十九套完正版朱晓敏"
    segline = "绍 东 跳跳 乐 快乐舞步 健身操 第 十九 套 完 正版 朱晓敏"
    seglist = segline.split(" ")
    qc_query, qc_type = corrector.get_newquery_byseg_norm(query, None, None, seglist, None)

    print(qc_query, qc_type)
    norm = SynonymNorm()
    print(norm.transform('健身操闫密队二O一八年第三套', '健身操 闫密 队 二 o 一八 年 第三套'))

