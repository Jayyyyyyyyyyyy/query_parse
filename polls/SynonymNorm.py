# -*- coding: utf-8 -*-
import re
import logging

__all__=["SynonymNorm"]

class Config:
    CN_NUM = {
        '〇': 0,
        '一': 1,
        '二': 2,
        '三': 3,
        '四': 4,
        '五': 5,
        '六': 6,
        '七': 7,
        '八': 8,
        '九': 9,
    
        '零': 0,
        '壹': 1,
        '贰': 2,
        '叁': 3,
        '肆': 4,
        '伍': 5,
        '陆': 6,
        '柒': 7,
        '捌': 8,
        '玖': 9,

        # '两': 2,
    }
    NUM = {
        '0':0,
        '1':1,
        '2':2,
        '3':3,
        '4':4,
        '5':5,
        '6':6,
        '7':7,
        '8':8,
        '9':9,
    }

    CN_UNIT = {
        '十': 10,
        '拾': 10,
        '百': 100,
        '佰': 100,
    }

    WRONG_NUM0 = {
        'o':'0',
        'O':'0'
    }
    WRONG_NUM2 = {
        'z':'2',
        'Z':'2'
    }
    BD_DICT = {
        '0':'零',
        '1':'一',
        '2':'二',
        '3':'三',
        '4':'四',
        '5':'五',
        '6':'六',
        '7':'七',
        '8':'八',
        '9':'九',
        '10':'十',

        'o':'零',
        'O':'零',
        'z':'二',
        'Z':'二',
    }

    PATTERN_N = '[0-9]+[oOzZ]+[步套式节拍段度月岁个秒]|[0-9]+[oOzZ]+分钟|[0-9]+[oOzZ]+分解' # oO:分钟，分解，度，步，分，节，个，拍，套，岁，式 ,月,秒 ; zZ:步，年，岁，式
    PATTERN_S = '[0-9零壹贰叁肆伍陆柒捌玖貮〇一二三四五六七八九oOzZ]+年'
    PATTERN =  '[0-9oOzZ零壹贰叁肆伍陆柒捌玖貮〇一二三四五六七八九十拾百佰]+[步套式节秒岁年]|[0-9oOzZ零壹贰叁肆伍陆柒捌玖貮〇一二三四五六七八九十拾百佰]+分钟|[0-9oOzZ零壹贰叁肆伍陆柒捌玖貮〇一二三四五六七八九十拾百佰]+分解|第[0-9oOzZ零壹贰叁肆伍陆柒捌玖貮〇一二三四五六七八九十拾百佰]+段'
    PATTERN_K = '[0-9]+[零壹贰叁肆伍陆柒捌玖貮〇一二三四五六七八九十拾百佰]+[步式]'
    PATTERN_DJ = '[0-9oOzZ]+段锦'

    '''
    TODO:长尾的 数字 + 段锦 ——> 中文数字 + 段锦
    '''


