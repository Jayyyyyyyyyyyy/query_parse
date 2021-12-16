#-*- coding: utf-8 -*-
'''
@Author    :  Cath Zhang  sunjian
@Time      :  2019/11/4 下午5:11
@File      :  td_corrector.py
'''
from .Trie  import Trie
import numpy as np
import re


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


class Corrector(object):
    def __init__(self,user_confusion_wrong_right, user_dict_right_set,user_confusion_wrongpinyin_rightterm,
                 user_confusion_rightpinyin_rightterm, dance_teacher_fix_set,jb, pinyin, edit_sim_dict, prefix_wordline_dict):
        self.name = 'corrector'
        self.user_confusion_wrong_right = user_confusion_wrong_right
        #纠错字典映射字典
        self.user_dict_right_set = user_dict_right_set
        self.user_confusion_wrongpinyin_rightterm = user_confusion_wrongpinyin_rightterm
        self.user_confusion_rightpinyin_rightterm = user_confusion_rightpinyin_rightterm
        #舞蹈类型，老师 前后缀
        self.dance_teacher_fix_set = dance_teacher_fix_set
        m_dict = {}
        gcw = u'广场舞'
        # m_dict[gcw] = len(gcw)
        for dance in self.dance_teacher_fix_set:
            m_dict[dance] = len(dance)

        m_dict_sorted = sorted(m_dict.items(), key=lambda k: k[1], reverse=True)
        self.dance_teacher_fix_list = m_dict_sorted
        # for k,v in self.song_type_list:
        #     print(k+"\t"+str(v))
        self.pinyin = pinyin
        self.jb = jb

        self.mytrie = Trie()
        for word in user_dict_right_set:
            self.mytrie.insert(word)
        for q, qc in user_confusion_wrong_right.items():
            self.mytrie.insert(q)
            self.mytrie.insert(qc)
        self.edit_sim_dict = edit_sim_dict
        self.prefix_wordline_dict = prefix_wordline_dict

    def dump_edit_sim_dict(self, fileout):

        with open(fileout, "w") as fw:
            for query, sim_dict in self.edit_sim_dict.items():
                outlist = []
                for sim_word, sim_value in sim_dict.items():
                    outlist.append(str(sim_word) + ":" + str(round(sim_value, 4)))
                outline = str(query) + "\t" + "#".join(outlist)
                fw.write(outline + "\n")

    def dump_prefix_wordline_dict(self, fileout):

        with open(fileout, "w") as fw:
            for query, prefix_list in self.prefix_wordline_dict.items():
                outline = str(query) + "\t" + "#".join(prefix_list)
                fw.write(outline + "\n")

    def complete_query(self,type_index, replaced_type, corrected_sentence):
        if type_index == 0:
            corrected_sentence = replaced_type + corrected_sentence
        elif type_index > 0:
            corrected_sentence = corrected_sentence + replaced_type
        return corrected_sentence

    # find and correct
    def find_and_replace(self,merge_token, sentence):
        idx = sentence.find(merge_token)
        if idx > -1:
            corrected_index = idx
        else:
            corrected_index = -1
        return corrected_index

    def replace_by_term_with_correct(self,original_term, correct_term):
        correct_word_pinyin = {}
        for word in correct_term:
            correct_word_pinyin[self.pinyin.get_pinyin(word, splitter='')] = word
        for word_index, word in enumerate(original_term):
            original_term_pinyin = self.pinyin.get_pinyin(word, splitter='')
            if original_term_pinyin in correct_word_pinyin:
                original_term = original_term[:word_index] + correct_word_pinyin[original_term_pinyin] + original_term[
                                                                                                         word_index + 1:]
        return original_term

    def compare_pinyin(self,term, term_pinyin, corrected_sentence, pinyin_term,standard_index, standard_length):
        correct_term = pinyin_term[term_pinyin]
        corrected_index = self.find_and_replace(term, corrected_sentence)
        correct_term_length = len(term)
        # 开始比较下标，标准化的不会再被更改
        if (corrected_index > standard_index and corrected_index > standard_index + standard_length - 1) \
                or (corrected_index < standard_index and corrected_index + correct_term_length - 1 < standard_index) \
                or (
                corrected_index <= standard_index and corrected_index + correct_term_length >= standard_index + standard_length):
            corrected_sentence = corrected_sentence.replace(term, correct_term)
        return corrected_sentence, correct_term

    def complete_query(self,type_index, replaced_type, corrected_sentence):
        if type_index == 0:
            corrected_sentence = replaced_type + corrected_sentence
        elif type_index > 0:
            corrected_sentence = corrected_sentence + replaced_type
        return corrected_sentence

    def qc(self, query, yuyin=False, whole_flag = 1, prefix="", suffix=""):

        sentence= query
        re_sentence = sentence
        type_index = -1
        replaced_type = ''
        result_type = 0
        pro_query = query

        re_sentence_pinyin = self.pinyin.get_pinyin(re_sentence, splitter='')

        #es = re.search('\d+', s)

        pattern2 = re.search("(第.+套)|(第.+节)", query)

        # 1. query 本身是正确的query
        if sentence in self.user_dict_right_set:
            corrected_sentence = sentence
            type_index = -1
            result_type = 1
            return self.complete_query(type_index, replaced_type, corrected_sentence), result_type
        # 2. query 本身是映射字典的错误query
        elif sentence in self.user_confusion_wrong_right:
            corrected_sentence = self.user_confusion_wrong_right[sentence]
            type_index = -1
            result_type = 2
            return self.complete_query(type_index, replaced_type, corrected_sentence), result_type
        # 3,4 逻辑有问题， 比如初学 初雪 可能是同音，会纠反
        # # 3. 拼音在是正确的拼音
        # elif re_sentence_pinyin in self.user_confusion_rightpinyin_rightterm:
        #
        #     corrected_sentence = self.user_confusion_rightpinyin_rightterm[re_sentence_pinyin]
        #     result_type = 3
        #     return self.complete_query(type_index, replaced_type, corrected_sentence), result_type
        # # 4. 拼音在是错误的拼音，查找对应的正确关键词
        # elif re_sentence_pinyin in self.user_confusion_wrongpinyin_rightterm:
        #
        #     corrected_sentence = self.user_confusion_wrongpinyin_rightterm[re_sentence_pinyin]
        #     result_type = 4
        #     return self.complete_query(type_index, replaced_type, corrected_sentence), result_type
        # 5. query 去掉字典后 字数少于3个，直接返回
        elif len(sentence) <= 3:
            corrected_sentence = sentence
            type_index = -1
            result_type = 5
            return self.complete_query(type_index, replaced_type, corrected_sentence), result_type

        elif pattern2:
            corrected_sentence = sentence
            type_index = -1
            result_type = 5
            return self.complete_query(type_index, replaced_type, corrected_sentence), result_type
        # 6. 剩余  1 根据前缀 判断相似的right 词
        # 7.      2 先切词 判断seg是否错词  再 二元组合判断是否
        else:

            if whole_flag==0:
                # tri 检索 候选的词

                res = re.search('\d+步', re_sentence)

                m_len = len(re_sentence)
                re_sentence2 = re_sentence
                # 折半查找
                while len(re_sentence2)>1:

                    tri_list = []
                    if re_sentence2 not in self.prefix_wordline_dict:
                        tri_list = self.mytrie.get_start(re_sentence2)
                        #self.prefix_wordline_dict[re_sentence2] = tri_list
                    else:
                        tri_list = self.prefix_wordline_dict[re_sentence2]

                    right_dict = {}
                    for triword in tri_list:
                        #print(re_sentence, triword)

                        if re_sentence not in self.edit_sim_dict:
                            self.edit_sim_dict[re_sentence] = {}
                            if triword not in self.edit_sim_dict[re_sentence]:
                                sim, edit_count = cal_sim(re_sentence, triword, re_sentence2)
                                # self.edit_sim_dict[re_sentence][triword] = sim
                            else:
                                pass
                        else:
                            if triword not in self.edit_sim_dict[re_sentence]:
                                sim, edit_count = cal_sim(re_sentence, triword, re_sentence2)
                                # self.edit_sim_dict[re_sentence][triword] = sim
                            else:
                                sim = self.edit_sim_dict[re_sentence][triword]



                        right_word= triword
                        if triword in self.user_confusion_wrong_right:
                            right_word = self.user_confusion_wrong_right[triword]

                                #print("\tdebug:prefix["+prefix+"]\tright_word:"+right_word)

                        if right_word.startswith(prefix) and prefix != "":
                            right_word = right_word[len(prefix):]
                        if re_sentence.startswith(right_word):
                            right_word = re_sentence
                            #print("\tdebug:query[" + query + "]\tright_word:" + right_word)

                        if right_word not in right_dict:
                            right_dict[right_word] = sim
                        else:
                            if sim > right_dict[right_word]:
                                right_dict[right_word] = sim
                        if right_word.startswith(re_sentence):
                            right_dict[re_sentence] = 1.0

                    right_dict_sorted = sorted(right_dict.items(), key=lambda k: k[1], reverse=True)
                    if len(right_dict_sorted)>0:
                        outlist = []
                        for (k,v) in right_dict_sorted:
                            outlist.append(str(k)+":"+str(v))
                        #print("sim_detail:"+query+"\t"+re_sentence2+"\t"+"#".join(outlist))
                        if right_dict_sorted[0][1] >=0.80 and not res:
                            corrected_sentence = right_dict_sorted[0][0]
                            type_index = -1
                            result_type = 6
                            return self.complete_query(type_index, replaced_type, corrected_sentence), result_type
                        break
                    else:
                        m_len = int(m_len/2)
                        re_sentence2 = re_sentence2[:m_len+1]

                # corrected_sentence = sentence
                # type_index = -1
                # result_type = 0
                # return self.complete_query(type_index, replaced_type, corrected_sentence), result_type

            # next step
            # 分词
            tokens = list(self.jb.cut(re_sentence))
            #print("seg:"+" ".join(tokens))
            corrected_sentence = re_sentence
            standard_index = -1
            standard_length = -1
            replace_token = ''
            for index, term in enumerate(tokens):
                if term in self.user_dict_right_set:
                    standard_index = re_sentence.find(term)
                    standard_length = len(term)
                if term in self.user_confusion_wrong_right:
                    replace_token = term
                    corrected_index = self.find_and_replace(term, re_sentence)
                    correct_term_length = len(term)
                    # 开始比较下标，标准化的不会再被更改
                    if (
                            corrected_index > standard_index and corrected_index > standard_index + standard_length - 1) or (
                            corrected_index < standard_index and corrected_index + correct_term_length - 1 < standard_index):
                        correct_term = self.user_confusion_wrong_right[replace_token]
                        corrected_sentence = re_sentence.replace(replace_token, correct_term)
                        tokens[index] = self.replace_by_term_with_correct(term, correct_term)

            if len(tokens) > 1 and yuyin:
                for i in range(len(tokens) - 1):
                    merge_token = (tokens[i] + tokens[i + 1])
                    #print(str(i)+":"+merge_token)
                    term_pinyin = self.pinyin.get_pinyin(merge_token, splitter='')
                    if term_pinyin in self.user_confusion_rightpinyin_rightterm:
                        #print("debug1")
                        corrected_sentence, correct_term = self.compare_pinyin(merge_token, term_pinyin,
                                                                               corrected_sentence,
                                                                               self.user_confusion_rightpinyin_rightterm,
                                                                               standard_index, standard_length)
                        tokens[i] = self.replace_by_term_with_correct(tokens[i], correct_term)
                        tokens[i + 1] = self.replace_by_term_with_correct(tokens[i + 1], correct_term)
                        merge_token = (tokens[i] + tokens[i + 1])
                    elif term_pinyin in self.user_confusion_wrongpinyin_rightterm:
                        #print("debug2")
                        corrected_sentence, correct_term = self.compare_pinyin(merge_token, term_pinyin,
                                                                               corrected_sentence,
                                                                               self.user_confusion_wrongpinyin_rightterm,
                                                                               standard_index, standard_length)
                        tokens[i] = self.replace_by_term_with_correct(tokens[i], correct_term)
                        tokens[i + 1] = self.replace_by_term_with_correct(tokens[i + 1], correct_term)
                        merge_token = (tokens[i] + tokens[i + 1])
                    #elif merge_token in self.user_confusion_wrong_right:
                    elif merge_token in self.user_confusion_wrong_right and corrected_sentence.find(
                             merge_token) > -1:
                        #print("debug3")
                        replace_token = merge_token
                        corrected_index1 = self.find_and_replace(merge_token, corrected_sentence)
                        corrected_length1 = len(merge_token)
                        if (
                                corrected_index1 > standard_index and corrected_index1 > standard_index + standard_length - 1) or (
                                corrected_index1 < standard_index and corrected_index1 + corrected_length1 - 1 < standard_index):
                            correct_term = self.user_confusion_wrong_right[replace_token]
                            corrected_sentence = corrected_sentence.replace(replace_token, correct_term)
            result_type = 7
            return self.complete_query(type_index, replaced_type, corrected_sentence), result_type

    def compare(self, query, yuyin=False):
        # user_confusion_wrong_right, user_dict_right_set,user_confusion_wrongpinyin_rightterm,user_confusion_rightpinyin_rightterm, song_type_set,jb, pinyin
        sentence = query.split('\t')[0]
        # sentence = (line.split(',')[1]).strip('"')
        gcw = u'广场舞'
        # # compare confusion dict
        # self.dance_teacher_fix_set.add(gcw)
        re_sentence = sentence
        whole_flag = 1
        result_type = 0
        #print("--------------------------")
        qc_query, result_type = self.qc(query, yuyin, 0, "", "")

        if result_type<=5:
            # if result_type==6 and query!=qc_query:
            #     pass
            #     print("rawquery:" + query+"\t"+str(qc_query)+"\t"+str(result_type))
            # if query!=qc_query:
            #     print("rawquery:" + query + "\t" + str(qc_query) + "\t" + str(result_type))
            #print("rawquery:" + query + "\t" + str(qc_query) + "\t" + str(result_type))
            return qc_query, result_type
        else:
            #print("subquery_raw:" + query)
            #预处理 前缀，后缀舞蹈类型 分割

            prefix_wordlist = []
            suffix_wordlist = []
            for danceword,type_len in self.dance_teacher_fix_list:
                if re_sentence.startswith(danceword):
                    prefix_wordlist.append(danceword)
                    re_sentence = re_sentence[len(danceword):]
                if re_sentence.endswith(danceword):
                    suffix_wordlist.append(danceword)
                    re_sentence = re_sentence[:-len(danceword)]

            true_re_sentence = re_sentence

            true_re_sentence= true_re_sentence.replace(gcw, " "+gcw+" ")
            #true_re_sentence = true_re_sentence.strip()
            #print("#".join(prefix_wordlist))

            prefix_wordline = " ".join(prefix_wordlist).strip()
            suffix_wordline = " ".join(suffix_wordlist[::-1]).strip()
            re_sentence = " ".join(prefix_wordlist) + " " + true_re_sentence + " " + " ".join(suffix_wordlist[::-1])

            true_senten_list = true_re_sentence.split(" ")

            result_qc_query = ""
            #print("subquery_true:"+true_re_sentence)
            for sub_query in true_senten_list:

                qc_query, result_type = self.qc(sub_query, yuyin, 0, prefix_wordline, suffix_wordline)
                #print("\t"+sub_query+"\t"+qc_query+"\t"+str(result_type))

                result_qc_query +=qc_query

            result_qc_query = ''.join(prefix_wordlist)+result_qc_query+''.join(suffix_wordlist[::-1])
            # if result_type>=6 and query!=result_qc_query:
            #     print("subquery:"+query + '\t' + re_sentence+"\t"+result_qc_query+"\t"+str(result_type))
            #print("subquery:" + query + '\t' + re_sentence + "\t" + result_qc_query + "\t" + str(result_type))
            return result_qc_query,result_type

    def compare_zx(self,query):
        # user_confusion_wrong_right, user_dict_right_set,user_confusion_wrongpinyin_rightterm,user_confusion_rightpinyin_rightterm, song_type_set,jb, pinyin
        sentence = query.split('\t')[0]
        # sentence = (line.split(',')[1]).strip('"')
        gcw = u'广场舞'
        # compare confusion dict
        self.dance_teacher_fix_set.add(gcw)
        re_sentence = sentence
        type_index = -1
        replaced_type = ''
        for type in self.dance_teacher_fix_set:
            if sentence.startswith(type) or sentence.endswith(type):
                replaced_type = type
                re_sentence = sentence.replace(type, '')
                type_index = sentence.find(type)
                if len(re_sentence) <=2:
                    return sentence

        re_sentence_pinyin = self.pinyin.get_pinyin(re_sentence, splitter='')
        if re_sentence in self.user_dict_right_set:
            corrected_sentence = re_sentence
            return self.complete_query(type_index, replaced_type, corrected_sentence)

        elif re_sentence in self.dance_teacher_fix_set:
            corrected_sentence = re_sentence
            return self.complete_query(type_index, replaced_type, corrected_sentence)
        elif re_sentence in self.user_confusion_wrong_right:
            corrected_sentence = self.user_confusion_wrong_right[re_sentence]
            return self.complete_query(type_index, replaced_type, corrected_sentence)
        elif re_sentence_pinyin in self.user_confusion_rightpinyin_rightterm:
            corrected_sentence = self.user_confusion_rightpinyin_rightterm[re_sentence_pinyin]
            return self.complete_query(type_index, replaced_type, corrected_sentence)
        elif re_sentence_pinyin in self.user_confusion_wrongpinyin_rightterm:
            corrected_sentence = self.user_confusion_wrongpinyin_rightterm[re_sentence_pinyin]
            return self.complete_query(type_index, replaced_type, corrected_sentence)
        else:
            tokens = list(self.jb.cut(re_sentence))
            corrected_sentence = re_sentence
            standard_index = -1
            standard_length = -1
            replace_token = ''
            for index, term in enumerate(tokens):
                if term in self.user_dict_right_set:
                    standard_index = re_sentence.find(term)
                    standard_length = len(term)
                if term in self.user_confusion_wrong_right:
                    replace_token = term
                    corrected_index = self.find_and_replace(term, re_sentence)
                    correct_term_length = len(term)
                    # 开始比较下标，标准化的不会再被更改
                    if (
                            corrected_index > standard_index and corrected_index > standard_index + standard_length - 1) or (
                            corrected_index < standard_index and corrected_index + correct_term_length - 1 < standard_index):
                        correct_term = self.user_confusion_wrong_right[replace_token]
                        corrected_sentence = re_sentence.replace(replace_token, correct_term)
                        tokens[index] = self.replace_by_term_with_correct(term, correct_term)

            if len(tokens) > 1:
                for i in range(len(tokens) - 1):
                    merge_token = (tokens[i] + tokens[i + 1])
                    term_pinyin = self.pinyin.get_pinyin(merge_token, splitter='')
                    if term_pinyin in self.user_confusion_rightpinyin_rightterm:
                        corrected_sentence, correct_term = self.compare_pinyin(merge_token, term_pinyin,corrected_sentence,
                                                                          self.user_confusion_rightpinyin_rightterm,standard_index,standard_length)
                        tokens[i] = self.replace_by_term_with_correct(tokens[i], correct_term)
                        tokens[i + 1] = self.replace_by_term_with_correct(tokens[i + 1], correct_term)
                        merge_token = (tokens[i] + tokens[i + 1])
                    elif term_pinyin in self.user_confusion_wrongpinyin_rightterm:
                        corrected_sentence, correct_term = self.compare_pinyin(merge_token, term_pinyin,
                                                                               corrected_sentence,
                                                                               self.user_confusion_wrongpinyin_rightterm,
                                                                               standard_index, standard_length)
                        tokens[i] = self.replace_by_term_with_correct(tokens[i], correct_term)
                        tokens[i + 1] = self.replace_by_term_with_correct(tokens[i + 1], correct_term)
                        merge_token = (tokens[i] + tokens[i + 1])
                    elif merge_token in self.user_confusion_wrong_right and corrected_sentence.find(merge_token) > -1:
                        replace_token = merge_token
                        corrected_index1 = self.find_and_replace(merge_token, corrected_sentence)
                        corrected_length1 = len(merge_token)
                        if (
                                corrected_index1 > standard_index and corrected_index1 > standard_index + standard_length - 1) or (
                                corrected_index1 < standard_index and corrected_index1 + corrected_length1 - 1 < standard_index):
                            correct_term = self.user_confusion_wrong_right[replace_token]
                            corrected_sentence = corrected_sentence.replace(replace_token, correct_term)
            return self.complete_query(type_index, replaced_type, corrected_sentence)




