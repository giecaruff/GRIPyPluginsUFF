import numpy as np

def _calcgrlimits1(gr):
    meansattrname = 'means_'
    try:
        from sklearn.mixture import GaussianMixture as GMM
        covarsattrname = 'covariances_'
    except:
        from sklearn.mixture import GMM
        covarsattrname = 'covars_'
    
    em = GMM(n_components=3)
    em.fit(gr[np.isfinite(gr)])
    
    means = getattr(em, meansattrname)
    covars = getattr(em, covarsattrname)
    
    idxmin = np.argmin(means)
    idxmax = np.argmax(means)
    grmin = means[idxmin] - covars[idxmin]**0.5
    grmax = means[idxmax] + covars[idxmax]**0.5
    
    return grmin, grmax

def _calcgrlimits2(gr):
    where = np.isfinite(gr)
    grmin = np.percentile(gr[where], 5)
    grmax = np.percentile(gr[where], 95)
    
    return grmin, grmax

def calcgrlimits(gr):
    try:
        grmin, grmax = _calcgrlimits1(gr)
    except:
        grmin, grmax = _calcgrlimits2(gr)
    
    return grmin, grmax