"""
Bernoulli chain selection to:
1. Generate N random 16-byte hex values.
2. Hash each (SHA-256) → gives you hashed_inputs.
3. Begin a deterministic chaining process:
    1. Generate an initial random seed (internally).
    2. From those, pick w inputs (e.g. the first w).    # alternatively include all N
    3. Use SHA-256(seed) to pick one from the list of w.
    4. Use the selected hash as the next seed.
    5. Remove selected from the candidate pool.
    6. Continue until all w are consumed → build a selection trail.
4. At the end, select k of w winners based on the first k items in the selection trail.
5. Return:
- The ordered k selected winners,
- And the final SHA-256 seed (used to "burn out" the entropy).
"""

import os
import hashlib

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def pick_index_from_seed(seed: str, pool_size: int) -> int:
    # Hash seed, convert to integer, take modulo of pool size
    h = hashlib.sha256(seed.encode()).hexdigest()
    return int(h, 16) % pool_size

def bernoulli_chain_selection_from_hex(hex_inputs, k, w):
    assert w <= len(hex_inputs), "w must be <= number of hex inputs"
    
    original_pool = hex_inputs[:w]          # Save for index lookup
    candidates = hex_inputs[:w].copy()      # Copy to safely mutate
    """ Alternatively, choose all N:
    original_pool = hex_inputs          # Save for index lookup
    candidates = hex_inputs.copy()      # Copy to safely mutate
    """
    initial_seed = sha256_hex(os.urandom(32))
    current_seed = initial_seed

    selection_order = []
    while candidates:
        idx = pick_index_from_seed(current_seed, len(candidates))
        selected = candidates.pop(idx)
        selection_order.append(selected)
        current_seed = selected

    final_seed = sha256_hex(current_seed.encode())
    return selection_order[:k], selection_order, final_seed, original_pool


# Example usage
N = 100
w = 50
k = 5

hex_inputs = [os.urandom(16).hex() for _ in range(N)]
print(f"Generated: {hex_inputs}")

winners, full_order, final_seed, original_pool = bernoulli_chain_selection_from_hex(hex_inputs, k, w)

# Output
print("Selected winners (in order):")
for i, winner in enumerate(winners):
    original_index = original_pool.index(winner)
    print(f"{i+1}: {winner} (original index in w={w}: {original_index})")

print("\nFinal seed after full chain:", final_seed)


