# Labsboot - Projet Pédagogique sur les Bootkits

> ⚠️ **AVERTISSEMENT** : Ce projet est destiné à des fins **éducatives et de recherche en cybersécurité uniquement**. 
> Il étudie les mécanismes de sécurité du processus de démarrage, les bootkits, MBR/VBR et UEFI. 
> **À utiliser EXCLUSIVEMENT dans une machine virtuelle isolée.**

## 📋 Vue d'ensemble

Ce projet pédagogique explore les techniques de manipulation du processus de démarrage en cybersécurité :

- **MBR (Master Boot Record)** - Secteur de démarrage principal
- **VBR (Volume Boot Record)** - Secteur de démarrage de volume
- **Bootkit** - Malware qui s'exécute avant le système d'exploitation
- **UEFI** - Unified Extensible Firmware Interface
- **Petya/NotPetya** - Analyse de ransomware au niveau boot
- **Forensique de démarrage** - Détection et analyse

## 🏗️ Architecture

```
Boot Process (Sécurité & Attaques)
│
├─ BIOS/UEFI Firmware
│  ├─ POST (Power-On Self Test)
│  └─ Bootloader Search
│
├─ MBR (512 bytes)
│  ├─ Boot Code (446 bytes)
│  ├─ Partition Table (64 bytes)
│  └─ Boot Signature (2 bytes)
│
├─ VBR (Volume Boot Record)
│  ├─ NTFS Boot Sector
│  ├─ FAT32 Boot Sector
│  └─ ext4 Boot Sector
│
├─ Bootloader Stages
│  ├─ Stage 1 (MBR)
│  ├─ Stage 2 (Bootloader)
│  └─ Stage 3 (Kernel)
│
└─ Kernel & OS Initialization
   ├─ Protected Mode
   ├─ Long Mode (x64)
   └─ Ring 0 Privileges
```

## 📁 Structure du projet

```
Labsboot/
├── docs/                          # Documentation
│   ├── MBR_VBR_explained.md      # Explications MBR/VBR
│   ├── UEFI_security.md          # Sécurité UEFI
│   ├── Petya_analysis.md         # Analyse Petya/NotPetya
│   └── Bootkit_detection.md      # Techniques de détection
├── resources/                     # Ressources externes
│   ├── references.md             # Références GitHub & papiers
│   ├── tools.md                  # Outils d'analyse
│   └── datasets.md               # Datasets pédagogiques
├── labs/                          # Laboratoires pédagogiques
│   ├── lab1_mbr_analysis/        # Analyse MBR
│   ├── lab2_vbr_modification/    # Modification VBR
│   ├── lab3_bootkit_detection/   # Détection bootkit
│   └── lab4_petya_simulation/    # Simulation Petya
├── tools/                         # Outils d'analyse
│   ├── mbr_analyzer.py           # Analyse MBR
│   ├── vbr_reader.py             # Lecture VBR
│   ├── bootkit_detector.py       # Détecteur bootkit
│   └── forensic_tools.py         # Outils forensiques
└── README.md                      # Ce fichier
```

## 🚀 Setup & Installation

### Prérequis

- **Python 3.8+**
- **Hex Editor** (HxD, Sublime, etc.)
- **Virtual Machine** (VirtualBox, VMware)
  - ⚠️ **ISOLATION OBLIGATOIRE** - Jamais sur machine hôte
  - Network Mode: Host-Only ou Isolated
- **Disassembler** (Ghidra, IDA, Radare2)
- **Forensic Tools** : 
  - ANSSI bootcode_parser
  - Volatility (memory analysis)

### Installation dépendances

```bash
# Créer environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer dépendances
pip install -r requirements.txt
```

## 🔬 Laboratoires pédagogiques

### Lab 1: Analyse MBR
```bash
cd labs/lab1_mbr_analysis
python mbr_analyzer.py /path/to/disk_image.img
```

Objectifs :
- Lire et interpréter la structure MBR
- Identifier code de démarrage malveillant
- Analyser la table de partitions

### Lab 2: Modification VBR
```bash
cd labs/lab2_vbr_modification
python vbr_reader.py --analyze
```

Objectifs :
- Comprendre la structure VBR
- Identifier modifications suspectes
- Détecter bootkit NTFS

