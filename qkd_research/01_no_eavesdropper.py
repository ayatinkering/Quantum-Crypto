"""Experiment 1: BB84 without an eavesdropper.

This script corresponds to the first experiment in the IBM QKD notebook.
Alice prepares states, Bob measures them, bases are compared, and matching
positions become a sifted key.
"""

from __future__ import annotations

from bb84_protocol import bits_to_text, run_bb84_no_eve


def main() -> None:
    run = run_bb84_no_eve(bit_count=64, seed=2026)

    print("BB84 experiment: no eavesdropper")
    print(f"Raw qubits sent: {len(run.alice_bits)}")
    print(f"Matching-basis positions: {len(run.kept_positions)}")
    print(f"Alice sifted key: {bits_to_text(run.alice_sifted_key[:48])}")
    print(f"Bob sifted key:   {bits_to_text(run.bob_sifted_key[:48])}")
    print(f"QBER: {run.qber:.2%}")
    print(f"Key accepted: {run.accepted}")

    print("\nFirst 16 transmission rows")
    print("idx | Alice bit | Alice basis | Bob basis | Bob bit | kept")
    for index in range(16):
        kept = "yes" if index in run.kept_positions else "no"
        print(
            f"{index:>3} |"
            f" {run.alice_bits[index]:>9} |"
            f" {run.alice_bases[index]:>11} |"
            f" {run.bob_bases[index]:>9} |"
            f" {run.bob_bits[index]:>7} |"
            f" {kept}"
        )


if __name__ == "__main__":
    main()
