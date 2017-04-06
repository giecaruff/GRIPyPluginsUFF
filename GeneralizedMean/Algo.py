# -*- coding: utf-8 -*-

import numpy as np

meantypes = [u"Aritimética", u"RMS", u"Mínimo", u"Máximo", u"Geométrica", u"Harmônica"]

def calcmeanbykey(data, key):
    if key == u"Aritimética":
        return np.mean(data, axis=1)
    elif key == u"RMS":
        return np.mean(data**2, axis=1)**0.5
    elif key == u"Mínimo":
        return np.min(data, axis=1)
    elif key == u"Máximo":
        return np.max(data, axis=1)
    elif key == u"Geométrica":
        return np.exp(np.mean(np.log(x), axis=1))
    elif key == u"Harmônica":
        return 1.0/np.mean(1.0/x, axis=1)
