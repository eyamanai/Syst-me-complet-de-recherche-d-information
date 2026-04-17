"""
etape6_tfidf.py - Calcul TF-IDF
"""


def compute_tfidf(tf, idf):
    """
    tf  : dict { terme : tf_val }
    idf : dict { terme : idf_val }
    Retourne dict { terme : tfidf_val }
    """
    return {terme: tf_val * idf.get(terme, 1.0)
            for terme, tf_val in tf.items()}
