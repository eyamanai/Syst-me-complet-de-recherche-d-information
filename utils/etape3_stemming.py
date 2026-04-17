"""
etape3_stemming.py - Stemming (PorterStemmer via nltk, fallback simple)
"""


def stem_words(mots):
    try:
        from nltk.stem import PorterStemmer
        ps = PorterStemmer()
        return [ps.stem(m) for m in mots]
    except Exception:
        # Fallback : suppression suffixes simples
        result = []
        for m in mots:
            if len(m) > 5:
                for suf in ("ing", "tion", "ment", "ness", "edly", "edly",
                            "ious", "eous", "ful", "less", "ism", "ist",
                            "er", "ed", "ly", "es", "en"):
                    if m.endswith(suf) and len(m) - len(suf) > 3:
                        m = m[:-len(suf)]
                        break
            result.append(m)
        return result
