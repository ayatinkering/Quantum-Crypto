# QKD Research Implementation

This folder breaks down IBM's Qiskit classroom quantum key distribution notebook into runnable Python files.

## Core Idea

Quantum key distribution does not encrypt the message directly. It distributes shared secret key bits. Those bits can then be used with a one-time pad or transformed into symmetric keys for classical encryption.

BB84 uses two facts from quantum mechanics:

- Measuring in the correct basis gives the intended bit.
- Measuring in the wrong basis produces randomness and can disturb the state.

An intercept-resend attacker must guess the basis. Wrong guesses introduce errors. Alice and Bob detect this by estimating QBER.

```text
QBER = mismatched sifted bits / total sifted bits
```

## Files

- `bb84_protocol.py` contains reusable BB84 functions.
- `01_no_eavesdropper.py` reproduces the clean-channel notebook experiment.
- `02_with_eavesdropper.py` reproduces the intercept-resend experiment.
- `03_qkd_secure_message.py` uses accepted QKD key bits for one-time-pad encryption.

## Run

From the repository root:

```bash
source .venv/bin/activate
python qkd_research/01_no_eavesdropper.py
python qkd_research/02_with_eavesdropper.py
python qkd_research/03_qkd_secure_message.py
python qkd_research/04_visualize_qkd.py
```

## What The Experiments Show

Clean channel:

```text
Alice prepares BB84 states.
Bob measures in random bases.
Matching bases become sifted key bits.
QBER should be very low in an ideal simulator.
The key is accepted.
```

Intercept-resend channel:

```text
Eve measures Alice's states before Bob.
Eve does not know Alice's bases.
Wrong-basis measurements disturb the states.
Bob receives some incorrect bits.
QBER increases.
The key is rejected when QBER exceeds the threshold.
```

## Security Notes

The implementation demonstrates the protocol mechanics. Production QKD requires more layers:

- authenticated classical channel
- error correction
- privacy amplification
- finite-key analysis
- device side-channel protection
- photon loss handling
- real optical or satellite quantum channel

The simulator is therefore a research and education implementation, not a production QKD system.

## Visualizations

`04_visualize_qkd.py` saves Qiskit circuit diagrams and protocol charts to:

```text
qkd_research/visualizations/
```

Generated files:

- `clean_bb84_circuit.png`
- `eve_measurement_circuit.png`
- `eve_resend_to_bob_circuit.png`
- `basis_match_chart.png`
- `qber_comparison.png`
