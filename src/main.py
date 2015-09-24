# -*- coding:UTF-8 -*-
import datas
import clusters
name = [name for name in datas.rows]
data = [data for data in datas.rows.values()]
coorclust=clusters.scaleDown(data)
clusters.draw2d(coorclust, name,jpeg='2d.jpg')