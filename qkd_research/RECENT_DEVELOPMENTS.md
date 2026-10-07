# Recent QKD Developments And Extension Ideas

This note summarizes current directions that can extend the BB84 implementation in this repository.

## IBM/Qiskit Context

IBM's current classroom QKD module presents BB84 as a Qiskit learning module and uses the Qiskit pattern workflow: map to circuit, optimize for hardware, execute with primitives, and post-process results. The module lists `qiskit>=2.1.0`, `qiskit-ibm-runtime>=0.40.1`, and `qiskit-aer>=0.17.0` as its working environment. Source: IBM Quantum Learning, "Quantum key distribution" (https://quantum.cloud.ibm.com/learning/en/modules/computer-science/quantum-key-distribution).

IBM's current Qiskit documentation emphasizes primitives such as Sampler and Estimator as higher-level interfaces for quantum execution. QKD classroom experiments are naturally sampling-oriented because the protocol depends on measured bitstrings. Source: IBM Quantum Documentation, "Introduction to primitives" (https://quantum.cloud.ibm.com/docs/en/guides/primitives).

## 1. Device-Independent QKD

Device-independent QKD reduces trust in the internal behavior of quantum devices. Instead of assuming the devices implement the intended measurements perfectly, security is tied to observed nonlocal correlations such as Bell inequality violations.

Research direction:

```text
Add an Ekert/E91-style demo:
entangled pairs -> random measurement settings -> Bell test -> key extraction
```

Implementation idea:

- create entangled Bell pairs in Qiskit
- simulate Alice and Bob measurement settings
- compute correlation values
- estimate whether the channel could support device-independent-style security

Recent source: "Device-Independent Quantum Key Distribution: Protocols, Quantum Games and Security", IET Quantum Communication, 2026 (https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/qtc2.70030).

## 2. Twin-Field QKD

Twin-field QKD is designed to improve long-distance QKD performance. It can beat the usual repeaterless scaling behavior by using interference at a middle station and has measurement-device-independent security properties.

Research direction:

```text
Add a channel-loss model comparing:
BB84 key rate decay
twin-field-style square-root loss scaling
```

Implementation idea:

- model fiber loss in dB/km
- plot estimated key-rate scaling over distance
- compare BB84-like direct transmission with twin-field-inspired scaling

Recent sources:

- "Free-Space Twin-Field Quantum Key Distribution", arXiv, 2025 (https://arxiv.org/abs/2503.17744)
- "Fully connected twin-field quantum key distribution network", arXiv, 2025 (https://arxiv.org/abs/2504.15137)

## 3. QKD Key Management APIs

Real QKD systems need a way to deliver generated keys to applications. ETSI has QKD standards for application interfaces and REST-based key delivery.

Research direction:

```text
Build a mock QKD key server:
GET /key/{key_id}
POST /encrypt
POST /decrypt
```

Implementation idea:

- QKD simulation fills a local key pool
- REST API serves key blocks with key IDs
- secure-message demo consumes keys from that pool

Recent standards context:

- ETSI QKD technical group page lists active QKD specifications, including 2026 work on REST-based interoperable key-management APIs (https://www.etsi.org/technical-groups/qkd/)
- ETSI GS QKD 014 defines a REST-based key delivery API over HTTPS and JSON (https://www.etsi.org/deliver/etsi_gs/QKD/001_099/014/01.01.01_60/gs_qkd014v010101p.pdf)

## 4. Hybrid PQC + QKD Security

Current quantum-safe network research often combines:

```text
classical cryptography
post-quantum cryptography
QKD-generated keys
```

This avoids treating QKD and PQC as competitors. PQC is practical for broad deployment; QKD can protect specialized high-security links.

Research direction:

```text
Combine ML-KEM and QKD-derived key bits into one session key.
```

Implementation idea:

- run `pqc_examples/01_ml_kem_key_exchange.py`
- run BB84 to get QKD key bits
- combine both secrets with HKDF
- use AES-GCM with the derived hybrid key

Recent sources:

- "Benchmarking hybrid quantum-safe cryptography over real-world infrastructures", EPJ Quantum Technology, 2026 (https://doi.org/10.1140/epjqt/s40507-026-00521-y)
- "A Hybrid Encryption Framework Combining Classical, Post-Quantum, and QKD Methods", arXiv, 2025 (https://arxiv.org/abs/2509.10551)
- "Hybrid Schemes of NIST Post-Quantum Cryptography Standard Algorithms and Quantum Key Distribution for Key Exchange and Digital Signature", arXiv, 2025 (https://arxiv.org/abs/2510.02379)

## 5. Satellite And Free-Space QKD

Fiber QKD is distance-limited by optical loss. Satellite/free-space QKD is studied for long-range and global-scale quantum-secure links.

Research direction:

```text
Add atmospheric/fiber loss simulation:
distance
loss
detector efficiency
background noise
estimated sifted key rate
```

Implementation idea:

- model free-space attenuation
- compare day/night background noise assumptions
- estimate how many raw qubits are needed for a target key size

Recent sources:

- "Exploring Satellite Quantum Key Distribution under Atmospheric Constraints", arXiv, 2025 (https://arxiv.org/abs/2508.05235)
- "All-day free-space quantum key distribution with thermal source towards quantum secure communications for unmanned vehicles", npj Quantum Information, 2025 (https://www.nature.com/articles/s41534-025-01085-y)

## 6. Reference-Frame-Independent And Access-Network QKD

Practical networks can have alignment and synchronization problems. Reference-frame-independent QKD and quantum access-network architectures reduce operational complexity.

Research direction:

```text
Extend BB84 with a simulated basis-misalignment/noise parameter.
```

Implementation idea:

- add a rotation/noise probability before Bob measures
- track how QBER changes
- add automatic reject/accept decisions at different noise levels

Recent source: "Fully passive received quantum access network based on reference-frame-independent quantum key distribution", npj Quantum Information, 2026 (https://doi.org/10.1038/s41534-026-01289-w).

## Most Practical Next Implementations

Best next files for this repository:

```text
qkd_research/04_noise_model_qber_sweep.py
qkd_research/05_privacy_amplification.py
qkd_research/06_qkd_key_pool_api.py
qkd_research/07_hybrid_qkd_mlkem_session_key.py
qkd_research/08_ekert_e91_bell_qkd.py
```

Priority order:

```text
1. Noise model and QBER sweep
2. Privacy amplification
3. Hybrid QKD + ML-KEM session key
4. Mock ETSI-style key delivery API
5. E91/device-independent research demo
```
