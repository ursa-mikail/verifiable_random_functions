# 🔐 Verifiable Random Functions (VRFs) and Public Randomness

This document outlines how **Verifiable Random Functions (VRFs)** can be used to generate **deterministic, verifiable, and fair randomness**, especially in applications like leader election in distributed systems or blockchains.

---

## 🔄 Overview

We explore the construction and verification of public randomness using either:

- **Pseudorandom Number Generators (PRNG)**
- **Verifiable Random Functions (VRFs)**
- **Digital Signatures (e.g., BLS)**

Each mechanism ensures that:
- Random outputs can be **deterministically reproduced**
- Anyone can **verify correctness**
- Bias or manipulation is **cryptographically infeasible**

---

## 🧠 Randomness Generation


Used when determinism and reproducibility are needed, but **no secret key** is involved.

---

### 📍 Using a VRF for Leadership selection

Leadership selection is modeled as dropping into a bucket (e.g., index 0 out of W buckets), using a probability function.

Bernoulli chain selection to:
1. Generate N random 16-byte hex values.
2. Hash each (SHA-256) → gives you hashed_inputs.
3. Begin a deterministic chaining process:
	1. Generate an initial random seed (internally).
	2. From those, pick w inputs (e.g. the first w).	# alternatively include all N
	3. Use SHA-256(seed) to pick one from the list of w.
	4. Use the selected hash as the next seed.
	5. Remove selected from the candidate pool.
	6. Continue until all w are consumed → build a selection trail.
4. At the end, select k of w winners based on the first k items in the selection trail.
5. Return:
- The ordered k selected winners,
- And the final SHA-256 seed (used to "burn out" the entropy).

---

## 📊 Bernoulli Process for Election

Given:
- \( w \): total number of tickets
- \( k \): winning tickets
- \( p \): probability of winning
- \( j \): number of actual wins

Probability distribution:

$$
B(k; w, p) = \binom{w}{k} \cdot p^k \cdot (1 - p)^{w - k}
$$

Example:  
If 2 winning tickets out of 4 are selected, and \( p = 0.5 \):

$$
B(2; 4, 0.5) = \binom{4}{2} \cdot 0.5^2 \cdot 0.5^2 = 6 \cdot 0.25 \cdot 0.25 = 0.375
$$

---

## ✅ Summary of Steps

1. **Generate randomness** using PRNG, VRF, or BLS signature:
   - All yield a verifiable and deterministic value.
2. **Hash the output** into a uniformly distributed integer.
3. **Use a probabilistic filter** (e.g., modulo or threshold):
   - e.g., `value_random_output_VRF < x`
4. **Drop into leadership bucket** using:
   - Bernoulli selection
   - Leader = index 0
5. **Verify publicly**:
   - Anyone with public key and seed can confirm randomness and fairness.

---

## 🔒 Security Guarantees

| Property               | PRNG    | VRF     | BLS Signature |
|------------------------|---------|---------|----------------|
| Deterministic          | ✅      | ✅      | ✅              |
| Secret-dependent       | ❌      | ✅      | ✅              |
| Public Verifiability   | ❌      | ✅      | ✅              |
| Bias Resistance        | ❌      | ✅      | ✅              |
| Unique Output          | ❌      | ✅      | ✅ (BLS avoids collisions) |

---

## 🔗 Applications

- Blockchain leader election (e.g., Ethereum, Algorand)
- Lottery systems and fair draws
- Privacy-preserving credentials
- Secure multi-party coordination

---

> ⚠️ This document describes **conceptual models**. For real-world use, cryptographic operations must be implemented using secure, audited libraries and proven protocols (e.g., EC-VRF, BLS12-381).



