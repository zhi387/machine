# -*- coding:UTF-8 -*-

import similardatas
import similar
from similar import similarDinstance
a = similar.rankingSample(similardatas.languagevalus, 'u1',similarity=similarDinstance)
print a