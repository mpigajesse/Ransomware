#!/usr/bin/env python3
"""
Lab 1: MBR Analysis & Forensics Tool
=====================================

Analyse et compare MBR de Windows 7 et Ubuntu Server 24
Détecte bootkit, anomalies, signatures de malware

Usage:
    python3 lab1_mbr_analyzer.py --analyze <mbr_file>
    python3 lab1_mbr_analyzer.py --inject-bootkit <input> <output>
    python3 lab1_mbr_analyzer.py --compare <file1> <file2>
"""

import sys
import struct
import hashlib
from pathlib import Path
from typing import Tuple, List, Dict
import argparse
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BootSignature:
    """Boot signature check (0xAA55)"""
    value: int
    is_valid: bool

    @property
    def hex_str(self) -> str:
        return f"0x{self.value:04X}"


@dataclass
class PartitionEntry:
    """Partition table entry (16 bytes)"""
    status: int
    chs_start: Tuple[int, int, int]
    partition_type: int
    chs_end: Tuple[int, int, int]
    lba_start: int
    sectors: int

    @property
    def type_name(self) -> str:
        types = {
            0x00: "Empty",
            0x07: "NTFS/HPFS",
            0x83: "Linux",
            0x8E: "LVM",
            0xEE: "GPT",
        }
        return types.get(self.partition_type, f"Unknown (0x{self.partition_type:02X})")

    @property
    def is_active(self) -> bool:
        return self.status == 0x80

    @property
    def is_bootable(self) -> bool:
        return self.status in (0x00, 0x80)


