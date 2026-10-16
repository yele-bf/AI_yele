#!/usr/bin/env python3
"""py_check — contrôle statique du module IA (sans installer les dépendances).

   1. compilation (syntaxe) de tous les .py du dépôt, hors environnements
      virtuels, caches et données ;
   2. service.py expose bien un point d'entrée module-level `app`
      (l'application FastAPI), vérifié par analyse AST — aucun import réel,
      donc pas besoin de fastapi/pyod/torch dans la CI.

Sortie : 0 si tout passe, 1 dès qu'un problème est détecté.
"""
import ast
import os
import sys

RACINE = os.getcwd()
IGNORES = {".git", ".github", ".venv", "venv", "__pycache__", ".ipynb_checkpoints",
           "dataset", "node_modules"}
problemes = []
nb_py = 0


def fichiers_py(dossier):
    for nom in sorted(os.listdir(dossier)):
        if nom in IGNORES:
            continue
        chemin = os.path.join(dossier, nom)
        if os.path.isdir(chemin):
            fichiers_py(chemin)
        elif nom.endswith(".py"):
            verifier(chemin)


def verifier(chemin):
    global nb_py
    nb_py += 1
    relatif = os.path.relpath(chemin, RACINE).replace(os.sep, "/")
    source = open(chemin, encoding="utf-8", errors="replace").read()
    try:
        arbre = ast.parse(source, filename=relatif)
    except SyntaxError as erreur:
        problemes.append(f"{relatif} · syntaxe Python invalide → {erreur.msg} (ligne {erreur.lineno})")
        return
    if os.path.basename(chemin) == "service.py":
        noms = {
            cible.id
            for noeud in arbre.body
            if isinstance(noeud, ast.Assign)
            for cible in noeud.targets
            if isinstance(cible, ast.Name)
        }
        if "app" not in noms:
            problemes.append("service.py · point d'entrée « app » (FastAPI) introuvable au niveau module")


fichiers_py(RACINE)
print(f"py_check · {nb_py} fichier(s) Python analysé(s)")

if not problemes:
    print("OK - aucun problème détecté.")
    sys.exit(0)
print(f"\n{len(problemes)} problème(s) :\n")
for p in problemes:
    print(f"  x {p}")
sys.exit(1)
