
import os
import pickle
import glob as glob_module

from utils.etape1_pdf import extract_words, extract_text_raw
from utils.etape2_stopwords import remove_stopwords
from utils.etape3_stemming import stem_words
from utils.etape4_tf import compute_tf
from utils.etape5_idf import compute_idf
from utils.etape6_tfidf import compute_tfidf

INDEX_FILE = "index.pkl"
EXTENSIONS = (".pdf", ".txt", ".html", ".htm", ".docx")


class IndexUtil:
    def __init__(self):
        self.index = {}        # terme -> [id_doc, ...]
        self.docs = {}         # id -> nom fichier
        self.tous = set()
        self.tfidf = {}        # tfidf par doc
        self.idf = {}
        self._docs_mots = {}   # mots stemisés par doc
        self._textes_bruts = {}  # texte brut par doc (pour extraits contextuels)

    # ------------------------------------------------------------------ #
    #  Construction                                                        #
    # ------------------------------------------------------------------ #
    def construire(self, dossier="documents"):
        print(f"[INDEX] Indexation du dossier : {dossier}")
        fichiers = []
        for ext in EXTENSIONS:
            fichiers.extend(glob_module.glob(os.path.join(dossier, f"*{ext}")))
            fichiers.extend(glob_module.glob(os.path.join(dossier, "**", f"*{ext}"), recursive=True))
        fichiers = list(set(fichiers))

        if not fichiers:
            print("[INDEX] Aucun document trouvé.")
            return

        docs_mots_bruts = {}

        for i, f in enumerate(fichiers):
            try:
                texte_brut = extract_text_raw(f)
                mots = extract_words(f)
                mots = remove_stopwords(mots)
                mots = stem_words(mots)
                mots = [m for m in mots if len(m) > 1 and not m.isdigit()]
                if mots:
                    nom = os.path.basename(f)
                    self.docs[i] = nom
                    docs_mots_bruts[nom] = mots
                    self._docs_mots[i] = mots
                    self._textes_bruts[i] = texte_brut
                    for terme in set(mots):
                        self.index.setdefault(terme, []).append(i)
            except Exception as e:
                print(f"[INDEX] Erreur {f}: {e}")

        self.tous = set(self.docs.keys())

        print("[INDEX] Calcul TF-IDF...")
        self.idf = compute_idf(docs_mots_bruts)
        for i, mots in self._docs_mots.items():
            nom = self.docs[i]
            tf = compute_tf(mots)
            self.tfidf[i] = compute_tfidf(tf, self.idf)

        self._sauvegarder()
        print(f"[INDEX] {len(self.docs)} documents indexés.")

    def _sauvegarder(self):
        data = {
            "index": self.index, "docs": self.docs,
            "tous": self.tous, "tfidf": self.tfidf,
            "idf": self.idf, "_docs_mots": self._docs_mots,
            "_textes_bruts": self._textes_bruts,
        }
        with open(INDEX_FILE, "wb") as f:
            pickle.dump(data, f)

    def charger(self):
        if not os.path.exists(INDEX_FILE):
            return False
        try:
            with open(INDEX_FILE, "rb") as f:
                data = pickle.load(f)
            self.index = data.get("index", {})
            self.docs = data.get("docs", {})
            self.tous = data.get("tous", set())
            self.tfidf = data.get("tfidf", {})
            self.idf = data.get("idf", {})
            self._docs_mots = data.get("_docs_mots", {})
            self._textes_bruts = data.get("_textes_bruts", {})
            print(f"[INDEX] {len(self.docs)} documents chargés depuis le cache.")
            return True
        except Exception as e:
            print(f"[INDEX] Erreur chargement: {e}")
            return False

    def reindexer(self, dossier="documents"):
        if os.path.exists(INDEX_FILE):
            os.remove(INDEX_FILE)
        self.__init__()
        self.construire(dossier)

    def get_poids_tfidf(self, terme, doc_id):
        return self.tfidf.get(doc_id, {}).get(terme, 0.0)

    def get_tfidf_doc(self, doc_id):
        return self.tfidf.get(doc_id, {})

    def docs_contenant(self, terme):
        return set(self.index.get(terme.lower().strip(), []))
