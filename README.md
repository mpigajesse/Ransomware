# Laboratoire Ransomware - Projet Éducatif

> ⚠️ **AVERTISSEMENT** : Ce projet est destiné à des fins **éducatives et de recherche en cybersécurité uniquement**. 
> Il simule un ransomware pour comprendre les mécanismes de chiffrement et les techniques de sécurité. 
> L'utilisation malveillante est strictement interdite.

## 📋 Vue d'ensemble

Ce projet démontre comment un ransomware sophistiqué pourrait fonctionner en implémentant :

- **Chiffrement hybride** : RSA pour la signature + AES pour le chiffrement des données
- **Signature numérique** : Authentification cryptographique de la clé AES
- **Gestion de base de données** : Chiffrement sélectif des données sensibles dans MariaDB
- **Communication sécurisée** : Transmission de clés publiques pour le déchiffrement

## 🏗️ Architecture

### Flux de chiffrement

```
1. Génération des clés RSA (1024 bits)
   ├─ Clé privée (gardée secrète par l'attaquant)
   └─ Clé publique (partagée avec la victime)

2. Extraction des données
   └─ Récupération des enregistrements depuis MariaDB

3. Chiffrement hybride
   ├─ Génération d'une clé AES aléatoire (256 bits)
   ├─ Chiffrement des données avec AES-256-CBC
   ├─ Signature de la clé AES avec la clé privée RSA
   └─ Assemblage du payload complet (signature + clé + données)

4. Mise à jour de la base de données
   └─ Remplacement des données par le payload chiffré

5. Demande de rançon
   └─ Message d'extorsion avec instructions de paiement
```

## 📁 Structure du projet

```
Ransomware/
├── kali/                          # Scripts principaux (Kali Linux - Attaquant)
│   ├── ransomware.py             # Script de chiffrement des données
│   ├── generer_cles.py           # Génération des clés RSA
│   ├── envoyer_cle.py            # Envoi de la clé publique à la victime
│   ├── requirements.txt           # Dépendances Python (kali)
│   ├── cle_privee.pem            # Clé privée RSA (secret)
│   ├── cle_publique.pem          # Clé publique RSA (partagée)
│   └── ransomware_info.txt       # Métadonnées du chiffrement
├── ubuntu/                        # Scripts de vérification/décryptage (Ubuntu - Victime)
│   ├── check_ransomware.py       # Vérification de l'intégrité des données
│   └── requirements.txt           # Dépendances Python (ubuntu)
└── README.md                      # Ce fichier
```

## 🚀 Installation et Configuration

### Prérequis

- Python 3.8+
- MariaDB/MySQL en réseau local
- Bibliothèques cryptographiques

### Étape 1 : Installation des dépendances

#### **Pour Kali Linux (Attaquant)**

```bash
cd kali

# Créer un environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate

# Installer les dépendances depuis requirements.txt
pip install -r requirements.txt
```

**Dépendances installées :**
- `cryptography` - Génération de clés RSA, chiffrement AES, signatures numériques
- `PyMySQL` - Connexion et manipulation de MariaDB/MySQL
- `yagmail` - Envoi d'email via SMTP (pour envoyer la clé publique)

---

#### **Pour Ubuntu/Debian (Victime)**

```bash
cd ubuntu

# Créer un environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate

# Installer les dépendances depuis requirements.txt
pip install -r requirements.txt
```

**Dépendances installées :**
- `cryptography` - Vérification de signatures, déchiffrement AES
- `PyMySQL` - Connexion et récupération de données dans MariaDB/MySQL

---

#### **Détail des dépendances**

| Bibliothèque | Version Min | Utilisation |
|---|---|---|
| `cryptography` | 42.0.0 | Chiffrement RSA/AES, signatures PKCS1v15-SHA256 |
| `PyMySQL` | 1.1.0 | Connexion MariaDB/MySQL, requêtes SQL |
| `yagmail` | 0.15.0 | Envoi d'email SMTP (Kali uniquement) |

### ✅ Fichiers requirements.txt inclus

Deux fichiers `requirements.txt` sont fournis avec le projet :

- **`kali/requirements.txt`** - Dépendances pour l'attaquant
  - cryptography, PyMySQL, yagmail
  - À utiliser dans le dossier `kali/`

- **`ubuntu/requirements.txt`** - Dépendances pour la victime
  - cryptography, PyMySQL
  - À utiliser dans le dossier `ubuntu/`

Ces fichiers spécifient les versions testées et recommandées. Utilisez-les avec :
```bash
pip install -r requirements.txt
```

