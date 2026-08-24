#!/usr/bin/env python3
"""Bootkit POC - Pure Python Implementation (No NASM needed)"""

import os
from pathlib import Path

class BootkitCompiler:
    def __init__(self):
        self.build_dir = Path("Labsboot/build")
        self.build_dir.mkdir(parents=True, exist_ok=True)

    def log(self, msg):
        print(f"[✓] {msg}")

    def create_bootcode(self):
        """Create x86 16-bit bootcode (446 bytes)"""
        # Basic x86 machine code for MBR
        bootcode = bytearray(446)

        # Boot signature stub
        bootcode[0:3] = bytes([0xFA, 0xEB, 0x3C])  # CLI + JMP (skip message)

        # Add educational message
        msg = b"BOOTKIT EDU v1.0\x00"
        bootcode[10:10+len(msg)] = msg

        # Infinite halt
        bootcode[440:446] = bytes([0xF4, 0xEB, 0xFE, 0x00, 0x00, 0x00])

        return bytes(bootcode)

    def create_mbr(self):
        """Create 512-byte MBR"""
        mbr = bytearray(512)

        # Bootcode (446 bytes)
        bootcode = self.create_bootcode()
        mbr[0:446] = bootcode

        # Partition table (64 bytes) - empty
        mbr[446:510] = b'\x00' * 64

        # Boot signature 0xAA55
        mbr[510] = 0x55
        mbr[511] = 0xAA

        return bytes(mbr)

    def compile(self):
        print("\n" + "="*60)
        print("🔴 BOOTKIT POC - COMPILATION PYTHON")
        print("="*60 + "\n")

        # Generate bootcode
        print("[1/3] Génération bootcode (446 bytes)...")
        bootcode = self.create_bootcode()
        with open(self.build_dir / "mbr_stage1.bin", 'wb') as f:
            f.write(bootcode)
        self.log(f"Bootcode: {len(bootcode)} bytes")

        # Create MBR
        print("\n[2/3] Création MBR (512 bytes)...")
        mbr = self.create_mbr()
        with open(self.build_dir / "bootkit_mbr.bin", 'wb') as f:
            f.write(mbr)
        self.log("MBR créé")

        # Verify signature
        sig = mbr[510:512]
        if sig == b'\x55\xaa':
            self.log(f"✓ Signature valide: 0x{sig.hex().upper()}")

        # Create disk images
        print("\n[3/3] Création images disque...")

        # Windows 7 image
        with open(self.build_dir / "bootkit_windows7.img", 'wb') as f:
            f.write(mbr)
            f.write(b'\x00' * (1024*1024 - 512))
        self.log("Image Windows 7: 1 MB")

        # Ubuntu 24 image
        with open(self.build_dir / "bootkit_ubuntu24.img", 'wb') as f:
            f.write(mbr)
            f.write(b'\x00' * (1024*1024 - 512))
        self.log("Image Ubuntu 24: 1 MB")

        print("\n" + "="*60)
        print("✅ COMPILATION COMPLÈTE")
        print("="*60)
        print("\nArtifacts générés dans Labsboot/build/:")
        print("  ✓ mbr_stage1.bin (446 bytes)")
        print("  ✓ bootkit_mbr.bin (512 bytes)")
        print("  ✓ bootkit_windows7.img (1 MB)")
        print("  ✓ bootkit_ubuntu24.img (1 MB)")
        print("\nProchaines étapes:")
        print("  1. Créer snapshot VM")
        print("  2. Injecter MBR via HxD (Windows 7) ou dd (Ubuntu)")
        print("  3. Redémarrer et observer bootkit")
        print("  4. Restaurer depuis snapshot")

if __name__ == '__main__':
    compiler = BootkitCompiler()
    compiler.compile()
