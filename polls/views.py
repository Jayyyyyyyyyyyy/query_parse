from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import json
import jieba
import html
import re
import random
import requests
import pandas as pd
import datetime
import threading
from .qcorrector import Corrector
from .dfa import DFAFilter
import numpy as np
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from .content_mp3 import Extracter
from .ToolTranslate import Translate




user_dict = './dict/userdict.sj'
jieba.initialize()
jieba.load_userdict(user_dict)

df_tag_lib = pd.read_csv('./dict/tag_lib.csv', delimiter=',', encoding='utf-8')

mp3_extracter = Extracter()

def pair_to_dict(df):
    pair_dict = {}
    for ind, (label, alias) in df.iterrows():
        pair_dict[alias] = label
    return pair_dict

def generate_dict(df, rec_field):
    pair_dict = {}
    df = df[df['rec_field']==rec_field][['id','name']]
    for ind, (id,name) in df.iterrows():
        pair_dict[name] = id
    return pair_dict

def to_term_weight_dict(list):
    mydict = {}
    values = []
    for term, df, value in list:
        values.append(float(value))
        mydict[term] = float(value)

    avg = np.mean(values)
    median = np.median(values)
    return mydict, avg, median

def to_co_show_dict(path):
    co_show_dict = {}
    co_show_dict_sum = {}
    with open(path, "r", encoding='utf-8') as f1:
        for line in f1:
            line = line.strip()
            tokens = line.split("\t")
            if len(tokens)!=5:continue
            key = tokens[0]
            wordline = tokens[4]
            sum = 0
            if key not in co_show_dict:
                co_show_dict[key] = {}
            for wordstr in wordline.split(" "):
                subkey = wordstr.split(":")[0]
                value = float(wordstr.split(":")[-1])

                sum +=value
                co_show_dict[key][subkey] = value
            co_show_dict_sum[key] = sum
    return co_show_dict, co_show_dict_sum

dance_tag_dict = generate_dict(df_tag_lib,'content_dance')
teacher_tag_dict = generate_dict(df_tag_lib,'content_teacher')
tag_tag_dict = generate_dict(df_tag_lib,'content_tag')



teacher_pair = pd.read_csv('./dict/content_teacher_pair.csv', delimiter=',', encoding='utf-8')
tag_pair = pd.read_csv('./dict/content_tag_pair.csv', delimiter=',', encoding='utf-8')
dance_pair = pd.read_csv('./dict/content_dance_pair.csv', delimiter=',', encoding='utf-8')
teacher_pair_dict = pair_to_dict(teacher_pair)
tag_pair_dict = pair_to_dict(tag_pair )
dance_pair_dict = pair_to_dict(dance_pair)
all_dance_type_list = list(dance_pair_dict.keys()) + list(dance_tag_dict.keys())
dance_type_without_gcw = all_dance_type_list.copy()
dance_type_without_gcw.remove('广场舞')



def get_tagname_tagid(words, df_pair, df_tag_lib, content_name):
    try:
        tag = []
        for word in words:
            df_label = df_pair[df_pair.alias == word][['label']]
            df_tag = df_tag_lib[(df_tag_lib.rec_field == content_name) & (df_tag_lib.name == word)][['id']]
            if not df_label.empty:
                label_name = df_label.iat[0, 0]
                tag_id = df_tag_lib[(df_tag_lib.rec_field == content_name) & (df_tag_lib.name == label_name)][['id', 'name']].iat[0, 0]
                tag.append({'tagname': label_name, 'tagvalue': 1.0, 'tagid': int(tag_id)})
            elif not df_tag.empty:
                # logging.info(word + 'in the elif')
                tag_id = df_tag.iat[0, 0]
                tag.append({'tagname': word, 'tagvalue': 1.0, 'tagid': int(tag_id)})
            else:
                continue
        if len(tag) == 0:
            # logging.info(content_name +'is get taganmeid tag==0')
            return [{'tagname': 'unknown', 'tagvalue': 1.0, 'tagid': 0}]
        return tag
    except:
        logging.info(content_name + 'is get taganmeid run except')
        return [{}]


def get_tagname_from_tagid(content_teach_id, content_name, df_tag_lib):
    tag_name = ''
    content_teach_id = int(content_teach_id.strip())
    df_tag = df_tag_lib[(df_tag_lib.rec_field == content_name) & (df_tag_lib.id == content_teach_id)][['name']]
    if not df_tag.empty:
        tag_name = df_tag.iat[0, 0]
        return tag_name
    return tag_name

