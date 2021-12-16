# -*- coding: utf-8 -*-
# 开发团队   ：开发团队
# 开发人员   ：sunjian
# 开发时间   ：2019-11-19  15:44 
# 文件名称   ：Trie.PY
# 开发工具   ：PyCharm


class TrieNode(object):
    def __init__(self):

        self.data = {}
        self.is_word = False
        self.weight = 0.0

class Trie(object):

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        """
        Inserts a word into the trie.
        :type word: str
        :rtype: void
        """
        node = self.root
        for chars in word:

            # if chars in node.data:
            #     node = node.data[chars]
            # else:
            #     node.data[chars] = TrieNode()
            child = node.data.get(chars)
            if not child:
                node.data[chars] = TrieNode()
            node = node.data[chars]
        node.is_word = True

    def insertbyweight(self, word, weight):
        """
        Inserts a word into the trie.
        :type word: str
        :rtype: void
        """
        node = self.root
        for chars in word:

            child = node.data.get(chars)
            if not child:
                node.data[chars] = TrieNode()
            node = node.data[chars]
        node.is_word = True
        node.weight = weight


    def search(self, word):
        """
        Returns if the word is in the trie.
        :type word: str
        :rtype: bool
        """
        node = self.root
        for chars in word:
            node = node.data.get(chars)
            if not node:
                return False
        return node.is_word  # 判断单词是否是完整的存在在trie树中

    def startsWith(self, prefix):
        """
        Returns if there is any word in the trie that starts with the given prefix.
        :type prefix: str
        :rtype: bool
        """
        node = self.root
        for chars in prefix:
            node = node.data.get(chars)
            if not node:
                return False
        return True

    def get_start(self, prefix):
        """
          Returns words started with prefix
          :param prefix:
          :return: words (list)
        """

        def get_key(pre, pre_node):
            word_list = []
            if pre_node.is_word:
                word_list.append(pre)
            for x in pre_node.data.keys():
                word_list.extend(get_key(pre + str(x), pre_node.data.get(x)))
            return word_list

        words = []
        if not self.startsWith(prefix):
            return words
        # if self.search(prefix):
        #     words.append(prefix)
        #     return words
        node = self.root
        for chars in prefix:
            node = node.data.get(chars)
        return get_key(prefix, node)

    def get_start_byweight(self, prefix):
        """
          Returns words started with prefix
          :param prefix:
          :return: words (list)
        """

        def get_key(pre, pre_node):
            word_list = []
            if pre_node.is_word:
                word_list.append((pre,pre_node.weight))
            for x in pre_node.data.keys():
                word_list.extend(get_key(pre + str(x), pre_node.data.get(x)))
            return word_list

        words = []
        if not self.startsWith(prefix):
            return words
        # if self.search(prefix):
        #     words.append(prefix)
        #     return words
        node = self.root
        for chars in prefix:
            node = node.data.get(chars)
        return get_key(prefix, node)

    def get_end_byweight2(self, suffix):
        """
          Returns words started with prefix
          :param prefix:
          :return: words (list)
        """

        # def get_key(pre, pre_node, historylist):
        #     word_list = []
        #     if pre_node.is_word:
        #         word_list.append((pre,pre_node.weight))
        #     for x in pre_node.data.keys():
        #         word_list.extend(get_key(pre + str(x), pre_node.data.get(x)))
        #     return word_list

        words = []
        if not self.startsWith(suffix):
            return words
        # if self.search(prefix):
        #     words.append(prefix)
        #     return words
        node = self.root

        pre = ""
        for i,chars in enumerate(suffix):
            node = node.data.get(chars)
            if node and node.is_word:
                words.append(suffix[:i+1])


        return words

