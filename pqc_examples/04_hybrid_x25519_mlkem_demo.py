"""Hybrid X25519 + ML-KEM key exchange demo.

Hybrid key exchange combines a classical secret with a post-quantum secret.
During migration, this provides defense in depth: the final session key remains
protected if at least one component remains secure.
"""

from __future__ import annotations

from hashlib import sha256

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import mlkem, x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def derive_hybrid_key(classical_secret: bytes, pqc_secret: bytes) -> bytes:
    """Combine both shared secrets into one 256-bit session key."""
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"hybrid x25519 ml-kem-768 demo",
    )
    return hkdf.derive(classical_secret + pqc_secret)


def raw_x25519_public_key(public_key: x25519.X25519PublicKey) -> bytes:
    """Serialize an X25519 public key as 32 raw bytes."""
    return public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def short_fingerprint(data: bytes) -> str:
    """Return a short digest for readable output."""
    return sha256(data).hexdigest()[:16]


def main() -> None:
    # Receiver creates one classical key pair and one post-quantum key pair.
    receiver_x25519_private = x25519.X25519PrivateKey.generate()
    receiver_x25519_public = receiver_x25519_private.public_key()
    receiver_mlkem_private = mlkem.MLKEM768PrivateKey.generate()
    receiver_mlkem_public = receiver_mlkem_private.public_key()

    # Sender creates an ephemeral X25519 key pair for the classical half.
    sender_x25519_private = x25519.X25519PrivateKey.generate()
    sender_x25519_public = sender_x25519_private.public_key()

    # Classical shared secret: X25519 Diffie-Hellman.
    sender_classical_secret = sender_x25519_private.exchange(receiver_x25519_public)
    receiver_classical_secret = receiver_x25519_private.exchange(sender_x25519_public)

    # Post-quantum shared secret: ML-KEM encapsulation and decapsulation.
    sender_pqc_secret, kem_ciphertext = receiver_mlkem_public.encapsulate()
    receiver_pqc_secret = receiver_mlkem_private.decapsulate(kem_ciphertext)

    # Final hybrid session key: HKDF over both component secrets.
    sender_session_key = derive_hybrid_key(sender_classical_secret, sender_pqc_secret)
    receiver_session_key = derive_hybrid_key(receiver_classical_secret, receiver_pqc_secret)

    print("Hybrid X25519 + ML-KEM-768 key exchange")
    print(f"X25519 public key size: {len(raw_x25519_public_key(receiver_x25519_public))} bytes")
    print(f"ML-KEM public key size: {len(receiver_mlkem_public.public_bytes_raw())} bytes")
    print(f"ML-KEM ciphertext size: {len(kem_ciphertext)} bytes")
    print(f"Classical secrets match: {sender_classical_secret == receiver_classical_secret}")
    print(f"PQC secrets match: {sender_pqc_secret == receiver_pqc_secret}")
    print(f"Session key fingerprint: {short_fingerprint(sender_session_key)}")
    print(f"Session keys match: {sender_session_key == receiver_session_key}")


if __name__ == "__main__":
    main()
