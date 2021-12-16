
import sys
import math

def statis_df(file1):

    query_dict = {}
    df_dict0 = {}
    df_dict1 = {}
    df_dict2 = {}
    df_dict3 = {}

    cc =0
    dd =0

    co_show = {}
    co_show_sum = {}
    re_co_show_sum = {}
    with open(file1,"r") as f0:
        for line in f0:
            line = line.strip()
            if line.startswith("NULL"):continue
            tokens = line.split('\t')
            if len(tokens)!=5:continue
            query = tokens[0]
            pv = int(tokens[1])
            wordlist0 = tokens[2].split(" ")
            wordlist1 = tokens[3].split(" ")
            wordlist2 = tokens[4].split(" ")

            query_dict[query] = pv

            for w in wordlist0:
                if w not in df_dict0:
                    df_dict0[w] = 1
                else:
                    df_dict0[w] +=1

            for w in wordlist1:
                if w not in df_dict1:
                    df_dict1[w] = 1
                else:
                    df_dict1[w] +=1

            for w in wordlist0:
                if w not in df_dict2:
                    df_dict2[w] = pv
                else:
                    df_dict2[w] +=pv

            for w in wordlist1:
                if w not in df_dict3:
                    df_dict3[w] = pv
                else:
                    df_dict3[w] +=pv

            wordlist3 = []
            for i, wordi in enumerate(wordlist2):
                subtokeni = wordi.split(":")
                if len(subtokeni)!=3:continue
                wordlist3.append(subtokeni)

            for i, subtokeni in enumerate(wordlist3):

                wi = subtokeni[0]
                w_fromi = int(subtokeni[1])
                w_toi = int(subtokeni[2])
                for j, subtokenj in enumerate(wordlist3):
                    if j>i:
                        wj = subtokenj[0]
                        w_fromj = int(subtokenj[1])
                        w_toj = int(subtokenj[2])
                        if w_fromi>=w_fromj and w_toi<=w_toj:
                            if wj not in co_show:
                                co_show[wj] = {}
                            if wi not in co_show[wj]:
                                co_show[wj][wi] = 1
                            else:
                                co_show[wj][wi] +=1
                            if wj not in co_show_sum:
                                co_show_sum[wj] = 1
                            else:
                                co_show_sum[wj] +=1
                            if wi not in re_co_show_sum:
                                re_co_show_sum[wi] = 1
                            else:
                                re_co_show_sum[wi] += 1

            cc += 1
            dd += pv
            if cc % 100000 == 0:
                print(cc / 10000, "w")

    fw = open(file1+".df0", "w")
    for (w,df) in sorted(df_dict0.items(), key= lambda k:k[1], reverse=False):
        outline = str(w)+'\t'+str(df)+"\t"+str(math.log(cc/df))
        fw.write(outline+"\n")
    fw.close()

    fw = open(file1+".df1", "w")
    for (w,df) in sorted(df_dict1.items(), key= lambda k:k[1], reverse=False):
        outline = str(w)+'\t'+str(df)+"\t"+str(math.log(cc/df))
        fw.write(outline+"\n")
    fw.close()

    fw = open(file1+".df2", "w")
    for (w,df) in sorted(df_dict2.items(), key= lambda k:k[1], reverse=False):
        outline = str(w)+'\t'+str(df)+"\t"+str(math.log(dd/df))
        fw.write(outline+"\n")
    fw.close()

    fw = open(file1+".df3", "w")
    for (w,df) in sorted(df_dict3.items(), key= lambda k:k[1], reverse=False):
        outline = str(w)+'\t'+str(df)+"\t"+str(math.log(dd/df))
        fw.write(outline+"\n")
    fw.close()

    fw = open(file1 + ".co_show", "w")
    for wj, wi_dict in co_show.items():
        sum = co_show_sum[wj]
        pv = 0
        if wj in query_dict:
            pv = query_dict[wj]
        impt_key = round(math.log(float(pv + 1)) * 1.0, 6)
        outline = str(wj)+"\t"+str(sum)+"\t"+str(pv)+"\t"+str(impt_key)+"\t"
        for wi,count in wi_dict.items():
            score = round(float(count)/sum,6)
            i_pv = 0
            if wi in query_dict:
                i_pv = query_dict[wi]
            i_sum = 0
            if wi in re_co_show_sum:
                i_sum = re_co_show_sum[wi]
            i_sum +=1
            ratio = float(count+1)/i_sum
            impt = round(math.log(float(i_pv+1))*ratio,6)
            outline +=str(wi)+":"+str(count)+":"+str(i_sum)+":"+str(round(ratio,6))+":"+str(score)+":"+str(i_pv)+":"+str(impt)+" "
        fw.write(outline.strip()+"\n")
    fw.close()


