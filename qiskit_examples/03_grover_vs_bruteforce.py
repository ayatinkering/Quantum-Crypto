"""Compare Grover search with classical brute force on a tiny search problem.

Grover's algorithm gives a quadratic speedup for unstructured search. A
classical brute-force search needs O(N) oracle checks in the worst case, while
Grover needs about O(sqrt(N)) oracle applications. This file demonstrates the
idea on 3 qubits, where N = 8.
"""

from __future__ import annotations

from math import floor, pi, sqrt

from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import grover_operator
from qiskit_aer import AerSimulator


TARGET = "101"
NUMBER_OF_QUBITS = len(TARGET)


def classical_bruteforce(target: str) -> tuple[str, int]:
    """Search every bitstring in order until the target is found."""
    checks = 0

    for value in range(2 ** len(target)):
        candidate = format(value, f"0{len(target)}b")
        checks += 1

        # This equality check is the classical version of the oracle question.
        if candidate == target:
            return candidate, checks

    raise RuntimeError("Target not found")


def build_phase_oracle(target: str) -> QuantumCircuit:
    """Build an oracle that marks the target state with a phase flip."""
    oracle = QuantumCircuit(len(target), name=f"oracle_{target}")

    # Qiskit qubit order is little-endian, so reverse the display string.
    for qubit, bit in enumerate(reversed(target)):
        if bit == "0":
            oracle.x(qubit)

    # Multi-controlled Z: convert the last qubit to X basis, apply MCX, restore.
    oracle.h(len(target) - 1)
    oracle.mcx(list(range(len(target) - 1)), len(target) - 1)
    oracle.h(len(target) - 1)

    for qubit, bit in enumerate(reversed(target)):
        if bit == "0":
            oracle.x(qubit)

    return oracle


def build_grover_circuit(target: str) -> QuantumCircuit:
    """Build a complete Grover circuit for one marked state."""
    number_of_qubits = len(target)
    oracle = build_phase_oracle(target)
    grover_iteration = grover_operator(oracle)

    circuit = QuantumCircuit(number_of_qubits, number_of_qubits)

    # The initial Hadamard layer creates a uniform superposition over all bitstrings.
    circuit.h(range(number_of_qubits))

    # For one target, the near-optimal iteration count is about pi/4 * sqrt(N).
    iterations = max(1, floor((pi / 4) * sqrt(2**number_of_qubits)))
    for _ in range(iterations):
        circuit.compose(grover_iteration, inplace=True)

    circuit.measure(range(number_of_qubits), range(number_of_qubits))
    return circuit


def main() -> None:
    classical_answer, classical_checks = classical_bruteforce(TARGET)

    circuit = build_grover_circuit(TARGET)
    simulator = AerSimulator(seed_simulator=23)
    compiled_circuit = transpile(circuit, simulator)
    result = simulator.run(compiled_circuit, shots=1000).result()
    counts = result.get_counts()

    quantum_answer = max(counts, key=counts.get)
    oracle_calls = max(1, floor((pi / 4) * sqrt(2**NUMBER_OF_QUBITS)))

    print(f"Classical brute force found {classical_answer} after {classical_checks} checks.")
    print(f"Grover's algorithm used {oracle_calls} oracle iteration(s).")
    print(f"Most frequent quantum measurement: {quantum_answer}")
    print("Measurement counts:")
    print(counts)


if __name__ == "__main__":
    main()
