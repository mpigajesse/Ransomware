# 🔨 Guide de Compilation et Build du Bootkit POC

## 📋 Prérequis

### Système d'exploitation
- **Windows 11** (host machine)
- **Ubuntu/WSL** (pour NASM)
- **Python 3.8+**

### Outils requis

#### 1. NASM (Netwide Assembler)
Requis pour compiler `mbr_stage1.asm`

**Installation** :
```bash
# Windows (via Chocolatey)
choco install nasm

# Windows (via MSI)
# Télécharger: https://www.nasm.us/

# Ubuntu/WSL
sudo apt update && sudo apt install nasm

# macOS
brew install nasm

# Verification
nasm --version
```

#### 2. Python 3.8+
```bash
python3 --version  # Doit être >= 3.8
```

---

## 🚀 Process de Build

### Option 1: Build Complète (Recommandée)

Compile tout (ASM, MBR, images disque) en une seule commande :

```bash
cd "G:\Mon Drive\CyberSécurite\RansomwareProjet\Ransomware"
python3 Labsboot/bootkit_implementation.py --build
```

**Sortie attendue** :
```
[✓] ============================================================
[✓] BOOTKIT POC - COMPILATION COMPLÈTE
[✓] ============================================================

[✓] [1/4] Compilation assembleur...
[✓] Compilation: mbr_stage1.asm
[✓] Compilé avec succès: mbr_stage1.bin

[✓] [2/4] Vérification taille...
[✓] Taille bootcode: 446 bytes (max 446)

[✓] [3/4] Création MBR infecté...
[✓] Création MBR infecté
[✓] MBR infecté créé: bootkit_mbr.bin
[✓]   - Bootcode: 446 bytes
[✓]   - Partition Table: 64 bytes
[✓]   - Boot Signature: 2 bytes (0xAA55)

[✓] [4/4] Création images disque...
[✓] Création image disque: .../bootkit_windows7.img (windows)
[✓] Image créée: bootkit_windows7.img (1024 KB)
[✓] Création image disque: .../bootkit_ubuntu24.img (linux)
[✓] Image créée: bootkit_ubuntu24.img (1024 KB)
[✓] Création image VMware: .../bootkit_windows7.vmdk (40 GB)
[✓] VMDK créé: bootkit_windows7.vmdk

[✓] ============================================================
[✓] COMPILATION COMPLÈTE ✓
[✓] ============================================================
```

### Option 2: Étapes Individuelles

#### Étape 1 : Compiler l'assembleur
```bash
python3 Labsboot/bootkit_implementation.py --compile
```
Génère : `Labsboot/build/mbr_stage1.bin` (446 bytes)

#### Étape 2 : Créer l'image disque
```bash
python3 Labsboot/bootkit_implementation.py --image Labsboot/build/bootkit.img
```
Génère : `Labsboot/build/bootkit.img` (1 MB)

#### Étape 3 : Créer l'image VMware
```bash
python3 Labsboot/bootkit_implementation.py --vmware Labsboot/build/bootkit.vmdk
```
Génère :
- `Labsboot/build/bootkit.vmdk` (descriptor)
- `Labsboot/build/bootkit.img` (data file)

---

## 📁 Fichiers Générés

Après build complète, la structure :

```
Labsboot/
├── src/
│   └── mbr_stage1.asm              ◄─── Source assembleur
│
└── build/                          ◄─── Artifacts générés
    ├── mbr_stage1.bin              (446 bytes - bootcode compilé)
    ├── bootkit_mbr.bin             (512 bytes - MBR complet)
    ├── bootkit_windows7.img        (1 MB - Image disque simple)
    ├── bootkit_ubuntu24.img        (1 MB - Image disque simple)
    ├── bootkit_windows7.vmdk       (Descriptor VMware)
    ├── bootkit_windows7.img        (Data file VMware)
    ├── bootkit_ubuntu24.vmdk       (Descriptor VMware)
    └── bootkit_ubuntu24.img        (Data file VMware)
```

---

## ✅ Vérification Build

### 1. Vérifier la taille du bootcode

```bash
# Windows PowerShell
(Get-Item "Labsboot\build\mbr_stage1.bin").Length

# Linux/WSL
ls -lh Labsboot/build/mbr_stage1.bin
```

**Attendu** : 446 bytes exactement

### 2. Inspecter MBR compilé

```bash
# Voir les premiers bytes (bootcode)
hexdump -C Labsboot/build/mbr_stage1.bin | head -20

# Voir signature boot (derniers bytes)
hexdump -C Labsboot/build/bootkit_mbr.bin | tail -5

# Attendu:
# 000001f0: xxxx xxxx xxxx xxxx xxxx xxxx 55aa  |....xxxx....U.|
```

