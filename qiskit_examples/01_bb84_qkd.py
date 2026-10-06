"""Simulate the BB84 quantum key distribution protocol with Qiskit.

BB84 is a key-exchange protocol, not a message-encryption algorithm. Alice sends
qubits prepared in random bases. Bob measures in random bases. They publicly
compare bases, keep only matching positions, and use a small sample to detect
eavesdropping.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


Z_BASIS = "+"
X_BASIS = "x"


@dataclass
class BB84Result:
    alice_bits: list[int]
    alice_bases: list[str]
    bob_bases: list[str]
    bob_bits: list[int]
    sifted_alice_key: list[int]
    sifted_bob_key: list[int]
    quantum_bit_error_rate: float


def prepare_qubit(bit: int, basis: str) -> QuantumCircuit:
    """Prepare one BB84 signal qubit.

    In the Z basis, Alice sends |0> or |1>.
    In the X basis, Alice sends |+> or |->, created with a Hadamard gate.
    """
    circuit = QuantumCircuit(1)

    # A bit value of 1 starts from |0> and flips to |1>.
    if bit == 1:
        circuit.x(0)

    if basis == X_BASIS:     # The X basis is produced by rotating the computational basis with H.
        circuit.h(0)

    return circuit


def measure_qubit(circuit: QuantumCircuit, basis: str, rng: random.Random) -> int:
    """Measure one signal qubit in the requested basis.

    Statevector simulation gives the exact probabilities. One result is then
    sampled to mimic a physical photon measurement.
    """
    measurement_circuit = circuit.copy()

    # Measuring in the X basis is equivalent to applying H, then measuring Z.
    if basis == X_BASIS:
        measurement_circuit.h(0)

    state = Statevector.from_instruction(measurement_circuit)
    probabilities = state.probabilities_dict()

    # For one qubit, the possible outcomes are strings "0" and "1".
    probability_of_zero = probabilities.get("0", 0.0)
    return 0 if rng.random() < probability_of_zero else 1


def intercept_resend(circuit: QuantumCircuit, rng: random.Random) -> QuantumCircuit:
    """Model Eve with the basic intercept-resend attack.

    Eve chooses a random basis, measures the qubit, and sends Bob a new qubit
    matching her result. Wrong-basis measurements disturb the state, creating
    errors Alice and Bob can detect.
    """
    eve_basis = rng.choice([Z_BASIS, X_BASIS])
    eve_bit = measure_qubit(circuit, eve_basis, rng)
    return prepare_qubit(eve_bit, eve_basis)


def run_bb84(number_of_qubits: int = 64, eve_present: bool = True, seed: int = 11) -> BB84Result:
    """Run a complete BB84 simulation."""
    rng = random.Random(seed)

    alice_bits = [rng.randrange(2) for _ in range(number_of_qubits)]
    alice_bases = [rng.choice([Z_BASIS, X_BASIS]) for _ in range(number_of_qubits)]
    bob_bases = [rng.choice([Z_BASIS, X_BASIS]) for _ in range(number_of_qubits)]
    bob_bits: list[int] = []

    for bit, alice_basis, bob_basis in zip(alice_bits, alice_bases, bob_bases):
        signal = prepare_qubit(bit, alice_basis)

        # If Eve listens, the quantum state may be disturbed before Bob sees it.
        if eve_present:
            signal = intercept_resend(signal, rng)

        bob_bits.append(measure_qubit(signal, bob_basis, rng))

    matching_basis_positions = [
        index for index, (a_basis, b_basis) in enumerate(zip(alice_bases, bob_bases))
        if a_basis == b_basis
    ]

    sifted_alice_key = [alice_bits[index] for index in matching_basis_positions]
    sifted_bob_key = [bob_bits[index] for index in matching_basis_positions]

    errors = sum(a != b for a, b in zip(sifted_alice_key, sifted_bob_key))
    qber = errors / len(sifted_alice_key) if sifted_alice_key else 0.0

    return BB84Result(
        alice_bits=alice_bits,
        alice_bases=alice_bases,
        bob_bases=bob_bases,
        bob_bits=bob_bits,
        sifted_alice_key=sifted_alice_key,
        sifted_bob_key=sifted_bob_key,
        quantum_bit_error_rate=qber,
    )


def main() -> None:
    clean_run = run_bb84(eve_present=False)
    attacked_run = run_bb84(eve_present=True)

    print("BB84 without Eve")
    print(f"Sifted key length: {len(clean_run.sifted_alice_key)}")
    print(f"Quantum bit error rate: {clean_run.quantum_bit_error_rate:.2%}")
    print(f"First 24 key bits: {''.join(map(str, clean_run.sifted_alice_key[:24]))}")

    print("\nBB84 with intercept-resend Eve")
    print(f"Sifted key length: {len(attacked_run.sifted_alice_key)}")
    print(f"Quantum bit error rate: {attacked_run.quantum_bit_error_rate:.2%}")
    print(f"First 24 Alice key bits: {''.join(map(str, attacked_run.sifted_alice_key[:24]))}")
    print(f"First 24 Bob key bits:   {''.join(map(str, attacked_run.sifted_bob_key[:24]))}")


if __name__ == "__main__":
    main()
