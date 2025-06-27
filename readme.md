# 🔐 Verifiable Random Functions (VRFs) and Public Randomness

This document outlines how **Verifiable Random Functions (VRFs)** can be used to generate **deterministic, verifiable, and fair randomness**, especially in applications like leader election in distributed systems or blockchains.

VRF: used to sign random, and send to a PRF that is also signed - ensure no single person has control; ensure no single seed is excluded (e.g. using Shamir sharing threshold, etc). 

The ID can be proven by H(x, time_stamp_secure, h(key_private),  key_private).

---

## VRF Methodology for Verifiable Randomness and Leader Selection
This methodology outlines the generation and verification of deterministic, verifiable randomness using a cryptographic VRF construction, ensuring fairness, unpredictability, and resistance to manipulation in distributed systems (e.g., consensus, lottery, leader election).

1. Randomness Generation
2 main approaches for randomness generation:

A. Pseudorandom Number Generator (PRNG)

```
PRNG(seed || key) → number_random_00, proof
```
- Produces an initial random number with a verifiable output.
- proof can be a hash or deterministic transformation tied to the seed and key.

A PRNG alone doesn't provide verifiability. Only the VRF part is truly "verifiable randomness".

B. VRF-Based Randomness
```
VRF(seed || key, key_secret) → value_random_01, proof
```
- A secret key is used to generate a unique, verifiable random value and proof.
- Ensures that randomness is unique and tamper-evident.

2. Signature-Based Randomness
To ensure uniqueness and reduce collision risk:

```
sign(seed, key_secret) → signature
hash(signature) → number_random
verify(signature, key_public, seed) → True/False
```

- BLS Signatures are preferred for uniqueness guarantees.
- Signature verification ensures the integrity of the source randomness.

BLS signatures are a good choice because they are:
- Unique (reducing collision risk)
- Aggregateable (useful in distributed protocols)


3. Verifiability
To verify the random output:

```
verify_VRF(value_random, key_public, proof, seed) → True/False
```
or

```
verify(signature, key_public, seed) → True/False
```

Ensures that outputs were indeed derived from the claimed seed/key pair.

4. Application: Leader Selection via Bernoulli Sampling

```
VRF(seed || round || steps, key_secret) → value_random_output_VRF, proof
```
Output is bounded:

```
value_random_output_VRF < x
```

Apply a hash to this VRF output for deterministic bucketing:

```
hash(value_random_output_VRF) → bucket_index ∈ [0, w)
```

Binomial trial model:
- B(k,w,p) with:
	- w: number of trials (tickets)
	- p: probability of winning
	- k: winning tickets
	- j: selected winners based on bucket index

Bernoulli trial: 1 trial per participant, you are sampling B(1, p).

✅ VRFs use a secret key to produce a random output and proof, which can be verified using the public key.

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



