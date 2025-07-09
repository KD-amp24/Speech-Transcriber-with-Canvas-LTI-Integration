from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from jwcrypto import jwk

# Load public key from PEM file
with open("public.key", "rb") as f:
    pub_pem = f.read()

key = jwk.JWK.from_pem(pub_pem)
with open("jwk_public.json", "w") as out:
    out.write(key.export(private_key=False))
