# IBM QKD Notebook Breakdown

This document explains the attached IBM Quantum Learning notebook as a repository implementation. The notebook content is treated as reference material. The implemented files in this folder provide the same learning path in smaller runnable pieces.

Source notebook topic: quantum key distribution with Qiskit, focused on BB84, no-eavesdropper behavior, intercept-resend eavesdropping, and Qiskit pattern workflow.

## 1. Motivation: Encryption Needs Keys

The notebook begins with simple replacement ciphers and one-time pads.

Simple replacement ciphers replace one symbol with another. They are weak because repeated patterns leak information. A one-time pad avoids this by using a fresh random key for every message bit.

One-time pad requirements:

- the key is random
- the key is at least as long as the message
- the key is used once
- the key remains secret

The hard part is not the XOR encryption step. The hard part is safely sharing the key.

QKD addresses key distribution.

## 2. BB84 State Encoding

BB84 uses two bases:

```text
Z basis:
bit 0 -> |0>
bit 1 -> |1>

X basis:
bit 0 -> |+>
bit 1 -> |->
```

The implementation uses the same convention:

```python
Z_BASIS = 0
X_BASIS = 1
```

State preparation appears in `prepare_alice_states()`:

```text
bit 0, Z basis -> no gate
bit 1, Z basis -> X
bit 0, X basis -> H
bit 1, X basis -> X then H
```

The Hadamard gate moves between Z-basis and X-basis descriptions.

## 3. Bob's Measurement

Qiskit measures in the Z basis by default.

Bob's measurement rule:

```text
Bob basis Z -> measure directly
Bob basis X -> apply H, then measure
```

This is implemented in `add_measurements()`.

If Alice and Bob choose the same basis, Bob should recover Alice's bit in an ideal noiseless simulation.

If Alice and Bob choose different bases, Bob's result is random and that position is discarded.

## 4. Public Basis Discussion

Alice and Bob publicly compare only their bases.

They do not reveal the secret bit values for all kept positions.

The implementation keeps only positions where:

```text
alice_basis == bob_basis
```

This process is called key sifting.

Implemented in:

```text
sift_keys()
```

## 5. QBER

QBER means quantum bit error rate.

```text
QBER = mismatched sifted bits / total sifted bits
```

Low QBER means the key is probably usable.

High QBER means noise or eavesdropping is present.

The implementation uses a simple threshold:

```text
qber_threshold = 0.11
```

This is a demonstration threshold, not a full security proof.

## 6. Experiment 1: No Eavesdropper

Run:

```bash
python qkd_research/01_no_eavesdropper.py
```

Expected behavior:

```text
Alice and Bob randomly choose bases.
Matching bases produce identical sifted key bits.
QBER is 0% in the ideal simulator.
The key is accepted.
```

This corresponds to the notebook's first experiment.

## 7. Experiment 2: Intercept-Resend Eve

Run:

```bash
python qkd_research/02_with_eavesdropper.py
```

Attack flow:

```text
Eve intercepts Alice's qubits.
Eve chooses random bases.
Eve measures the qubits.
Eve prepares replacement states from her measurements.
Bob measures Eve's replacement states.
```

Eve does not know Alice's bases. Wrong-basis measurements disturb the states. This produces mismatches in Alice and Bob's sifted keys.

Expected behavior:

```text
QBER increases.
The key is rejected if QBER exceeds the threshold.
```

## 8. Secure Message Demo

Run:

```bash
python qkd_research/03_qkd_secure_message.py
```

This adds one practical layer after QKD:

```text
accepted QKD key bits + message bits -> XOR -> ciphertext
ciphertext + same key bits -> XOR -> original message
```

Clean channel:

```text
key accepted
message encrypted
message recovered
```

Eve channel:

```text
QBER too high
key rejected
message encryption blocked
```

## 9. What The Notebook Does With IBM Hardware

The IBM notebook also shows the Qiskit pattern workflow:

```text
1. Map the problem to quantum circuits.
2. Optimize/transpile for target hardware.
3. Execute with Sampler primitives.
4. Post-process the measured bitstrings.
```

The local implementation keeps the same protocol logic but uses `AerSimulator` by default. Hardware execution requires IBM Quantum credentials and a selected backend.

## 10. What Is Not Implemented Yet

The current folder demonstrates protocol mechanics. Full QKD systems also need:

- authenticated classical channel
- error correction
- privacy amplification
- finite-key security analysis
- noise modeling
- detector/source side-channel analysis
- key-management API
- integration with classical encryption protocols

