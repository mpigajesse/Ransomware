# 📊 Structure Complète du Projet Ransomware & Labsboot

**Date mise à jour** : 2026-08-24  
**Statut** : ✅ Production-Ready  
**Repo** : https://github.com/mpigajesse/Ransomware

---

## 🏗️ Arborescence Globale

```
Ransomware/
├── README.md                    # Documentation principale du projet
├── PROJECT_STRUCTURE.md         # Ce fichier (arborescence détaillée)
│
├── 🔴 kali/                     # MODULE 1: Ransomware Attacker
│   ├── requirements.txt         # Dependencies Python
│   ├── generer_cles.py         # Générateur clés RSA 1024-bit
│   ├── envoyer_cle.py          # Envoi clés via email (yagmail)
│   ├── ransomware.py           # Payload RSA+AES chiffrement
│   ├── ransomware_info.txt     # Metadata infection
│   ├── cle_privee.pem          # Clé privée RSA (attaquant)
│   ├── cle_publique.pem        # Clé publique RSA (chiffrement)
│   └── captures ecrans/         # Documentation visuels
│       ├── *.png               # Screenshots exécution
│       ├── googlelinkspasswordapp.md
│       └── vms.pdf             # Architecture VMs
│
├── 🟡 ubuntu/                   # MODULE 2: Ransomware Victim (Decryption)
│   ├── requirements.txt         # Dependencies Python (crypto)
│   ├── check_ransomware.py     # Détecteur chiffrement
│   └── captures ecrans/         # Screenshots déchiffrage
│       └── *.png
│
└── 🔵 Labsboot/                 # MODULE 3: Bootkit Lab (NEW)
    ├── README.md                # Documentation Labsboot
    ├── BOOTKIT_POC.md          # Objectif: Créer bootkit qui attaque MBR
    ├── IMPLEMENTATION_PLAN.md  # Timeline 3 semaines + VMs setup
    ├── SETUP_REPO.md           # Instructions GitHub repos
    ├── requirements.txt         # Dependencies (cryptography, PyMySQL)
    │
    ├── docs/                    # Documentation technique
    │   └── MBR_VBR_explained.md # Explication MBR/VBR structures
    │
    ├── labs/                    # Laboratoires éducatifs
    │   └── lab1_mbr_analysis/   # Lab 1: MBR Analysis & Forensics
    │       └── instructions.md  # Guide complet (Windows 7 + Ubuntu 24)
    │
    ├── tools/                   # Outils d'analyse & injection
    │   ├── lab1_mbr_analyzer.py # MBRAnalyzer class (anályse MBR)
    │   │   ├── read_mbr()
    │   │   ├── parse_bootcode()
    │   │   ├── parse_partition_table()
    │   │   ├── detect_bootkit_signatures()
    │   │   ├── analyze_heuristics()
    │   │   ├── inject_bootkit()
    │   │   └── compare()
    │
    └── references/              # Ressources apprentissage (NEW)
        ├── README.md            # Index références GitHub
        └── GitHub_References.md # Projets bootkit éducatifs
            ├── OpenPetya
            ├── ANSSI bootcode_parser
            ├── Petya 2017 Notes
            └── OpenPetya-Defense
```

---

## 📋 Descriptif Détaillé par Module

### 🔴 **kali/** - Ransomware Encryption Module

**Objectif** : Créer ransomware éducatif avec chiffrement hybride

**Composants** :
| Fichier | Type | Description |
|---------|------|-------------|
| `generer_cles.py` | Script | Génère paire RSA 1024-bit (public/private) |
| `envoyer_cle.py` | Script | Envoie clé publique via email (yagmail) |
| `ransomware.py` | Malware | Chiffre fichiers via RSA+AES |
| `cle_privee.pem` | Config | Clé privée (pour décryptage) |
| `cle_publique.pem` | Config | Clé publique (pour chiffrement) |
| `ransomware_info.txt` | Metadata | Informations infection |

**Technologies** :
- **cryptography >= 42.0.0** - Opérations RSA/AES
- **PyMySQL >= 1.1.0** - Stockage données infection
- **yagmail >= 0.15.0** - Livraison clés par email

