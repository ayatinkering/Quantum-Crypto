"""Reusable BB84 quantum key distribution helpers.

This module breaks the IBM Qiskit classroom notebook into small functions.
The implementation keeps the classroom structure:

1. Alice creates random bits and random bases.
2. Alice prepares BB84 quantum states.
3. Bob chooses random bases and measures the states.
4. Alice and Bob publicly compare bases.
5. Matching-basis positions become the sifted key.
6. A sample of the sifted key is used to estimate QBER.

Basis convention:
- 0 means Z basis.
- 1 means X basis.

Bit/state convention:
- Z basis, bit 0: |0>
- Z basis, bit 1: |1>
- X basis, bit 0: |+>
- X basis, bit 1: |->
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit_aer import AerSimulator


Z_BASIS = 0
X_BASIS = 1


@dataclass(frozen=True)
class QKDRun:
    """Complete output from one BB84 simulation run."""

    alice_bits: list[int]
    alice_bases: list[int]
    bob_bases: list[int]
    bob_bits: list[int]
    kept_positions: list[int]
    alice_sifted_key: list[int]
    bob_sifted_key: list[int]
    qber: float
    accepted: bool


@dataclass(frozen=True)
class EavesdropperRun:
    """Complete output from an intercept-resend simulation."""

    alice_bits: list[int]
    alice_bases: list[int]
    eve_bases: list[int]
    eve_bits: list[int]
    bob_bases: list[int]
    bob_bits: list[int]
    kept_positions: list[int]
    alice_sifted_key: list[int]
    bob_sifted_key: list[int]
    qber: float
    accepted: bool


def random_bits_and_bases(bit_count: int, rng: np.random.Generator) -> tuple[list[int], list[int]]:
    """Generate random BB84 bits and bases."""
    bits = rng.integers(0, 2, size=bit_count).astype(int).tolist()
    bases = rng.integers(0, 2, size=bit_count).astype(int).tolist()
    return bits, bases


def prepare_alice_states(bits: list[int], bases: list[int]) -> QuantumCircuit:
    """Create a circuit that prepares Alice's BB84 states.

    Qiskit starts every qubit in |0>. The gates below transform |0> into the
    state required by the selected bit and basis.
    """
    bit_count = len(bits)
    quantum = QuantumRegister(bit_count, "q")
    classical = ClassicalRegister(bit_count, "c")
    circuit = QuantumCircuit(quantum, classical)

    for index, (bit, basis) in enumerate(zip(bits, bases)):
        if bit == 1:
            # X changes |0> into |1>. In the X basis, X followed by H creates |->.
            circuit.x(index)

        if basis == X_BASIS:
            # H changes Z-basis states into X-basis states.
            circuit.h(index)

    circuit.barrier()
    return circuit


def add_measurements(circuit: QuantumCircuit, bases: list[int]) -> QuantumCircuit:
    """Measure each qubit in the selected basis."""
    measured = circuit.copy()

    for index, basis in enumerate(bases):
        if basis == X_BASIS:
            # IBM/Qiskit measurement is naturally Z-basis measurement. Applying H
            # before measurement converts X-basis measurement into Z measurement.
            measured.h(index)
        measured.measure(index, index)

    return measured


def run_one_shot(circuit: QuantumCircuit, seed: int) -> list[int]:
    """Run one shot on a local simulator and return measured bits in qubit order."""
    simulator = AerSimulator(seed_simulator=seed)
    counts = simulator.run(circuit, shots=1).result().get_counts()
    bitstring = next(iter(counts.keys()))

    # Qiskit prints classical bits in little-endian order, so reverse the string
    # to align result[index] with qubit[index].
    return [int(bit) for bit in bitstring[::-1]]


def sift_keys(
    alice_bits: list[int],
    alice_bases: list[int],
    bob_bits: list[int],
    bob_bases: list[int],
) -> tuple[list[int], list[int], list[int]]:
    """Keep positions where Alice and Bob used the same basis."""
    kept_positions: list[int] = []
    alice_sifted_key: list[int] = []
    bob_sifted_key: list[int] = []

    for index, (alice_basis, bob_basis) in enumerate(zip(alice_bases, bob_bases)):
        if alice_basis == bob_basis:
            kept_positions.append(index)
            alice_sifted_key.append(alice_bits[index])
            bob_sifted_key.append(bob_bits[index])

    return kept_positions, alice_sifted_key, bob_sifted_key


def calculate_qber(alice_key: list[int], bob_key: list[int]) -> float:
    """Calculate quantum bit error rate for sifted keys."""
    if not alice_key:
        return 1.0

    errors = sum(alice_bit != bob_bit for alice_bit, bob_bit in zip(alice_key, bob_key))
    return errors / len(alice_key)


def run_bb84_no_eve(bit_count: int = 64, seed: int = 1234, qber_threshold: float = 0.11) -> QKDRun:
    """Run BB84 without an eavesdropper."""
    rng = np.random.default_rng(seed)
    alice_bits, alice_bases = random_bits_and_bases(bit_count, rng)
    _, bob_bases = random_bits_and_bases(bit_count, rng)

    alice_circuit = prepare_alice_states(alice_bits, alice_bases)
    bob_circuit = add_measurements(alice_circuit, bob_bases)
    bob_bits = run_one_shot(bob_circuit, seed=seed + 1)

    kept_positions, alice_sifted_key, bob_sifted_key = sift_keys(
        alice_bits, alice_bases, bob_bits, bob_bases
    )
    qber = calculate_qber(alice_sifted_key, bob_sifted_key)

    return QKDRun(
        alice_bits=alice_bits,
        alice_bases=alice_bases,
        bob_bases=bob_bases,
        bob_bits=bob_bits,
        kept_positions=kept_positions,
        alice_sifted_key=alice_sifted_key,
        bob_sifted_key=bob_sifted_key,
        qber=qber,
        accepted=qber <= qber_threshold,
    )


def run_bb84_with_intercept_resend(
    bit_count: int = 64,
    seed: int = 1234,
    qber_threshold: float = 0.11,
) -> EavesdropperRun:
    """Run BB84 with Eve using an intercept-resend attack.

    Eve measures Alice's states in random bases. Eve then prepares new BB84
    states from her measurement results and sends those replacement states to
    Bob. Wrong-basis measurements disturb the key and raise QBER.
    """
    rng = np.random.default_rng(seed)
    alice_bits, alice_bases = random_bits_and_bases(bit_count, rng)
    _, eve_bases = random_bits_and_bases(bit_count, rng)
    _, bob_bases = random_bits_and_bases(bit_count, rng)

    alice_circuit = prepare_alice_states(alice_bits, alice_bases)
    eve_measurement_circuit = add_measurements(alice_circuit, eve_bases)
    eve_bits = run_one_shot(eve_measurement_circuit, seed=seed + 1)

    eve_resend_circuit = prepare_alice_states(eve_bits, eve_bases)
    bob_circuit = add_measurements(eve_resend_circuit, bob_bases)
    bob_bits = run_one_shot(bob_circuit, seed=seed + 2)

    kept_positions, alice_sifted_key, bob_sifted_key = sift_keys(
        alice_bits, alice_bases, bob_bits, bob_bases
    )
    qber = calculate_qber(alice_sifted_key, bob_sifted_key)

    return EavesdropperRun(
        alice_bits=alice_bits,
        alice_bases=alice_bases,
        eve_bases=eve_bases,
        eve_bits=eve_bits,
        bob_bases=bob_bases,
        bob_bits=bob_bits,
        kept_positions=kept_positions,
        alice_sifted_key=alice_sifted_key,
        bob_sifted_key=bob_sifted_key,
        qber=qber,
        accepted=qber <= qber_threshold,
    )


def bits_to_text(bits: list[int]) -> str:
    """Render a bit list as compact text."""
    return "".join(str(bit) for bit in bits)
