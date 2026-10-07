"""QKD key usage demo with one-time-pad encryption.

BB84 creates shared key bits. A one-time pad uses those bits by XORing each
message bit with one key bit. The same operation decrypts the ciphertext.
"""

from __future__ import annotations

from bb84_protocol import run_bb84_no_eve, run_bb84_with_intercept_resend


MESSAGE = "QKD DEMO"


def bytes_to_bits(data: bytes) -> list[int]:
    """Convert bytes into bits, most significant bit first."""
    bits: list[int] = []
    for byte in data:
        bits.extend((byte >> shift) & 1 for shift in range(7, -1, -1))
    return bits


def bits_to_bytes(bits: list[int]) -> bytes:
    """Convert a multiple-of-eight bit list back into bytes."""
    output = bytearray()
    for start in range(0, len(bits), 8):
        byte = 0
        for bit in bits[start : start + 8]:
            byte = (byte << 1) | bit
        output.append(byte)
    return bytes(output)


def xor_bits(left: list[int], right: list[int]) -> list[int]:
    """XOR two equal-length bit lists."""
    return [a ^ b for a, b in zip(left, right)]


def encrypt_with_qkd_key(message: str, key_bits: list[int]) -> tuple[list[int], str]:
    """Encrypt a message with one-time-pad XOR."""
    message_bits = bytes_to_bits(message.encode("utf-8"))
    if len(key_bits) < len(message_bits):
        raise ValueError("QKD key is shorter than the message bits.")

    ciphertext_bits = xor_bits(message_bits, key_bits[: len(message_bits)])
    ciphertext_hex = bits_to_bytes(ciphertext_bits).hex()
    return ciphertext_bits, ciphertext_hex


def decrypt_with_qkd_key(ciphertext_bits: list[int], key_bits: list[int]) -> str:
    """Decrypt a one-time-pad ciphertext with the same QKD key bits."""
    recovered_bits = xor_bits(ciphertext_bits, key_bits[: len(ciphertext_bits)])
    return bits_to_bytes(recovered_bits).decode("utf-8")


def run_scenario(name: str, eve_present: bool) -> None:
    """Run key generation and message encryption for one channel scenario."""
    bit_count = 256
    run = (
        run_bb84_with_intercept_resend(bit_count=bit_count, seed=7)
        if eve_present
        else run_bb84_no_eve(bit_count=bit_count, seed=7)
    )

    print(f"\nScenario: {name}")
    print(f"Sifted key length: {len(run.alice_sifted_key)} bits")
    print(f"QBER: {run.qber:.2%}")
    print(f"Key accepted: {run.accepted}")

    if not run.accepted:
        print("Message encryption blocked: QBER is above the accepted threshold.")
        return

    ciphertext_bits, ciphertext_hex = encrypt_with_qkd_key(MESSAGE, run.alice_sifted_key)
    recovered_message = decrypt_with_qkd_key(ciphertext_bits, run.bob_sifted_key)

    print(f"Original message: {MESSAGE}")
    print(f"Ciphertext hex: {ciphertext_hex}")
    print(f"Recovered message: {recovered_message}")
    print(f"Message recovered correctly: {recovered_message == MESSAGE}")


def main() -> None:
    print("QKD secure message demo")
    run_scenario("clean quantum channel", eve_present=False)
    run_scenario("intercept-resend attack", eve_present=True)


if __name__ == "__main__":
    main()