**Flux** :
```
1. Générer clés RSA (2048-bit)
2. Charger fichiers cibles
3. Chiffrer avec AES-256-CBC (IV aléatoire)
4. Chiffrer clé AES avec RSA public
5. Envoyer clé RSA par email
6. Afficher message de rançon
```

---

### 🟡 **ubuntu/** - Ransomware Decryption Module

**Objectif** : Déchiffrer fichiers avec clé privée RSA

**Composants** :
| Fichier | Type | Description |
|---------|------|-------------|
| `check_ransomware.py` | Script | Détecteur chiffrement AES |
| `requirements.txt` | Config | Dependencies décryptage |

**Technologies** :
- **cryptography >= 42.0.0** - Vérification signatures RSA
- **PyMySQL >= 1.1.0** - Accès données infection
- **AES-256-CBC** - Déchiffrage symétrique

---

### 🔵 **Labsboot/** - Bootkit Educational Project

**Objectif Principal** : 
> **Créer un virus qui attaque le secteur de boot**  
> (MBR - Master Boot Record)

**Architecture VMs** :
```
Windows 11 Hôte (VMware Workstation)
    │
    ├─ Windows 7 VM (Cible)         [MBR attaque testée]
    ├─ Ubuntu Server 24 (Analyse)   [MBR forensics]
    └─ Kali Linux (Développement)   [Outils + déploiement]
```

**Composants Labsboot** :

#### `BOOTKIT_POC.md` (453 lignes)
Implémentation complète bootkit éducatif :
- **Phase 1** : Analyse OpenPetya, Petya 2017, ANSSI
- **Phase 2** : 
  - `mbr_stage1.asm` - Code x86 16-bit (446 bytes)
  - `bootkit_implementation.py` - Python PoC
- **Phase 3** : Déploiement sur Windows 7 + Ubuntu 24

**Structure MBR** (512 bytes) :
```
┌─────────────────────────────────┐
│ Bootcode (446 bytes)     ◄───── NOTRE BOOTKIT
│ - Display message
│ - Simulate encryption (beeps)
│ - System halt (reversible)
├─────────────────────────────────┤
│ Partition Table (64 bytes)      (preserved)
│ - 4 entries × 16 bytes
├─────────────────────────────────┤
│ Boot Signature (2 bytes)        (0xAA55)
└─────────────────────────────────┘
```

#### `IMPLEMENTATION_PLAN.md` (337 lignes)
Timeline 3 semaines :
- **Semaine 1** : Infrastructure VMs
- **Semaine 2** : Labs 1-2 (MBR + VBR)
- **Semaine 3** : Labs 3-4 (Detection + Petya Sim)

#### `tools/lab1_mbr_analyzer.py` (357 lignes)
Analyse MBR forensique :

**Classe MBRAnalyzer** :
```python
class MBRAnalyzer:
    # Lecture & parsing
    - read_mbr(file_path)           # Charge 512 bytes
    - parse_bootcode()              # Analyse 446 bytes
    - parse_partition_table()       # Parse 4 entries
    - parse_signature()             # Vérifie 0xAA55
    
    # Détection
    - detect_bootkit_signatures()   # Petya/Rovnix/Gapz
    - analyze_heuristics()          # Anomalies (hidden sectors, checksum)
    - compare()                     # Différences MBRs
    
    # Injection (simulation éducative)
    - inject_bootkit()              # Créer MBR infecté
```

**Méthodes clés** :
- `_calculate_entropy()` - Shannon entropy (détecte chiffrement)
- `_detect_compression()` - Seuil entropie > 7.0

#### `docs/MBR_VBR_explained.md` (5.4 KB)
Documentation technique :
- Structure MBR (bootcode + partition table + signature)
- Hex dumps comparatifs (légitime vs infecté)
- Cas réels (Petya, Rovnix, Gapz)
- Défenses contre bootkits

#### `labs/lab1_mbr_analysis/instructions.md` (295 lignes)
Guide complet lab :
- Extraction MBR (Windows 7 + Ubuntu 24)
- Analyse comparée NTFS vs ext4
- Injection simulation bootkit
- Détection anomalies
- Recovery procédures

#### `references/` (NEW - Changement principal)
**Ressources d'apprentissage** :
- `GitHub_References.md` - Projets bootkit éducatifs
- `README.md` - Index des ressources

