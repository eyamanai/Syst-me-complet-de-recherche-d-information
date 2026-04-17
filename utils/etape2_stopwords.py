"""
etape2_stopwords.py - Suppression des mots vides (EN + FR)
"""
STOPWORDS_FR = {
    "le","la","les","de","du","des","un","une","et","en","au","aux",
    "ce","ces","se","sa","son","ses","leur","leurs","je","tu","il","elle",
    "nous","vous","ils","elles","qui","que","quoi","dont","où","si","ne",
    "pas","plus","par","sur","sous","dans","avec","sans","pour","mais","ou",
    "donc","or","ni","car","est","sont","être","avoir","fait","faire",
    "tout","tous","toute","toutes","très","bien","aussi","même","comme",
    "plus","moins","entre","après","avant","lors","puis","cela","ceci",
}
STOPWORDS_EN = {
    "the","a","an","of","in","to","and","is","are","was","were","be",
    "been","being","have","has","had","do","does","did","will","would",
    "could","should","may","might","shall","can","it","its","this","that",
    "these","those","with","for","on","at","by","from","or","not","but",
    "as","into","about","than","then","when","which","who","what","how",
    "all","each","both","few","more","most","other","some","such","no",
    "only","same","so","than","too","very","just","because","if","while",
    "through","during","before","after","above","below","between","up",
    "out","off","over","under","again","further","once","here","there",
    "where","why","any","he","she","they","we","you","their","our","your",
    "his","her","my","me","him","us","them","i","s","t","re","ll","ve",
}
STOPWORDS = STOPWORDS_FR | STOPWORDS_EN


def remove_stopwords(mots):
    return [m for m in mots if m.lower() not in STOPWORDS and len(m) > 1]
