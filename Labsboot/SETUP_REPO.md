# Setup - Créer le repo GitHub séparé pour Labsboot

## 📝 Instructions pour créer un repo GitHub indépendant

### Étape 1 : Créer un nouveau repo GitHub

1. Aller sur [github.com/new](https://github.com/new)
2. Remplir les informations :
   - **Repository name** : `Labsboot`
   - **Description** : `Projet pédagogique sur les bootkits, MBR, VBR, UEFI - Recherche en sécurité du démarrage`
   - **Visibility** : Public (documentation pédagogique)
   - **Add README** : Non (on a le nôtre)
   - **Add .gitignore** : Non (on a le nôtre)
   - **Add license** : Oui - MIT ou Educational

3. Cliquer **"Create repository"**

### Étape 2 : Initialiser le repo local

```bash
# Aller au répertoire Labsboot
cd G:\Mon\ Drive\CyberSécurite\RansomwareProjet\Labsboot

# Initialiser git
git init

# Ajouter tous les fichiers
git add .

# Commit initial
git commit -m "Initial commit: Labsboot - Bootkit educational lab"

# Ajouter le remote GitHub
git remote add origin https://github.com/mpigajesse/Labsboot.git

# Changer la branche par défaut à 'main'
git branch -M main

# Push vers GitHub
git push -u origin main
```

### Étape 3 : Configurer les branches & protections

Sur GitHub :
1. **Settings** > **Branches**
2. **Add rule** pour protéger `main` :
   - Require pull request reviews
   - Require status checks
   - Dismiss stale PR approvals

### Étape 4 : Ajouter des labels & milestones

**Labels** :
- `educational` - Contenu pédagogique
- `lab` - Exercice/laboratoire
- `bootkit` - Sujet bootkit
- `mbr-vbr` - Sujet MBR/VBR
- `petya` - Analyse Petya
- `security-research` - Recherche sécurité
- `help wanted` - Contributeurs bienvenus

**Milestones** :
- v1.0 - Documentation de base
- v1.1 - Laboratoires implémentés
- v2.0 - Outils forensiques complets

## 🔐 Configuration de sécurité GitHub

### Secrets & Tokens

⚠️ **JAMAIS commiter** :
- Clés de chiffrement
- Tokens d'accès
- Credentials
- Chemins sensibles

### Branch Protection

```yaml
# main branch rules
- Require pull request reviews (2 approvals)
- Require status checks to pass
- Require branches to be up to date
- Include administrators
```

## 📚 Structure GitHub finale

```
mpigajesse/Labsboot/
├── README.md                   # Documentation principale
├── requirements.txt            # Dépendances Python
├── .gitignore                  # Fichiers à ignorer
├── SETUP_REPO.md              # Ce fichier
├── docs/
│   ├── MBR_VBR_explained.md
│   ├── UEFI_security.md
│   ├── Petya_analysis.md
│   └── Bootkit_detection.md
├── resources/
│   ├── references.md
│   ├── tools.md
│   └── datasets.md
├── labs/
│   ├── lab1_mbr_analysis/
│   ├── lab2_vbr_modification/
│   ├── lab3_bootkit_detection/
│   └── lab4_petya_simulation/
└── tools/
    ├── mbr_analyzer.py
    ├── vbr_reader.py
    ├── bootkit_detector.py
    └── forensic_tools.py
```

## 🚀 Workflow GitHub Actions (Optional)

```yaml
name: Tests & Documentation

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run pylint
        run: pip install pylint && pylint tools/
      - name: Check security
        run: pip install bandit && bandit -r tools/
  
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build docs
        run: pip install sphinx && sphinx-build docs/ docs/_build/
```

## 📊 Release & Versioning

### Semantic Versioning

```
v1.0.0
│    │    │
│    │    └─ Patch (bug fixes)
│    └────── Minor (new features)
└──────────── Major (breaking changes)
```

### Création d'une release

```bash
# Créer un tag
git tag -a v1.0.0 -m "v1.0.0 - Initial documentation release"

# Push le tag
git push origin v1.0.0
```

Sur GitHub : **Releases** > **Draft a new release** > Sélectionner le tag

## 🎯 Contribution Guidelines

Créer un `CONTRIBUTING.md` :

```markdown
# Contributing to Labsboot

## Code of Conduct
- Respect pédagogique obligatoire
- Pas de contenu malveillant réel
- Isolation VM obligatoire pour tests

## How to Contribute
1. Fork le repo
2. Créer une branche (`git checkout -b feature/description`)
3. Commit les changements
4. Push vers la branche
5. Ouvrir une Pull Request

## Testing
- Tous les labs doivent passer en VM
- Pas de tests destructifs sur hôte
- Documentation requise pour chaque lab
```

## ✅ Checklist finales

- [ ] Repo GitHub créé
- [ ] README complet
- [ ] .gitignore configuré
- [ ] requirements.txt finalisé
- [ ] Premiers commits pushés
- [ ] Branch protection activée
- [ ] Labels & milestones créés
- [ ] GitHub Actions (optionnel)
- [ ] CONTRIBUTING.md ajouté
- [ ] GitHub Pages pour docs (optionnel)

---

## 📌 Liens utiles

- **Repo**: https://github.com/mpigajesse/Labsboot
- **Issues**: https://github.com/mpigajesse/Labsboot/issues
- **Discussions**: https://github.com/mpigajesse/Labsboot/discussions
- **Wiki**: https://github.com/mpigajesse/Labsboot/wiki

---

**Labsboot est maintenant un projet GitHub séparé et indépendant du Ransomware project ! 🎉**
