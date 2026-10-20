#!/usr/bin/env python3
"""yele_guard — garde-fou « commit ↔ classeur V14 » (CONTRIBUTING §2 et §5).

Usage :
    python3 scripts/ci/yele_guard.py <base_sha> <head_sha>
    python3 scripts/ci/yele_guard.py --items docs/items-v14.json \
        --registry docs/registre-revisions.md <base_sha> <head_sha>

Contrôles, pour chaque commit **non-merge** de <base_sha>..<head_sha> :

  1. le sujet suit `<type>(<périmètre>): <descriptif>`   (§2)
     type ∈ feat | fix | docs | refactor | perf | test | chore
  2. tout Sous-ID cité (IMP-xx / ISS-xx), dans le sujet ou le corps, existe
     dans items-v14.json (l'extraction de l'onglet « Completion »)          (§2)
  3. le corps porte un trailer `Agent: <nom>`                              (§5)
  4. tout Sous-ID cité possède une ligne dans registre-revisions.md        (§5)

Code de sortie : 0 si tout passe, 1 dès qu'un contrôle échoue.
"""
import argparse
import json
import os
import re
import subprocess
import sys

SUBJECT_RE = re.compile(r"^(feat|fix|docs|refactor|perf|test|chore)(?:\(([^)]+)\))?: \S.*$")
ID_RE = re.compile(r"\b(?:IMP|ISS)-\d{2}\b")
AGENT_RE = re.compile(r"^Agent:[ \t]*\S.*$", re.M)
DEFAULT_ITEMS = os.path.join("docs", "items-v14.json")
DEFAULT_REGISTRY = os.path.join("docs", "registre-revisions.md")


def _sortie_utf8():
    """Évite un plantage d'encodage hors Linux (console Windows cp1252, CI LANG=C)."""
    for flux in (sys.stdout, sys.stderr):
        try:
            flux.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def git(*args):
    return subprocess.check_output(["git", *args], text=True)


def read_commits(base, head):
    """Retourne [(sha, sujet, corps)] pour les commits non-merge de base..head."""
    raw = git("log", "--no-merges", "--format=%H%x1f%s%x1f%b%x1e", f"{base}..{head}")
    for bloc in raw.split("\x1e"):
        bloc = bloc.strip("\n")
        if not bloc.strip():
            continue
        parties = bloc.split("\x1f")
        sha = parties[0]
        sujet = parties[1] if len(parties) > 1 else ""
        corps = parties[2] if len(parties) > 2 else ""
        yield sha, sujet.strip(), corps


def main(argv=None):
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--items", default=DEFAULT_ITEMS)
    parseur.add_argument("--registry", default=DEFAULT_REGISTRY)
    parseur.add_argument("base", help="SHA de base, ou directement la plage BASE..HEAD")
    parseur.add_argument("head", nargs="?", help="SHA de tête (omettre si la plage est donnée)")
    args = parseur.parse_args(argv)
    _sortie_utf8()

    if args.head is None:
        if ".." not in args.base:
            parseur.error("fournir soit BASE HEAD, soit la plage BASE..HEAD")
        args.base, args.head = args.base.split("..", 1)

    if not os.path.exists(args.items):
        print(
            f"yele_guard · ERREUR : {args.items.replace(os.sep, '/')} est absent — "
            "dépôt non préparé (voir CONTRIBUTING §2).",
            file=sys.stderr,
        )
        return 1
    with open(args.items, encoding="utf-8") as f:
        items = json.load(f)["items"]
    connus = {i["sousId"] for i in items}

    registre = ""
    if os.path.exists(args.registry):
        with open(args.registry, encoding="utf-8") as f:
            registre = f.read()

    erreurs, nb = [], 0
    for sha, sujet, corps in read_commits(args.base, args.head):
        nb += 1
        court = sha[:8]

        if not SUBJECT_RE.match(sujet):
            erreurs.append(
                f"{court} · sujet non conforme au §2 → « {sujet} »\n"
                f"           attendu : <type>(<périmètre>): <descriptif>"
            )

        cites = set(ID_RE.findall(f"{sujet}\n{corps}"))
        inconnus = sorted(cites - connus)
        if inconnus:
            erreurs.append(
                f"{court} · Sous-ID absent du classeur V14 → {', '.join(inconnus)}"
            )

        if not AGENT_RE.search(corps):
            erreurs.append(
                f"{court} · trailer « Agent: <nom> » manquant dans le corps du commit"
            )

        for sous_id in sorted(cites & connus):
            if not re.search(r"\|[ \t]*" + re.escape(sous_id) + r"[ \t]*\|", registre):
                erreurs.append(
                    f"{court} · {sous_id} n'a pas de ligne dans "
                    f"{args.registry.replace(os.sep, '/')}"
                )

    print(f"yele_guard · {nb} commit(s) vérifié(s) sur {args.base[:8]}..{args.head[:8]}")
    if not erreurs:
        print("OK - lien commit <-> classeur V14 conforme.")
        return 0
    print(f"\n{len(erreurs)} problème(s) :\n")
    for e in erreurs:
        print(f"  x {e}")
    print("\nVoir CONTRIBUTING.md §2 (format des commits) et §5 (registre).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
