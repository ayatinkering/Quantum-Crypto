"""ML-DSA signature demo.

ML-DSA is the NIST-standardized post-quantum digital signature algorithm
formerly known as CRYSTALS-Dilithium. It provides authenticity and integrity,
not encryption.
"""

from __future__ import annotations

from hashlib import sha256

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import mldsa


MESSAGE = b"Firmware update manifest: version=1.4.2, sha256=example"
TAMPERED_MESSAGE = b"Firmware update manifest: version=9.9.9, sha256=example"


def short_fingerprint(data: bytes) -> str:
    """Return a short digest for readable output."""
    return sha256(data).hexdigest()[:16]


def verify_signature(public_key: mldsa.MLDSA65PublicKey, signature: bytes, message: bytes) -> bool:
    """Return True when the ML-DSA signature is valid for the message."""
    try:
        public_key.verify(signature, message)
        return True
    except InvalidSignature:
        return False


def main() -> None:
    # ML-DSA-65 is a middle security level suitable for many demonstrations.
    private_key = mldsa.MLDSA65PrivateKey.generate()
    public_key = private_key.public_key()

    # Signing binds the private key to the exact message bytes.
    signature = private_key.sign(MESSAGE)

    valid_original = verify_signature(public_key, signature, MESSAGE)
    valid_tampered = verify_signature(public_key, signature, TAMPERED_MESSAGE)

    print("ML-DSA-65 signature verification")
    print(f"Public key size: {len(public_key.public_bytes_raw())} bytes")
    print(f"Signature size: {len(signature)} bytes")
    print(f"Message fingerprint: {short_fingerprint(MESSAGE)}")
    print(f"Signature fingerprint: {short_fingerprint(signature)}")
    print(f"Original message verifies: {valid_original}")
    print(f"Tampered message verifies: {valid_tampered}")


if __name__ == "__main__":
    main()
