"""Estimate physical qubits versus logical qubits.

Logical qubits are error-corrected qubits. Physical qubits are the noisy device
qubits used to encode them. The ratio is not fixed: it depends on hardware error
rates, code family, decoder, target circuit length, and acceptable failure rate.

This file uses a deliberately simple surface-code-style toy model:
physical_qubits ~= logical_qubits * 2 * distance**2

That model is useful for intuition, not for hardware planning.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Estimate:
    logical_qubits: int
    code_distance: int
    physical_qubits_per_logical: int
    total_physical_qubits: int


def estimate_physical_qubits(logical_qubits: int, code_distance: int) -> Estimate:
    """Estimate physical qubit overhead for a simple 2D error-correcting code."""
    physical_per_logical = 2 * code_distance**2
    total_physical = logical_qubits * physical_per_logical

    return Estimate(
        logical_qubits=logical_qubits,
        code_distance=code_distance,
        physical_qubits_per_logical=physical_per_logical,
        total_physical_qubits=total_physical,
    )


def print_estimate_table() -> None:
    """Print a small table showing how overhead grows with code distance."""
    logical_targets = [1, 10, 100, 200, 1000]
    code_distances = [7, 11, 15, 21, 31]

    print("Toy physical/logical qubit estimates")
    print("logical_qubits, code_distance, physical_per_logical, total_physical")

    for logical_qubits in logical_targets:
        for distance in code_distances:
            estimate = estimate_physical_qubits(logical_qubits, distance)
            print(
                f"{estimate.logical_qubits:>4}, "
                f"{estimate.code_distance:>2}, "
                f"{estimate.physical_qubits_per_logical:>5}, "
                f"{estimate.total_physical_qubits:>9}"
            )
        print()


def main() -> None:
    print_estimate_table()

    print(
        "Result: logical-qubit count is only one part of the scaling challenge. "
        "Long cryptographic circuits also require enough error correction to survive "
        "many gates, so physical-qubit requirements can grow very quickly."
    )


if __name__ == "__main__":
    main()
