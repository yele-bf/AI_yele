# CONTRIBUTING — Équipe YELE (22 agents · organisation GitHub `yele-bf`)

> Convention de collaboration validée le 09/10/2026 par le porteur du projet,
> mise à jour le 20/10/2026 sur la base du cahier des charges **V14
> (19.10.2026)** — onglets « Completion Correct. & Amelior. », « Cahier des
> charges » et « Analyse & Planning » : **27 Sous-ID** (15 IMP, 12 ISS).
> La référence des items est `docs/items-v14.json`. L'archive V11 (25 items)
> reste dans `docs/items-v11.json` mais **n'est plus lue par la CI**.
> Ce document fait foi pour les 4 dépôts
> de l'organisation : `yele-bf/mobilefront` (app Flutter),
> `yele-bf/mobiletest` (backend Go), `yele-bf/New_web` (dashboard web),
> `yele-bf/AI_yele` (service IA FastAPI).

---

## 1. Modèle de collaboration (validé)

- **Dépôts partagés** de l'organisation (pas de fork par défaut). Le fork est
  réservé aux contributeurs **externes** sans droits d'écriture.
- **GitHub Flow** : une seule branche `main`, **protégée**, des **branches
  feature courtes** et des **Pull Requests obligatoires**.
- Pas de Gitflow complet (pas de `develop`, pas de branches `release`):
  les dépôts se déploient indépendamment et les livraisons se font par
  **vagues thématiques** (tags).

### 1.1 Règles de branche

| Règle | Détail |
|---|---|
| Nom | `<type>/<SOUS-ID>-<slug>` : `imp/IMP-11-export-csv`, `iss/ISS-12-reglages` |
| Source | toujours depuis `main` à jour |
| Durée | **courte** (< 2-3 jours) ; une branche = **un Sous-ID du classeur V14** |
| Multi-dépôts | même nom de branche dans chaque dépôt touché ; les PR se référencent mutuellement (`yele-bf/mobiletest#12`) |
| Merge | **squash merge uniquement** → 1 PR = 1 commit traçable dans `main` |

### 1.2 Règles de Pull Request

1. Titre = même format que les commits (§2), corps pré-rempli :
   - `Sous-ID V14 :` (ex. `IMP-11`, `IMP-15`)
   - `Critères d'acceptation :` (repris du classeur)
   - `Validation :` (colonne « Validation / test » du classeur : Chrome/APK/local)
   - `Dépôts impactés :`
2. La PR **ferme l'issue** correspondante (`Closes #n`) — issues à créer, §1.3.
3. Review d'**au moins 1 membre** avant merge (aucun reviewer imposé : le
   `CODEOWNERS` est indicatif, voir §1.3).
4. CI verte obligatoire : les checks **`guard`** (commits ↔ classeur V14) et
   **`build`** (compilation/tests du dépôt) sont requis sur `main`.
5. La fiche d'impact (§4) est jointe ou déjà commitée dans la même PR.

### 1.3 Mise en place GitHub (état au 20/10/2026)

**Fait**

- [x] `main` protégée sur les 4 dépôts : PR obligatoire, **1 review**, checks
      requis, historique linéaire, force-push et suppression interdits.
      (`enforce_admins` désactivé : seul le porteur peut contourner.)
- [x] Fusions en **squash uniquement**, branche supprimée après merge.
- [x] Checks obligatoires : **`guard`** (`.github/workflows/yele-guard.yml`,
      `scripts/ci/yele_guard.py`, `docs/items-v14.json`,
      `docs/registre-revisions.md`) et **`build`**
      (`.github/workflows/yele-build.yml`) : `flutter analyze` + `flutter test`
      (mobilefront), `go build/vet/test` (mobiletest), syntaxe JS et ressources
      de `index.html` (New_web), syntaxe Python et point d'entrée du service
      (AI_yele).
- [x] Équipe `nperf-agents` : permission **write** (push / triage / pull) sur
      les 4 dépôts, **sans** `admin` ni `maintain`.
- [x] **9 chefs de groupe** membres actifs de l'organisation, tous rattachés à
      `nperf-agents` : `KikaiNoKami`, `aspinfo10`, `SeydouBamba`, `firminosama`,
      `yanzo-prime`, `taminiH`, `Aicha710`, `agnesnana-hash`, `angedemon`
      (= SANOU Zossoun Aristide Daouda, Groupe 10).
- [x] **27 Issues** créées (une par Sous-ID du classeur V14) —
      `docs/issues-map.md`.
- [x] **GitHub Project** « Chantier C2 nPerf — 22 agents » créé.
- [x] `CODEOWNERS` renseigné avec les comptes réellement membres.
- [x] `CONTRIBUTING` et gabarit de PR disponibles dans les 4 dépôts.

**À faire**

- [ ] `Fatahou980` (NIKIEMA Abdoul Fatahou, Groupe 4) : invitation **en attente**
      depuis le 20/10/2026. GitHub l'expire au bout de 7 jours ; à relancer
      depuis *Org → People → Invitations* s'il n'a pas accepté.