"""
Generated: ['c0dc3dfb162735e44f87bd90f9c7663d', 'bbc8af6a52a7aa30ec4449348a037c8a', '410e6ded7b7733d83a5cdc859ab2c79d', '7c24da555ed8cc21ba3510a196066fad', '48fa48f81f7a46c33cd072cd2ef88531', '445d2a9647b0b491247d74ce2205c5d3', 'dfc40907add3584812cc7b9ac89028c3', 'e7908799f19fe62121b1d3a9b8d32a18', 'ec2a068455f99360f0262eb0938f9f56', 'f45aa3877e965b9111943f295b16b294', 'cb4efaafdf3bca2cd27982733bef6f08', 'a85bd4aa50fc9debfe4d83ad96b4bcce', 'c951b28731b706370d5e81a6f05c6a44', 'a45c956d11737a174f5cad561619533f', '1463a2a0454bc7f282cd96e217d8d874', '6e95da3d8859d901edaa1e928f8d27b4', 'bfd91b5866818670a35aceba7cac4a30', '2353b923cef0f3ae1d3631079b64c795', '6f0146fa6346509767c55c0625daddbc', 'e6d971f7a26620ed93349564da221e3c', 'e62ac0ad421f7afa204c2b521602479f', '34f23ac93f0e6ffa3c4070419a70ccd5', 'a016b5cb27abe606438c2cd422f2f71c', '6c899d0ebaef8ea4af4bb9ac884770f9', 'b02bbccf473d092e5f5016d879363f0c', '3a93e736ea89ab3a0482b429f8e0797c', 'd22ee78476b8e1ecf5e17fe1f48e4f86', 'b20d58846132f87ceefa86a574fd9a6d', '8e844039e2850809205f8340f0479baf', '246df9b031255f488ca5eced8867bbbc', '3976a9ae20f2119047de423121cb086f', '130a04edbdac418479f03d1d01970ae1', '13935d64350ec4a4b5e2e9a2cce31c37', 'ea42966445ce29de08cb1c9221c0e088', 'ee49f0fa0fdab381b1062dec2637724f', 'a37e1653555219842700e87d15e6e8b5', '9c5111dc3d0fdbbbbdc66d959dd0a1b7', '174f1647c1c68be5767f6983b2c74cc5', 'c6e9d1f3e8227bf843524e7de1780882', '3cc535796e3e387ae22fac58a751f233', '27583f2e331dbd60851717db023f29b9', 'bac3148df1ec46e1c17a293843375781', '303cb9295757df80cb03b411bee6cbe3', '55c28587d14ec9f87bf6450d0c2a5e5e', '641f1c14009c66dea0781b7af01123fa', 'd5ae45c1c61362f38e3b19a61504e77b', '7620ec091e91934c4048a632bb659fb4', '6b7cef636090fa480cac0a1ec4a3d415', '56aea71a458b9fc5690447acad479764', '5639afca5b3cdac907006a6694129c66', 'c7d465af8056167955a7796ff513b40b', '8ae56c0ccb3dee2f9aace25bc68b643a', '76310c1c441cb24c0516e4e4b7ef21c7', '3702246db3a56c4b8d6fdc2a8b43032c', 'be3547092f816165091a6fc9658e5b09', '4ffa9e02059a9f564535f926b065b244', 'bf05e4108d24c65912146a89abfe18a7', 'dc5173a9363c404c92e86c17316a1d73', 'e006b5382e82e022897cf3c0c13bd83f', '2ab61df02d5b6d7556e79a3bd8c5efa2', '9231337fc213aebc59605c0b3db2aab2', '0e43fc2bc82aba5fa3b2c0287ce20569', '4c7847c67688dccbbcda93feb454f744', '482b58bc837ec30690bba25a85ec12d3', '52cbbeb8be7d2a22b01b70f5a63d6fb2', '385d309282329fa3ec2e0cdbbf30ff8a', '0cbabc2afd10bf09d1989ae49638ba86', '8cd5eec36936ba243417dd0b60198223', '350dc10d38520eb92fbdea213171ac89', '6736efc5d1097a58a7e8e95aa81dd6e6', 'e84a6ad45d8509781a45f4689481ef26', '0b65c21472db7561ea9e7d232338445d', '99bad37672594dbee45bf948a2d35f5c', '06dc6b76f83b4866b0dd03e91e502cd4', '82f080d93a1b8eaa20b6c76a24c743ce', 'fa5a74db0b181918705ba925bb09175e', '52fcd5173afc5147d00351241bcd447a', 'c54bc9ad6f0500505bda3394494f11de', 'e0df7dc8cb4f0cfc402135ab1c5bb4b9', '3119f28d29fc171afa9fe1c3253e93a6', '2fcd70272cd42a9d7ea8987dfefde78e', 'a37e5744f5cc8a27af0d8ed91083adb4', '88154b23387825aab14b0069f40b83de', '5c1f683186c1a0225fea3ccc3e0c0edb', 'e8ea39952257dbdcca70fcbdbe97a027', '33ba1594eb198aecad04979792970f50', 'bb9c529e319b5dc2afe43d2d9e67ff96', '1232cf3007c4e6c15afd97f6d86d77b7', '691545602066ee77e82988f72b67c189', '1b55b5d38b99daff62c1d48a085a1192', 'e7508d43399812fd931d8b7bbadf6839', 'bc18bd00f3fd1216b81bb6f7e5a53d9b', 'f31baed2f1be79e33ecdd88a45ea7a2b', '8d44492957dd4b071dfac6305a11dd01', '44c4045b445442ccd9952c27e1e12cc6', 'da1c33bee5cc354b6a0603fb28837a56', '4b1dd970f3c637910fc28877bfa53b1e', '7f385ad3f9b0ac36243b99a1f0ef8442', 'd7ca242e4a213bc410bb3be82c1107ba', 'a512ebdc2447d248918c9af37602d3b7']
Selected winners (in order):
1: 48fa48f81f7a46c33cd072cd2ef88531 (original index: 4)
2: 303cb9295757df80cb03b411bee6cbe3 (original index: 42)
3: 174f1647c1c68be5767f6983b2c74cc5 (original index: 37)
4: 1463a2a0454bc7f282cd96e217d8d874 (original index: 14)
5: 27583f2e331dbd60851717db023f29b9 (original index: 40)

Final seed after full chain: f1b04ade4bfce43675191ba9878b89521be5e53f7da5bc23282d0ec71ed17578


"""