def create_struct_data(words,pair_dict,tag_dict):
    try:
        tag = []
        for word in words:
            # 标准化
            if word in pair_dict:
                id = tag_dict[pair_dict[word]]
                tag.append({'tagname': pair_dict[word], 'tagvalue': 1.0, 'tagid': id})
            elif word in tag_dict:
                # logging.info(word + 'in the elif')
                id = tag_dict[word]
                tag.append({'tagname': word, 'tagvalue': 1.0, 'tagid': id})
            else:
                continue
        if len(tag) == 0:
            return [{'tagname': 'unknown', 'tagvalue': 1.0, 'tagid': 0}]
        return tag
    except:
        logging.info('content_dance is get taganmeid run except')
        return [{'tagname': 'unknown', 'tagvalue': 1.0, 'tagid': 0}]

# content_dance
def dance_type(words):
    return create_struct_data(words,dance_pair_dict,dance_tag_dict)[0]


#  content_teacher
def teacher_type(words, title):
    m_set = set(words)
    newwords = words
    for word in words:
        word2 = ''
        if word.startswith("广场舞") or word.endswith("广场舞"):
            word2 = word.replace("广场舞", "")
        if word2 != "" and word2 not in m_set:
            newwords = [word2] + newwords
            m_set.add(word2)
    return create_struct_data(newwords, teacher_pair_dict, teacher_tag_dict)[0]


# content_tag
def tags_type(words, content_dance_id):
    newwords = words
    #if content_dance_id.strip():
        #tag_name = get_tagname_from_tagid(content_dance_id, 'content_dance', df_tag_lib)
        #newwords #= [tag_name] + newwords
    return create_struct_data(newwords, tag_pair_dict, tag_tag_dict)


# jcx
# clearning query  ==>> Task 0.
def cleaning_query(raw_query):
    clean_query = html.unescape(raw_query.strip())
    clean_query = re.sub("[^a-zA-Z0-9\u4e00-\u9fa5]+", "", clean_query)
    clean_query = clean_query.lower()
    re.sub('\s', '', clean_query)
    return clean_query

def url_choise():
    urls = [
            "http://10.42.16.15:11091/KwService/Kwpro",
            "http://10.42.42.82:11091/KwService/Kwpro",
            "http://10.42.21.112:11091/KwService/Kwpro"
            ]
    return random.choice(urls)

def request_kw(jsonbody, url, times = 0):
    s = requests.Session()
    s.keep_alive = False
    #url = "http://10.42.16.15:11091/KwService/Kwpro"
    #url = "http://127.0.0.1:11091/KwService/Kwpro"
    head = {"Content-Type": "application/json",
            "Connection": "close"}
    resjson = {}
    try:
        if times >=5:
            return None
        times += 1
        res = s.post(url, json=jsonbody, headers=head)
        resjson = res.json()
        logging.info(resjson)
    except Exception as e:
        print(e)
        return request_kw(jsonbody, url_choise(), times)
    return resjson