### 3. Vérifier signature 0xAA55

```python
# Script Python
with open("Labsboot/build/bootkit_mbr.bin", "rb") as f:
    data = f.read()
    sig = data[510:512]
    assert sig == b'\x55\xaa', f"Signature invalide: {sig.hex()}"
    print(f"✓ Signature valide: 0x{sig.hex().upper()}")
```

---

## 🔧 Troubleshooting

### Erreur : "NASM not found"

**Solution** : Installer NASM

```bash
# Windows (Chocolatey)
choco install nasm

# Ajouter NASM au PATH:
# Ajouter : C:\Program Files\NASM
# ou où NASM est installé

# Vérifier:
nasm --version
```

### Erreur : "Bootcode too large"

Si le compilé > 446 bytes :

**Solution** : Réduire la taille du code assembleur
- Diminuer les messages (moins de db strings)
- Supprimer beeps/delays
- Optimiser loops

### Erreur : "File not found: mbr_stage1.asm"

**Solution** : Vérifier le chemin relatif
```bash
# Depuis la racine du projet
ls Labsboot/src/mbr_stage1.asm

# Ou spécifier le chemin complet
python3 Labsboot/bootkit_implementation.py --build \
  --asm "G:\Mon Drive\CyberSécurite\RansomwareProjet\Ransomware\Labsboot\src\mbr_stage1.asm"
```

---

## 🧪 Test Local (Avant Déploiement VM)

### Test 1 : Vérifier sortie binaire

```bash
# Vérifier que les fichiers existent
ls -la Labsboot/build/*.bin

# Vérifier tailles
wc -c Labsboot/build/*.bin
```

**Attendu** :
- `mbr_stage1.bin` : 446 bytes
- `bootkit_mbr.bin` : 512 bytes

### Test 2 : Inspecter le code compilé

```bash
# Voir hex dump complet
hexdump -C Labsboot/build/mbr_stage1.bin | head -30

# Chercher messages
strings Labsboot/build/mbr_stage1.bin | grep -i bootkit
```

### Test 3 : Vérifier image disque

```bash
# Vérifier MBR dans image
dd if=Labsboot/build/bootkit_windows7.img bs=512 count=1 | hexdump -C | tail -5

# Doit montrer: ...55aa à offset 0x1f0
```

---

## 📤 Préparation Déploiement VM

### Checklist avant test sur VM

- [ ] Build complète exécutée (`--build`)
- [ ] Tous les fichiers générés dans `Labsboot/build/`
- [ ] Signatures vérifiées (0xAA55 valide)
- [ ] Tailles correctes (bootcode 446, MBR 512)
- [ ] Windows 7 VM prête (snapshot créé)
- [ ] Ubuntu 24 VM prête (snapshot créé)

### Copier files vers VM

**Windows 7** :
```batch
REM Copier image disque
copy Labsboot\build\bootkit_windows7.img C:\temp\

REM Ou via partage réseau
net use Z: \\ubuntu-server\share
copy Labsboot\build\bootkit_windows7.img Z:\
```

**Ubuntu 24** :
```bash
# Via scp
scp -r Labsboot/build/ ubuntu-user@ubuntu-server:/tmp/bootkit/

# Vérifier
ssh ubuntu-user@ubuntu-server "ls -la /tmp/bootkit/"
```

---

## 🚀 Déploiement VMs

Voir : `BOOTKIT_DEPLOYMENT.md` pour :
- Injection MBR sur Windows 7
- Injection MBR sur Ubuntu 24
- Test et observation
- Recovery via snapshot

---

## 📊 Performance Build

Temps estimés :

| Étape | Temps |
|-------|--------|
| Compile ASM | <1s |
| Vérify size | <1s |
| Create MBR | <1s |
| Create images (4x) | 2-5s |
| **Total** | **< 10s** |

---

## 🔐 Notes Sécurité

✅ **À faire** :
- Compiler sur machine sécurisée
- Stocker artifacts dans dossier isolé
- Backup originals avant modifications
- Documentation complète de chaque test

❌ **À ÉVITER** :
- Compiler sur machine production
- Partager artifacts sur internet
- Tester en dehors VMs isolées
- Laisser MBR infecté sans snapshot

---

## 📚 Références

- **NASM Manual** : https://www.nasm.us/doc/
- **x86 Real Mode** : https://en.wikipedia.org/wiki/Real_mode
- **MBR Structure** : https://en.wikipedia.org/wiki/Master_boot_record
- **BIOS Interrupts** : https://www.ctyme.com/intr/int-10.htm

---

**Bootkit Build Guide - Educational and Authorized Testing Only 🎓**
