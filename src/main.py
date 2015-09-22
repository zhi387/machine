# -*- coding:UTF-8 -*-

import similardatas
import similar
a = similardatas.languagevalus
b = similar.getRecommendationsInAll(a, 'u2')
c = similar.getRecommendationsInCache(a, similar.calculateSample(a), 'u2')
print b
print c