def process_query(title, stop_word_flag = False):
    content_dance_id = "0"
    content_tag = []
    cutted_title = []
    content_dance = {}
    content_mp3 = {}
    content_teacher = {}
    content_team_name = {}
    segment_def = ""
    segment_seach = ""
    segment_better = ""
    # add  childcategory_id = "0"
    # 判断title的异常处理
    if len(title.strip()) == 0:
        return cutted_title, title, content_tag, content_dance, content_mp3, content_teacher, content_team_name, segment_def, segment_seach, segment_better
    only_chinese = re.sub("[^\u4e00-\u9fa5]+", "", title.strip())
    if len(only_chinese) >= 40:
        title = title[:40]

    clearned_title = cleaning_query(title)


    jsonbody = {}
    jsonbody["title"] = title
    jsonbody["onlyseg"] = 2
    jsonbody["segmode"] = 0
    seg_def = request_kw(jsonbody, "http://127.0.0.1:11091/KwService/Kwpro")
    seg_def_obj = json.loads(seg_def['result'], encoding='utf-8')
    if 'segment' in seg_def_obj:
        seg_def_obj = seg_def_obj['segment']
    else:
        seg_def_obj = ''
    cutted_title = [x.split('/')[0] for x in seg_def_obj.split(' ')]
    for word in cutted_title:
        if word in block_words_dict:
            clearned_title = clearned_title.replace(word, '')

    jsonbody = {}
    jsonbody["title"] = clearned_title
    jsonbody["onlyseg"] = 2
    jsonbody["segmode"] = 0
    seg_def = request_kw(jsonbody, "http://127.0.0.1:11091/KwService/Kwpro")
    jsonbody["segmode"] = 3
    seg_search = request_kw(jsonbody, "http://127.0.0.1:11091/KwService/Kwpro")
    jsonbody["segmode"] = 2
    seg_bet = request_kw(jsonbody, "http://127.0.0.1:11091/KwService/Kwpro")





    seg_def_obj = json.loads(seg_def['result'], encoding='utf-8')
    seg_search_obj = json.loads(seg_search['result'], encoding='utf-8')
    seg_bet_obj = json.loads(seg_bet['result'], encoding='utf-8')

    # pingbici process  \block_words

    #seg_def_obj = '杨丽萍/0.128132 杨/0.018131 丽萍/0.067956 广场舞/0.015290 广场/0.005392 舞/0.002612 妹妹你是我的人/0.356774 妹妹/0.066029 你/0.005698 是/0.004839 我/0.006512 的/0.005079 人/0.006623 的/0.005079 鬼步舞/0 版本/0.034278 的/0.005079 心/0.012636'
    #seg_search_obj = '杨丽萍/0.128132 杨/0.018131 丽萍/0.067956 广场舞/0.015290 广场/0.005392 舞/0.002612 妹妹你是我的人/0.356774 妹妹/0.066029 你/0.005698 是/0.004839 我/0.006512 的/0.005079 人/0.006623 的/0.005079 鬼步舞/0 版本/0.034278 的/0.005079 心/0.012636'
    if 'segment' in seg_def_obj:
        seg_def_obj = seg_def_obj['segment']
    else:
        seg_def_obj = ''
    if 'segment' in seg_search_obj:
        seg_search_obj = seg_search_obj['segment']
    else:
        seg_search_obj = ''

    if 'segment' in seg_bet_obj:
        seg_bet_obj = seg_bet_obj['segment']
    else:
        seg_bet_obj = ''


    #segments = words_segment(title)
    cutted_title = [x.split('/')[0] for x in seg_def_obj.split(' ') if len(x.split('/')) == 2]
    cutted_title_weight = [x.split('/')[1] for x in seg_def_obj.split(' ') if len(x.split('/')) == 2]

    if len(cutted_title) == 0:
        return cutted_title, clearned_title, content_tag, content_dance, content_mp3, content_teacher, content_team_name, segment_def, segment_seach, segment_better

    #content_mp3 = get_mp3name(cutted_title, title)
    res = mp3_extracter.my_main('123', title, '', '', 1)
    content_mp3_ojb = json.loads(res)['tag']['profileinfo']['content_mp3']
    if 'tagname' in content_mp3_ojb:
        content_mp3 = content_mp3_ojb
    else:
        content_mp3 = {}

    # get dance tag
    content_dance = dance_type(cutted_title)
    # get teacher tag
    content_teacher = teacher_type(cutted_title, title)
    # get content tags ,is a list
    content_tag = tags_type(cutted_title, content_dance_id)

    weighted_cutted_title = []
    for ind, term in enumerate(cutted_title):
        if term in stop_words_dict_new and stop_word_flag:
            continue
        if term in synon_dict:
            synons = synon_dict[term].copy()
            synons.remove(term)
            my_tmp = "{}[{}]/{}".format(term, "|".join(synons), cutted_title_weight[ind])
        else:
            my_tmp = "{}/{}".format(term, cutted_title_weight[ind])
        weighted_cutted_title.append(my_tmp)




    cutted_title_seach = [x.split('/')[0] for x in seg_search_obj.split(' ')]
    cutted_title_seach_weight = [x.split('/')[1] for x in seg_search_obj.split(' ')]

    weighted_cutted_title_search = []
    for ind, term in enumerate(cutted_title_seach):
        if term in stop_words_dict_new and stop_word_flag:
            continue

        # if term in synon_dict:
        #     synons = synon_dict[term]
        #     synons.remove(term)
        #     my_tmp = "{}[{}]/{}".format(term, "|".join(synons), cutted_title_seach_weight[ind])
        # else:
        my_tmp = "{}/{}".format(term, cutted_title_seach_weight[ind])

        weighted_cutted_title_search.append(my_tmp)

    cutted_title_bet = [x.split('/')[0] for x in seg_bet_obj.split(' ')]
    cutted_title_bet_weight = [x.split('/')[1] for x in seg_bet_obj.split(' ')]

    weighted_cutted_title_bet = []
    for ind, term in enumerate(cutted_title_bet):
        if term in stop_words_dict_new and stop_word_flag:
            continue

        # if term in synon_dict:
        #     synons = synon_dict[term]
        #     synons.remove(term)
        #     my_tmp = "{}[{}]/{}".format(term, "|".join(synons), cutted_title_seach_weight[ind])
        # else:
        my_tmp = "{}/{}".format(term, cutted_title_bet_weight[ind])

        weighted_cutted_title_bet.append(my_tmp)

    segment_def = " ".join(weighted_cutted_title)
    segment_seach = " ".join(weighted_cutted_title_search)
    segment_bet = " ".join(weighted_cutted_title_bet)
    return cutted_title, clearned_title, content_tag, content_dance, content_mp3, content_teacher, content_team_name, segment_def, segment_seach, segment_bet