def termweight(df_file, co_show_file, query_file):
    idf = {}
    with open(df_file) as f0:
        for line in f0:
            line = line.strip()
            tokens = line.split('\t')
            if len(tokens)!=3:continue
            idf[tokens[0]] = float(tokens[2])
    co_show_dict = {}
    co_show_dict_sum = {}
    with open(co_show_file, "r") as f1:
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

    cc =0
    fw = open(query_file+".termweight", "w")
    with open(query_file) as f2:
        for line in f2:
            line = line.strip()
            if line.startswith("NULL"):continue
            tokens = line.split('\t')
            if len(tokens)!=5:continue
            query = tokens[0]
            pv = int(tokens[1])

            wordlist0 = tokens[2].split(" ")
            wordlist1 = tokens[3].split(" ")
            wordlist2 = tokens[4].split(" ")

            ## 未加入共现字典的termweight  计算 精确模式

            termweight0 = []
            sum0 = 0
            for w in wordlist0:
                if w in idf:
                    termweight0.append((w, idf[w]))
                    sum0 += idf[w]
                    # termweight[w] = idf[w]
            outline0 = ''
            for (term, weight) in termweight0:
                score = float(weight / sum0)
                outline0 += str(term) + "/" + str(round(score,4)) + " "


            ## 未加入共现字典的termweight  计算  搜索模式

            termweight = []
            sum = 0
            for w in wordlist1:
                if w in idf:
                    termweight.append((w,idf[w]))
                    sum += idf[w]
                    #termweight[w] = idf[w]
            outline = ''
            for (term, weight) in termweight:
                score = float(weight/sum)
                outline +=str(term) +"/"+ str(round(score,4))+" "


            ## 加入共现字典的termweight  计算 搜索模式

            wordlist3 = []
            for i, wordi in enumerate(wordlist2):
                subtokeni = wordi.split(":")
                if len(subtokeni) != 3: continue
                wordlist3.append(subtokeni)

            tmp_dict = {}
            for i, subtokeni in enumerate(wordlist3):

                wi = subtokeni[0]
                w_fromi = int(subtokeni[1])
                w_toi = int(subtokeni[2])
                for j, subtokenj in enumerate(wordlist3):
                    if j > i:
                        wj = subtokenj[0]
                        w_fromj = int(subtokenj[1])
                        w_toj = int(subtokenj[2])
                        if w_fromi >= w_fromj and w_toi <= w_toj:

                            if wj in co_show_dict and wi in co_show_dict[wj]:
                                v2 = co_show_dict[wj][wi]

                                if wj not in tmp_dict:
                                    tmp_dict[wj] = v2
                                else:
                                    tmp_dict[wj] += v2
                                if wi not in tmp_dict:
                                    tmp_dict[wi] = -v2
                                else:
                                    tmp_dict[wi] += -v2
            min =0
            max = 0
            for w, value in tmp_dict.items():
                if value < min:
                    min = value
                if value > max:
                    max = value
            jiange = max-min +0.0001

            term_score = []
            sum2 = 0
            for (term, weight) in termweight:
                score = float(weight/sum)
                v2 = 0
                if term in tmp_dict:
                    v2 = tmp_dict[term]
                score2 = score +score*float(v2)/jiange
                term_score.append((term,score2))
                sum2 +=score2
                #outline +=str(term) +"/"+ str(round(score,4))+" "


            #归一化
            outline2 = ""
            for (term, score) in term_score:
                score2 = float(score)/sum2
                outline2 += str(term) + "/" + str(round(score2, 4)) + " "

            fw.write(query+"\t"+outline0.strip()+"\t"+outline.strip()+"\t"+outline2.strip()+"\n")
            cc += 1

            if cc % 100000 == 0:
                print(cc / 10000, "w")
    fw.close()





if __name__ =='__main__':

    #statis_df(sys.argv[1])
    termweight(sys.argv[1], sys.argv[2], sys.argv[3])
    pass

