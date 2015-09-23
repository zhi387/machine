# -*-coding:utf-8-*-
from math import sqrt
import Image
import ImageDraw
#pearson ���ܶ�
def pearson(v1,v2):
    #���
    sum1 = sum(v1)
    sum2 = sum(v2)
    #��ƽ����
    sumsq1 = sum([pow(v,2) for v in v1])
    sumsq2 = sum([pow(v,2) for v in v2])
    #��˻���
    sump = sum([v1[i]*v2[i] for i in range(len(v1))])
    #����ܶ�r 
    num = sump - (sum1*sum2/len(v1))
    den = sqrt((sumsq1 - pow(sum1,2)/len(v1))*(sumsq2 - pow(sum2,2)/len(v2)))
    if den == 0:
        return 0
    # r 0~1~2 ���ܶ�Խ��rԽС
    return 1-num/den

class cluster:
    def __init__(self,vec,left=None,right=None,distance=0.0,cid=None):
        self.left = left
        self.right = right
        self.vec = vec
        self.cid = cid
        self.distance = distance

def hculster(rows,distance=pearson):
    distances = {}
    currentclustid = -1
    #��ʼ��
    clust = [cluster(rows[i],cid=i) for i in range(len(rows))]
    while len(clust)>1:
        lowestpair = (0,1)
        closest = distance(clust[0].vec,clust[1].vec)
        #����
        for i in range(len(clust)):
            for j in range(i+1,len(clust)):
                if (clust[i].cid,clust[j].cid) not in distances:
                    distances[clust[i].cid,clust[j].cid] = distance(clust[i].vec,clust[j].vec)
                d = distances[(clust[i].cid,clust[j].cid)]
                if d<closest:
                    closest = d
                    lowestpair = (i,j)
        #��������ֵ
        mergevec = [(clust[lowestpair[0]].vec[i]+clust[lowestpair[1]].vec[i])/2.0 for i in range(len(clust[0].vec))]
        #�����µľ���
        newcluster = cluster(mergevec,left=clust[lowestpair[0]],right=clust[lowestpair[1]],distance=closest,cid=currentclustid)
        currentclustid-=1
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)
    return clust[0]

#print clust
def printClust(clust,labels=None,n=0):
    #��������
    for n in range(n):print '    ',
    if clust.cid < 0:
        #����Ϊ��֧
        print '-'
    else:
        if labels==None:
            print clust.cid
        else:
            print labels[clust.cid]
    #��ӡ����
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
    