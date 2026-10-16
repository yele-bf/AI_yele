# Registre des révisions — `yele-bf/<DÉPÔT>`

> Une ligne par contribution **mergée** (CONTRIBUTING §5). Le hash de commit est
> complété **après** le merge. Vocabulaire de statut : `À faire | En cours |
> Transmis | Validé | Rejeté | À re-vérifier`.

| Date | Sous-ID (V11) | Type | Agent | Owner (classeur) | Branche / PR | Commit | Validation | Statut |
|---|---|---|---|---|---|---|---|---|
| 2026-10-14 | IMP-11 | feat | _(exemple — à remplacer)_ | COMPAORE Bobodo Kévin Aymar | `imp/IMP-11-export-csv` | _après merge_ | local Chrome | En cours |
| 2026-10-14 | ISS-12 | fix | _(exemple — à remplacer)_ | COMPAORE Bobodo Kévin Aymar | `iss/ISS-12-reglages` | _après merge_ | APK réel | Transmis |

## Nomenclature V11 vs V4 (à lire avant de citer un Sous-ID)

- **Baromètre de comparaison = IMP-09 en V11** (il s'appelait **IMP-11 en V4**).
  Deux commits déjà poussés portent l'ancien libellé et doivent être référencés
  comme **IMP-09** : `16d2a89` (mobilefront), `836b4cf` (mobiletest).
- **IMP-11 en V11 = export CSV/JSON** des mesures depuis le dashboard ou l'API :
  **pas encore implémenté** (périmètre `mobiletest` + `New_web`). Ne jamais
  citer `IMP-11` pour le baromètre.

## État connu au 14/10/2026 (audit des commits déjà poussés)

Cette section est documentaire : elle reflète l'historique **antérieur** à la
mise en place du garde-fou, dont les commits ne respectent pas encore le §2.

| Sous-ID | Commits poussés | Validation | Statut |
|---|---|---|---|
| IMP-09 | `16d2a89` (mobilefront), `836b4cf` (mobiletest) — libellé « IMP-11 » au moment du commit | Local (écran résultat + base) | Validé |
| IMP-04 | `f9c2f0e` | APK réel | Validé |
| IMP-08 | `1f6f62a` | APK réel | Validé |
| IMP-13 | `fb7cccd`, `7f81eac` | APK réel | Validé |
| ISS-09 | `1a889e3` | APK (GPS off) | Validé |
| ISS-12 | `709dd26` | Chrome + APK | Validé |

## Suivi des 25 items V11 (une ligne par Sous-ID — référence du garde-fou §5)

| Sous-ID | Intitulé (V11) | Owner (classeur) | Statut classeur |
|---|---|---|---|
| IMP-01 | Consommation data — P3 | COMPAORE Bobodo Kévin Aymar | Valide |
| IMP-02 | Paramètres — P3 | NANA Amoin Agnès / Cissé Aboubacar Sidiki | Valide |
| IMP-03 | Compte utilisateur — P3 | SANOU Zossoun Aristide Daouda / SANNA Abdoul Salam | Transmis |
| IMP-04 | Permissions — P3 | COMPAORE Bobodo Kévin Aymar | Valide |
| IMP-05 | Échelle de score — P2 | TRAORE Abdoulaye / KIEMA François | Valide |
| IMP-06 | Référentiel ARCEP — P2 | NIKIEMA Abdoul Fatahou / NONGUIERMA WENDINSOO LEONEL | Valide |
| IMP-07 | Débit / Latence — P2 | TRAORE Oumou Kal / Ilboudo Wendpagnagdé Elsa Fleur | En cours |
| IMP-08 | Consommation data — P3 | COMPAORE Bobodo Kévin Aymar | Valide |
| IMP-09 | Comparaison — P3 | SANOU Zossoun Aristide Daouda / SANNA Abdoul Salam | Transmis |
| IMP-10 | Dashboard / Carte — P3 | SAWADOGO Wend-kuni Cédric / KOUNANGA Benoit / ZOUNGRANA Wendkuni Brice Yannick / OUEDRAOGO AZIZ | Valide |
| IMP-11 | Données / Export — P2 | COMPAORE Bobodo Kévin Aymar | Valide |
| IMP-12 | Échelle de score — P2 | TRAORE Abdoulaye / KIEMA François | Valide |
| IMP-13 | Identification appareil — P3 | COMPAORE Bobodo Kévin Aymar | Valide |
| ISS-01 | Mesures radio — P1 | SAWADOGO Hassan Achraf Ammar | Valide |
| ISS-02 | Identification réseau — P1 | BAMBA Seydou / NANEMA Wendinkonté Dimitri Judicaël | Valide |
| ISS-03 | Identification réseau — P1 | SAWADOGO Hassan Achraf Ammar | Valide |
| ISS-04 | Serveur — P1 | KOHOUN Damou Daniel / TAMINI Heremave | Valide |
| ISS-05 | Comparaison — P1 | ZOUNGRANA Wendkuni Brice Yannick / OUEDRAOGO AZIZ | Valide |
| ISS-06 | Débit / Latence — P2 | Wangraoua Aicha Bénédicte Flore Myriam / SAWADOGO Sutongnoma Saturnin | Valide |
| ISS-07 | Streaming — P2 | SAWADOGO Hassan Achraf Ammar | Valide |
| ISS-08 | Synchronisation — P2 | BAMBA Seydou / NANEMA Wendinkonté Dimitri Judicaël | Valide |
| ISS-09 | GPS — P2 | COMPAORE Bobodo Kévin Aymar | Valide |
| ISS-10 | Historique — P2 | SAWADOGO Hassan Achraf Ammar | Valide |
| ISS-11 | Dashboard / Carte — P2 | COMPAORE Bobodo Kévin Aymar | Valide |
| ISS-12 | Paramètres — P2 | COMPAORE Bobodo Kévin Aymar | Valide |

## Suivi des 25 items V11 (une ligne par Sous-ID — référence du garde-fou §5)

| Sous-ID | Intitulé (V11) | Owner (classeur) | Statut classeur |
|---|---|---|---|
| IMP-01 | Consommation data — P3 | COMPAORE Bobodo Kévin Aymar | Valide |
| IMP-02 | Paramètres — P3 | NANA Amoin Agnès / Cissé Aboubacar Sidiki | Valide |
| IMP-03 | Compte utilisateur — P3 | SANOU Zossoun Aristide Daouda / SANNA Abdoul Salam | Transmis |
| IMP-04 | Permissions — P3 | COMPAORE Bobodo Kévin Aymar | Valide |
| IMP-05 | Échelle de score — P2 | TRAORE Abdoulaye / KIEMA François | Valide |
| IMP-06 | Référentiel ARCEP — P2 | NIKIEMA Abdoul Fatahou / NONGUIERMA WENDINSOO LEONEL | Valide |
| IMP-07 | Débit / Latence — P2 | TRAORE Oumou Kal / Ilboudo Wendpagnagdé Elsa Fleur | En cours |
| IMP-08 | Consommation data — P3 | COMPAORE Bobodo Kévin Aymar | Valide |
| IMP-09 | Comparaison — P3 | SANOU Zossoun Aristide Daouda / SANNA Abdoul Salam | Transmis |
| IMP-10 | Dashboard / Carte — P3 | SAWADOGO Wend-kuni Cédric / KOUNANGA Benoit / ZOUNGRANA Wendkuni Brice Yannick / OUEDRAOGO AZIZ | Valide |
| IMP-11 | Données / Export — P2 | COMPAORE Bobodo Kévin Aymar | Valide |
| IMP-12 | Échelle de score — P2 | TRAORE Abdoulaye / KIEMA François | Valide |
| IMP-13 | Identification appareil — P3 | COMPAORE Bobodo Kévin Aymar | Valide |
| ISS-01 | Mesures radio — P1 | SAWADOGO Hassan Achraf Ammar | Valide |
| ISS-02 | Identification réseau — P1 | BAMBA Seydou / NANEMA Wendinkonté Dimitri Judicaël | Valide |
| ISS-03 | Identification réseau — P1 | SAWADOGO Hassan Achraf Ammar | Valide |
| ISS-04 | Serveur — P1 | KOHOUN Damou Daniel / TAMINI Heremave | Valide |
| ISS-05 | Comparaison — P1 | ZOUNGRANA Wendkuni Brice Yannick / OUEDRAOGO AZIZ | Valide |
| ISS-06 | Débit / Latence — P2 | Wangraoua Aicha Bénédicte Flore Myriam / SAWADOGO Sutongnoma Saturnin | Valide |
| ISS-07 | Streaming — P2 | SAWADOGO Hassan Achraf Ammar | Valide |
| ISS-08 | Synchronisation — P2 | BAMBA Seydou / NANEMA Wendinkonté Dimitri Judicaël | Valide |
| ISS-09 | GPS — P2 | COMPAORE Bobodo Kévin Aymar | Valide |
| ISS-10 | Historique — P2 | SAWADOGO Hassan Achraf Ammar | Valide |
| ISS-11 | Dashboard / Carte — P2 | COMPAORE Bobodo Kévin Aymar | Valide |
| ISS-12 | Paramètres — P2 | COMPAORE Bobodo Kévin Aymar | Valide |
