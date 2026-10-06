"""Getting started with Qiskit.

This file mirrors the first steps from IBM Quantum documentation:
build a circuit, simulate it locally, and inspect the measured bitstrings.
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


def build_bell_circuit() -> QuantumCircuit:
    """Construct a two-qubit Bell state circuit.

    A Bell state is a simple entangled state. After measurement, the two
    classical bits should usually match: either 00 or 11.
    """
    circuit = QuantumCircuit(2, 2)

    # Put qubit 0 into superposition: it is now balanced between |0> and |1>.
    circuit.h(0)

    # Entangle qubit 1 with qubit 0. If qubit 0 is measured as 1, qubit 1 flips.
    circuit.cx(0, 1)

    # Measure both qubits into classical bits so the simulator returns counts.
    circuit.measure([0, 1], [0, 1])
    return circuit


def main() -> None:
    circuit = build_bell_circuit()

    # AerSimulator is a local simulator, so this does not use IBM cloud time.
    simulator = AerSimulator(seed_simulator=7)

    # Run 1,000 shots. A shot is one repeated execution of the quantum circuit.
    result = simulator.run(circuit, shots=1000).result()

    # Counts are the observed classical bitstrings and how often each appeared.
    counts = result.get_counts(circuit)

    print(circuit.draw(output="text"))
    print("\nBell-state measurement counts:")
    print(counts)


if __name__ == "__main__":
    main()