workdir = "./"
user_confusion_path = workdir + 'dict3/custom_confusion.txt'
sj_user_confusion_path = workdir + "dict3/sj_custom_confusion.txt"
plus_user_confusion_path = workdir + 'dict3/plus_custom_confusion.txt'
syn_path = workdir + "dict3/syn.txt"
mp3all_file = workdir + "hdfs_dict/mp3.all"
corrector = Corrector(user_confusion_path, sj_user_confusion_path, plus_user_confusion_path, syn_path, mp3all_file, 1)

def load_hdfs_corrector_dict():
    global corrector
    while True:
        ts = time.time()
        time.sleep(1)
        c = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        if c == "08:00:00":
            corrector = Corrector(user_confusion_path, sj_user_confusion_path, plus_user_confusion_path, syn_path,
                                  mp3all_file, 1)

t = threading.Thread(target=load_hdfs_corrector_dict,args=())
t.start()

# 纠错部分
def to_stop_word_dict(data):
    words = []
    for line in data:
        words.append(line.strip())
    mydict = set(words)
    return mydict

stop_word_path = './dict/stop_words'
stop_words_dict = to_stop_word_dict(open(stop_word_path)).union(set([' ']))
stop_words_dict_new = stop_words_dict.union(set(['广场','场舞','舞',' ']))

translate = Translate()
gfw = DFAFilter()
path="./dict/weijinci.txt"
gfw.parse(path)

block_words_dict = set()
copyright_block_words  = './dict/copyright.txt'
with open(copyright_block_words, 'r', encoding='utf-8') as copyf:
    for line in copyf:
        line = line.strip()
        block_words_dict.add(line)


##同义词字典加载，添加字段
synon_dict = {}
with open('./dict/synon', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip().split('\t')
        for ind, value in enumerate(line):
            synon_dict[line[ind]] = line

@csrf_exempt
def querytag(request):
    start = time.time()
    querytitle = ""
    if request.method == "POST":
        querytitle = request.POST.get('title', '')
        search_type = request.POST.get('search_type', '')
    elif request.method == "GET":
        querytitle = request.GET.get('title', '')
        search_type = request.GET.get('search_type', '')
    try:
        result = {}
        result['search_type'] = search_type
        request_info = {}

        querytitle = translate.ToSimplifiedChinese(querytitle)
        content = re.sub("[^a-zA-Z0-9\u4e00-\u9fa5]+", "", querytitle)
        if len(content.strip())==0:
            result['code'] = 0
            responsejson = json.dumps({'tag': result}, ensure_ascii=False)
            logging.info("Response:" + responsejson)

            return HttpResponse(responsejson)
        request_info['query'] = querytitle

        # dfa 清除违禁词
        querytitle = gfw.filter(querytitle)
        requestjson = json.dumps(request_info, ensure_ascii=False)
        logging.info("Request:" + requestjson)
        cutted_title, clearned_title, content_tag, content_dance, content_mp3, content_teacher, content_team_name, segment_def, segment_seach, segment_better = process_query(querytitle)

        ori = {}
        ori['ori_query'] = clearned_title
        ori['content_tag'] = [dict(t) for t in {tuple(d.items()) for d in content_tag}]
        ori['content_dance'] = content_dance
        ori['content_mp3'] = content_mp3
        ori['content_teacher'] = content_teacher
        ori['content_team_name'] = content_team_name
        ori['segment_def'] = segment_def
        # synonym;

        ori['segment_seach'] = segment_seach
        ori['segment_better'] = segment_better
        correct = {}

        #querytitle2, result_type= td.compare(querytitle, False)

        #segment_def = [x.split('/') for x in segment_def.split()]
        querytitle2, result_type = corrector.get_newquery_byseg_norm(querytitle, None, None, cutted_title, None)

        if querytitle2 == querytitle:
            result['original'] = ori
            result['code'] = 1
        else:
            cutted_title, clearned_title, content_tag, content_dance, content_mp3, content_teacher, content_team_name, segment_def, segment_seach, segment_better = process_query(
                querytitle2)
            correct['cor_query'] = querytitle2
            correct['content_tag'] = [dict(t) for t in {tuple(d.items()) for d in content_tag}]
            correct['content_dance'] = content_dance
            correct['content_mp3'] = content_mp3
            correct['content_teacher'] = content_teacher
            correct['content_team_name'] = content_team_name
            correct['segment_def'] = segment_def
            correct['segment_seach'] = segment_seach
            correct['segment_better'] = segment_better
            result['original'] = ori
            result['correct'] = correct
            result['code'] = 1
        responsejson = json.dumps({'tag': result}, ensure_ascii=False)
        logging.info("Response:" + responsejson)
        end = time.time()
        logging.info("Time spent: " + str(end-start))
        return HttpResponse(responsejson)
    except Exception as e:
        logging.error("querytag exception: " + e)
