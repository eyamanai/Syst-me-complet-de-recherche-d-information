"""
modeles/__init__.py - Tous les modèles de recherche
TP5 : Vectoriel (Cosine, Dice, Jaccard, Overlap, Euclidienne, Produit scalaire)
      Booléen étendu (p-norm)
      Flou Lukasiewicz
      Flou Kraft (min-max)
"""
import math


# ══════════════════════════════════════════════════════════════════════ #
#  Helpers vectoriels                                                    #
# ══════════════════════════════════════════════════════════════════════ #

def _dot(a, b):
    """Produit scalaire de deux vecteurs dict."""
    return sum(a.get(t, 0) * b.get(t, 0) for t in a)


def _norm(v):
    """Norme euclidienne d'un vecteur dict."""
    return math.sqrt(sum(x * x for x in v.values()))


def _terms_union(a, b):
    return set(a) | set(b)


def _terms_inter(a, b):
    return set(a) & set(b)


# ══════════════════════════════════════════════════════════════════════ #
#  Modèle vectoriel – 6 mesures de similarité                           #
# ══════════════════════════════════════════════════════════════════════ #

class ModeleVectoriel:
    """Similarité cosinus (défaut) + 5 autres mesures."""

    MESURES = ["cosine", "dice", "jaccard", "overlap",
               "euclidienne", "produit_scalaire"]

    def __init__(self, mesure="cosine"):
        if mesure not in self.MESURES:
            mesure = "cosine"
        self.mesure = mesure

    def score(self, query_vec, doc_vec):
        m = self.mesure
        if m == "cosine":
            return self._cosine(query_vec, doc_vec)
        elif m == "dice":
            return self._dice(query_vec, doc_vec)
        elif m == "jaccard":
            return self._jaccard(query_vec, doc_vec)
        elif m == "overlap":
            return self._overlap(query_vec, doc_vec)
        elif m == "euclidienne":
            return self._euclidienne(query_vec, doc_vec)
        elif m == "produit_scalaire":
            return self._produit_scalaire(query_vec, doc_vec)
        return 0.0

    def _cosine(self, q, d):
        num = _dot(q, d)
        den = _norm(q) * _norm(d)
        return num / den if den > 0 else 0.0

    def _dice(self, q, d):
        num = 2 * _dot(q, d)
        den = _norm(q) ** 2 + _norm(d) ** 2
        return num / den if den > 0 else 0.0

    def _jaccard(self, q, d):
        num = _dot(q, d)
        den = _norm(q) ** 2 + _norm(d) ** 2 - num
        return num / den if den > 0 else 0.0

    def _overlap(self, q, d):
        num = _dot(q, d)
        den = min(_norm(q) ** 2, _norm(d) ** 2)
        return num / den if den > 0 else 0.0

    def _euclidienne(self, q, d):
        """Score inversé : plus la distance est faible, plus le score est élevé."""
        termes = _terms_union(q, d)
        dist_sq = sum((q.get(t, 0) - d.get(t, 0)) ** 2 for t in termes)
        dist = math.sqrt(dist_sq)
        return 1 / (1 + dist)

    def _produit_scalaire(self, q, d):
        return _dot(q, d)


# ══════════════════════════════════════════════════════════════════════ #
#  Modèle booléen étendu (p-norm, p=2)                                  #
# ══════════════════════════════════════════════════════════════════════ #

class ModeleEtendu:
    def score(self, poids):
        """poids : liste de float ∈ [0,1] pour chaque terme."""
        if not poids:
            return 0.0
        m = len(poids)
        r_or  = math.sqrt(sum(p ** 2 for p in poids) / m)
        r_and = 1 - math.sqrt(sum((1 - p) ** 2 for p in poids) / m)
        return (r_or + r_and) / 2


# ══════════════════════════════════════════════════════════════════════ #
#  Modèle flou – Lukasiewicz                                            #
# ══════════════════════════════════════════════════════════════════════ #

class ModeleLukasiewicz:
    def score(self, poids):
        if not poids:
            return 0.0
        # AND = produit, OR = somme complémentaire bornée à 1
        and_score = 1.0
        for p in poids:
            and_score *= p
        or_score = min(1.0, sum(poids))
        return (and_score + or_score) / 2


# ══════════════════════════════════════════════════════════════════════ #
#  Modèle flou – Kraft (min-max)                                        #
# ══════════════════════════════════════════════════════════════════════ #

class ModeleKraft:
    def score(self, poids):
        if not poids:
            return 0.0
        return (min(poids) + max(poids)) / 2
