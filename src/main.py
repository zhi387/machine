# -*- coding=utf-8 -*- 
import nn
mynet=nn.searchnet('nn.db')
wWorld,wRiver,wBank=101,102,103
uWorldBank,uRiver,uEarth=201,202,203
print mynet.getresult([wWorld,wBank], [uWorldBank,uRiver,uEarth])
