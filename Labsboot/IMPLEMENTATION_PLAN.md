# Plan d'Implémentation Labsboot - Environment VMware

## 🎯 Objectif Global

Créer un **bootkit éducatif** qui attaque le secteur de boot avec :
- **Inspirations** : OpenPetya, Petya 2017, ANSSI bootcode_parser
- **Architecture** : Windows 7 (cible) + Ubuntu Server 24 (analyse)
- **VMs** : Complètement isolées dans VMware
- **Résultat** : Suite de 4 labs pédagogiques + outils forensiques

---

## 🏗️ Architecture VMware

```
                    ┌─────────────────────────┐
                    │   Hôte Windows 11       │
                    │   (VMware Workstation)  │
                    └────────────┬────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
        ┌───────▼────────┐  ┌────▼────────┐  ┌──▼─────────┐
        │  Windows 7 VM  │  │ Ubuntu 24   │  │ Kali Linux │
        │  (Cible)       │  │ (Analyse)   │  │ (Outils)   │
        │  Isolated Mode │  │ Host-Only   │  │ Host-Only  │
        └────────────────┘  └─────────────┘  └────────────┘
             │                     │              │
             └─────────────────────┼──────────────┘
                                   │
                          ┌────────▼────────┐
                          │ Network Isolé   │
                          │ (Pas d'accès    │
                          │  internet)      │
                          └─────────────────┘
```

