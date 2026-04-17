# -*- coding: utf-8 -*-
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

def generer():
    output_pdf = "Rapport_Final_Eya_Manai.pdf"
    doc = SimpleDocTemplate(output_pdf, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    style_titre = ParagraphStyle('Titre', parent=styles['Title'], fontSize=18, textColor=colors.navy)
    style_h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=14, textColor=colors.navy, spaceBefore=10)
    style_n = styles['Normal']
    story = []

    # --- SECTION 1 : ARCHITECTURE ---
    story.append(Paragraph("TP5 : Systeme de Recherche d'Information (SRI)", style_titre))
    story.append(Paragraph("<b>Etudiante :</b> Eya Manai | <b>Classe :</b> 2 LSI - ISI Kef", style_n))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=5, spaceAfter=15))
    story.append(Paragraph("1. Architecture du systeme", style_h2))
    story.append(Paragraph("Le SRI repose sur une collection de 40 documents, un moteur d'indexation TF-IDF et une interface de recherche.", style_n))

    # --- SECTION 2 : INTERFACE ---
    story.append(Paragraph("2. Apercu de l'interface graphique", style_h2))
    if os.path.exists("interface.png"):
        story.append(Image("interface.png", width=15*cm, height=8.5*cm))
    story.append(Spacer(1, 0.5*cm))

    # --- SECTION 3 : ANALYSE COMPARATIVE (Manquante precedemment) ---
    story.append(Paragraph("3. Analyse comparative des modeles", style_h2))
    data = [
        ["Modele", "Classement", "Avantage", "Inconvenient"],
        ["Vectoriel", "Oui (Score)", "Tres precis (Cosinus)", "Lourd a calculer"],
        ["Booleen", "Non (0 ou 1)", "Simple et rapide", "Pas de pertinence"],
        ["Flou", "Oui (Degre)", "Gere l'incertitude", "Regles complexes"]
    ]
    t = Table(data, colWidths=[3*cm, 3*cm, 5*cm, 4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 6)
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("<b>Conclusion :</b> Le modele Vectoriel est le plus performant pour ce projet car il permet de classer les documents par pertinence.", style_n))

    doc.build(story)
    print("REUSSI : Le rapport complet de Eya est genere !")

if __name__ == "__main__":
    generer()