"""
etape4_tf.py - Calcul TF (Term Frequency)
"""
import math
from collections import Counter


def compute_tf(mots):
    """TF logarithmique : 1 + log(count) si count > 0."""
    counts = Counter(mots)
    n = len(mots)
    if n == 0:
        return {}
    tf = {}
    for terme, count in counts.items():
        tf[terme] = 1 + math.log(count) if count > 0 else 0
    return tf