**Projets référencés** :
| Projet | Repo | À apprendre |
|--------|------|------------|
| **OpenPetya** | iss4cf0ng | MBR bootcode + stages |
| **ANSSI bootcode_parser** | ANSSI-FR | Forensic analysis |
| **Petya 2017 Notes** | aguinet | Reverse engineering |
| **OpenPetya-Defense** | mutedmouse | YARA rules, detection |

---

## 📊 Données Clés par Module

### Ransomware Keys
```
RSA 1024-bit:
├── Clé Privée : kali/cle_privee.pem (1704 bytes)
├── Clé Publique : kali/cle_publique.pem (426 bytes)
└── Format : PEM text

AES-256-CBC:
├── IV : Random (16 bytes)
├── Key : Dérivée RSA
└── Padding : PKCS7
```

### Labsboot Specs
```
MBR Bootkit:
├── Taille totale : 512 bytes
├── Bootcode : 446 bytes (x86 16-bit real mode)
├── Partition Table : 64 bytes (4 entries × 16)
└── Signature : 2 bytes (0xAA55)

Boot Sequence:
├── BIOS/UEFI → MBR (sector 0)
├── Stage 1 : Notre bootkit code
├── Stage 2 : Payload (optionnel)
└── OS : Windows Boot Manager / GRUB (interception)
```

---

## 🚀 Commandes Principales

### Ransomware Kali
```bash
# Générer clés RSA
python3 kali/generer_cles.py

# Envoyer clé publique
python3 kali/envoyer_cle.py

# Chiffrer fichiers
python3 kali/ransomware.py
```

### Ransomware Ubuntu
```bash
# Vérifier chiffrement
python3 ubuntu/check_ransomware.py

# Déchiffrer (avec clé privée)
python3 ubuntu/decrypt_ransomware.py
```

### Labsboot Tools
```bash
# Analyser MBR
python3 Labsboot/tools/lab1_mbr_analyzer.py --analyze <mbr_file>

# Injecter bootkit (simulation)
python3 Labsboot/tools/lab1_mbr_analyzer.py --inject-bootkit <input> <output>

# Comparer MBRs
python3 Labsboot/tools/lab1_mbr_analyzer.py --compare <file1> <file2>
```

---

## ✅ Checklist Intégration

- ✅ Restructuration Labsboot (boot/ → Labsboot/references/)
- ✅ Création Labsboot/references/README.md
- ✅ Intégration GitHub_References.md
- ✅ Git commit et push
- ✅ README.md principal mis à jour
- ✅ PROJECT_STRUCTURE.md (ce fichier) créé

---

## 📈 Statistiques Projet

```
Total Fichiers:         30+
Total Lignes Code:      2500+
Documentation:          1500+ lignes
Tests Dispos:           Lab 1 - Forensics complet

Composants Actifs:
├── Ransomware (kali)   : 3 scripts Python
├── Decryption (ubuntu) : 1 script Python
└── Labsboot            : 5+ scripts + docs

GitHub Repo:
├── Commits : 10+
├── Branches : main
└── Status : Production-Ready
```

---

## 🔐 Sécurité & Limitations

### Ransomware (Éducatif UNIQUEMENT)
✅ **Avec** :
- Clés RSA 1024-bit PKCS1v15-SHA256
- AES-256-CBC chiffrement symétrique
- Base de données emails

❌ **Sans** :
- Vrai malware payload
- Déploiement en dehors lab
- Demandes rançon réelles

### Labsboot Bootkit (Éducatif UNIQUEMENT)
✅ **Avec** :
- MBR stage 1 x86 16-bit
- Simulation chiffrement (beeps)
- Message de démarrage éducatif

❌ **Sans** :
- Chiffrement données réel
- Persistance malveillante
- Déploiement production

---

## 📚 Apprentissages Clés

1. **Ransomware** :
   - Chiffrement hybride RSA+AES
   - Delivery via email
   - Recovery mechanisms

2. **Labsboot** :
   - Architecture MBR (bootcode + partition)
   - x86 16-bit real mode assembly
   - Boot process interception
   - Forensic analysis
   - Multi-OS comparison (Windows 7 vs Ubuntu 24)

---

**🎓 Projet éducatif complet - Production-Ready pour formation cybersécurité**

*Last Updated: 2026-08-24*
