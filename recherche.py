"""
recherche.py - Moteur de recherche unifié (5 modèles + 6 mesures vectorielles)
Intègre : TP3 (booléen) + TP4 (étendu, Lukasiewicz, Kraft) + TP5 (vectoriel complet)
"""
import re
import os

from operateurs import et, ou, non
from modeles import ModeleEtendu, ModeleLukasiewicz, ModeleKraft, ModeleVectoriel
from utils.etape2_stopwords import remove_stopwords
from utils.etape3_stemming import stem_words
from utils.etape4_tf import compute_tf
from utils.etape6_tfidf import compute_tfidf


class MoteurRecherche:
    def __init__(self, index):
        self.index = index
        self.modele_courant = "vectoriel"
        self.mesure_vectorielle = "cosine"
        self.modeles = {
            "booleen":      None,
            "etendu":       ModeleEtendu(),
            "lukasiewicz":  ModeleLukasiewicz(),
            "kraft":        ModeleKraft(),
            "vectoriel":    ModeleVectoriel("cosine"),
        }

    def set_modele(self, nom):
        if nom in self.modeles:
            self.modele_courant = nom
            return True
        return False

    def set_mesure(self, mesure):
        self.mesure_vectorielle = mesure
        self.modeles["vectoriel"] = ModeleVectoriel(mesure)

    def _pretraiter(self, requete_brute):
        mots = re.sub(r"[^\w\s]", "", requete_brute.lower()).split()
        mots = remove_stopwords(mots)
        mots = stem_words(mots)
        return [m for m in mots if len(m) > 1 and not m.isdigit()]

    def _docs_terme(self, terme):
        mots = self._pretraiter(terme)
        if not mots:
            return set()
        resultat = self.index.docs_contenant(mots[0])
        for m in mots[1:]:
            resultat = resultat | self.index.docs_contenant(m)
        return resultat

    def _parser_booleen(self, requete):
        r = requete.lower().strip()
        r = r.replace(" and ", " et ").replace(" or ", " ou ").replace(" not ", " non ")
        if r.startswith("not "):
            r = "non " + r[4:]
        if "(" in r:
            return self._eval_parentheses(r)
        if " ou " in r:
            return self._eval_ou(r.split(" ou "))
        if " et " in r:
            return self._eval_et(r.split(" et "))
        if r.startswith("non "):
            return non(self.index.tous, self._docs_terme(r[4:].strip()))
        mots = r.split()
        if len(mots) > 1:
            return self._eval_et(mots)
        return self._docs_terme(r.strip())

    def _eval_et(self, termes):
        if not termes:
            return set()
        r = self._docs_terme(termes[0].strip())
        for t in termes[1:]:
            t = t.strip()
            if t:
                r = et(r, self._docs_terme(t))
        return r

    def _eval_ou(self, termes):
        if not termes:
            return set()
        r = self._docs_terme(termes[0].strip())
        for t in termes[1:]:
            t = t.strip()
            if t:
                r = ou(r, self._docs_terme(t))
        return r

    def _eval_parentheses(self, r):
        m = re.search(r'\(([^()]+)\)', r)
        if not m:
            return self._eval_simple(r)
        contenu = m.group(1)
        rs = self._parser_booleen(contenu)
        token = "__GRP__"
        reste = r[:m.start()] + token + r[m.end():]
        return self._eval_avec_token(reste, token, rs)

    def _eval_avec_token(self, expr, token, token_result):
        if " ou " in expr:
            parts = expr.split(" ou ")
            result = set()
            for p in parts:
                p = p.strip()
                s = token_result if p == token else self._docs_terme(p) if p else set()
                result = ou(result, s)
            return result
        if " et " in expr:
            parts = expr.split(" et ")
            result = None
            for p in parts:
                p = p.strip()
                s = token_result if p == token else self._docs_terme(p) if p else set()
                result = s if result is None else et(result, s)
            return result or set()
        if expr.strip().startswith("non "):
            return non(self.index.tous, token_result)
        return token_result

    def _eval_simple(self, expr):
        expr = expr.strip()
        if " ou " in expr:
            return self._eval_ou(expr.split(" ou "))
        if " et " in expr:
            return self._eval_et(expr.split(" et "))
        if expr.startswith("non "):
            return non(self.index.tous, self._docs_terme(expr[4:].strip()))
        return self._docs_terme(expr)

    def recherche_booleenne(self, requete):
        ids = self._parser_booleen(requete)
        resultats = [(self.index.docs.get(doc_id, "?"), 1.0, doc_id) for doc_id in ids]
        resultats.sort(key=lambda x: x[0])
        return resultats

    def recherche_score(self, requete):
        mots = self._pretraiter(requete)
        if not mots:
            return []
        modele = self.modeles[self.modele_courant]
        resultats = []
        if self.modele_courant == "vectoriel":
            tf_query = compute_tf(mots)
            tfidf_query = compute_tfidf(tf_query, self.index.idf)
            for doc_id, nom in self.index.docs.items():
                tfidf_doc = self.index.get_tfidf_doc(doc_id)
                score = modele.score(tfidf_query, tfidf_doc)
                if score > 0:
                    resultats.append((nom, score, doc_id))
        else:
            for doc_id, nom in self.index.docs.items():
                poids = [self.index.get_poids_tfidf(m, doc_id) for m in mots]
                max_p = max(poids) if poids else 1.0
                poids_norm = [p / max_p for p in poids] if max_p > 0 else poids
                score = modele.score(poids_norm)
                if score > 0:
                    resultats.append((nom, score, doc_id))
        resultats.sort(key=lambda x: -x[1])
        return resultats

    def rechercher(self, requete):
        if self.modele_courant == "booleen":
            return self.recherche_booleenne(requete)
        return self.recherche_score(requete)

    def get_apercu(self, doc_id, n_mots=80):
        mots = self.index._docs_mots.get(doc_id, [])
        if not mots:
            return "(Aperçu non disponible)"
        return " ".join(mots[:n_mots])

    def get_extrait_contextuel(self, doc_id, requete, n_lignes=2):
        """2 lignes du texte brut contenant les termes de la requête (exigence TP5)."""
        texte_brut = self.index._textes_bruts.get(doc_id, "")
        if not texte_brut:
            return self.get_apercu(doc_id)
        mots_req = re.sub(r"[^\w\s]", "", requete.lower()).split()
        mots_req = [m for m in mots_req if len(m) > 2]
        lignes = [l.strip() for l in re.split(r'[.\n!?]', texte_brut) if l.strip()]
        extraits = []
        for ligne in lignes:
            ligne_lower = ligne.lower()
            if any(m in ligne_lower for m in mots_req):
                extraits.append(ligne)
            if len(extraits) >= n_lignes:
                break
        if extraits:
            return "\n".join(extraits[:n_lignes])
        return "\n".join(lignes[:n_lignes]) if lignes else "(Aperçu non disponible)"

    def ouvrir_document(self, doc_id, dossier="documents"):
        """Ouvre le document avec l'application système par défaut."""
        nom = self.index.docs.get(doc_id, "")
        if not nom:
            return False
        chemin = os.path.join(dossier, nom)
        if not os.path.exists(chemin):
            return False
        try:
            import subprocess, sys
            if sys.platform.startswith("win"):
                os.startfile(chemin)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", chemin])
            else:
                subprocess.Popen(["xdg-open", chemin])
            return True
        except Exception:
            return False
