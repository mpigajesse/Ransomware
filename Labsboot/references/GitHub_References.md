# Ressources GitHub et documentation
## Bootkits, MBR, VBR, UEFI, Boot Sector et Petya

> Document de recherche destiné à l'étude de la sécurité du processus de démarrage, des bootkits, du MBR/VBR, de l'UEFI et des techniques de détection.
>
> Les projets capables de modifier directement le démarrage ou le disque doivent être étudiés exclusivement dans une machine virtuelle/laboratoire isolé.

---

# 1. Projets MBR / Boot Sector

## 1.1 OpenPetya

**GitHub :**  
https://github.com/iss4cf0ng/OpenPetya

**Domaine :**
- MBR
- Bootloader
- Bootkit
- NTFS
- Petya
- Ransomware PoC
- Assembly
- C/C++

**Description :**

OpenPetya est un Proof-of-Concept éducatif inspiré de Petya. Le projet implémente notamment un MBR personnalisé, un bootloader en plusieurs étapes, une transition vers le Protected Mode et une simulation de mécanismes de chiffrement liés à NTFS.

Le dépôt indique explicitement qu'il est destiné à l'apprentissage et à la recherche.

**Intérêt académique :** ★★★★★

**Lien :**  
https://github.com/iss4cf0ng/OpenPetya

---

# 2. Analyse de Petya

## 2.1 Petya 2017 Reverse Engineering Notes

**GitHub :**  
https://github.com/aguinet/petya2017_notes

**Domaine :**
- Reverse engineering
- Petya
- MBR
- Bootloader
- Ransomware analysis

**Intérêt :**

Permet d'étudier le fonctionnement interne de Petya et les mécanismes utilisés autour du processus de démarrage.

**Intérêt académique :** ★★★★★

---

# 3. Analyse des MBR / VBR / IPL

## 3.1 ANSSI — bootcode_parser

**GitHub :**  
https://github.com/ANSSI-FR/bootcode_parser

**Auteur/Organisation :** ANSSI

**Domaine :**
- MBR
- VBR
- IPL
- Forensics
- Bootkit detection
- Disk image analysis

**Description :**

`bootcode_parser.py` analyse les enregistrements de démarrage des systèmes BIOS et recherche des signatures connues afin d'identifier des anomalies.

Il peut notamment analyser :

- MBR
- VBR
- IPL
- images disque complètes

Le dépôt fournit également des exemples d'images infectées par des bootkits tels que Gapz et Rovnix.

**Intérêt académique :** ★★★★★

**Lien :**  
https://github.com/ANSSI-FR/bootcode_parser

---

# 4. Détection OpenPetya / Petya

## 4.1 OpenPetya-Defense

**GitHub :**  
https://github.com/mutedmouse/OpenPetya-Defense

**Domaine :**
- YARA
- Malware detection
- Bootkit detection
- MBR analysis
- Petya detection

Le dépôt contient notamment des règles YARA permettant d'identifier des caractéristiques associées au MBR et au bootloader de type Petya/OpenPetya.

**Intérêt académique :** ★★★★★

**Lien :**  
https://github.com/mutedmouse/OpenPetya-Defense

---

# 5. Collection de Bootkits

## 5.1 HardenedVault — bootkit-samples

**GitHub :**  
https://github.com/hardenedvault/bootkit-samples

**Domaine :**
- Bootkits
- Firmware attacks
- MBR
- VBR
- ESP
- DXE
- UEFI
- Threat research

Le dépôt rassemble des références et échantillons liés à plusieurs générations de bootkits.

On y retrouve notamment :

- FinSpy
- ESPecter
- Rovnix
- MosaicRegressor
- MoonBounce
- CosmicStrand
- BlackLotus
- Bootkitty

Le dépôt montre également l'évolution des attaques, des anciennes techniques MBR/VBR vers les attaques modernes ciblant ESP, DXE et PEI.

**Intérêt académique :** ★★★★★

**Lien :**  
https://github.com/hardenedvault/bootkit-samples

---

# 6. Développement de Bootkits UEFI

## 6.1 Bootkits Development Starter Pack

**GitHub :**  
https://github.com/TheMalwareGuardian/Bootkits-Development-Starter-Pack