class MBRAnalyzer:
    """Analyse MBR pour détecter bootkits et anomalies"""

    MBR_SIZE = 512
    BOOTCODE_SIZE = 446
    PARTITION_TABLE_SIZE = 64
    SIGNATURE_OFFSET = 510
    SIGNATURE_VALUE = 0xAA55

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.report = []

    def log(self, message: str, level: str = "INFO"):
        """Logging with levels"""
        if self.verbose:
            prefix = {
                "INFO": "[✓]",
                "WARN": "[⚠]",
                "ERROR": "[✗]",
                "DEBUG": "[•]"
            }.get(level, "[•]")
            print(f"{prefix} {message}")
        self.report.append(f"{level}: {message}")

    def read_mbr(self, file_path: str) -> bytes:
        """Lire un fichier MBR"""
        with open(file_path, 'rb') as f:
            data = f.read(self.MBR_SIZE)

        if len(data) != self.MBR_SIZE:
            raise ValueError(f"Fichier trop petit: {len(data)} bytes (attendu 512)")

        return data

    def parse_bootcode(self, bootcode: bytes) -> Dict:
        """Analyser le bootcode (446 bytes)"""
        return {
            "size": len(bootcode),
            "has_jump": bootcode[0] in (0xEB, 0xE9),  # JMP ou JMP far
            "hex_start": bootcode[:16].hex(),
            "entropy": self._calculate_entropy(bootcode),
            "compression_detected": self._detect_compression(bootcode),
        }

    def parse_partition_table(self, table_data: bytes) -> List[PartitionEntry]:
        """Parser table des partitions (64 bytes = 4 entries × 16)"""
        entries = []
        for i in range(4):
            offset = i * 16
            entry_data = table_data[offset:offset+16]

            status = entry_data[0]
            chs_start = (entry_data[1], entry_data[2], entry_data[3])
            part_type = entry_data[4]
            chs_end = (entry_data[5], entry_data[6], entry_data[7])
            lba_start = struct.unpack('<I', entry_data[8:12])[0]
            sectors = struct.unpack('<I', entry_data[12:16])[0]

            entry = PartitionEntry(
                status=status,
                chs_start=chs_start,
                partition_type=part_type,
                chs_end=chs_end,
                lba_start=lba_start,
                sectors=sectors
            )
            entries.append(entry)

        return entries

    def parse_signature(self, sig_bytes: bytes) -> BootSignature:
        """Vérifier signature de boot (0xAA55)"""
        value = struct.unpack('<H', sig_bytes)[0]
        return BootSignature(value=value, is_valid=(value == self.SIGNATURE_VALUE))

    def detect_bootkit_signatures(self, bootcode: bytes) -> List[str]:
        """Détecter signatures connues de bootkit"""
        signatures = [
            (b"Petya", "Petya/NotPetya signature"),
            (b"Rovnix", "Rovnix bootkit"),
            (b"Gapz", "Gapz bootkit"),
            (b"\x0F\x01\x16", "Protected Mode transition"),
        ]

        detected = []
        for sig, name in signatures:
            if sig in bootcode:
                detected.append(name)

        return detected

    def analyze_heuristics(self, mbr_data: bytes, partitions: List[PartitionEntry]) -> Dict:
        """Analyse heuristiques pour anomalies"""
        heuristics = {
            "empty_partition": False,
            "hidden_sectors": False,
            "invalid_checksum": False,
            "suspicious_bootcode": False,
            "invalid_chs": False,
        }

        # Vérifier partition vide
        if any(p.partition_type == 0x00 and p.sectors > 0 for p in partitions):
            heuristics["empty_partition"] = True

        # Vérifier secteurs cachés (LBA start avant première partition)
        if partitions[0].lba_start > 2048:
            heuristics["hidden_sectors"] = True

        # Checksum simple (somme tous les bytes % 256)
        checksum = sum(mbr_data[:510]) % 256
        if checksum != 0:
            heuristics["invalid_checksum"] = True

        # Déterminer compression/chiffrement du bootcode
        entropy = self._calculate_entropy(mbr_data[:446])
        if entropy > 7.5:  # Entropie élevée = chiffré/compressé
            heuristics["suspicious_bootcode"] = True

        return heuristics

    def _calculate_entropy(self, data: bytes) -> float:
        """Calculer l'entropie Shannon (0-8)"""
        if not data:
            return 0

        freq = {}
        for byte in data:
            freq[byte] = freq.get(byte, 0) + 1

        entropy = 0
        for count in freq.values():
            p = count / len(data)
            entropy -= p * (p.bit_length() - 1)  # Approximation log2

        return entropy

    def _detect_compression(self, data: bytes) -> bool:
        """Détecter si données sont compressées/chiffrées"""
        entropy = self._calculate_entropy(data)
        return entropy > 7.0  # Seuil empirique

    def analyze(self, file_path: str, filesystem: str = None) -> Dict:
        """Analyser un MBR complet"""
        self.log(f"Analyse: {file_path}")

        mbr_data = self.read_mbr(file_path)

        # Parser composants
        bootcode = mbr_data[:self.BOOTCODE_SIZE]
        partition_table = mbr_data[446:510]
        signature_bytes = mbr_data[510:512]

        bootcode_info = self.parse_bootcode(bootcode)
        partitions = self.parse_partition_table(partition_table)
        signature = self.parse_signature(signature_bytes)
        bootkit_sigs = self.detect_bootkit_signatures(bootcode)
        heuristics = self.analyze_heuristics(mbr_data, partitions)

        # Logging résultats
        self.log(f"Boot Signature: {signature.hex_str} {'(VALID)' if signature.is_valid else '(INVALID)'}")

        self.log("Partition Table:")
        for i, p in enumerate(partitions):
            if p.partition_type != 0x00:
                self.log(f"  Entry {i}: {p.type_name} | Start: {p.lba_start} | Size: {p.sectors} sectors")

        if bootkit_sigs:
            self.log(f"Bootkit Signatures Detected: {', '.join(bootkit_sigs)}", "WARN")

        if any(heuristics.values()):
            self.log("Anomalies Detected:", "WARN")
            for heuristic, detected in heuristics.items():
                if detected:
                    self.log(f"  - {heuristic}")
        else:
            self.log("No anomalies detected (CLEAN)", "INFO")

        return {
            "file": file_path,
            "bootcode": bootcode_info,
            "partitions": partitions,
            "signature": signature,
            "bootkit_signatures": bootkit_sigs,
            "heuristics": heuristics,
            "report": self.report
        }

    def inject_bootkit(self, input_file: str, output_file: str, target: str = "windows"):
        """
        Créer une version "infectée" du MBR (simulation éducative)

        WARNING: Ceci est à des fins ÉDUCATIVES UNIQUEMENT
        """
        self.log(f"Injection simulation bootkit: {input_file} → {output_file}")

        mbr_data = bytearray(self.read_mbr(input_file))

        # Remplacer bootcode par un code "malveillant" (simulation)
        malicious_code = bytearray(self.BOOTCODE_SIZE)

        # Bootcode simple avec références suspectes
        malicious_code[0:3] = b'\xFC\x89\xE5'  # code x86
        malicious_code[10:30] = b'BOOTKIT_MARKER_EDU'

        # Modifier la table de partitions
        if target.lower() == "windows":
            # Masquer partition en définissant la taille à 0
            mbr_data[446+16:446+16+4] = b'\x00\x00\x00\x00'
        elif target.lower() == "linux":
            # Modifier GRUB refs
            mbr_data[300:318] = b'INFECTED_GRUB_BOOT'

        # Remplacer bootcode
        mbr_data[:self.BOOTCODE_SIZE] = malicious_code

        # Garder la signature intacte (pour stealth)
        mbr_data[510:512] = b'\x55\xAA'

        # Sauvegarder
        with open(output_file, 'wb') as f:
            f.write(mbr_data)

        self.log(f"Version infectée créée: {output_file}")

    def compare(self, file1: str, file2: str):
        """Comparer deux MBRs"""
        self.log(f"Comparaison: {file1} vs {file2}")

        mbr1 = self.read_mbr(file1)
        mbr2 = self.read_mbr(file2)

        # Comparer bootcode
        bootcode_equal = (mbr1[:446] == mbr2[:446])
        self.log(f"Bootcode identique: {bootcode_equal}")

        # Comparer partition table
        pt1 = self.parse_partition_table(mbr1[446:510])
        pt2 = self.parse_partition_table(mbr2[446:510])

        for i in range(4):
            if pt1[i].sectors != pt2[i].sectors:
                self.log(f"Partition {i}: Size change {pt1[i].sectors} → {pt2[i].sectors}", "WARN")

        # Comparer signature
        sig1 = struct.unpack('<H', mbr1[510:512])[0]
        sig2 = struct.unpack('<H', mbr2[510:512])[0]
        self.log(f"Signature: 0x{sig1:04X} vs 0x{sig2:04X}")


