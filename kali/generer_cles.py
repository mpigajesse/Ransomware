from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

# Affiche un message indiquant le début de la génération des clés.
print("Génération des clés RSA (1024 bits)...")

# Génère une nouvelle clé privée RSA de 1024 bits.
# Le paramètre public_exponent=65537 est une valeur couramment utilisée pour RSA.
# La taille de 1024 bits est volontairement utilisée ici pour simplifier la démonstration.
# Pour une utilisation réelle en production, une taille plus importante est recommandée.
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=1024,
    backend=default_backend()
)

# Extrait la clé publique à partir de la clé privée.
public_key = private_key.public_key()

# Enregistre la clé privée dans un fichier PEM.
# La clé privée ne doit pas être partagée et doit rester confidentielle.
with open("cle_privee.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Enregistre la clé publique dans un fichier PEM.
# Contrairement à la clé privée, cette clé peut être communiquée aux personnes
# qui doivent pouvoir chiffrer des données destinées au propriétaire de la clé privée.
with open("cle_publique.pem", "wb") as f:
    f.write(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

# Confirme que les deux clés ont été générées et enregistrées.
print("Clés RSA générées avec succès !")
print("   cle_privee.pem : clé privée à conserver secrètement")
print("   cle_publique.pem : clé publique pouvant être partagée")

# Ouvre le fichier de clé publique et calcule sa longueur en caractères.
with open("cle_publique.pem", "r") as f:
    public_key_content = f.read()

print(f"   Taille de la clé publique : {len(public_key_content)} caractères")