- [ ] Inviter les **membres de groupe** (11 personnes encore en « N.A. » dans
      l'onglet « Liens perso Github ») dès que leurs comptes GitHub existent.
- [ ] Renseigner les `CODEOWNERS` de périmètre fin au fur et à mesure que ces
      membres arrivent (une nomination ne fonctionne qu'avec un compte membre).
- [ ] **Sécurité** : les 4 dépôts sont `public` et sont des `fork` — tout push
      est immédiatement visible publiquement ; `.env` et secrets restent hors
      dépôt.
- [ ] **Sécurité** : le PAT de développement est encore présent en clair dans
      `repos/*/.git/config` (local uniquement, jamais committé) ; prévoir
      `gh auth login` / credential manager lors de la rotation.

### 1.4 Groupes, chefs de groupe et périmètres (classeur V14)

Dix groupes de travail ; chaque groupe est représenté sur GitHub par son
**chef de groupe**. Les Sous-ID listés sont ceux dont il est owner dans
l'onglet « Completion Correct. & Amelior. » : c'est le périmètre sur lequel il
est reviewer naturel (voir `CODEOWNERS`).

| Grp | Chef de groupe | Compte GitHub | Items (owner au classeur) |
|---|---|---|---|
| 1 | COMPAORE Bobodo Kévin Aymar | `KikaiNoKami` | IMP-01, IMP-04, IMP-08, IMP-11, IMP-13, ISS-09, ISS-11, ISS-12 |
| 2 | SAWADOGO Hassan Achraf Ammar | `aspinfo10` | ISS-01, ISS-03, ISS-07, ISS-10 |
| 3 | BAMBA Seydou | `SeydouBamba` | ISS-02, ISS-08 |
| 4 | NIKIEMA Abdoul Fatahou | `Fatahou980` *(invitation en attente)* | IMP-06 |
| 5 | TRAORE Abdoulaye | `firminosama` | IMP-05, IMP-12 |
| 6 | ZOUNGRANA Wendkuni Brice Yannick | `yanzo-prime` | IMP-10, ISS-05 |
| 7 | TAMINI Heremave | `taminiH` | ISS-04 |
| 8 | Wangraoua Aicha Bénédicte Flore Myriam | `Aicha710` | ISS-06 |
| 9 | NANA Amoin Agnès | `agnesnana-hash` | IMP-02 |
| 10 | SANOU Zossoun Aristide Daouda | `angedemon` | IMP-03, IMP-07, IMP-09, **IMP-14**, **IMP-15** |

Règle de review : le chef de groupe du Sous-ID est reviewer en priorité ; à
defaut, n'importe quel autre membre (`CODEOWNERS` reste **indicatif** : GitHub
ne bloque pas le merge sur une review manquante, le check `guard` et la review
obligatoire de la protection de `main` font foi).

---

## 2. Nomenclature des commits (Conventional Commits + Sous-ID obligatoire)

```
<type>(<sous-id>): <descriptif concis>

<corps facultatif : avant/après, décision, liens>
```

- `type` ∈ `feat | fix | docs | refactor | perf | test | chore`
- `sous-id` = identifiant **V14** du classeur (ex. `IMP-11`, `IMP-15`, `ISS-09`) ;
  hors item, utiliser le périmètre : `feat(api): …`, `docs(equipe): …`.
- Le corps mentionne systématiquement : critère d'acceptation vérifié et
  support de validation (« terrain APK », « local Chrome », …).

Exemples :

```
feat(IMP-11): export CSV/JSON des mesures filtrées depuis l'API dashboard
fix(ISS-12): persister le choix d'unité de débit dans la box appSettings
docs(IMP-09): fiche de correction du baromètre de comparaison
```

## 3. CHANGELOG (Keep a Changelog 1.1.0)

- Un `CHANGELOG.md` **par dépôt** + un `CHANGELOG-global.md` (socle unique).
- Section `## [Non publiée]` toujours à jour, catégories :
  `Ajouté / Modifié / Corrigé / Supprimé`.
- Une **version par vague** (`v1-quickwins`, `v2-reseau-app`, …) avec date ISO.
- Les *release notes* (rédigées à la main) restent distinctes du CHANGELOG.

## 4. Fiche d'impact par item

Gabarit : `docs/modeles/fiche-impact-modele.md` → une fiche par Sous-ID dans
`docs/fiches/<SOUS-ID>-<slug>.md`. Obligatoire dans la PR.

## 5. Registre des révisions

`docs/registre-revisions.md` : une ligne par contribution **mergée**
(Sous-ID · type · owner · dépôt · hash · branche/PR · validation · statut).
Mise à jour dans la même PR que le merge.

## 6. Statuts & règle de sortie de vague

Vocabulaire unique (classeur V14, fiches, PR, Project) :

```
À faire → En cours → Transmis → Validé   (ou : Rejeté / À re-vérifier)
```

Un item passe **Validé** que si les 4 conditions sont réunies :
1. PR mergée dans `main` (hash de commit renseigné) ;
2. fiche d'impact complétée ;
3. critère d'acceptation vérifié ;
4. validation réalisée sur le support imposé par le classeur.

> **Règle anti-divergence** : aucun statut « Valide » sans hash de commit.
> (Précédent : V11-IMP-11 marqué « Valide » sans implémentation.)

## 7. Secrets & environnements

- Aucun secret dans le dépôt ni dans les URLs `remote` ; `.env` ignoré.
- Variables d'API backend en *Settings → Secrets and variables → Actions*.
- Le dashboard `config.js` ne contient que des URLs publiques.

## 8. Vagues (release trains)

| Tag | Contenu |
|---|---|
| `v1-quickwins` | V1 Quick wins — IMP-04, IMP-11, IMP-13, IMP-14, ISS-04, ISS-09, ISS-11 |
| `v2-reseau-app` | V2 Réseau app (terrain) — ISS-01, ISS-02, ISS-03, ISS-07 |
| `v3-mesures` | V3 Mesures & synchronisation — IMP-01, ISS-05, ISS-06, ISS-08, ISS-10, ISS-12 |
| `v4-metriques` | V4 Métriques & score — IMP-07, IMP-08, IMP-12 |
| `v5-referentiel` | V5 Dashboard & référentiel — IMP-05, IMP-06, IMP-09, IMP-10 |
| `v6-evolutions-lourdes` | V6 Évolutions lourdes — IMP-02, IMP-03, IMP-15 |
