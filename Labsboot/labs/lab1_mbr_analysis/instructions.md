# Lab 1: MBR Analysis & Forensics - Attaque Boot Sector sur 2 OS

## 📋 Objectif

Analyser comment une **attaque de boot sector** impacte différemment :
- **Windows 7** (NTFS)
- **Ubuntu Server 24** (ext4)

---

## 🎯 Architecture du Lab

```
┌──────────────────────────────┐
│  Kali Linux (Attaquant)      │
│  - Crée le bootkit           │
│  - Génère MBR malveillant    │
└────────────┬─────────────────┘
             │
   ┌─────────┴──────────┐
   │                    │
┌──▼────────────┐  ┌───▼──────────────┐
│ Windows 7 VM  │  │ Ubuntu Server 24 │
│ (Cible 1)     │  │ (Cible 2)        │
│ - NTFS        │  │ - ext4           │
│ - Bootloader  │  │ - GRUB bootloader│
│   Windows     │  │                  │
└───────────────┘  └──────────────────┘
```

---

## 🔍 Part 1: Analyse MBR Windows 7

### Étape 1.1: Extraire l'image MBR

**Sur Windows 7** :
```batch
REM Utiliser HxD ou autre hex editor
1. Ouvrir "\\.\PhysicalDrive0" (disque 0)
2. Sélectionner premiers 512 bytes
3. Exporter en "windows7_mbr.bin"
```

**OU depuis Ubuntu** :
```bash
# Accès au disque Windows 7 en réseau
ssh user@windows7-vm
# Puis utiliser dd sur Windows (Cygwin)
dd if=\\?\PhysicalDrive0 of=windows7_mbr.bin bs=512 count=1
```

### Étape 1.2: Analyser l'MBR légitime

```bash
# Sur Ubuntu (Kali)
python3 tools/lab1_mbr_analyzer.py --analyze windows7_mbr.bin

# Sortie attendue:
#
# ═══════════════════════════════════════════════
# MBR ANALYSIS REPORT - windows7_mbr.bin
# ═══════════════════════════════════════════════
#
# [✓] BOOT SIGNATURE: 0xAA55 (VALID)
# [✓] BOOTCODE SIZE: 446 bytes
# [✓] PARTITION TABLE: 4 entries
#     Entry 0: Type=0x07 (NTFS), Start=2048, Size=209711104
#     Entry 1: Type=0x00 (Empty)
#     Entry 2: Type=0x00 (Empty)
#     Entry 3: Type=0x00 (Empty)
#
# [✓] HEURISTICS:
#     - Boot code contains valid jump instruction
#     - Partition table not suspicious
#     - Checksum valid
#     - No hidden sectors detected
#
# [✓] STATUS: CLEAN
```

### Étape 1.3: Injecter bootkit (simulation)

```bash
# Créer une version "infectée" de l'MBR
python3 tools/lab1_mbr_analyzer.py --inject-bootkit windows7_mbr.bin windows7_mbr_infected.bin

# Cela crée un MBR avec:
# - Bootcode malveillant (446 bytes)
# - Partition table modifiée
# - Signature 0xAA55 toujours présente (pour stealth)
```

### Étape 1.4: Analyser l'MBR infecté

```bash
python3 tools/lab1_mbr_analyzer.py --analyze windows7_mbr_infected.bin

# Sortie attendue:
#
# ⚠️  ANOMALIES DÉTECTÉES:
# 
# [✗] Bootcode: Code inhabituel détecté
#     - Références à secteurs cachés
#     - Pas de structures partition valides
#
# [✗] Partition table: Anomalies
#     - Entrée 0: Size=0 (SUSPECTE!)
#     - Entrées cachées dans bootcode
#
# [✗] Heuristics:
#     - Checksum invalide
#     - 2 secteurs cachés détectés (offset 300-301)
#     - Boot code compressé/chiffré détecté
#
# ⚠️  STATUS: INFECTED - BOOTKIT PROBABLE
# 
# [Recommandations]
# - Restaurer depuis backup
# - Analyser avec Volatility (memory forensics)
# - Vérifier logs du démarrage
```

---

## 🔍 Part 2: Analyse MBR Ubuntu Server 24

### Étape 2.1: Extraire l'MBR

**Sur Ubuntu Server 24** :
```bash
# Utiliser dd (plus direct qu'HxD)
sudo dd if=/dev/sda of=ubuntu_mbr.bin bs=512 count=1

# Vérifier l'extraction
hexdump -C ubuntu_mbr.bin | head -20
```

### Étape 2.2: Analyser l'MBR légitime

