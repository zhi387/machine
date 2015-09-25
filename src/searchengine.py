# -*- coding=utf-8 -*- 
import urllib2
import sqlite3
from BeautifulSoup import BeautifulSoup
from urlparse import urljoin
import re

ignorewords={''}

class crawler:
    def __init__(self,dbname):
        self.con = sqlite3.connect(dbname)
    
    def __del__(self):
        self.con.close()
    
    def dbCommit(self):
        self.con.commit()
    
    def getEntryid(self,table,field,value,createnew=True):
        cur=self.con.execute("select rowid from %s where %s='%s'" % (table,field,value))
        res=cur.fetchone()
        if res==None:
            cur=self.con.execute("insert into %s(%s) values ('%s')" % (table,field,value))
            return cur.lastrowid
        else:
            return res[0]
    
    def add2Index(self,url,soup):
        if self.isIndexed(url):
            return
        print 'Indexing '+url
        #获取单词
        text=self.getTextOnly(soup)
        words=self.separatewords(text)
        #urlid
        urlid=self.getEntryid('urllist','url',url)
        #关联url 单词
        for i in range(len(words)):
            word=words[i]
            if word in ignorewords:
                continue
            wordid=self.getEntryid('wordlist', 'word', word)
            self.con.execute("insert into wordlocation(urlid,wordid,location) values (%d,%d,%d)" % (urlid,wordid,i))
            
    def getTextOnly(self,soup):
        v=soup.string
        if v==None:
            c=soup.contents
            resulttext=''
            for t in c:
                subtext=self.getTextOnly(t)
                resulttext+=subtext+"\n"
            return resulttext
        else:
            return v.strip()
    
    def separatewords(self,text):
        splitter=re.compile('\\W*')
        return [s.lower() for s in splitter.split(text) if s!='']
    
    def isIndexed(self,url):
        u=self.con.execute("select rowid from urllist where url='%s'" % url).fetchone()
        if u!=None:
            v=self.con.execute("select * from wordlocation where urlid=%d" % u[0]).fetchone()
            if v!=None:
                return True
        return False
    
    def addLinkRef(self,urlfrom,urlto,linktext):
        words=self.separatewords(linktext)
        fromid=self.getEntryid('urllist','url',urlfrom)
        toid=self.getEntryid('urllist','url',urlto)
        if fromid==toid: return
        cur=self.con.execute("insert into link(fromid,toid) values (%d,%d)" % (fromid,toid))
        linkid=cur.lastrowid
        for word in words:
            if word in ignorewords: continue
            wordid=self.getEntryid('wordlist','word',word)
            self.con.execute("insert into linkwords(linkid,wordid) values (%d,%d)" % (linkid,wordid))
    
    def crawl(self,pages,depth=2):
        for i in range(depth):
            newpages=set()
            for page in pages:
                try:
                    c=urllib2.urlopen(page)
                except:
                    print "could not open %s" % page
                    continue
                soup=BeautifulSoup(c.read())
                self.add2Index(page,soup)
                
                links=soup('a')
                for link in links:
                    if ('href' in dict(link.attrs)):
                        url=urljoin(page,link['href'])
                        if url.find("'") !=-1:
                            continue
                        url=url.split('#')[0]
                        if url[0:4]=='http' and not self.isIndexed(url):
                            newpages.add(url)
                        linkText=self.getTextOnly(link)
                        self.addLinkRef(page,url,linkText)
                    self.dbCommit()
            pages=newpages
    
    def createIndexTables(self):
        sql='''create table urllist(url)
        create table wordlist(word)
        create table wordlocation(urlid,wordid,location)
        create table link(fromid integer,toid integer)
        create table linkwords(wordid,linkid)
        create index wordidx on wordlist(word)
        create index urlidx on urllist(url)
        create index wordurlidx on wordlocation(wordid)
        create index urltoidx on link(toid)
        create index urlfromidx on link(fromid)'''
        self.con.execute('create table urllist(url)')
        self.con.execute('create table wordlist(word)')
        self.con.execute('create table wordlocation(urlid,wordid,location)')
        self.con.execute('create table link(fromid integer,toid integer)')
        self.con.execute('create table linkwords(wordid,linkid)')
        self.con.execute('create index wordidx on wordlist(word)')
        self.con.execute('create index urlidx on urllist(url)')
        self.con.execute('create index wordurlidx on wordlocation(wordid)')
        self.con.execute('create index urltoidx on link(toid)')
        self.con.execute('create index urlfromidx on link(fromid)')
        self.dbCommit()
    
