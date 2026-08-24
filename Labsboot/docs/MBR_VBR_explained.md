# MBR & VBR - Explications Détaillées

## Master Boot Record (MBR)

### Structure MBR (512 octets)

```
┌─────────────────────────────────────────┐
│ Boot Code (446 bytes)                   │  Bootloader Stage 1
│ - Instructions CPU (x86)                │  Charges VBR/Bootloader
│ - Signatures d'attaque ici ⚠️           │
├─────────────────────────────────────────┤
│ Partition Table (64 bytes)              │  4 entrées × 16 bytes
│ - 4 partitions primaires                │
│ - Type, début, taille de chaque         │
├─────────────────────────────────────────┤
│ Boot Signature (2 bytes)                │  0xAA55 (magic number)
│ 0xAA 0x55 = "c'est un boot valide"     │
└─────────────────────────────────────────┘
Total: 512 bytes (1 secteur disque)
```

### Hex Dump MBR Légitime

```hex
00000000: eb 52 90 4e 54 46 53 20 20 20 20 00 02 08 00 00  .R.NTFS  ...
00000010: 00 00 00 00 f8 00 00 00 3f 00 0f 00 00 08 00 00  ........?.......
... [bootcode continues]
000001fe: 55 aa                                               U.
```

### Hex Dump MBR Infecté (Bootkit)

```hex
00000000: fc 89 e5 53 57 56 83 ec 08 e8 1a 00 00 00 6e 6f  ......SVU......
00000010: 70 61 75 73 65 20 6d 6f 64 65 00 00 00 00 00 00  pause mode......
... [malware code]
000001fe: 55 aa  (signature still present ✓)
```

⚠️ **Signature MBR** : Le bootkit CONSERVE `0xAA55` pour rester "invisible"

## Volume Boot Record (VBR)

### VBR NTFS (512 bytes)

```
Offset  Size  Field
0x00    3     Jump Instruction (EB xx 90)
0x03    8     OEM Name (NTFS)
0x0B    2     Bytes per Sector (512)
0x0D    1     Sectors per Cluster
0x0E    2     Reserved Sectors
0x10    3     (Unused in NTFS)
0x13    2     (Unused in NTFS)
0x15    1     Media Descriptor
0x16    2     (Unused in NTFS)
0x18    2     Sectors per Track
0x1A    2     Heads
0x1C    4     Hidden Sectors
0x20    4     (Unused)
0x24    4     (Unused)
0x28    8     Total Sectors (NTFS)
0x30    8     MFT Start Cluster
0x38    8     MFT Mirror Start Cluster
0x40    4     Clusters per File Record
0x44    4     Clusters per Index Block
0x48    8     Serial Number
0x50    4     Checksum
0x1FE   2     Boot Signature (0xAA55)
```

### VBR FAT32 (512 bytes)

```
Offset  Size  Field
0x00    3     Jump Instruction
0x03    8     OEM Name
0x0B    2     Bytes per Sector (512)
0x0D    1     Sectors per Cluster
0x0E    2     Reserved Sectors
0x10    1     Number of FATs
0x11    2     Root Dir Entries
0x13    2     Total Sectors (old)
0x15    1     Media Descriptor
0x16    2     Sectors per FAT
0x18    2     Sectors per Track
0x1A    2     Heads
0x1C    4     Hidden Sectors
0x20    4     Total Sectors (new)
0x24    4     Sectors per FAT32
0x28    2     Flags
0x2A    2     Version
0x2C    4     Root Directory Cluster
0x30    2     FSInfo Sector
0x32    2     Boot Sector Backup
0x34    12    Reserved
0x40    1     Drive Number
0x41    1     Reserved
0x42    1     Boot Signature (0x29)
0x43    4     Serial Number
0x47    11    Volume Label
0x52    8     File System Type
0x1FE   2     Boot Signature (0xAA55)
```

## Bootkit Detection

### Signes d'infection MBR

✅ **Indicateurs Normaux**
- Boot signature = 0xAA55
- Code contient JMP/CALL vers kernel
- Taille = 512 bytes

❌ **Signes de bootkit**
- Bootcode inhabituellement court
- References à addresses externes
- Absence de structures de partition valides
- Checksum invalide
- Secteurs "cachés" réalloués
- Entrées de partition modifiées (taille = 0)

### Outils d'analyse

**ANSSI bootcode_parser**
```bash
./bootcode_parser.py disk.img
```

**Radare2**
```bash
r2 disk.img
p6d 512  # Print 512 bytes as disassembly
```

**Ghidra**
- Charger l'image disque brute
- Désassembler le MBR
- Analyser le flux de contrôle

## Cas réels

### Petya MBR

Petya modifie le MBR pour :
1. **Interception du démarrage** - Avant Windows
2. **Affichage du message** - "Oops, your important files have been encrypted"
3. **Chiffrement MFT** - Master File Table
4. **Demande de rançon** - Message avec adresse Bitcoin

### Rovnix Bootkit

Rovnix est un bootkit sophistiqué qui :
- Persiste dans le secteur de démarrage
- Charge rootkit kernel depuis disque
- Exfiltration de données
- Résistant à la réinstallation OS

## Défense

### Protection MBR

```python
# Vérifier l'intégrité du MBR
def verify_mbr_integrity(disk_path):
    with open(disk_path, 'rb') as f:
        mbr = f.read(512)
        
    # Vérifier signature
    signature = mbr[510:512]
    if signature != b'\x55\xAA':
        print("⚠️ MBR signature invalide !")
        return False
    
    # Vérifier bootcode (hash connu)
    bootcode_hash = hashlib.sha256(mbr[:446]).hexdigest()
    if bootcode_hash not in KNOWN_HASHES:
        print("⚠️ Bootcode modifié détecté !")
        return False
    
    return True
```

### Outils de protection

- **BIOS/UEFI Lockdown** - Firmware password
- **TPM** - Sealed boot measurements
- **Secure Boot** - Signature verification
- **MBR Monitoring** - Alert sur modifications
