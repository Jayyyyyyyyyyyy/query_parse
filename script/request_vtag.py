import requests
import json

def wx_search(jsonbody):
    url = "http://127.0.0.1:9002/polls/querytag"

    #url = "http://10.42.16.15:9002/polls/querytag"
    resp1 = requests.post(url, data=jsonbody)
    return resp1.text
# query = '我想看凤凰传奇的有关荷塘月色音乐的广场舞'
# parms = {"query": query}
# result = wx_search(parms)
# print(result)

cnt = 0
rows = []
with open('order.txt', 'r', encoding='utf-8') as reader, open('segment_res1213.txt', 'w', encoding='utf-8') as writer :
    for line in reader:
        # cnt += 1
        # if cnt == 10:
        #     break
        query, pv = line.strip().split('\t')
        print(query)
        parms = {"title": query}
        result = wx_search(parms)
        print(result)
        tmpres = json.loads(result)
        writer.write(result+'\n')
# print(cnt)
#pd.DataFrame(rows,columns=['query','pku','jieba']).to_excel('top50000.xlsx', index=None)