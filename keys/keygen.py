from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Generate private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Serialize the private key to PEM format
pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Save to file
with open("private.key", "wb") as f:
    f.write(pem)

print("✅ private.key file successfully generated.")