### Étape 2 : Générer les clés RSA

```bash
cd kali
python generer_cles.py
```

**Sortie attendue :**
```
Génération des clés RSA (1024 bits)...
Clés RSA générées avec succès !
   cle_privee.pem : clé privée à conserver secrètement
   cle_publique.pem : clé publique pouvant être partagée
   Taille de la clé publique : 451 caractères
```

### Étape 3 : Configurer la base de données

Éditer `ransomware.py` et mettre à jour `DB_CONFIG` :

```python
DB_CONFIG = {
    'host': '192.168.X.X',         # IP de votre serveur MariaDB
    'user': 'your_username',        # Utilisateur MariaDB
    'password': 'your_password',    # Mot de passe
    'database': 'your_database',    # Nom de la base
    'charset': 'utf8mb4'
}
```

**La table cible doit avoir une colonne `donnees_chiffrees` :**

```sql
ALTER TABLE salariée ADD COLUMN donnees_chiffrees LONGTEXT;
```

## 🔐 Utilisation

### 1. Chiffrer les données

```bash
cd kali
python ransomware.py
```

**Actions effectuées :**
- ✅ Charge les clés RSA
- ✅ Se connecte à la base de données
- ✅ Récupère les enregistrements sensibles
- ✅ Chiffre les données avec AES-256-CBC
- ✅ Signe la clé AES avec RSA-PKCS1v15-SHA256
- ✅ Stocke le payload chiffré dans `donnees_chiffrees`
- ✅ Efface les colonnes originales (nom, prénom, email, etc.)
- ✅ Enregistre les métadonnées dans `ransomware_info.txt`
- ✅ Affiche un message de rançon

### 2. Envoyer la clé publique à la victime

```bash
python envoyer_cle.py
```

La clé publique `cle_publique.pem` est envoyée au contact spécifié.

### 3. Vérifier les données (côté victime)

```bash
cd ubuntu
python check_ransomware.py
```

Ce script :
- Charge la clé publique RSA
- Vérifie la signature du payload
- Déchiffre les données AES
- Affiche les enregistrements restaurés

## 🔍 Détails techniques

### Chiffrement AES-256-CBC

```python
def chiffrer_aes(data, cle_aes):
    iv = os.urandom(16)  # IV aléatoire (nécessaire pour CBC)
    cipher = Cipher(algorithms.AES(cle_aes), modes.CBC(iv), ...)
    # Padding PKCS7
    pad_len = 16 - (len(data) % 16)
    data_padded = data + bytes([pad_len] * pad_len)
    # Retour: IV + données chiffrées
    return iv + chiffre
```

**Propriétés :**
- **Clé** : 256 bits (32 octets)
- **Mode** : CBC (Cipher Block Chaining)
- **Padding** : PKCS7
- **IV** : Aléatoire et non secret (transmis en clair)

### Signature RSA-PKCS1v15-SHA256

```python
def signer_cle_aes_avec_privee(cle_aes, cle_privee):
    return cle_privee.sign(
        cle_aes,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
```

**Vérification (côté victime) :**
```python
public_key.verify(
    signature,
    cle_aes,
    padding.PKCS1v15(),
    hashes.SHA256()
)
```

### Structure du Payload

```
[Taille Signature (4 bytes)] + [Signature RSA] + [Taille AES (4 bytes)] 
+ [Clé AES] + [Données chiffrées AES]
```

Tout est encodé en Base64 pour transmission textuelle.

## 📊 Flux d'exécution détaillé

```
┌─────────────────────────────────────────────┐
│ 1. GÉNÉRATION DES CLÉS (generer_cles.py)   │
│    Output: cle_privee.pem, cle_publique.pem│
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│ 2. CHIFFREMENT (ransomware.py)              │
│    • Connexion BD                           │
│    • Extraction données                     │
│    • Génération clé AES                     │
│    • Chiffrement AES-256-CBC                │
│    • Signature RSA de la clé AES            │
│    • Update BD avec payload chiffré         │
│    • Sauvegarde ransomware_info.txt         │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│ 3. ENVOI CLÉ PUBLIQUE (envoyer_cle.py)     │
│    Email: cle_publique.pem à la victime    │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│ 4. DÉCHIFFREMENT (check_ransomware.py)      │
│    • Charger cle_publique.pem              │
│    • Récupérer payload chiffré BD          │
│    • Vérifier signature RSA                │
│    • Extraire clé AES                      │
│    • Déchiffrer données AES-256-CBC        │
│    • Parser JSON et restaurer données      │
└─────────────────────────────────────────────┘
```

## 🛡️ Concepts de sécurité enseignés

