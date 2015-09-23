# -*- coding:UTF-8 -*-
import clustersdatas
import clusters
from clusters import pearson
name = [name for name in clustersdatas.rows]
data = [data for data in clustersdatas.rows.values()]
clust = clusters.hculster(data, pearson)
clusters.printClust(clust, name)
clusters.drawDendrogram(clust, name,jpeg='1.jpg')