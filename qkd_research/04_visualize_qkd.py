"""Generate Qiskit visualizations for the BB84 QKD experiments.

The generated images are saved in `qkd_research/visualizations/`.
Small circuits are used for readability; larger protocol runs are still used
for the QBER comparison chart.
"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt
import numpy as np

from bb84_protocol import (
    add_measurements,
    prepare_alice_states,
    random_bits_and_bases,
    run_bb84_no_eve,
    run_bb84_with_intercept_resend,
)


OUTPUT_DIR = Path(__file__).resolve().parent / "visualizations"


def save_circuit_diagram(circuit, filename: str, title: str) -> Path:
    """Save a Qiskit circuit diagram as a PNG file."""
    figure = circuit.draw(output="mpl", fold=-1, scale=0.75)
    figure.suptitle(title, fontsize=14)
    path = OUTPUT_DIR / filename
    figure.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(figure)
    return path


def save_basis_match_chart(alice_bases: list[int], bob_bases: list[int]) -> Path:
    """Save a chart showing where Alice and Bob used matching bases."""
    kept = [int(a == b) for a, b in zip(alice_bases, bob_bases)]
    data = np.array([alice_bases, bob_bases, kept])

    figure, axis = plt.subplots(figsize=(10, 2.6))
    axis.imshow(data, aspect="auto", cmap="viridis", vmin=0, vmax=1)
    axis.set_title("BB84 basis comparison")
    axis.set_xlabel("Qubit index")
    axis.set_yticks([0, 1, 2])
    axis.set_yticklabels(["Alice basis", "Bob basis", "Kept"])
    axis.set_xticks(range(len(alice_bases)))

    for row in range(data.shape[0]):
        for col in range(data.shape[1]):
            label = "X" if data[row, col] == 1 and row < 2 else "Z" if row < 2 else str(data[row, col])
            axis.text(col, row, label, ha="center", va="center", color="white", fontsize=8)

    path = OUTPUT_DIR / "basis_match_chart.png"
    figure.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(figure)
    return path


def save_qber_chart() -> Path:
    """Save a QBER comparison chart for clean and attacked channels."""
    clean_run = run_bb84_no_eve(bit_count=128, seed=2026)
    eve_run = run_bb84_with_intercept_resend(bit_count=128, seed=2026)

    labels = ["Clean channel", "Intercept-resend Eve"]
    values = [clean_run.qber * 100, eve_run.qber * 100]
    colors = ["#26734d", "#b33430"]

    figure, axis = plt.subplots(figsize=(7, 4))
    bars = axis.bar(labels, values, color=colors)
    axis.axhline(11, color="#555555", linestyle="--", linewidth=1.2, label="Example threshold: 11%")
    axis.set_title("QBER comparison")
    axis.set_ylabel("QBER (%)")
    axis.set_ylim(0, max(values + [11]) + 8)
    axis.legend()

    for bar, value in zip(bars, values):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.6,
            f"{value:.2f}%",
            ha="center",
            va="bottom",
        )

    path = OUTPUT_DIR / "qber_comparison.png"
    figure.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(figure)
    return path


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(2026)
    bit_count = 8
    alice_bits, alice_bases = random_bits_and_bases(bit_count, rng)
    _, bob_bases = random_bits_and_bases(bit_count, rng)
    _, eve_bases = random_bits_and_bases(bit_count, rng)

    alice_circuit = prepare_alice_states(alice_bits, alice_bases)
    clean_bob_circuit = add_measurements(alice_circuit, bob_bases)
    eve_measurement_circuit = add_measurements(alice_circuit, eve_bases)

    # Fixed example Eve bits make the resend circuit deterministic and readable.
    eve_example_bits = [1, 0, 1, 1, 0, 0, 1, 0]
    eve_resend_circuit = prepare_alice_states(eve_example_bits, eve_bases)
    eve_to_bob_circuit = add_measurements(eve_resend_circuit, bob_bases)

    saved_paths = [
        save_circuit_diagram(
            clean_bob_circuit,
            "clean_bb84_circuit.png",
            "Clean BB84: Alice prepares states, Bob measures",
        ),
        save_circuit_diagram(
            eve_measurement_circuit,
            "eve_measurement_circuit.png",
            "Eve intercepts: Alice prepares states, Eve measures",
        ),
        save_circuit_diagram(
            eve_to_bob_circuit,
            "eve_resend_to_bob_circuit.png",
            "Eve resends replacement states, Bob measures",
        ),
        save_basis_match_chart(alice_bases, bob_bases),
        save_qber_chart(),
    ]

    print("QKD visualizations generated")
    for path in saved_paths:
        print(path)


if __name__ == "__main__":
    main()