class searcher:
    def __init__(self,dbname):
        self.con=sqlite3.connect(dbname)
            
    def __del__(self):
        self.con.close()
            
    def getMatchRows(self,q):
        #
        fieldlist='w0.urlid'
        tablelist=''
        clauselist=''
        rows=[]
        wordids=[]
        #
        words=q.split(' ')
        tablenumber=0
            
        for word in words:
            #
            wordrow = self.con.execute("select rowid from wordlist where word = '%s'" % word).fetchone()
            if wordrow!=None:
                wordid=wordrow[0]
                wordids.append(wordid)
                if tablenumber>0:
                    tablelist +=','
                    clauselist +=' and '
                    clauselist +='w%d.urlid=w%d.urlid and ' % (tablenumber-1,tablenumber)
                fieldlist+=',w%d.location' % tablenumber
                tablelist+='wordlocation w%d' % tablenumber
                clauselist+='w%d.wordid=%d' % (tablenumber,wordid)
                tablenumber+=1
                #
                fullquery='select %s from %s where %s' % (fieldlist,tablelist,clauselist)
                cur=self.con.execute(fullquery)
                rows=[row for row in cur]
        return rows,wordids
        
    def getScoredList(self,rows,wordids):
        totalscores=dict([(row[0],0) for row in rows])
        
        #
        weights=[(0.6,self.locationScore(rows)),
                (0.3,self.frequencyScore(rows)),
                (0.1,self.distancesScore(rows))]
        
        for (weight,scores) in weights:
            for url in totalscores:
                totalscores[url]+=weight*scores[url]
        return totalscores
    
    def getUrlName(self,id):
        return self.con.execute("select url from urllist where rowid=%d" % id).fetchone()[0]
    
    def query(self,q):
        rows,wordids=self.getMatchRows(q)
        scores=self.getScoredList(rows, wordids)
        rankedscores=sorted([(score,url) for (url,score) in scores.items()],reverse=1)
        for (score,urlid) in rankedscores[0:10]:
            print '%f\t%s' % (score,self.getUrlName(urlid))
            
    def normalizeScores(self,scores,smallisbetter=0):
        #weight归一化
        vsmall=0.00001
        if smallisbetter:
            minscore=min(scores.values())
            return dict([(u,float(minscore)/max(vsmall,l)) for (u,l) in scores.items()])
        else:
            maxscore=max(scores.values())
            if maxscore==0:
                maxscore=vsmall
            return dict([(u,float(c)/maxscore) for (u,c) in scores.items()])
        
    def frequencyScore(self,rows):
        counts=dict([(row[0],0) for row in rows])
        for row in rows:
            counts[row[0]]+=1
        return self.normalizeScores(counts)
    
    def locationScore(self,rows):
        locations=dict([(row[0],1000000)for row in rows])
        for row in rows:
            loc=sum(row[1:])
            if loc<locations[row[0]]:
                locations[row[0]]=loc
        return self.normalizeScores(locations,smallisbetter=1)
    
    def distancesScore(self,rows):
        if len(rows[0])<=2:
            return dict([(row[0],1.0)for row in rows])
        #
        mindistance=dict([(row[0],1000000)for row in rows])
        for row in rows:
            dist=sum([abs(row[i]-row[i-1])for i in range(2,len(row))])
            if dist<mindistance[row[0]]:
                mindistance[row[0]]=dist
        return self.normalizeScores(mindistance, smallisbetter=1)
    
    def inboundLinkScore(self,rows):
        uniqueurls=set([row[0] for row in rows])
        inboundcount=dict([(u,self.con.execute("select count(*) from link where toid=%d" % u).fetchone()[0]) for u in uniqueurls])
        return self.normalizeScores(inboundcount)
    
     