"""
etape5_idf.py - Calcul IDF (Inverse Document Frequency)
"""
import math


def compute_idf(docs_mots):
    """
    docs_mots : dict { nom_doc : [mots_stemmes] }
    Retourne dict { terme : idf }
    """
    N = len(docs_mots)
    if N == 0:
        return {}
    df = {}
    for mots in docs_mots.values():
        for terme in set(mots):
            df[terme] = df.get(terme, 0) + 1
    idf = {}
    for terme, freq in df.items():
        idf[terme] = math.log((N + 1) / (freq + 1)) + 1  # smooth IDF
    return idf
