# Premier pas — d'une issue à une PR verte

> Pour un agent qui arrive sur un dépôt de `yele-bf`. Les règles complètes sont
> dans [`CONTRIBUTING-equipe.md`](CONTRIBUTING-equipe.md) ; ce guide ne donne
> que la suite concrète des commandes, dans l'ordre.

## 1. Choisir son item

Chaque item du classeur V14 a **une issue** dans le dépôt principal :
`docs/issues-map.md` donne le numéro et le lien. Une branche = **un seul
Sous-ID** (`IMP-14`, `ISS-07`, …).

## 2. Cloner et partir de `main` à jour

```bash
git clone https://github.com/yele-bf/mobilefront.git
cd mobilefront
git checkout main && git pull
git checkout -b imp/IMP-14-conditions-utilisation
```

Nom de branche : `<type>/<SOUS-ID>-<slug>`, avec `type` ∈ `imp` / `iss` /
`docs` / `fix`. La même branche porte le même nom dans chaque dépôt touché.

## 3. Travailler, puis commiter

Le sujet **doit** suivre `<type>(<périmètre>): <descriptif>` et le corps
**doit** porter le trailer `Agent:` :

```bash
git add lib/screens/conditions_screen.dart docs/fiches/IMP-14-conditions-utilisation.md
git commit -m "$(cat <<'EOF'
feat(IMP-14): accepter les conditions au premier lancement

Critère : première ouverture = écran de conditions bloquant ; ouvertures
suivantes = accès direct. Validé en local Chrome puis APK.

Agent: SANOU Zossoun Aristide Daouda
EOF
)"
```

`type` ∈ `feat | fix | docs | refactor | perf | test | chore`.

## 4. Mettre à jour le registre **dans la même PR**

Le garde-fou refuse un commit qui cite un Sous-ID absent de
`docs/registre-revisions.md`. Ajoute ta ligne avant de pousser :

| Date | Sous-ID (V14) | Type | Agent | Owner (classeur) | Branche / PR | Commit | Validation | Statut |
|---|---|---|---|---|---|---|---|---|
| 2026-10-21 | IMP-14 | feat | SANOU Zossoun Aristide Daouda | SANOU Zossoun Aristide Daouda | `imp/IMP-14-conditions-utilisation` | _après merge_ | Chrome + APK | En cours |

## 5. Pousser et ouvrir la PR

```bash
git push -u origin imp/IMP-14-conditions-utilisation
```

GitHub affiche « Compare & pull request ». Le gabarit se remplit tout seul :
Sous-ID, constat, critère d'acceptation, dépôts impactés, liste de contrôle.
Termine le corps par `Closes #27`.

## 6. Attendre les deux checks

| Check | Ce qu'il vérifie | Où le lire |
|---|---|---|
| `guard` | format du commit, Sous-ID connu du classeur, trailer `Agent:`, ligne de registre | onglet *Checks* de la PR |
| `build` | que le dépôt compile et que ses tests passent | idem |

Une PR rouge n'est pas un échec personnel : le message d'erreur nomme le
fichier ou le champ fautif. Corrige, `git commit --amend` ou nouveau commit,
`git push` — la PR se relance seule.

## 7. Revue et merge

Un membre (idéalement le chef de groupe titulaire de l'item, voir
`CONTRIBUTING-equipe.md` §1.4) relit. Le merge se fait en **squash** ;
la branche est supprimée ensuite.

---

## Les 6 pièges qui font échouer la CI

1. **Sujet sans `type(...) :`** → `guard` rouge. `Ajout ecran conditions` est refusé, `feat(IMP-14): ajout ecran conditions` passe.
2. **Sous-ID inexistant** (`IMP-99`, `IMP-11` pour le baromètre qui est `IMP-09`) → `guard` rouge : « Sous-ID absent du classeur V14 ».
3. **Pas de trailer `Agent: NOM Prénom`** dans le corps → `guard` rouge.
4. **Aucune ligne dans `docs/registre-revisions.md`** pour le Sous-ID cité → `guard` rouge, même si le code est parfait.
5. **Push direct sur `main`** → refusé (branche protégée) ; tout passe par une PR.
6. **`git add -A` ou `--force`** → jamais : cela embarque les fichiers locaux non suivis (`.env`, exports, `*.json`) et réécrit l'historique des autres.
