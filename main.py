

import os
import sys


def main():
    dossier   = "documents"
    reindexer = False

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--reindex":
            reindexer = True
        elif args[i] == "--dossier" and i + 1 < len(args):
            dossier = args[i + 1]
            i += 1
        i += 1

    if not os.path.isdir(dossier):
        print(f"[ERREUR] Dossier introuvable : {dossier}")
        sys.exit(1)

    # Compter tous les fichiers supportés
    extensions = (".pdf", ".txt", ".html", ".htm", ".docx")
    nb_docs = 0
    for root, _, files in os.walk(dossier):
        nb_docs += sum(1 for f in files if os.path.splitext(f)[1].lower() in extensions)

    print(f"[INFO] Dossier : {dossier} | {nb_docs} document(s) trouvé(s)")

    if nb_docs == 0:
        print("[ERREUR] Aucun document PDF/TXT/HTML/DOCX dans le dossier.")
        sys.exit(1)

    from index_util import IndexUtil
    from recherche  import MoteurRecherche
    from interface  import Interface

    index = IndexUtil()

    if reindexer:
        print("[INDEX] Réindexation forcée...")
        index.reindexer(dossier)
    elif not index.charger():
        print("[INDEX] Aucun cache trouvé, indexation en cours...")
        index.construire(dossier)
    elif len(index.docs) == 0:
        index.construire(dossier)

    if not index.docs:
        print("[ERREUR] Aucun document n'a pu être indexé.")
        sys.exit(1)

    print(f"[INFO] {len(index.docs)} document(s) prêt(s).")

    moteur = MoteurRecherche(index)
    Interface(moteur, index, dossier_docs=dossier).lancer()


if __name__ == "__main__":
    main()
