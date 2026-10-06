"""Educational Shor-style factorization demo for N = 15.

Real Shor's algorithm uses quantum phase estimation to find the period r of
f(x) = a^x mod N. Once r is known, classical arithmetic often gives factors:
gcd(a^(r/2) - 1, N) and gcd(a^(r/2) + 1, N).

This file keeps the number small, N = 15, so the circuit can run on a laptop.
It is not a scalable RSA-breaking implementation.
"""

from __future__ import annotations

from fractions import Fraction
from math import gcd, pi

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.circuit.library import QFTGate
from qiskit.circuit.library.generalized_gates import UnitaryGate
from qiskit_aer import AerSimulator


N = 15
A = 2
COUNTING_QUBITS = 4
WORK_QUBITS = 4


def modular_multiplication_gate(a: int, power: int, modulus: int) -> UnitaryGate:
    """Build a unitary gate for |y> -> |a**power * y mod modulus>.

    For y >= modulus, the gate leaves the state unchanged. This keeps the
    operation reversible on all 2**WORK_QUBITS computational states.
    """
    dimension = 2**WORK_QUBITS
    matrix = np.zeros((dimension, dimension), dtype=complex)
    multiplier = pow(a, power, modulus)

    for y in range(dimension):
        if y < modulus:
            target = (multiplier * y) % modulus
        else:
            target = y

        # Qiskit uses column vectors, so matrix[target, y] maps |y> to |target>.
        matrix[target, y] = 1

    return UnitaryGate(matrix, label=f"{a}^{power} mod {modulus}")


def continued_fraction_period(measured_value: int, counting_qubits: int) -> int | None:
    """Estimate the period r from a measured phase value."""
    phase = measured_value / (2**counting_qubits)

    # Shor's post-processing approximates the phase by s / r.
    fraction = Fraction(phase).limit_denominator(N)
    candidate_period = fraction.denominator

    if candidate_period > 0 and pow(A, candidate_period, N) == 1:
        return candidate_period
    return None


def factors_from_period(period: int) -> tuple[int, int] | None:
    """Convert a valid even period into non-trivial factors of N."""
    if period % 2 != 0:
        return None

    half_power = pow(A, period // 2, N)
    if half_power in (1, N - 1):
        return None

    factor_1 = gcd(half_power - 1, N)
    factor_2 = gcd(half_power + 1, N)

    if factor_1 * factor_2 == N:
        return factor_1, factor_2
    return None


def build_order_finding_circuit() -> QuantumCircuit:
    """Build the quantum phase estimation part of Shor's algorithm."""
    counting = QuantumRegister(COUNTING_QUBITS, "count")
    work = QuantumRegister(WORK_QUBITS, "work")
    classical = ClassicalRegister(COUNTING_QUBITS, "c")
    circuit = QuantumCircuit(counting, work, classical)

    # Put counting qubits into a uniform superposition over possible exponents.
    circuit.h(counting)

    # Initialize the work register to |1>, the standard input for order finding.
    circuit.x(work[0])

    # Apply controlled modular multiplication gates for a^(2^j) mod N.
    for j in range(COUNTING_QUBITS):
        gate = modular_multiplication_gate(A, 2**j, N).control(1)
        circuit.append(gate, [counting[j], *work])

    # Inverse QFT turns phase information into measurable computational states.
    inverse_qft = QFTGate(COUNTING_QUBITS).inverse()
    circuit.append(inverse_qft, counting)

    # Measure only the counting register; the work register is no longer needed.
    circuit.measure(counting, classical)
    return circuit


def main() -> None:
    circuit = build_order_finding_circuit()
    simulator = AerSimulator(seed_simulator=19)

    # Transpilation rewrites the circuit into operations supported by the backend.
    compiled_circuit = transpile(circuit, simulator)
    result = simulator.run(compiled_circuit, shots=2048).result()
    counts = result.get_counts()

    print("Most common measured phases:")
    for bitstring, shots in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:8]:
        measured_value = int(bitstring, 2)
        phase_angle = 2 * pi * measured_value / (2**COUNTING_QUBITS)
        period = continued_fraction_period(measured_value, COUNTING_QUBITS)
        factors = factors_from_period(period) if period else None

        print(
            f"{bitstring} -> value={measured_value:2d}, "
            f"phase angle={phase_angle:.3f}, period={period}, factors={factors}, shots={shots}"
        )


if __name__ == "__main__":
    main()

