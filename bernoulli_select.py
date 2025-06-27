import os, hashlib, random

def generate_random_hex16():
    return os.urandom(16).hex()

def hash_input(hex_str):
    return hashlib.sha256(bytes.fromhex(hex_str)).hexdigest()

def bernoulli_selection(hashed_inputs, k, p):
    selected = []
    attempts = 0
    order = []
    indices = list(range(len(hashed_inputs)))
    random.shuffle(indices)  # introduce unbiased ordering
    for i in indices:
        if len(selected) >= k:
            break
        if random.random() < p:
            selected.append(hashed_inputs[i])
            order.append(i)
    return selected, order

# Parameters
N = 100    # Total inputs
w = 50     # Inputs to consider
k = 5      # Winners to select
p = 0.2    # Probability of accepting a candidate

# Generate and hash inputs
hex_inputs = [generate_random_hex16() for _ in range(N)]
hashed_inputs = [hash_input(h) for h in hex_inputs]

# Select winners
winners, selection_order = bernoulli_selection(hashed_inputs[:w], k, p)

# Output
print("Selected winners in order:")
for idx in selection_order:
    print(f"Index {idx}: {hashed_inputs[idx]}")

"""
In this current setup, the hash is effectively just an identifier — a way to uniquely represent each 16-byte hex input.

Exactly k winners always, and still want Bernoulli sampling behavior:
- Run Bernoulli trials until k successes, or
- Select randomly from those who passed the Bernoulli trial if more than 𝑘

Selected winners in order:
Index 42: b2b9439980c7bcf44967402b5120c8b8c43adff8093b6b43f6791feebbdad7bf
Index 39: 690d23ed20813a9087fe6e1435c16e29ad5922e0913413e45ae010785a5834d1
Index 21: 81341b22dfcdcfcb563f08553f0d3a6767cc3a9b7ccd4bfbdebf016419487859
Index 25: 3757cd5ae7814b57e084a0f9b02b2b6a082cb93cf8af75e14767a10d2db51096
Index 19: 6fa5ea27e03b61ebe49b92b69049bd9fed44074953ab8e18cf0190b501f1ed86
"""