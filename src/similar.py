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
    s = num/den
    return s 

def similarTanimoto(totalsample,user1,user2):
    pass

def rankingSample(totalsample,user,l=4,similarity=similarPearson):
    scores = [(similarity(totalsample,user,otherusers),otherusers) for otherusers in totalsample if otherusers != user]
    scores.sort()
    scores.reverse()
    return scores[0 : l]
    