```bash
python3 tools/lab1_mbr_analyzer.py --analyze ubuntu_mbr.bin --filesystem ext4

# Sortie attendue:
#
# ═══════════════════════════════════════════════
# MBR ANALYSIS REPORT - ubuntu_mbr.bin
# ═══════════════════════════════════════════════
#
# [✓] BOOT SIGNATURE: 0xAA55 (VALID)
# [✓] BOOTCODE: GRUB bootloader v2.04
#     - Detected bootloader: GRUB2
#     - Supports: multi-boot, LVM, encryption
#
# [✓] PARTITION TABLE:
#     Entry 0: Type=0x83 (Linux), Start=2048, Size=104857600 (boot)
#     Entry 1: Type=0x83 (Linux), Start=104859648, Size=514088960 (/)
#     Entry 2: Type=0x00 (Empty)
#     Entry 3: Type=0x00 (Empty)
#
# [✓] GRUB ANALYSIS:
#     - GRUB core found at sector 23
#     - Boot modules: part_msdos, ext2, linux
#     - Configuration OK
#
# [✓] STATUS: CLEAN
```

### Étape 2.3: Injecter bootkit pour ext4

```bash
python3 tools/lab1_mbr_analyzer.py --inject-bootkit ubuntu_mbr.bin ubuntu_mbr_infected.bin --target linux

# Différences vs Windows:
# - Préserver structure GRUB (plus complexe)
# - Infecter stage 1.5 (secteurs 23+)
# - Rediriger boot vers rootkit
```

### Étape 2.4: Comparer impacts

```bash
python3 tools/lab1_mbr_analyzer.py --compare windows7_mbr_infected.bin ubuntu_mbr_infected.bin

# Rapport de comparaison:
#
# ═══════════════════════════════════════════════
# BOOTKIT IMPACT COMPARISON
# ═══════════════════════════════════════════════
#
# Windows 7 (NTFS):
# ├─ Bootloader: Windows Boot Manager
# ├─ Attack Surface: 446 bytes bootcode + VBR
# ├─ Recovery: WinRE + repair tools
# └─ Persistence: MBR + System Reserved partition
#
# Ubuntu Server 24 (ext4):
# ├─ Bootloader: GRUB2
# ├─ Attack Surface: MBR + /boot/grub (disk)
# ├─ Recovery: GRUB recovery mode + chroot
# └─ Persistence: MBR + /boot partition
#
# SIMILARITIES:
# - Both use MBR as entry point
# - Both have multi-stage bootloaders
# - Both vulnerable to sector 0 attacks
#
# DIFFERENCES:
# - Windows: Bootcode + VBR (2 levels)
# - Ubuntu: MBR + GRUB + Kernel (3+ levels)
# - Recovery mechanisms different
# - Filesystem encryption support varies
```

---

## 🛠️ Tools utilisés

### mbr_analyzer.py
```python
from tools.lab1_mbr_analyzer import MBRAnalyzer

analyzer = MBRAnalyzer()

# Analyze clean MBR
analyzer.analyze("windows7_mbr.bin", output_file="windows7_report.txt")

# Create infected version
analyzer.inject_bootkit("windows7_mbr.bin", "windows7_mbr_infected.bin")

# Compare two MBRs
analyzer.compare("windows7_mbr.bin", "ubuntu_mbr.bin")

# Generate forensic timeline
analyzer.generate_timeline()
```

---

## 📊 Résultats attendus

### Tableau comparatif

| Aspect | Windows 7 | Ubuntu Server 24 |
|--------|-----------|-----------------|
| **Bootloader** | Windows Boot Mgr | GRUB 2 |
| **MBR Bootcode** | 446 bytes code | 446 bytes + GRUB refs |
| **VBR/Stage1.5** | NTFS Boot Sector | /boot/grub/boot.img |
| **Encryption** | BitLocker support | dm-crypt support |
| **Attack Vector** | MBR + VBR | MBR + /boot partition |
| **Detection** | Hard (needs recovery) | Easier (GRUB recovery) |
| **Recovery Time** | 15-30 min | 5-10 min |

---

## ✅ Checklist Lab 1

- [ ] Extraire MBR Windows 7 (clean)
- [ ] Analyser avec mbr_analyzer.py
- [ ] Extraire MBR Ubuntu Server 24 (clean)
- [ ] Analyser avec mbr_analyzer.py
- [ ] Créer versions "infectées" (simulation)
- [ ] Analyser versions infectées
- [ ] Générer rapports comparatifs
- [ ] Documenter différences OS
- [ ] Tester recovery sur les deux systèmes
- [ ] Valider tous les scripts

---

## 🔐 Sécurité

✅ **À faire** :
- Snapshots VM avant injection bootkit
- Analyse en environnement isolé
- Backup des MBR originaux
- Logs détaillés de toutes opérations

❌ **À ÉVITER** :
- Tester en dehors des VMs
- Modifier disque hôte
- Laisser infection persistante

---

## 📚 Références

- ANSSI bootcode_parser: https://github.com/ANSSI-FR/bootcode_parser
- OpenPetya MBR analysis: https://github.com/iss4cf0ng/OpenPetya
- Petya 2017 Notes: https://github.com/aguinet/petya2017_notes

---

**Lab 1 Complete - Bootkit MBR Analysis on 2 Operating Systems 🎓**
