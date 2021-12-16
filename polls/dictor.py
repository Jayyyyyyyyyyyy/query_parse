#-*- coding: utf-8 -*-
'''
@Author    :  Cath Zhang
@Time      :  2019/11/4 下午5:19
@File      :  dictor.py
'''
from xpinyin import Pinyin
import jieba
import codecs
import os

class Dictor(object):
    def __init__(self,user_confusion_path, sj_user_confusion_path, plus_user_confusion_path, standard_song_path, ground_true_dict_path, dance_teacher_fix_path,jb_dict_path,edit_sim_path,prefix_wordline_path):
        self.name = 'Dictor'
        #3个纠错对应表,取前两列
        self.user_confusion_path = user_confusion_path
        self.sj_user_confusion_path = sj_user_confusion_path
        self.plus_user_confusion_path = plus_user_confusion_path
        #歌曲名字典,取前一列
        self.standard_dict_path = standard_song_path
        self.ground_true_dict_path = ground_true_dict_path
        #self.song_type_path = dance_teacher_fix_path
        self.dance_teacher_fix_path = dance_teacher_fix_path
        self.jb_dict_path = jb_dict_path
        self.edit_sim_path = edit_sim_path
        self.prefix_wordline_path =prefix_wordline_path


    def load_pinyin(self):
        p = Pinyin()
        self.p = p

    # 去掉头尾的：广场舞、舞蹈类型 该方法不好用，
    # def remove_fix(self,filter_set,variant,origin):
    #     for dance_type in filter_set:
    #         if variant.startswith(dance_type) and origin.startswith(dance_type):
    #             new_variant = variant.replace(dance_type, '')
    #             new_origin = origin.replace(dance_type, '')
    #             if len(new_variant)>2 and len(new_origin) >2:
    #                 return new_variant, new_origin
    #         elif variant.endswith(dance_type) and origin.endswith(dance_type):
    #             new_variant = variant.replace(dance_type, '')
    #             new_origin = origin.replace(dance_type, '')
    #
    #             if len(new_variant)>2 and len(new_origin) >2:
    #                 return new_variant, new_origin
    #         else:
    #             new_variant = variant
    #             new_origin = origin
    #     return new_variant, new_origin

    # load user confusion dict
    def init_user_confusion(self,path, dance_teacher_fix_set,flag):
        confusion_wrong = {}
        confusion_right_set = set()
        confusion_wrongpinyin_rightterm = {}
        confusion_rightpinyin_rightterm = {}
        gcw = set()
        gcw.add(u'广场舞')
        filter_set = dance_teacher_fix_set | gcw
        with codecs.open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    continue
                info = line.split('\t')
                if len(info) < 2:
                    continue

                if len(info[1]) >= 2:
                    variant = info[0]
                    origin = info[1]
                    confusion_wrong[variant] = origin
                    confusion_right_set.add(origin)
                    # 去掉以下逻辑，保证字典里面的都是正确的映射，不要拆前缀，后缀
                    # new_variant,new_origin = self.remove_fix(filter_set,variant,origin)
                    # confusion_wrong[new_variant] = new_origin
                    # confusion_right_set.add(new_origin)
        if flag:
            for wrong,right in confusion_wrong.items():
                term_pinyin = self.p.get_pinyin(wrong, splitter='')
                confusion_wrongpinyin_rightterm[term_pinyin] = right
            for right_term in confusion_right_set:
                term_pinyin = self.p.get_pinyin(right_term, splitter='')
                confusion_rightpinyin_rightterm[term_pinyin] = right_term
        return confusion_wrong, confusion_right_set, confusion_wrongpinyin_rightterm,confusion_rightpinyin_rightterm

    def load_song_dict(self):
        song_pinyin_term = {}
        song_set = set()
        with codecs.open(self.standard_dict_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    continue
                info = line.split("\t")
                mp3name = info[0]
                mp3name_pinyin = self.p.get_pinyin(mp3name, splitter='')
                song_set.add(info[0])
                song_pinyin_term[mp3name_pinyin] = mp3name
        return song_pinyin_term, song_set

    def load_one_column(self,path,flag):
        gt_set = set()
        gt_pinyin_term = {}
        with codecs.open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    continue
                query = line.split()[0].strip()
                gt_set.add(query)
                if flag:
                    query_pinyin = self.p.get_pinyin(query, splitter='')
                    gt_pinyin_term[query_pinyin] = query
        return gt_set,gt_pinyin_term

    def load_edit_sim(self):
        edit_sim_dict = {}
        if os.path.exists(self.edit_sim_path):
            with open(self.edit_sim_path, 'r') as fr:
                for line in fr:
                    line = line.strip()
                    tokens = line.split("\t")
                    if len(tokens)<2:continue
                    query = tokens[0]
                    sim_wordline = tokens[1]
                    edit_sim_dict[query] = {}

                    for sim_word_pair in sim_wordline.split("#"):
                        subtoken = sim_word_pair.split(":")
                        if len(subtoken)<2:continue
                        edit_sim_dict[query][subtoken[0]] = float(subtoken[1])
        return edit_sim_dict

    def load_prefix_wordline(self):
        prefix_wordline_dict = {}
        if os.path.exists(self.prefix_wordline_path):
            with open(self.prefix_wordline_path, 'r') as fr:
                for line in fr:
                    line = line.strip()
                    tokens = line.split("\t")
                    if len(tokens) < 2: continue
                    query = tokens[0]
                    pre_wordline = tokens[1]
                    prefix_wordline_dict[query] = pre_wordline.split("#")

        return prefix_wordline_dict


    # def dump_edit_sim(self, edit_sim_dict):
    #     with open(self.edit_sim_path, "w") as fw:
    #         for query, sim_dict in edit_sim_dict.items():
    #             outlist = []
    #             for sim_word,sim_value in sim_dict.items():
    #                 outlist.append(str(sim_word)+":"+str(round(sim_value,4)))
    #             outline = str(query)+"\t"+"#".join(outlist)
    #             fw.write(outline+"\n")




    def load_all_dict(self):
        self.load_pinyin()
        # load jieba user dict
        user_dict_path = self.jb_dict_path
        jieba.load_userdict(user_dict_path)

        #  ground_true_dict只有top的query中正确的
        #gt_set,gt_pinyin_term = self.load_one_column(self.ground_true_dict_path,True)
        gt_set = set()
        gt_pinyin_term = {}
        dance_teacher_fix_set,_ = self.load_one_column(self.dance_teacher_fix_path,False)
        # load user confusion dict
        confusion_wrong, confusion_right_set, confusion_wrongpinyin_rightterm, confusion_rightpinyin_rightterm = self.init_user_confusion(
            self.user_confusion_path,dance_teacher_fix_set, True)
        sj_confusion_wrong, sj_confusion_right_set, sj_confusion_wrongpinyin_rightterm, sj_confusion_rightpinyin_rightterm = self.init_user_confusion(
            self.sj_user_confusion_path,dance_teacher_fix_set, True)
        plus_confusion_wrong, plus_confusion_right_set, plus_confusion_wrongpinyin_rightterm, plus_confusion_rightpinyin_rightterm = self.init_user_confusion(
            self.plus_user_confusion_path,dance_teacher_fix_set, True)
        # load song dict
        song_pinyin_term, song_set = self.load_song_dict()

        # edit_sim dict

        edit_sim_dict = self.load_edit_sim()

        prefix_wordline_dict = self.load_prefix_wordline()


        # 3 in 1 dict
        user_confusion_wrong_right = {}
        user_confusion_wrong_right.update(confusion_wrong)
        user_confusion_wrong_right.update(sj_confusion_wrong)
        user_confusion_wrong_right.update(plus_confusion_wrong)
        #  5 in 1 set
        user_dict_right_set = confusion_right_set|sj_confusion_right_set|plus_confusion_right_set|song_set|gt_set
        # 3 in 1 dict
        user_confusion_wrongpinyin_rightterm = {}
        user_confusion_wrongpinyin_rightterm.update(confusion_wrongpinyin_rightterm)
        user_confusion_wrongpinyin_rightterm.update(sj_confusion_wrongpinyin_rightterm)
        user_confusion_wrongpinyin_rightterm.update(plus_confusion_wrongpinyin_rightterm)
        # 5 in 1 dict
        user_confusion_rightpinyin_rightterm = {}
        user_confusion_rightpinyin_rightterm.update(confusion_rightpinyin_rightterm)
        user_confusion_rightpinyin_rightterm.update(sj_confusion_rightpinyin_rightterm)
        user_confusion_rightpinyin_rightterm.update(plus_confusion_rightpinyin_rightterm)
        user_confusion_rightpinyin_rightterm.update(song_pinyin_term)
        user_confusion_rightpinyin_rightterm.update(gt_pinyin_term)

        # print(len(user_dict_right_set))
        # print(len(user_confusion_wrong_right))

        return user_confusion_wrong_right, user_dict_right_set, user_confusion_wrongpinyin_rightterm, \
               user_confusion_rightpinyin_rightterm, dance_teacher_fix_set,jieba,self.p, edit_sim_dict,prefix_wordline_dict






