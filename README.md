# Quantum-Crypto Qiskit Workspace

This repository contains a starter workspace for researching quantum security and cryptography with IBM Qiskit.

The examples follow the current IBM Quantum documentation style:

- Qiskit SDK supports local circuit construction and simulation.
- `qiskit-aer` provides local shot-based simulation.
- `qiskit-ibm-runtime` supports later execution on IBM Quantum hardware.
- Cryptography demos remain small and educational. The examples explain algorithm behavior; they do not break real RSA or ECC.

## Setup

Virtual environment creation:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Dependency installation:

```bash
pip install -r requirements.txt
```

Qiskit import and simulation check:

```bash
python qiskit_examples/00_getting_started.py
```

Optional IBM Quantum hardware access requires an IBM Quantum account and an API token saved through `qiskit-ibm-runtime`. The examples in this repository run locally by default.

## Files

- `qiskit_examples/00_getting_started.py` - constructs and simulates a Bell-state circuit.
- `qiskit_examples/01_bb84_qkd.py` - simulates BB84 quantum key distribution.
- `qiskit_examples/02_shor_factor_15.py` - demonstrates Shor-style order finding for factoring 15.
- `qiskit_examples/03_grover_vs_bruteforce.py` - compares Grover search with classical brute force.
- `qiskit_examples/04_logical_vs_physical_qubits.py` - estimates physical-qubit overhead for logical qubits.
- `notebooks/why_toy_demos_do_not_scale_to_rsa2048.ipynb` - explains why small factoring demos do not scale to RSA-2048 today.

## Main References

- IBM Quantum install guide: https://quantum.cloud.ibm.com/docs/en/guides/install-qiskit-runtime
- IBM Quantum exact simulation guide: https://quantum.cloud.ibm.com/docs/en/guides/simulate-with-qiskit-sdk-primitives
- IBM Quantum Shor tutorial: https://quantum.cloud.ibm.com/docs/en/tutorials/shors-algorithm
- IBM Quantum Grover tutorial: https://quantum.cloud.ibm.com/docs/en/tutorials/grovers-algorithm
- IBM Quantum Safe Cryptography course: https://learning.quantum.ibm.com/course/practical-introduction-to-quantum-safe-cryptography
