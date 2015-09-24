# -*-coding:utf-8-*-
from math import sqrt
import Image
import ImageDraw
import random
#pearson 紧密度
def pearson(v1,v2):
    #求和
    sum1 = sum(v1)
    sum2 = sum(v2)
    #求平方和
    sumsq1 = sum([pow(v,2) for v in v1])
    sumsq2 = sum([pow(v,2) for v in v2])
    #求乘积和
    sump = sum([v1[i]*v2[i] for i in range(len(v1))])
    #求紧密度r 
    num = sump - (sum1*sum2/len(v1))
    den = sqrt((sumsq1 - pow(sum1,2)/len(v1))*(sumsq2 - pow(sum2,2)/len(v2)))
    if den == 0:
        return 0
    # r 0~1~2 紧密度越大，r越小
    return 1-num/den

class cluster:
    def __init__(self,vec,left=None,right=None,distance=0.0,cid=None):
        self.left = left
        self.right = right
        self.vec = vec
        self.cid = cid
        self.distance = distance

def hCluster(rows,distance=pearson):
    distances = {}
    currentclustid = -1
    #初始化
    clust = [cluster(rows[i],cid=i) for i in range(len(rows))]
    while len(clust)>1:
        lowestpair = (0,1)
        closest = distance(clust[0].vec,clust[1].vec)
        #遍历
        for i in range(len(clust)):
            for j in range(i+1,len(clust)):
                if (clust[i].cid,clust[j].cid) not in distances:
                    distances[clust[i].cid,clust[j].cid] = distance(clust[i].vec,clust[j].vec)
                d = distances[(clust[i].cid,clust[j].cid)]
                if d<closest:
                    closest = d
                    lowestpair = (i,j)
        #计算评价值
        mergevec = [(clust[lowestpair[0]].vec[i]+clust[lowestpair[1]].vec[i])/2.0 for i in range(len(clust[0].vec))]
        #建立新的聚类
        newcluster = cluster(mergevec,left=clust[lowestpair[0]],right=clust[lowestpair[1]],distance=closest,cid=currentclustid)
        currentclustid-=1
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)
    return clust[0]

#print clust
def printClust(clust,labels=None,n=0):
    #定义缩进
    for n in range(n):print '    ',
    if clust.cid < 0:
        #负数为分支
        print '-'
    else:
        if labels==None:
            print clust.cid
        else:
            print labels[clust.cid]
    #打印子树
    if clust.left!=None:
        printClust(clust.left,labels=labels,n=n+1)
    if clust.right!=None:
        printClust(clust.right,labels=labels,n=n+1)
    
def getHeight(clust):
    if clust.left==None and clust.right==None:
        return 1
    return getHeight(clust.left)+getHeight(clust.right)

def getDepth(clust):
    if clust.left==None and clust.right==None:
        return 0
    return max(getDepth(clust.left),getDepth(clust.right))+clust.distance

def drawDendrogram(clust,labels,jpeg='clusters.jpg'):
    #
    h=getHeight(clust)*20
    w=800
    depth=getDepth(clust)
    #
    scaling=float(w-150)/depth
    #
    img = Image.new('RGB',(w,h),(255,255,255))
    draw = ImageDraw.Draw(img)
    draw.line((0,h/2,10,h/2),fill=(255,0,0))
    #
    drawNode(draw,clust,10,(h/2),scaling,labels)
    img.save(jpeg,'JPEG')

def drawNode(draw,clust,x,y,scaling,labels):
    if clust.cid<0:
        h1=getHeight(clust.left)*20
        h2=getDepth(clust.right)*20
        top=y-(h1+h2)/2
        bottom=y+(h1+h2)/2
        #
        l1=clust.distance*scaling
        #
        draw.line((x,top+h1/2,x,bottom-h2/2),fill=(255,0,0))
        #
        draw.line((x,top+h1/2,x+l1,top+h1/2),fill=(255,0,0))
        #
        draw.line((x,bottom-h2/2,x+l1,bottom-h2/2),fill=(255,0,0))
        #
        drawNode(draw,clust.left,x+l1,top+h1/2,scaling,labels)
        drawNode(draw,clust.right,x+l1,bottom-h2/2,scaling,labels)
    else:
        draw.text((x+5,y-7),labels[clust.cid],(0,0,0,))

def kCluster(rows,distance=pearson,k=4):
    #每个点的最大最小值
    ranges=[(min([row[i] for row in rows]),max([row[i] for row in rows])) for i in range(len(rows[0]))]
    #随机创建k个中心点
    clusters=[[random.random()*(ranges[i][1]-ranges[i][0])+ranges[i][0] for i in range(len(rows[0]))] for j in range(k)]
    lastmatches = None
    for t in range(100):
        print 'Iteration %d' % t
        bestmatches=[[] for i in range(k)]
        #每行找中心点
        for j in range(len(rows)):
            row=rows[j]
            bestmatch=0
            for i in range(k):
                d=distance(clusters[i],row)
                if d<distance(clusters[bestmatch],row):
                    bestmatch=i
            bestmatches[bestmatch].append(j)
        if bestmatches==lastmatches:
            break
        lastmatches=bestmatches
        for i in range(k):
            avgs=[0.0]*len(rows[0])
            if len(bestmatches[i])>0:
                for rowid in bestmatches[i]:
                    for m in range(len(rows[rowid])):
                        avgs[m]+=rows[rowid][m]
                    for j in range(len(avgs)):
                        avgs[j]/=len(bestmatches[i])
                    clusters[i]=avgs
    return bestmatches

def scaleDown(data,distance=pearson,rate=0.01):
    l=len(data)
    #真实距离
    realdist=[[distance(data[i],data[j]) for j in range(l)]for i in range(l)]
    #随机初始化
    loc=[[random.random(),random.random()]for i in range(l)]
    fakedist=[[0.0 for j in range(l)]for i in range(l)]
    lasterror=None
    m=1
    while m < 10000:
        m+=1
        #投影后距离
        for i in range(l):
            for j in range(l):
                fakedist[i][j]=sqrt(sum([pow(loc[i][x]-loc[j][x],2)for x in range(len(loc[i]))]))
        #移动节点
        grad=[[0.0,0.0]for i in range(l)]
        totalerror=0
        for k in range(l):
            for j in range(l):
                if realdist[j][k]==0:
                    continue
                #目标距离！=实际距离，差值百分比
                errorterm=(fakedist[j][k]-realdist[j][k])/realdist[j][k]
                #按比例移动
                grad[k][0]+=((loc[k][0]-loc[j][0])/fakedist[j][k])*errorterm
                grad[k][0]+=((loc[k][1]-loc[j][1])/fakedist[j][k])*errorterm
                totalerror+=abs(errorterm)
        print totalerror
        if lasterror and lasterror<totalerror:
            break
        lasterror=totalerror
        #
        for k in range(l):
            loc[k][0]-=rate*grad[k][0]
            loc[k][1]-=rate*grad[k][1]
    return loc  

def  draw2d(data,labels,jpeg='mds2d.jpg'):
    img=Image.new('RGB', (800,600), (255,255,255))
    draw=ImageDraw.Draw(img)
    for i in range(len(data)):
        x=(data[i][0]+0.5)*400
        y=(data[i][1]+0.5)*300
        draw.text((x,y), labels[i],(0,0,0))
    img.save(jpeg,'JPEG')
        