### Configuration réseau
- **Windows 7** : Isolated (snapshot disque uniquement)
- **Ubuntu 24** : Host-Only (accès au réseau lab)
- **Kali Linux** : Host-Only (outils d'analyse)
- **Partage** : NFS ou SSH pour fichiers

---

## 📋 Phases d'implémentation

### Phase 1️⃣ : Setup Infrastructure (Semaine 1)

#### 1.1 VM Windows 7 (Cible)
```bash
# Specs minimales
- CPU: 2 cores
- RAM: 2-4 GB
- HDD: 40-50 GB
- Network: Isolated
- Snapshots: AVANT toute infection
```

**Préparation** :
```bat
# Sur Windows 7
1. Désactiver Antivirus/Defender (éducation)
2. Activer affichage extensions fichiers
3. Installer Hex editor (HxD)
4. Installer Python 3.8
5. Désactiver Secure Boot (BIOS/UEFI)
6. Créer snapshot "Clean State"
```

#### 1.2 VM Ubuntu Server 24 (Analyse)
```bash
# Specs
- CPU: 2 cores
- RAM: 4 GB
- HDD: 50 GB
- Network: Host-Only
```

**Setup** :
```bash
sudo apt update && sudo apt upgrade
sudo apt install python3-pip nasm gcc binutils hexdump
sudo apt install volatility3 radare2 ghidra
pip install construct capstone pydisk bitstring
git clone https://github.com/ANSSI-FR/bootcode_parser.git
```

#### 1.3 VM Kali Linux (Outils)
```bash
# Déjà packagé avec tous les outils
# Ajouter :
pip install capstone construct pydisk yara-python
```

---

### Phase 2️⃣ : Développement Labs (Semaine 2-3)

#### Lab 1: MBR Analysis & Forensics
```python
# Objectifs:
1. Lire et analyser MBR d'une image disque
2. Identifier signatures de bootkit
3. Comparer MBR légitime vs infecté

# Fichiers à créer:
tools/lab1_mbr_analyzer.py
labs/lab1_mbr_analysis/sample_clean_mbr.bin
labs/lab1_mbr_analysis/sample_infected_mbr.bin
labs/lab1_mbr_analysis/instructions.md
```

**Inspiration** : ANSSI bootcode_parser

#### Lab 2: VBR Modification Simulation
```python
# Objectifs:
1. Parser structure VBR (NTFS/FAT32)
2. Créer VBR personnalisé
3. Implémenter bootloader stage 2

# Code de base:
- Lire VBR depuis image disque
- Analyser champs BIOS Parameter Block
- Modifier tout en conservant signature 0xAA55
```

**Inspiration** : OpenPetya bootloader stages

#### Lab 3: Bootkit Detection
```python
# Objectifs:
1. Détecter anomalies MBR (bootkit)
2. Utiliser YARA rules
3. Analyser comportement démarrage

# Implémentation:
- YARA rules pour signatures Petya/Rovnix
- Heuristics : secteurs cachés, checksum invalide
- Logging détaillé des détections
```

**Inspiration** : OpenPetya-Defense + ANSSI

#### Lab 4: Petya Simulation (Educational PoC)
```python
# Objectifs:
1. Simuler chiffrement Petya (sans vraiment chiffrer)
2. Afficher message de rançon
3. Démontrer impact technique

# À NE PAS faire:
❌ Vrai chiffrement de données
❌ Demande de rançon réelle
❌ Déploiement en dehors de VM
```

**Inspiration** : OpenPetya PoC

---

## 🛠️ Outils à implémenter

### 1. mbr_analyzer.py
```python
class MBRAnalyzer:
    def read_mbr(disk_image_path)
    def parse_bootcode(bootcode_446bytes)
    def parse_partition_table(64bytes)
    def verify_signature(boot_signature)
    def detect_anomalies()
    def compare_with_known_samples()
    def generate_report()
```

### 2. vbr_reader.py
```python
class VBRReader:
    def read_vbr(disk_image_path)
    def parse_bios_parameter_block()
    def parse_extended_bpb()
    def detect_filesystem_type()
    def create_custom_vbr()
    def validate_integrity()
```

### 3. bootkit_detector.py
```python
class BootkitDetector:
    def scan_disk(disk_path)
    def detect_hidden_sectors()
    def analyze_checksum()
    def apply_yara_rules()
    def check_heuristics()
    def generate_forensic_report()
```

### 4. petya_simulator.py
```python
class PetyaSimulator:
    def simulate_encryption() # Educational, pas réel
    def create_ransom_message()
    def demonstrate_mft_impact()
    def show_boot_screen()
    def recover_filesystem() # Démo
```

---

## 📊 Timeline d'exécution

```
SEMAINE 1 : Infrastructure
├─ Jour 1-2  : Setup VMs (W7 + Ubuntu24 + Kali)
├─ Jour 3-4  : Network configuration (Isolated/Host-Only)
├─ Jour 5    : Snapshots de base + test
└─ Jour 6-7  : Documentation & préparation labs

SEMAINE 2 : Labs 1 & 2
├─ Jour 1-2  : Lab 1 (MBR Analysis)
│   ├─ mbr_analyzer.py
│   └─ Sample files
├─ Jour 3-4  : Lab 2 (VBR Modification)
│   ├─ vbr_reader.py
│   └─ Stage 2 bootloader
├─ Jour 5-7  : Testing & Documentation
└─ Push à GitHub

SEMAINE 3 : Labs 3 & 4
├─ Jour 1-2  : Lab 3 (Bootkit Detection)
│   ├─ bootkit_detector.py
│   └─ YARA rules
├─ Jour 3-4  : Lab 4 (Petya Simulation)
│   ├─ petya_simulator.py
│   └─ Educational PoC
├─ Jour 5-7  : Integration & final testing
└─ Final push + Release v1.0
```

---

## 🔗 Projets de référence à adapter

### OpenPetya
- **Lien** : https://github.com/iss4cf0ng/OpenPetya
- **À adapter** : 
  - MBR bootcode (446 bytes)
  - Bootloader stages
  - Transition Protected Mode
  - NTFS chiffrement simulation

### ANSSI bootcode_parser
- **Lien** : https://github.com/ANSSI-FR/bootcode_parser
- **À adapter** :
  - MBR/VBR parsing
  - Anomaly detection logic
  - Forensic reports
  - Sample images

### Petya 2017 Notes
- **Lien** : https://github.com/aguinet/petya2017_notes
- **À adapter** :
  - MBR modification techniques
  - Ransomware behavior
  - Analysis methods

### OpenPetya-Defense
- **Lien** : https://github.com/mutedmouse/OpenPetya-Defense
- **À adapter** :
  - YARA rules
  - Detection heuristics
  - Bootkit signatures

---

## ✅ Checklist implementation

### Phase 1
- [ ] VMs téléchargées et importées
- [ ] Windows 7 avec snapshot "Clean State"
- [ ] Ubuntu Server 24 configuré
- [ ] Kali Linux opérationnel
- [ ] Network isolé testé
- [ ] Documentation infrastructure

### Phase 2
- [ ] Lab 1 (MBR) implémenté
- [ ] Lab 2 (VBR) implémenté
- [ ] Lab 3 (Detection) implémenté
- [ ] Lab 4 (Petya Sim) implémenté
- [ ] Tests sur VMs
- [ ] Documentation labs complète

### Phase 3
- [ ] Tous les outils Python fonctionnels
- [ ] Samples/images disque prêtes
- [ ] YARA rules complètes
- [ ] Tests forensiques validés
- [ ] GitHub push final
- [ ] Release v1.0

---

## 🚀 Après implémentation

### Evolutions futures
1. **Agents IA** pour détection automatique
2. **Integration** avec Ransomware project
3. **Compliance** avec NIST/CIS
4. **Contributions** à la communauté

### Partage
- Laboratoire pédagogique complet
- Ressources pour formations cybersécurité
- Outils forensiques réutilisables
- Community contributions

---

## ⚠️ Rappels importants

✅ **À faire** :
- Environnements complètement isolés
- Snapshots avant chaque test
- Documentation détaillée
- Tests progressifs

❌ **À ÉVITER ABSOLUMENT** :
- Utiliser sur machine hôte
- Tester sur réseau public
- Demandes de rançon réelles
- Chiffrement de données réelles

---

**Labsboot : Bootkit Educational Project - Production Ready 🚀**