| Concept | Implémentation | But éducatif |
|---------|----------------|------------|
| **Chiffrement asymétrique** | RSA 1024 bits | Comprendre les clés publique/privée |
| **Chiffrement symétrique** | AES-256-CBC | Vitesse + sécurité pour données volumineuses |
| **Signature numérique** | RSA-PKCS1v15-SHA256 | Authentification et non-répudiation |
| **Chaînage hybride** | RSA(AES_key) | Combiner avantages des deux algorithmes |
| **Gestion de clés** | Fichiers PEM | Sérialisation et stockage sécurisé |
| **Injecter en base de données** | Modification des schémas | Impact réel des attaques |

## ⚠️ Limitations intentionnelles

Cette implémentation est volontairement **simplifiée** pour l'apprentissage :

- ⚠️ **Clés RSA 1024 bits** (non cryptographiquement sûres en 2026)
- ⚠️ **Pas de chiffrement de fichiers** (uniquement base de données)
- ⚠️ **Métadonnées en texte clair** (ransomware_info.txt)
- ⚠️ **Logs verbeux** (un vrai ransomware serait silencieux)
- ⚠️ **Pas de persistance** (un vrai ransomware resterait actif)
- ⚠️ **Pas de C2** (Communication & Control)

## 📚 Points d'apprentissage recommandés

1. **Cryptographie** :
   - Différence RSA vs AES
   - Pourquoi utiliser un hybride ?
   - Rôle de l'IV en CBC

2. **Sécurité des bases de données** :
   - Injection SQL (risque lors de l'extraction)
   - Chiffrement au repos
   - Sauvegarde et restauration

3. **Détection et défense** :
   - Signatures de malware
   - Analyse comportementale
   - Segmentation réseau
   - Backups immuables

4. **Forensique** :
   - Récupération de données chiffrées
   - Analyse des métadonnées
   - Timeline des événements

## 🔗 Ressources

- [Cryptography.io - Python](https://cryptography.io/)
- [OWASP - Ransomware](https://owasp.org/www-community/attacks/Ransomware)
- [CIS Controls - Ransomware Defense](https://www.cisecurity.org/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

## 📝 Auteur

**Jesse Mpiga-Odoumba**

- **Titre** : Développeur Full-Stack Web & Mobile | Ingénieur IA & Big Data
- **Spécialités** : Cybersécurité, Cryptographie, Architecture système
- **Email** : [jesse.mpiga@a-ct.ma](mailto:jesse.mpiga@a-ct.ma) | [mpigajesse@gmail.com](mailto:mpigajesse@gmail.com)
- **Téléphone** : +212 779-635-687
- **LinkedIn** : [linkedin.com/in/mpiga-jesse](https://linkedin.com/in/mpiga-jesse)
- **GitHub** : [github.com/mpigajesse](https://github.com/mpigajesse)
- **Localisation** : Casablanca, Maroc

**Compétences pertinentes au projet** :
- Cryptographie appliquée (libsodium, RSA, AES)
- Systèmes, réseaux & cybersécurité
- Python, TypeScript, Rust
- Architecture logicielle souveraine
- Analyse de sécurité et forensique

**Formation** :
- 🎓 Diplôme d'Ingénieur IA & Big Data (EIGSI Casablanca) - 2026
- 🎓 Licence Pro. Administration & Sécurités Réseaux (INPTIC Gabon) - 2023
- 🎓 Technicien Supérieur Réseaux & Télécoms (INPTIC Gabon) - 2022

**Certifications** :
- OCI 2025 - AI Foundations Associate
- OCI 2025 - Generative AI Professional
- OCI 2025 - Multicloud Architect Pro

**Contexte du projet** : Laboratoire pédagogique de cybersécurité (2026)

## ⚖️ Légalité

**Ce code est fourni à titre éducatif uniquement.** 

Toute utilisation pour :
- Attaquer des systèmes sans autorisation
- Demander des rançons
- Voler des données
- Perturber des services

est **illégale** et poursuivie pénalement selon les lois locales sur la cybercriminalité.

## 🚫 Clause de non-responsabilité

Les auteurs de ce projet ne sont **pas responsables** de tout dommage, perte de données, ou activité malveillante résultant de l'utilisation de ce code. 

**L'utilisateur accepte d'utiliser ce matériel dans un contexte éducatif approuvé et légal uniquement.**

---

✅ **Utilisation autorisée** : Laboratoires universitaires, formation en cybersécurité, recherche approuvée  
❌ **Utilisation interdite** : Attaques réelles, activités criminelles, utilisation sans consentement