def main():
    parser = argparse.ArgumentParser(
        description="Lab 1: MBR Analysis & Forensics Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 lab1_mbr_analyzer.py --analyze windows7_mbr.bin
  python3 lab1_mbr_analyzer.py --inject-bootkit clean.bin infected.bin
  python3 lab1_mbr_analyzer.py --compare file1.bin file2.bin
        """
    )

    parser.add_argument('--analyze', type=str, help='Analyser un MBR')
    parser.add_argument('--inject-bootkit', nargs=2, metavar=('INPUT', 'OUTPUT'),
                       help='Créer version infectée (simulation)')
    parser.add_argument('--compare', nargs=2, metavar=('FILE1', 'FILE2'),
                       help='Comparer deux MBRs')
    parser.add_argument('--filesystem', type=str, choices=['ntfs', 'ext4'],
                       help='Type filesystem')
    parser.add_argument('--target', type=str, choices=['windows', 'linux'],
                       default='windows', help='Cible de l\'injection')
    parser.add_argument('-v', '--verbose', action='store_true', default=True,
                       help='Mode verbeux')

    args = parser.parse_args()

    analyzer = MBRAnalyzer(verbose=args.verbose)

    if args.analyze:
        analyzer.analyze(args.analyze, filesystem=args.filesystem)
    elif args.inject_bootkit:
        analyzer.inject_bootkit(args.inject_bootkit[0], args.inject_bootkit[1],
                               target=args.target)
    elif args.compare:
        analyzer.compare(args.compare[0], args.compare[1])
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
