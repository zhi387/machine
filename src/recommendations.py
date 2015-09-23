# -*- coding:utf-8 -*-
from math import sqrt

#欧几内德算法求similar{}
#s 0~1 ,1 为完全相同。
def similarDinstance(totalsample,user1,user2):
    similarsample = {}
    for item in totalsample[user1]:
        if item in totalsample[user2]:
            similarsample[item] = 1
    if len(similarsample) == 0:
        return 0
    # sumsquare= sum([t]) ,,, t = pow（a[x]-b[x],2） for x in a[] if x in b[]
    sumsquare = sum([pow(totalsample[user1][item] - totalsample[user2][item],2) for item in similarsample])
    s = 1/(1+sqrt(sumsquare))
    return s

#pearson算法求similar,,, s -1~1 1为完全一致。
def similarPearson(totalsample,user1,user2):
    similarsample = {}
    for item in totalsample[user1]:
        if item in totalsample[user2]:
            similarsample[item] = 1
    l = len(similarsample)
    if l == 0 :
        return 1
    #求和sum
    sum1 = sum([totalsample[user1][item] for item in similarsample])
    sum2 = sum([totalsample[user2][item] for item in similarsample])
    #求平方和 sumpow
    sumsq1 = sum([pow(totalsample[user1][item],2) for item in similarsample])
    sumsq2 = sum([pow(totalsample[user2][item],2) for item in similarsample])
    #求乘积和sump
    sump = sum([totalsample[user1][item]*totalsample[user2][item] for item in similarsample])
    #求pearson评价值
    num = sump - (sum1*sum2/l)
    den = sqrt((sumsq1 - pow(sum1,2)/l))*(sumsq2 - pow(sum2,2)/l)
    if den == 0:
        return 0
    s = num/den
    return s 

def similarTanimoto(totalsample,user1,user2):
    pass

#求长度l 相近样本
def rankingSample(totalsample,user,l=4,similarity=similarPearson):
    scores = [(similarity(totalsample,user,otherusers),otherusers) for otherusers in totalsample if otherusers != user]
    scores.sort()
    scores.reverse()
    return scores[0 : l]

#转换数据字典
def transformSample(totalsample):
    result = {}
    for user in totalsample:
        for item in totalsample[user]:
            result.setdefault(item,{})
            result[item][user] = totalsample[user][item]
    return result

#构造比较数据集，，，用于推荐，不用每次遍历数据字典
def calculateSample(totalsample,n=10):
    result = {}
    #翻转，以生成推荐品数据集
    totalsample = transformSample(totalsample)
    for item in totalsample:
        score =rankingSample(totalsample, item, l=n, similarity=similarPearson)
        result[item] = score
    return result

#给user推荐inall
def getRecommendationsInAll(totalsample,user,similarity=similarPearson):
    total = {}
    sumsim ={}
    for otherusers in totalsample:
        #排查推荐人
        if otherusers == user:
            continue
        sim = similarity(totalsample,user,otherusers)
        #排除相似度小于0
        if sim <= 0:
            continue
        for item in totalsample[otherusers]:
            #排查推荐人已看过或评价为0
            if item not in totalsample[user] or totalsample[user][item] == 0:
                total.setdefault(item,0)
                total[item] += totalsample[otherusers][item]*sim
                sumsim.setdefault(item,0)
                sumsim[item] += sim
    rankings = [(values/sumsim[item],item) for item,values in total.items()]
    rankings.sort()
    rankings.reverse()
    return rankings

#给user推荐incache,传入calculateSample
def getRecommendationsInCache(totalsample,calsample,user):
    scores = {}
    totals = {}
    for (item,v1) in totalsample[user].items():
        for (v2,item2) in calsample[item]:
            if item2 in totalsample[user]:
                continue
            scores.setdefault(item2,0)
            scores[item2] += v1*v2
            totals.setdefault(item2,0)
            totals[item2] += v2
    rankings = [(score/totals[item],item) for item,score in scores.items()]
    rankings.sort()
    rankings.reverse()
    return rankings