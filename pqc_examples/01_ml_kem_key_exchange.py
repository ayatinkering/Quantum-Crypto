"""ML-KEM key exchange demo.

ML-KEM is the NIST-standardized post-quantum key encapsulation mechanism
formerly known as CRYSTALS-Kyber. It is used to establish a shared secret over
an insecure channel.
"""

from __future__ import annotations

from hashlib import sha256

from cryptography.hazmat.primitives.asymmetric import mlkem


def short_fingerprint(data: bytes) -> str:
    """Return a short digest for printing binary values safely."""
    return sha256(data).hexdigest()[:16]


def main() -> None:
    # Receiver generates an ML-KEM private/public key pair.
    receiver_private_key = mlkem.MLKEM768PrivateKey.generate()
    receiver_public_key = receiver_private_key.public_key()

    # Sender uses the receiver public key to create a ciphertext and a secret.
    sender_shared_secret, ciphertext = receiver_public_key.encapsulate()

    # Receiver decapsulates the ciphertext with the private key to recover the
    # same shared secret.
    receiver_shared_secret = receiver_private_key.decapsulate(ciphertext)

    # Public key, ciphertext, and shared secret are byte strings. Only the public
    # key and ciphertext are sent over the network.
    public_key_bytes = receiver_public_key.public_bytes_raw()

    print("ML-KEM-768 key exchange")
    print(f"Public key size: {len(public_key_bytes)} bytes")
    print(f"Ciphertext size: {len(ciphertext)} bytes")
    print(f"Shared secret size: {len(sender_shared_secret)} bytes")
    print(f"Sender secret fingerprint:   {short_fingerprint(sender_shared_secret)}")
    print(f"Receiver secret fingerprint: {short_fingerprint(receiver_shared_secret)}")
    print(f"Secrets match: {sender_shared_secret == receiver_shared_secret}")


if __name__ == "__main__":
    main()
