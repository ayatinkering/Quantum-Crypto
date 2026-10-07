"""ML-KEM plus AES-GCM file encryption demo.

ML-KEM establishes a shared secret. HKDF converts that shared secret into a
fixed-length symmetric encryption key. AES-GCM encrypts and authenticates the
file content.
"""

from __future__ import annotations

import base64
import json
from os import urandom
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import mlkem
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


OUTPUT_PATH = Path("/tmp/mlkem_aes_demo_message.json")
PLAINTEXT = b"Quantum-safe file encryption demo using ML-KEM + AES-GCM."


def derive_aes_key(shared_secret: bytes, salt: bytes) -> bytes:
    """Derive a 256-bit AES key from the ML-KEM shared secret."""
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=b"ml-kem-768 aes-gcm file encryption demo",
    )
    return hkdf.derive(shared_secret)


def b64encode(data: bytes) -> str:
    """Encode bytes as printable text for JSON storage."""
    return base64.b64encode(data).decode("ascii")


def b64decode(data: str) -> bytes:
    """Decode base64 text back into bytes."""
    return base64.b64decode(data.encode("ascii"))


def encrypt_message() -> dict[str, str]:
    """Encrypt the demo message with a key established through ML-KEM."""
    receiver_private_key = mlkem.MLKEM768PrivateKey.generate()
    receiver_public_key = receiver_private_key.public_key()

    # Sender creates a shared secret and a KEM ciphertext for the receiver.
    sender_shared_secret, kem_ciphertext = receiver_public_key.encapsulate()

    # A random salt keeps HKDF output separated across different encryptions.
    salt = urandom(16)
    aes_key = derive_aes_key(sender_shared_secret, salt)

    # AES-GCM requires a unique nonce for each encryption under the same key.
    nonce = urandom(12)
    aesgcm = AESGCM(aes_key)
    encrypted_payload = aesgcm.encrypt(nonce, PLAINTEXT, associated_data=None)

    # The receiver private key is kept only for the local decrypt step in this
    # demo. Real applications store it securely and never write it into messages.
    return {
        "algorithm": "ML-KEM-768 + HKDF-SHA256 + AES-256-GCM",
        "kem_ciphertext": b64encode(kem_ciphertext),
        "salt": b64encode(salt),
        "nonce": b64encode(nonce),
        "encrypted_payload": b64encode(encrypted_payload),
        "receiver_private_key": b64encode(receiver_private_key.private_bytes_raw()),
    }


def decrypt_message(package: dict[str, str]) -> bytes:
    """Decrypt the package by decapsulating ML-KEM and opening AES-GCM."""
    receiver_private_key = mlkem.MLKEM768PrivateKey.from_seed_bytes(
        b64decode(package["receiver_private_key"])
    )
    receiver_shared_secret = receiver_private_key.decapsulate(
        b64decode(package["kem_ciphertext"])
    )

    aes_key = derive_aes_key(receiver_shared_secret, b64decode(package["salt"]))
    aesgcm = AESGCM(aes_key)
    return aesgcm.decrypt(
        b64decode(package["nonce"]),
        b64decode(package["encrypted_payload"]),
        associated_data=None,
    )


def main() -> None:
    package = encrypt_message()
    OUTPUT_PATH.write_text(json.dumps(package, indent=2), encoding="utf-8")

    recovered_plaintext = decrypt_message(package)

    print("ML-KEM + AES-GCM file encryption")
    print(f"Encrypted package written to: {OUTPUT_PATH}")
    print(f"Plaintext size: {len(PLAINTEXT)} bytes")
    print(f"Encrypted payload size: {len(b64decode(package['encrypted_payload']))} bytes")
    print(f"Recovered plaintext: {recovered_plaintext.decode('utf-8')}")
    print(f"Decryption successful: {recovered_plaintext == PLAINTEXT}")


if __name__ == "__main__":
    main()