### Lab 3: Détection Bootkit
```bash
cd labs/lab3_bootkit_detection
python bootkit_detector.py --disk /dev/sda
```

Objectifs :
- Détecter signatures de bootkit connues
- Analyser anomalies de démarrage
- Générer rapports forensiques

### Lab 4: Simulation Petya
```bash
cd labs/lab4_petya_simulation
python petya_simulation.py --vm-only
```

Objectifs :
- Simuler mécanismes de chiffrement Petya
- Comprendre masterkey encryption
- Analyser impact sur système fichiers

## 📊 Concepts clés

### MBR (Master Boot Record)

```
Offset  | Size | Description
--------|------|----------------------------------
0x0000  | 446  | Boot Code (bootloader stage 1)
0x01BE  | 64   | Partition Table (4 entries × 16)
0x01FE  | 2    | Boot Signature (0xAA55)
```

### VBR (Volume Boot Record)

**NTFS VBR:**
```
Offset  | Size | Description
--------|------|----------------------------------
0x0000  | 3    | Jump Instruction
0x0003  | 8    | OEM Name
0x000B  | 25   | BIOS Parameter Block
0x0024  | 22   | Extended BIOS Parameter Block
```

### Bootkit vs Rootkit

| Aspect | Bootkit | Rootkit |
|--------|---------|---------|
| **Niveau** | Firmware/Boot | Kernel |
| **Timing** | Avant OS | Après OS |
| **Persistance** | Très forte | Forte |
| **Détection** | Difficile | Difficile |
| **Impact** | Total contrôle | Contrôle partiel |

## 🛡️ Défense & Détection

### Techniques de sécurisation

- **Secure Boot** - Vérification signatures UEFI
- **UEFI Lockdown** - Restrictions firmware
- **MBR Protection** - Monitoring écriture MBR
- **TPM (Trusted Platform Module)** - Chaîne de confiance
- **Measured Boot** - Vérification intégrité démarrage

### Outils de détection

1. **ANSSI bootcode_parser** - Analyse MBR/VBR
2. **Volatility** - Memory forensics
3. **Ghidra** - Reverse engineering bootkit
4. **IDA Pro** - Désassembly code de démarrage
5. **Radare2** - Analyse statique/dynamique

## 📚 Ressources pédagogiques

### Projets GitHub de référence

- [OpenPetya](https://github.com/iss4cf0ng/OpenPetya) - Petya PoC éducatif
- [ANSSI bootcode_parser](https://github.com/ANSSI-FR/bootcode_parser) - Analyse officielle
- [Petya 2017 Notes](https://github.com/aguinet/petya2017_notes) - Reverse engineering

### Documentation technique

- **Secure Boot & UEFI** : Intel/Microsoft specifications
- **MBR/VBR** : Wikipedia, OSDev.org
- **Bootkit Analysis** : SANS papers, Phrack magazine
- **Petya Research** : Securelist, ZDNet technical analysis

### Datasets pédagogiques

- [CNET Petya samples](https://cnet.example.com/) (lab isolé)
- [Malwr.com](https://malwr.com/) - Sandbox analysis
- [VirusTotal](https://www.virustotal.com/) - Threat intelligence
- [Hybrid Analysis](https://hybrid-analysis.com/) - Dynamic analysis

## ⚖️ Légalité & Éthique

**Ce code est fourni à titre éducatif uniquement.**

Utilisation autorisée :
- ✅ Laboratoires universitaires
- ✅ Formations en cybersécurité approuvées
- ✅ Recherche académique
- ✅ Pentesting autorisé

Utilisation interdite :
- ❌ Attaques réelles
- ❌ Déploiement malveillant
- ❌ Perturbation de services
- ❌ Utilisation sans consentement

---

## 🚫 Clause de non-responsabilité

Les auteurs ne sont **pas responsables** de tout dommage, perte de données, ou activité malveillante résultant de l'utilisation de ce projet.

**L'utilisateur accepte d'utiliser ce matériel dans un contexte éducatif isolé uniquement.**

---

## 📝 Auteur

**Jesse Mpiga-Odoumba**
- Développeur Full-Stack & Ingénieur IA & Big Data
- Spécialistes cybersécurité & cryptographie
- Email: jesse.mpiga@a-ct.ma
- GitHub: github.com/mpigajesse

---

✨ **Projet pédagogique - Recherche en sécurité du démarrage**