class SynonymNorm:
    def __init__(self, pattern=Config.PATTERN, pattern_n=Config.PATTERN_N, pattern_s=Config.PATTERN_S, pattern_k=Config.PATTERN_K, \
        pattern_dj=Config.PATTERN_DJ, cn_to_num_dict='cn_to_num_dict', logger=''):
        self.__cn_to_num_dict = cn_to_num_dict
        self.__pattern = pattern
        self.__pattern_n = pattern_n
        self.__pattern_s = pattern_s
        self.__pattern_k = pattern_k
        self.__pattern_dj = pattern_dj
        self.__logger = self.__set_logger() if not logger else logger

    def __set_logger(self):
        logger = logging.getLogger()
        logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(levelname)s - %(message)s')
        return logger
    
    def _num2cn(self, sub):
        new_sub = sub
        try:
            if len(sub) == 1:
               new_sub = Config.BD_DICT[sub]
            if len(sub) == 2:
                # 只处理30以內的段锦
                if sub[0]  in ['1', '2']:
                    if sub[1] in ['0', 'o', 'O']:
                        if sub[0] == '1':
                            new_sub = '十'
                        else:
                            new_sub = Config.BD_DICT[sub[0]] + '十'
                    else:
                        if sub[0] == '1':
                            new_sub = '十' + Config.BD_DICT[sub[1]] 
                        else:
                            new_sub = Config.BD_DICT[sub[0]] + '十' + Config.BD_DICT[sub[1]]
        except Exception as e:
            self.__logger.debug('Illegal format sub:%s, %s' % (sub, str(e)))
            return sub
        return new_sub
    
    def _cn2num(self, sub):
        '''
        process words like:
        玖拾二 ——> 92 or 玖二 ——>92
        '''
        new_sub = sub

        try:
            if len(sub) == 1:
                # 百 + keywords 不处理
                
                if sub in ['十', '拾']:
                    new_sub = '10'
                elif sub in ['百', '佰']:
                    return new_sub
                else:
                    new_sub = str(Config.CN_NUM[sub])
            
            if len(sub) == 2:
                if not any([s in Config.CN_UNIT for s in sub]):
                    new_sub = str(Config.CN_NUM[sub[0]]) + str(Config.CN_NUM[sub[1]])
                elif sub.startswith('十') or sub.startswith('拾'):
                    new_sub = '1' + str(Config.CN_NUM[sub[1]])
                elif sub.startswith('零'):
                    new_sub = '0' + str(Config.CN_NUM[sub[1]])
                else:
                    if sub.endswith('十') or sub.endswith('拾'):
                        new_sub =  str(Config.CN_NUM[sub[0]]*10)
                    if sub.endswith('百') or sub.endswith('佰'):
                        if sub[0] in ['一', '壹']: # 大于100的不处理
                            new_sub =  str(Config.CN_NUM[sub[0]]*100)
            if len(sub) == 3:
                if sub[1] == '十' or sub[1] == '拾':
                    if sub[0] == '零' or sub[0] == '十' or sub[0] == '拾' or sub[2] == '十' or sub[2] == '拾':
                        self.__logger.debug('Illegal format sub:%s ' % sub)
                        return sub
                    else:
                        new_sub = str(Config.CN_NUM[sub[0]]) + str(Config.CN_NUM[sub[2]])
        except Exception as e:
            self.__logger.debug('Illegal format sub:%s, %s' % (sub, str(e)))
            return sub
        return new_sub

    def _parse_year(self, sub):
        '''
        only parse [1900，2099]
        '''
        new_sub = sub
        all_maps = dict(Config.NUM, **Config.CN_NUM)
        if all([x in all_maps.keys() for x in sub]):
            if sub.startswith('壹') or sub.startswith('一') or sub.startswith('1'):
                if sub[1] in ['玖', '九', '9']:
                    new_sub = ''.join([str(all_maps[sub[i]]) for i in range(len(sub))])
            if sub.startswith('贰') or sub.startswith('二') or sub.startswith('2'):
                if sub[1] == '零' or sub[1] == '0':
                    new_sub = ''.join([str(all_maps[sub[i]]) for i in range(len(sub))])
        return new_sub

    def _correct_num(self, sub, query, num):
        '''
        correct num of 0:
        4o岁 ——>40岁 or 4O岁 ——>40岁
        3z步 ——> 32步
        '''
        new_sub = sub
        # correct 0
        if num == 0:
            keys = Config.WRONG_NUM0.keys()
            for key in keys:
                if key in new_sub:
                    new_sub = re.sub(key, Config.WRONG_NUM0[key], new_sub)
        if num == 2:
            keys = Config.WRONG_NUM2.keys()
            for key in keys:
                if key in new_sub:
                    new_sub = re.sub(key, Config.WRONG_NUM2[key], new_sub)
        return re.sub(sub, new_sub, query)


    def _process(self, sub, query, start):
        ret_query = query
        new_sub = sub
        # 处理 分钟 分解：
        if '分钟' in sub or '分解' in sub:
            new_sub = self._cn2num(sub[:-2])
            # if '分钟' in sub:
            # 只处理60以內分钟、秒数据。比如“三十分钟” -> "30分钟" 
                # try:
                #     new_sub = int(new_sub)
                #     if new_sub > 60:
                #         new_sub = sub[:-2]
                #     else:
                #         new_sub = str(new_sub)
                # except:
                #     pass
            new_sub = new_sub + sub[-2:]
        # 处理年
        elif '年' in sub:
            if len(sub) == 5:
                new_sub = self._parse_year(sub[:-1])
                new_sub = new_sub + sub[-1:]
        # 处理第xx段
        elif sub.startswith('第'):
            new_sub = self._cn2num(sub[1:-1])
            new_sub = sub[:1] + new_sub + sub[-1:]
        # 处理 xx段锦
        elif sub.endswith('段锦'):
            new_sub = self._num2cn(sub[:-2])
            new_sub = new_sub + sub[-2:]
        
        # 处理 秒 [套、式、节、岁、步]
        else:
            new_sub = self._cn2num(sub[:-1])
            # if '秒' in sub:
            # # 只处理60以內分钟、秒数据。比如“三十分钟” -> "30分钟" 
            #     try:
            #         new_sub = int(new_sub)
            #         if new_sub > 60:
            #             new_sub = sub[:-1]
            #         else:
            #             new_sub = str(new_sub)
            #     except:
            #         pass
            new_sub = new_sub + sub[-1:]
        
        ret_query = ret_query[:start] + re.sub(sub, new_sub, ret_query[start:], count=1)
        return ret_query

    def _process_by_dic(self, query):
        word_to_num = {}
        with open(self.__cn_to_num_dict, 'r', encoding='utf-8') as f:
            for line in f:
                tmp = line.strip().split(',')
                word_to_num[tmp[0]] = tmp[1]
        for key in word_to_num.keys():
            if key in query:
                query = re.sub(key, word_to_num[key], query)
        
        return query

    def _process_wrong_num_n(self, pattern, query):
        ret_query = query
        # correct wrong num 0 or 2 before key words:
        zero_tmp = re.findall(pattern, query)
        for zero in set(zero_tmp):
            ret_query = self._correct_num(zero, ret_query, 0)
        two_tmp = re.findall(pattern, query)
        for two in set(two_tmp):
            ret_query = self._correct_num(two, ret_query, 2)
        return ret_query

    def _process_wrong_num_s(self, pattern, query):
        ret_query = query
        # correct wrong num 0 or 2 before 年, maxlength=5：
        zero_tmp = re.findall(pattern, query)
        for zero in set(zero_tmp):
            if len(zero) <= 5:
                ret_query = self._correct_num(zero, ret_query, 0)
        two_tmp = re.findall(pattern, ret_query)
        for two in set(two_tmp):
            if len(two) <= 5:
                ret_query = self._correct_num(two, ret_query, 2)
        return ret_query

    def _process_by_seg(self, pattern, query, seg_query):
        # 特殊处理 ”数字 + 中文数字 + 关键字”
        ret_query = query
        sp_tmp = re.findall(pattern, ret_query)
        start = ret_query.find(sp_tmp[0]) if sp_tmp else ''
        tokens = list(seg_query.split(' '))
        if '步' in tokens or '式' in tokens:
            for sp_sub in sp_tmp:
                new_sub = sp_sub
                print(sp_sub)
                sp_sub = re.sub('[0-9]+', '', sp_sub)
                new_sub = self._cn2num(sp_sub[:-1]) + sp_sub[-1:]
                print(new_sub)
                ret_query = ret_query[:start] + re.sub(sp_sub, new_sub, ret_query[start:], count=1)
                start += len(sp_sub)
                print(ret_query)
        return ret_query
    
    def _process_by_song(self, query, seg_query, song_list=['三月三', '九月九']):
        ret_query = query
        for song in song_list:
            if song in seg_query.split(' '):
                sp_subs = re.findall(song+'[0-9零壹贰叁肆伍陆柒捌玖貮〇一二三四五六七八九十拾百佰]+步', ret_query)
                for sp_sub in sp_subs:
                    new_sub = sp_sub[:3] + self._cn2num(sp_sub[3:-1]) + sp_sub[-1:]
                    ret_query = re.sub(sp_sub, new_sub, ret_query, count=1)
        return ret_query
    
    def _convert(self, old_query, query, seg_query, base_key, target_key, flag=True):
        ret_query = query
        if target_key in list(seg_query.split(' ')):
            tmp = seg_query
            s_index = 0
            l = len(target_key)
            while tmp.find(target_key, s_index) != -1:
                s_index = tmp.find(target_key, s_index)
                s_index_q = s_index - tmp[:s_index].count(' ')
                tmp_index = s_index_q
                while True:
                    if ret_query[tmp_index] == old_query[s_index_q]:
                        s_index_q = tmp_index
                        break
                    else:
                        tmp_index -= 1
                if seg_query.find(target_key+' 十', s_index) != -1 and flag == True:
                    if ret_query.find(base_key, s_index_q, s_index_q+l) != -1:
                        ret_query = ret_query[:s_index_q] + re.sub(base_key, target_key+'1', ret_query[s_index_q:], count=1)
                else:
                    if ret_query.find(base_key, s_index_q, s_index_q+l+1) != -1:
                        ret_query = ret_query[:s_index_q] + re.sub(base_key, target_key, ret_query[s_index_q:], count=1)
                s_index += l
        return ret_query

    def _process_by_special(self, old_query, query, seg_query):
        ret_query = query

        # 矫正特别的关键字：一拖二， 一拖三， 慢三
        ret_query = self._convert(old_query, ret_query, seg_query, '一拖2', '一拖二')
        ret_query = self._convert(old_query, ret_query, seg_query, '一拖3', '一拖三')
        ret_query = self._convert(old_query, ret_query, seg_query, '慢3', '慢三')
        if re.findall('[一拖\s[23]', seg_query):
           #原始的一拖2，一拖3转换成中文的二三，flag专门为这里设计，防止：一拖2十四步踩曾峰——>一拖二114步踩曾峰
           seg_query = re.sub('一拖\s2', '一拖二', seg_query)
           seg_query = re.sub('一拖\s3', '一拖三', seg_query)
           ret_query = self._convert(old_query, ret_query, seg_query, '一拖2', '一拖二', False)
           ret_query = self._convert(old_query, ret_query, seg_query, '一拖3', '一拖三', False)

        return ret_query

    def transform(self, query, seg_query):
        self.__logger.debug('process query:%s' % query)
        ret_query = query
        if len(list(seg_query.split(' '))) <= 1:
            return ret_query

        self.__logger.debug('correct wrong num of 0 and 2……')
        # correct wrong num 0 and 2 near by key words:
        ret_query = self._process_wrong_num_n(self.__pattern_n, query)
        
        # correct wrong num 0 and 2 surrounded by number: 2oo2年
        ret_query = self._process_wrong_num_s(self.__pattern_s, query)
        
        #process special items by dicrt key words like: 三月二十十二步
        ret_query = self._process_by_dic(ret_query)

        ret_query = self._process_by_song(ret_query, seg_query)

        # process nomal re pattern, num <= 100 can be transformed
        self.__logger.debug('process normal pattern')
        sub_tmp = re.findall(self.__pattern, ret_query)
        start = ret_query.find(sub_tmp[0]) if sub_tmp else ''
        for sub in sub_tmp:
            ret_query = self._process(sub, ret_query, start)
            start += len(sub)
        
        # process 段锦
        self.__logger.debug('process 段锦 pattern')
        sub_dj = re.findall(self.__pattern_dj, ret_query)
        start_dj = ret_query.find(sub_dj[0]) if sub_dj else ''
        for s_dj in sub_dj:
            ret_query = self._process(s_dj, ret_query, start_dj)
            start_dj += len(s_dj)

        # process ”数字 + 中文数字 + 步|式”
        self.__logger.debug('process special pattern')
        ret_query = self._process_by_seg(self.__pattern_k, ret_query, seg_query)

        # 根据关键字处理:一拖二、一拖三、慢三
        self.__logger.debug('process special keywords')
        ret_query = self._process_by_special(query, ret_query, seg_query)
        self.__logger.debug('process done! the new_query is:%s' % ret_query)
        return ret_query


if __name__ == "__main__":
    norm = SynonymNorm()
    print(norm.transform('健身操闫密队二O一八年第三套', '健身操 闫密 队 二 o 一八 年 第三套'))

    # def trans(input_file='query_with_num_norm', output_file='query_with_num_norm_new'):
    #     with open(input_file, 'r', encoding='utf-8') as fi:
    #         lines = fi.readlines()

    #     with open(output_file, 'w+', encoding='utf-8') as fo:
    #         fo.write('pv' + '\t' + 'query' + '\t' + 'qc_query' + '\t' + 'norm_query' + '\t' + 'segline' + '\n')
    #         for line in lines:
    #             line = line.strip().split('\t')
    #             pv = line[0]
    #             query = line[1]
    #             segline = line[4]
    #             qc_query = line[2]

    #             norm_query = norm.transform(query, segline)
    #             fo.write(str(pv) + '\t' + query + '\t' + qc_query + '\t' + norm_query + '\t' + segline + '\n')
    
    # trans()

