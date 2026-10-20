## Sous-ID V14

`IMP-xx` / `ISS-xx` → <!-- doit exister dans docs/items-v14.json -->

Titre de la PR = même format que le commit : `<type>(<SOUS-ID>): <descriptif>`

## Constat du classeur (onglet « Completion Correct. & Amelior. »)

<!-- coller la ligne « Problème / Constat » de l'item, sans la reformuler -->

## Critère d'acceptation

<!-- tel qu'il figure dans le classeur -->

## Ce que fait cette PR

-

## Dépôts impactés

- [ ] `mobilefront`   - [ ] `mobiletest`   - [ ] `New_web`   - [ ] `AI_yele`

## Validation (support imposé par le classeur)

<!-- APK réel / terrain / local Chrome / Mongo local / … avec ce qui a été observé -->

## Agent et owner

- **Agent** : <!-- NOM Prénom, l'auteur réel du code -->
- **Owner (colonne du classeur)** :

## Liste de contrôle

- [ ] Branche nommée `<type>/<SOUS-ID>-<slug>`, repartie de `main` à jour
- [ ] Un seul Sous-ID traité dans cette PR
- [ ] Commit(s) au format `<type>(<SOUS-ID>): …` avec le trailer `Agent:`
- [ ] Ligne ajoutée dans `docs/registre-revisions.md` (colonne `Commit` remplie après merge)
- [ ] Fiche d'impact `docs/fiches/<SOUS-ID>-<slug>.md`
- [ ] Aucun secret, aucun `git add -A`, aucun `--force`
- [ ] `yele-guard` vert
