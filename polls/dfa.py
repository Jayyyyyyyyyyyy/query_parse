# -*- coding: utf-8 -*-
# @Author    : Chenxi Jiang
# @Time      : 2019/11/28 7:52 PM
# @File      : dfa.py
# @Software  : PyCharm
# @Company   : Xiao Tang

import json
import time
time1=time.time()

# DFA算法
class DFAFilter():
    def __init__(self):
        self.keyword_chains = {}
        self.delimit = '\x00'

    def add(self, keyword):
        keyword = keyword.lower()
        chars = keyword.strip()
        if not chars:
            return
        level = self.keyword_chains
        for i in range(len(chars)):
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def parse(self, path):
        with open(path,encoding='utf-8') as f:
            for keyword in f:
                self.add(str(keyword).strip())

    def filter(self, message, repl=""):
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret.append(repl * step_ins)
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])
            start += 1
        return ''.join(ret)


if __name__ == "__main__":
    gfw = DFAFilter()
    path="/Users/tangdou1/PycharmProjects/poem/query_parse/dict/weijinci.txt"
    gfw.parse(path)
    tmp = []
    with open(path, encoding='utf-8') as f:
        for keyword in f:
            tmp.append(str(keyword).strip())
    with open('querydata','r',encoding='utf-8') as read,open('res', 'w', encoding='utf-8') as w:
        for line in read:
            text,pv = json.loads(line.strip())
            if text == None:
                continue
            result = gfw.filter(text)
            if text != result:
                for word in tmp:
                    if word in text:
                        myword=word
                        break

                newl = "{}\t{}\t{}\n".format(text, pv,myword)
                w.write(newl)
            # print(text)
            # print(result)
            # time2 = time.time()
            # print('总共耗时：' + str(time2 - time1) + 's')
