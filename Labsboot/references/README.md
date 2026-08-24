# Références Bootkit - Ressources d'apprentissage

Ce dossier contient les ressources utilisées pour comprendre et implémenter le Bootkit POC.

## Fichiers de référence

- **GitHub_References.md** - Collection complète de projets GitHub bootkit éducatifs
  - OpenPetya
  - Petya 2017 Notes
  - ANSSI bootcode_parser
  - OpenPetya-Defense
  - HardenedVault bootkit-samples

## Projets principaux à étudier

1. **OpenPetya** (https://github.com/iss4cf0ng/OpenPetya)
   - MBR bootcode implementation
   - Stage 1 + Stage 2 architecture
   - NTFS encryption simulation

2. **ANSSI bootcode_parser** (https://github.com/ANSSI-FR/bootcode_parser)
   - MBR/VBR forensic analysis
   - Bootkit detection
   - Anomaly identification

3. **Petya 2017 Notes** (https://github.com/aguinet/petya2017_notes)
   - Reverse engineering insights
   - Ransomware behavior
   - Boot sector attacks

## Utilisation pour Labsboot

Ces références informent l'implémentation du Bootkit POC:
- Architecture MBR stage 1 (446 bytes)
- x86 16-bit assembly code
- Partition table stealth techniques
- Detection avoidance strategies

Voir BOOTKIT_POC.md pour l'implémentation complète.