**Domaine :**
- UEFI
- EFI
- DXE
- Bootkit
- Boot process
- Low-level programming

Le projet rassemble plusieurs Proof-of-Concept UEFI et DXE destinés à comprendre différentes étapes du processus de démarrage et certaines fonctionnalités utilisées par les bootkits.

**Intérêt académique :** ★★★★★

**Lien :**  
https://github.com/TheMalwareGuardian/Bootkits-Development-Starter-Pack

---

# 7. UEFI Vulnerability Research

## 7.1 Awesome Bring Your Own Vulnerable UEFI Application

**GitHub :**  
https://github.com/TheMalwareGuardian/Awesome-Bring-Your-Own-Vulnerable-UEFI-Application

**Domaine :**
- UEFI
- Firmware security
- Vulnerabilities
- Secure Boot
- Bootkit research
- Exploitation research

Il s'agit d'une collection de ressources, PoC, publications et recherches concernant les vulnérabilités UEFI et les attaques permettant potentiellement l'installation de bootkits.

**Intérêt académique :** ★★★★★

**Lien :**  
https://github.com/TheMalwareGuardian/Awesome-Bring-Your-Own-Vulnerable-UEFI-Application

---

# 8. UEFI Bootkit — Aidan Khoury

## 8.1 UEFI-Bootkit

**GitHub :**  
https://github.com/ajkhoury/UEFI-Bootkit

**Domaine :**
- UEFI
- EFI
- Runtime Driver
- Bootkit
- Windows internals

Projet de bootkit UEFI utilisant une architecture permettant de travailler sans dépendre directement de l'Assembly x64. Le dépôt date de 2016–2019 et est associé à des travaux de Quarkslab.

**Intérêt académique :** ★★★★★

**Lien :**  
https://github.com/ajkhoury/UEFI-Bootkit

---

# 9. UEFI Bootkit — umap

## 9.1 btbd/umap

**GitHub :**  
https://github.com/btbd/umap

**Domaine :**
- Windows
- UEFI
- Bootkit
- Driver mapping
- Kernel

Le projet étudie un bootkit UEFI capable de charger un mécanisme de mapping de driver pendant le processus de démarrage.

**Intérêt académique :** ★★★★☆

**Lien :**  
https://github.com/btbd/umap

---

# 10. Bootkit en Rust

## 10.1 disaqt/bootkit-rs

**GitHub :**  
https://github.com/disaqt/bootkit-rs

**Domaine :**
- Rust
- UEFI
- Bootkit
- Windows boot process

Le dépôt contient un PoC de bootkit UEFI et référence notamment plusieurs projets de recherche UEFI/bootkit.

**Intérêt académique :** ★★★★☆

**Lien :**  
https://github.com/disaqt/bootkit-rs

---

# 11. Sources et références associées

Le projet `bootkit-rs` référence notamment les travaux suivants :

## 11.1 BTBD — umap

https://github.com/btbd/umap

## 11.2 Austin Hudson — bootlicker

https://github.com/realoriginal/bootlicker

## 11.3 Aidan Khoury — UEFI-Bootkit

https://github.com/ajkhoury/UEFI-Bootkit

## 11.4 Matthijs Lavrijsen — EfiGuard

https://github.com/Mattiwatti/EfiGuard

EfiGuard est particulièrement intéressant pour l'étude de la chaîne de démarrage Windows et des mécanismes de protection associés.

---

# 12. Tableau récapitulatif

| Projet | Technologie | Domaine | Intérêt |
|---|---|---|---:|
| OpenPetya | MBR / Assembly / C++ | Petya / Bootkit | ★★★★★ |
| petya2017_notes | Reverse engineering | Petya | ★★★★★ |
| bootcode_parser | Python | MBR/VBR/Forensics | ★★★★★ |
| OpenPetya-Defense | YARA | Détection | ★★★★★ |
| bootkit-samples | MBR/ESP/DXE | Threat research | ★★★★★ |
| Bootkits Development Starter Pack | UEFI/DXE | Recherche UEFI | ★★★★★ |
| Awesome BYOVU | UEFI | Vulnerability research | ★★★★★ |
| UEFI-Bootkit | UEFI | Bootkit research | ★★★★★ |
| umap | UEFI | Windows bootkit | ★★★★☆ |
| bootkit-rs | UEFI/Rust | Bootkit research | ★★★★☆ |
| EfiGuard | UEFI/Windows | Boot security research | ★★★★☆ |

