
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os

BG_MAIN    = "#1e1e2e"
BG_PANEL   = "#2a2a3e"
BG_ENTRY   = "#313145"
FG_MAIN    = "#cdd6f4"
FG_ACCENT  = "#89b4fa"
FG_GREEN   = "#a6e3a1"
FG_YELLOW  = "#f9e2af"
FG_RED     = "#f38ba8"
FG_MAUVE   = "#cba6f7"
FG_TEAL    = "#94e2d5"
BTN_BG     = "#45475a"
BTN_HOVER  = "#585b70"
FONT_MAIN  = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_MONO  = ("Consolas", 10)


class Interface:
    def __init__(self, moteur, index_util, dossier_docs="documents"):
        self.moteur       = moteur
        self.index_util   = index_util
        self.dossier_docs = dossier_docs
        self.historique   = []

        self.root = tk.Tk()
        self.root.title("TP5 – Système de Recherche d'Information")
        self.root.geometry("1200x760")
        self.root.configure(bg=BG_MAIN)
        self.root.minsize(950, 600)

        self._build_ui()

    def _build_ui(self):
        self._build_header()
        self._build_body()
        self._build_statusbar()

    def _build_header(self):
        header = tk.Frame(self.root, bg=BG_PANEL, pady=10)
        header.pack(fill=tk.X)
        tk.Label(header, text="🔍  Système de Recherche d'Information  –  TP5",
                 font=FONT_TITLE, bg=BG_PANEL, fg=FG_ACCENT).pack(side=tk.LEFT, padx=20)
        nb = len(self.index_util.docs)
        self.lbl_info = tk.Label(header, text=f"{nb} documents indexés",
                                  font=FONT_MAIN, bg=BG_PANEL, fg=FG_GREEN)
        self.lbl_info.pack(side=tk.RIGHT, padx=20)

    def _build_body(self):
        body = tk.Frame(self.root, bg=BG_MAIN)
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        left = tk.Frame(body, bg=BG_PANEL, width=340)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        left.pack_propagate(False)
        self._build_controls(left)
        right = tk.Frame(body, bg=BG_MAIN)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._build_results(right)

    def _build_controls(self, parent):
        pad = {"padx": 12, "pady": 3}

        # ── Modèle ──
        self._section(parent, "Modèle de recherche")
        self.var_modele = tk.StringVar(value="vectoriel")
        modeles = [
            ("Vectoriel (TF-IDF)",          "vectoriel"),
            ("Booléen classique (ET/OU/NON)","booleen"),
            ("Booléen Étendu (p-norm)",      "etendu"),
            ("Flou – Lukasiewicz",           "lukasiewicz"),
            ("Flou – Kraft (min-max)",        "kraft"),
        ]
        for label, val in modeles:
            tk.Radiobutton(
                parent, text=label, variable=self.var_modele, value=val,
                bg=BG_PANEL, fg=FG_MAIN, selectcolor=BG_ENTRY,
                activebackground=BG_PANEL, activeforeground=FG_ACCENT,
                font=FONT_MAIN, command=self._on_modele_change
            ).pack(anchor=tk.W, **pad)

        # ── Mesure vectorielle ──
        self._section(parent, "Mesure vectorielle")
        self.var_mesure = tk.StringVar(value="cosine")
        mesures = [
            ("Cosinus (défaut)", "cosine"),
            ("Dice",             "dice"),
            ("Jaccard",          "jaccard"),
            ("Overlap",          "overlap"),
            ("Euclidienne",      "euclidienne"),
            ("Produit scalaire", "produit_scalaire"),
        ]
        frm_mesures = tk.Frame(parent, bg=BG_PANEL)
        frm_mesures.pack(fill=tk.X, padx=12, pady=(2, 4))
        self.cmb_mesure = ttk.Combobox(frm_mesures, textvariable=self.var_mesure,
                                        values=[m[0] for m in mesures],
                                        state="readonly", font=FONT_MAIN, width=22)
        self.cmb_mesure.pack(fill=tk.X)
        self._mesures_map = {m[0]: m[1] for m in mesures}
        self.cmb_mesure.bind("<<ComboboxSelected>>", self._on_mesure_change)

        # ── Requête ──
        self._section(parent, "Requête")
        self.entry_req = tk.Entry(parent, font=FONT_MONO,
                                   bg=BG_ENTRY, fg=FG_MAIN, insertbackground=FG_MAIN,
                                   relief=tk.FLAT, bd=5)
        self.entry_req.pack(fill=tk.X, padx=12, pady=(2, 4))
        self.entry_req.bind("<Return>", lambda e: self._chercher())

        ops_frame = tk.Frame(parent, bg=BG_PANEL)
        ops_frame.pack(fill=tk.X, padx=12, pady=(0, 6))
        for label, val in [("ET", " ET "), ("OU", " OU "), ("NON", " NON "),
                            ("( )", " () "), ("✕", "")]:
            color = FG_ACCENT if label != "✕" else FG_RED
            b = tk.Button(ops_frame, text=label, bg=BTN_BG, fg=color,
                          font=("Segoe UI", 9, "bold"), relief=tk.FLAT, bd=0,
                          padx=6, pady=3, cursor="hand2",
                          command=lambda v=val, l=label: self._insert_op(v, l))
            b.pack(side=tk.LEFT, padx=2)
            self._hover(b)

        btn_ch = tk.Button(parent, text="🔍  Chercher",
                            bg=FG_ACCENT, fg=BG_MAIN, font=FONT_BOLD,
                            relief=tk.FLAT, bd=0, pady=6, cursor="hand2",
                            command=self._chercher)
        btn_ch.pack(fill=tk.X, padx=12, pady=4)

        btn_eff = tk.Button(parent, text="Effacer", bg=BTN_BG, fg=FG_MAIN,
                             font=FONT_MAIN, relief=tk.FLAT, bd=0, pady=4,
                             cursor="hand2", command=self._effacer)
        btn_eff.pack(fill=tk.X, padx=12, pady=2)

        # ── Outils ──
        self._section(parent, "Outils")
        for text, color, cmd in [
            ("📊  Comparer les modèles",    FG_YELLOW, self._comparer_modeles),
            ("📂  Ouvrir document sélectionné", FG_GREEN, self._ouvrir_doc),
            ("🔄  Réindexer les documents", FG_TEAL,   self._reindexer),
        ]:
            b = tk.Button(parent, text=text, bg=BTN_BG, fg=color, font=FONT_MAIN,
                          relief=tk.FLAT, bd=0, pady=4, cursor="hand2", command=cmd)
            b.pack(fill=tk.X, padx=12, pady=3)
            self._hover(b)

        # ── Historique ──
        self._section(parent, "Historique des requêtes")
        self.lb_histo = tk.Listbox(parent, bg=BG_ENTRY, fg=FG_MAIN,
                                    font=FONT_MONO, height=5, relief=tk.FLAT,
                                    selectbackground=FG_ACCENT, selectforeground=BG_MAIN)
        self.lb_histo.pack(fill=tk.X, padx=12, pady=(2, 4))
        self.lb_histo.bind("<Double-Button-1>", self._charger_histo)

    def _build_results(self, parent):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook",     background=BG_MAIN, borderwidth=0)
        style.configure("TNotebook.Tab", background=BTN_BG, foreground=FG_MAIN,
                        padding=[12, 5], font=FONT_MAIN)
        style.map("TNotebook.Tab",
                  background=[("selected", BG_ENTRY)],
                  foreground=[("selected", FG_ACCENT)])

        nb = ttk.Notebook(parent)
        nb.pack(fill=tk.BOTH, expand=True)

        tab_res    = tk.Frame(nb, bg=BG_MAIN)
        tab_apercu = tk.Frame(nb, bg=BG_MAIN)
        tab_stats  = tk.Frame(nb, bg=BG_MAIN)
        nb.add(tab_res,    text="  Résultats  ")
        nb.add(tab_apercu, text="  Aperçu document  ")
        nb.add(tab_stats,  text="  Statistiques  ")

        self._build_tab_resultats(tab_res)
        self._build_tab_apercu(tab_apercu)
        self._build_tab_stats(tab_stats)

    def _build_tab_resultats(self, parent):
        top = tk.Frame(parent, bg=BG_MAIN)
        top.pack(fill=tk.X, pady=(6, 2))
        self.lbl_nb_res = tk.Label(top, text="", font=FONT_BOLD, bg=BG_MAIN, fg=FG_YELLOW)
        self.lbl_nb_res.pack(side=tk.LEFT, padx=8)
        self.lbl_modele_actif = tk.Label(top, text="Modèle : vectoriel | Mesure : cosine",
                                          font=FONT_MAIN, bg=BG_MAIN, fg=FG_MAUVE)
        self.lbl_modele_actif.pack(side=tk.RIGHT, padx=8)

        style = ttk.Style()
        style.configure("Res.Treeview", background=BG_ENTRY, foreground=FG_MAIN,
                        rowheight=26, fieldbackground=BG_ENTRY, font=FONT_MONO, borderwidth=0)
        style.configure("Res.Treeview.Heading", background=BTN_BG, foreground=FG_ACCENT,
                        font=FONT_BOLD, relief="flat")
        style.map("Res.Treeview",
                  background=[("selected", FG_ACCENT)],
                  foreground=[("selected", BG_MAIN)])

        frame_tree = tk.Frame(parent, bg=BG_MAIN)
        frame_tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        cols = ("Rang", "Document", "Type", "Score", "Extrait")
        self.tree = ttk.Treeview(frame_tree, columns=cols, show="headings",
                                  style="Res.Treeview")
        self.tree.heading("Rang",     text="Rang",     anchor=tk.CENTER)
        self.tree.heading("Document", text="Document", anchor=tk.W)
        self.tree.heading("Type",     text="Type",     anchor=tk.CENTER)
        self.tree.heading("Score",    text="Score",    anchor=tk.CENTER)
        self.tree.heading("Extrait",  text="Extrait",  anchor=tk.W)
        self.tree.column("Rang",     width=55,  minwidth=40,  anchor=tk.CENTER, stretch=False)
        self.tree.column("Document", width=280, minwidth=150, anchor=tk.W,      stretch=True)
        self.tree.column("Type",     width=60,  minwidth=50,  anchor=tk.CENTER, stretch=False)
        self.tree.column("Score",    width=120, minwidth=80,  anchor=tk.CENTER, stretch=False)
        self.tree.column("Extrait",  width=300, minwidth=100, anchor=tk.W,      stretch=True)

        sb = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.LEFT, fill=tk.Y)

        self.tree.tag_configure("pair",   background=BG_ENTRY)
        self.tree.tag_configure("impair", background=BG_PANEL)
        self.tree.bind("<Double-Button-1>", self._afficher_apercu)

    def _build_tab_apercu(self, parent):
        frm = tk.Frame(parent, bg=BG_MAIN)
        frm.pack(fill=tk.X, padx=10, pady=(8, 2))
        tk.Label(frm, text="Double-clic sur un résultat pour afficher l'aperçu.",
                 font=FONT_MAIN, bg=BG_MAIN, fg=FG_MAUVE).pack(side=tk.LEFT)
        tk.Button(frm, text="📂 Ouvrir", bg=BTN_BG, fg=FG_GREEN, font=FONT_MAIN,
                  relief=tk.FLAT, bd=0, padx=8, cursor="hand2",
                  command=self._ouvrir_doc).pack(side=tk.RIGHT)

        self.txt_apercu = scrolledtext.ScrolledText(parent, wrap=tk.WORD,
                                                     bg=BG_ENTRY, fg=FG_MAIN,
                                                     font=FONT_MONO, relief=tk.FLAT)
        self.txt_apercu.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

    def _build_tab_stats(self, parent):
        tk.Label(parent, text="Statistiques de l'index",
                 font=FONT_BOLD, bg=BG_MAIN, fg=FG_ACCENT).pack(anchor=tk.W, padx=10, pady=(10, 4))
        self.txt_stats = scrolledtext.ScrolledText(parent, wrap=tk.WORD,
                                                    bg=BG_ENTRY, fg=FG_MAIN,
                                                    font=FONT_MONO, relief=tk.FLAT, height=25)
        self.txt_stats.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        self._afficher_stats()

    def _build_statusbar(self):
        self.statusbar = tk.Label(self.root, text="Prêt.", bg=BTN_BG, fg=FG_MAIN,
                                   font=("Segoe UI", 9), anchor=tk.W, padx=10, pady=3)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    # ══════════════════════════════════════════════════════════════════ #
    #  Actions                                                           #
    # ══════════════════════════════════════════════════════════════════ #

    def _on_modele_change(self):
        m = self.var_modele.get()
        self.moteur.set_modele(m)
        mesure = self.var_mesure.get() if m == "vectoriel" else "-"
        self.lbl_modele_actif.config(text=f"Modèle : {m} | Mesure : {mesure}")
        self._set_status(f"Modèle → {m}")

    def _on_mesure_change(self, event=None):
        label = self.var_mesure.get()
        code = self._mesures_map.get(label, "cosine")
        self.moteur.set_mesure(code)
        self.lbl_modele_actif.config(
            text=f"Modèle : {self.var_modele.get()} | Mesure : {label}")
        self._set_status(f"Mesure vectorielle → {label}")

    def _insert_op(self, val, label):
        if label == "✕":
            self.entry_req.delete(0, tk.END)
        elif "(" in val:
            pos = self.entry_req.index(tk.INSERT)
            self.entry_req.insert(pos, "()")
            self.entry_req.icursor(pos + 1)
        else:
            self.entry_req.insert(tk.INSERT, val)
        self.entry_req.focus()

    def _effacer(self):
        self.entry_req.delete(0, tk.END)
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.lbl_nb_res.config(text="")
        self.txt_apercu.delete("1.0", tk.END)
        self._set_status("Effacé.")

    def _chercher(self):
        requete = self.entry_req.get().strip()
        if not requete:
            messagebox.showwarning("Attention", "Veuillez entrer une requête.")
            return
        modele = self.var_modele.get()
        self.moteur.set_modele(modele)
        self._set_status(f"Recherche : « {requete} »  [modèle : {modele}]…")
        threading.Thread(target=self._executer_recherche,
                         args=(requete,), daemon=True).start()

    def _executer_recherche(self, requete):
        try:
            resultats = self.moteur.rechercher(requete)
            self.root.after(0, self._afficher_resultats, resultats, requete)
        except Exception as e:
            self.root.after(0, self._set_status, f"Erreur : {e}")

    def _afficher_resultats(self, resultats, requete):
        if requete not in self.historique:
            self.historique.insert(0, requete)
            self.lb_histo.insert(0, requete)
            if len(self.historique) > 20:
                self.historique.pop()
                self.lb_histo.delete(tk.END)

        for row in self.tree.get_children():
            self.tree.delete(row)

        if not resultats:
            self.lbl_nb_res.config(text="0 résultat", fg=FG_RED)
            self._set_status("Aucun document trouvé.")
            return

        self.lbl_nb_res.config(text=f"{len(resultats)} résultat(s)", fg=FG_GREEN)

        for i, (nom, score, doc_id) in enumerate(resultats, 1):
            score_str = f"{score:.6f}" if isinstance(score, float) and score != 1.0 else "✓ présent"
            ext = os.path.splitext(nom)[1].upper().lstrip(".") or "?"
            # Extrait contextuel (1 ligne courte pour le tableau)
            extrait = self.moteur.get_extrait_contextuel(doc_id, requete, n_lignes=1)
            extrait_court = extrait[:60] + "…" if len(extrait) > 60 else extrait
            tag = "pair" if i % 2 == 0 else "impair"
            self.tree.insert("", tk.END, iid=str(doc_id),
                             values=(i, nom, ext, score_str, extrait_court),
                             tags=(tag,))

        self._set_status(
            f"{len(resultats)} document(s) trouvé(s) pour « {requete} » "
            f"[{self.var_modele.get()}]")

    def _afficher_apercu(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        doc_id = int(sel[0])
        nom = self.index_util.docs.get(doc_id, "?")
        requete = self.entry_req.get().strip()
        extrait = self.moteur.get_extrait_contextuel(doc_id, requete, n_lignes=10)
        self.txt_apercu.delete("1.0", tk.END)
        self.txt_apercu.insert(tk.END, f"Document : {nom}\n")
        self.txt_apercu.insert(tk.END, "─" * 60 + "\n\n")
        self.txt_apercu.insert(tk.END, extrait if extrait else "(Aperçu non disponible)")

    def _ouvrir_doc(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Sélectionnez un document dans les résultats.")
            return
        doc_id = int(sel[0])
        ok = self.moteur.ouvrir_document(doc_id, self.dossier_docs)
        if ok:
            self._set_status(f"Document ouvert : {self.index_util.docs.get(doc_id, '?')}")
        else:
            messagebox.showerror("Erreur", "Impossible d'ouvrir le document.")

    def _afficher_stats(self):
        idx = self.index_util
        nb_docs  = len(idx.docs)
        nb_terms = len(idx.index)
        nb_total = sum(len(v) for v in idx.index.values())

        # Stats par type
        types = {}
        for nom in idx.docs.values():
            ext = os.path.splitext(nom)[1].lower() or "?"
            types[ext] = types.get(ext, 0) + 1

        self.txt_stats.delete("1.0", tk.END)
        self.txt_stats.insert(tk.END, "═" * 50 + "\n")
        self.txt_stats.insert(tk.END, "  STATISTIQUES DE L'INDEX\n")
        self.txt_stats.insert(tk.END, "═" * 50 + "\n\n")
        self.txt_stats.insert(tk.END, f"  Documents indexés  : {nb_docs}\n")
        self.txt_stats.insert(tk.END, f"  Termes distincts   : {nb_terms}\n")
        self.txt_stats.insert(tk.END, f"  Postings total     : {nb_total}\n")
        if nb_docs > 0:
            self.txt_stats.insert(tk.END, f"  Densité moyenne    : {nb_total/nb_docs:.1f} termes/doc\n")
        self.txt_stats.insert(tk.END, "\n  Répartition par type :\n")
        for ext, cnt in sorted(types.items()):
            self.txt_stats.insert(tk.END, f"    {ext:<8} : {cnt} document(s)\n")

        self.txt_stats.insert(tk.END, "\n  Top 20 termes (IDF le plus bas) :\n")
        self.txt_stats.insert(tk.END, "  " + "─" * 40 + "\n")
        sorted_idf = sorted(idx.idf.items(), key=lambda x: x[1])[:20]
        for terme, idf_val in sorted_idf:
            df = len(idx.index.get(terme, []))
            self.txt_stats.insert(tk.END, f"  {terme:<22} IDF={idf_val:.3f}  df={df}\n")

        self.txt_stats.insert(tk.END, "\n  Liste des documents :\n")
        self.txt_stats.insert(tk.END, "  " + "─" * 40 + "\n")
        for i, (doc_id, nom) in enumerate(sorted(idx.docs.items()), 1):
            nb_mots = len(idx._docs_mots.get(doc_id, []))
            self.txt_stats.insert(tk.END, f"  {i:3d}. {nom:<42} ({nb_mots} mots)\n")

    def _comparer_modeles(self):
        requete = self.entry_req.get().strip()
        if not requete:
            messagebox.showinfo("Comparaison",
                                "Entrez une requête puis cliquez sur Comparer.")
            return

        win = tk.Toplevel(self.root)
        win.title(f"Comparaison – « {requete} »")
        win.geometry("1000x580")
        win.configure(bg=BG_MAIN)
        tk.Label(win, text=f"Comparaison des modèles pour : « {requete} »",
                 font=FONT_BOLD, bg=BG_MAIN, fg=FG_ACCENT).pack(pady=10)

        frame = tk.Frame(win, bg=BG_MAIN)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        modeles_list = [
            ("vectoriel",   "Vectoriel (Cosine)", FG_ACCENT),
            ("etendu",      "Étendu",             FG_GREEN),
            ("lukasiewicz", "Lukasiewicz",         FG_YELLOW),
            ("kraft",       "Kraft",               FG_MAUVE),
        ]
        for col_idx, (nom, label, couleur) in enumerate(modeles_list):
            col = tk.Frame(frame, bg=BG_PANEL, bd=1, relief=tk.RIDGE)
            col.grid(row=0, column=col_idx, padx=4, pady=4, sticky="nsew")
            frame.columnconfigure(col_idx, weight=1)
            frame.rowconfigure(0, weight=1)
            tk.Label(col, text=label, font=FONT_BOLD,
                     bg=BG_PANEL, fg=couleur).pack(pady=6)
            txt = scrolledtext.ScrolledText(col, wrap=tk.WORD, bg=BG_ENTRY, fg=FG_MAIN,
                                             font=("Consolas", 9), relief=tk.FLAT, width=20)
            txt.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 6))
            self.moteur.set_modele(nom)
            try:
                resultats = self.moteur.rechercher(requete)
                txt.insert(tk.END, f"{len(resultats)} résultat(s)\n")
                txt.insert(tk.END, "─" * 24 + "\n")
                for i, (doc, score, _) in enumerate(resultats[:15], 1):
                    score_str = f"{score:.4f}" if isinstance(score, float) and score != 1.0 else "✓"
                    txt.insert(tk.END, f"{i:2d}. {doc[:22]}\n    {score_str}\n")
            except Exception as e:
                txt.insert(tk.END, f"Erreur : {e}")
        self.moteur.set_modele(self.var_modele.get())

    def _reindexer(self):
        if not messagebox.askyesno("Réindexer",
                                    "Voulez-vous relancer l'indexation ?\n"
                                    "Cela peut prendre quelques instants."):
            return
        self._set_status("Réindexation en cours…")
        threading.Thread(target=self._thread_reindex, daemon=True).start()

    def _thread_reindex(self):
        self.index_util.reindexer(self.dossier_docs)
        self.root.after(0, self._post_reindex)

    def _post_reindex(self):
        nb = len(self.index_util.docs)
        self.lbl_info.config(text=f"{nb} documents indexés")
        self._afficher_stats()
        self._set_status(f"Réindexation terminée – {nb} documents.")

    def _charger_histo(self, event=None):
        sel = self.lb_histo.curselection()
        if sel:
            req = self.lb_histo.get(sel[0])
            self.entry_req.delete(0, tk.END)
            self.entry_req.insert(0, req)
            self._chercher()

    def _section(self, parent, titre):
        tk.Label(parent, text=f"  {titre}", font=FONT_BOLD,
                 bg=BG_PANEL, fg=FG_TEAL, anchor=tk.W).pack(fill=tk.X, pady=(12, 2))
        tk.Frame(parent, bg=FG_TEAL, height=1).pack(fill=tk.X, padx=12)

    def _hover(self, btn):
        btn.bind("<Enter>", lambda e: btn.config(bg=BTN_HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg=BTN_BG))

    def _set_status(self, msg):
        self.statusbar.config(text=f"  {msg}")

    def lancer(self):
        self.root.mainloop()