---

# 13. Requêtes GitHub utiles

Pour poursuivre la recherche directement sur GitHub :

```text
bootkit
```

```text
MBR bootkit
```

```text
boot sector malware
```

```text
MBR malware
```

```text
VBR bootkit
```

```text
UEFI bootkit
```

```text
UEFI rootkit
```

```text
UEFI malware
```

```text
EFI bootkit
```

```text
DXE bootkit
```

```text
Petya MBR
```

```text
Petya bootloader
```

```text
MBR ransomware
```

```text
bootkit detection
```

```text
boot sector forensics
```

---

# 14. Requêtes Google ciblées vers GitHub

```text
site:github.com "MBR" "bootkit"
```

```text
site:github.com "boot sector" malware
```

```text
site:github.com "VBR" bootkit
```

```text
site:github.com "UEFI" "bootkit"
```

```text
site:github.com "DXE" bootkit
```

```text
site:github.com "Petya" "MBR"
```

```text
site:github.com "Petya" bootloader
```

```text
site:github.com "bootkit" "ransomware"
```

```text
site:github.com "bootkit" "reverse engineering"
```

```text
site:github.com "MBR" malware analysis
```

```text
site:github.com "UEFI" malware research
```

---

# 15. Ressources à privilégier pour un laboratoire académique

Pour construire une étude sérieuse, l'ordre recommandé est :

### Étape 1 — Comprendre le démarrage

- MBR
- VBR
- IPL
- BIOS
- UEFI
- EFI System Partition
- Windows Boot Manager

### Étape 2 — Étudier les bootkits historiques

- Rovnix
- Gapz
- Petya
- NotPetya
- TDL4/Alureon

### Étape 3 — Étudier les bootkits modernes

- ESPecter
- MosaicRegressor
- MoonBounce
- CosmicStrand
- BlackLotus
- Bootkitty

### Étape 4 — Étudier la détection

- bootcode_parser
- YARA
- analyse hexadécimale
- comparaison de MBR/VBR
- analyse des images disque
- Secure Boot
- intégrité de l'ESP

### Étape 5 — Expérimentation contrôlée

Utiliser exclusivement :

- VMware/VirtualBox
- snapshots
- disques virtuels
- réseau isolé
- copies de machines virtuelles
- images de test
- données sans valeur

---

# 16. Sources principales

1. OpenPetya  
   https://github.com/iss4cf0ng/OpenPetya

2. ANSSI bootcode_parser  
   https://github.com/ANSSI-FR/bootcode_parser

3. OpenPetya-Defense  
   https://github.com/mutedmouse/OpenPetya-Defense

4. HardenedVault bootkit-samples  
   https://github.com/hardenedvault/bootkit-samples

5. Bootkits Development Starter Pack  
   https://github.com/TheMalwareGuardian/Bootkits-Development-Starter-Pack

6. Awesome Bring Your Own Vulnerable UEFI Application  
   https://github.com/TheMalwareGuardian/Awesome-Bring-Your-Own-Vulnerable-UEFI-Application

7. Aidan Khoury UEFI-Bootkit  
   https://github.com/ajkhoury/UEFI-Bootkit

8. BTBD umap  
   https://github.com/btbd/umap

9. disaqt bootkit-rs  
   https://github.com/disaqt/bootkit-rs

10. EfiGuard  
    https://github.com/Mattiwatti/EfiGuard

---

# 17. Conclusion

Ces ressources couvrent pratiquement toute la chaîne d'étude :

**Boot Sector → MBR → VBR → IPL → Bootloader → UEFI → ESP → DXE → Bootkit → Ransomware → Reverse Engineering → Detection → Forensics**

Pour un projet académique de cybersécurité, les trois ressources les plus complémentaires sont :

**OpenPetya** → comprendre une implémentation de PoC MBR/bootkit.  
**ANSSI bootcode_parser** → analyser et détecter les anomalies du démarrage.  
**bootkit-samples** → étudier l'évolution des bootkits historiques et modernes.

Toutes les expérimentations modifiant le secteur de démarrage doivent rester confinées à des machines virtuelles et des images disque de laboratoire.