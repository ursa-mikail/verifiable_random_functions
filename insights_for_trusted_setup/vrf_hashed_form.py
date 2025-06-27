import hashlib
import secrets
import os
from typing import Tuple, Optional

class SimpleVRF:
    """
    A simplified VRF implementation for demonstration purposes.
    Note: This is a basic implementation and should not be used in production.
    """
    
    def __init__(self):
        self.private_key = secrets.randbits(256)
        self.public_key = self.private_key  # Simplified for demo
    
    def evaluate(self, message: bytes) -> Tuple[bytes, bytes]:
        """
        Evaluate the VRF for a given message.
        Returns (hash_output, proof)
        """
        # Simplified VRF evaluation
        combined = self.private_key.to_bytes(32, 'big') + message
        hash_output = hashlib.sha256(combined).digest()
        
        # Simplified proof generation
        proof_data = str(self.private_key) + message.decode('utf-8', errors='ignore')
        proof = hashlib.sha256(proof_data.encode()).digest()
        
        return hash_output, proof
    
    def verify(self, message: bytes, hash_output: bytes, proof: bytes) -> bool:
        """
        Verify a VRF proof.
        Returns True if proof is valid, False otherwise.
        """
        # Simplified verification
        expected_hash, expected_proof = self.evaluate(message)
        return hash_output == expected_hash and proof == expected_proof

def main():
    # Initialize VRF
    vrf = SimpleVRF()
    
    # Default test messages
    d1 = "This is a test"
    d2 = "This is not a test"
    
    # Allow command line arguments or random input
    if len(os.sys.argv) > 1:
        d1 = os.sys.argv[1]
    if len(os.sys.argv) > 2:
        d2 = os.sys.argv[2]
    
    # Allow random input submission
    print("VRF Demo - Enter messages or press Enter to use defaults")
    user_input1 = input(f"Message 1 (default: '{d1}'): ").strip()
    if user_input1:
        d1 = user_input1
    
    user_input2 = input(f"Message 2 (default: '{d2}'): ").strip()
    if user_input2:
        d2 = user_input2
    
    # Convert to bytes
    m1 = d1.encode('utf-8')
    m2 = d2.encode('utf-8')
    
    # Generate VRF outputs and proofs
    index1, proof1 = vrf.evaluate(m1)
    index2, proof2 = vrf.evaluate(m2)
    
    print("\n== Creation of proofs ===")
    print(f"Data: [{d1}] Index: {index1.hex()} Proof: {proof1.hex()}")
    print(f"Data: [{d2}] Index: {index2.hex()} Proof: {proof2.hex()}")
    
    print("\n== Verification of proofs ===")
    
    # Verify first message
    if vrf.verify(m1, index1, proof1):
        print(f"Result 1: {index1.hex()}")
        print("Proven")
    else:
        print("Verification failed for message 1")
    
    # Verify second message
    if vrf.verify(m2, index2, proof2):
        print(f"Result 2: {index2.hex()}")
        print("Proven")
    else:
        print("Verification failed for message 2")
    
    # Interactive mode for additional random submissions
    print("\n== Interactive Mode ==")
    print("Enter additional messages to test (or 'quit' to exit):")
    
    while True:
        user_msg = input("Enter message: ").strip()
        if user_msg.lower() in ['quit', 'exit', 'q']:
            break
        if user_msg:
            msg_bytes = user_msg.encode('utf-8')
            index, proof = vrf.evaluate(msg_bytes)
            print(f"Data: [{user_msg}] Index: {index.hex()} Proof: {proof.hex()}")
            
            if vrf.verify(msg_bytes, index, proof):
                print("Proven ✓")
            else:
                print("Verification failed ✗")
        print()

if __name__ == "__main__":
    main()

"""
VRF Demo - Enter messages or press Enter to use defaults
Message 1 (default: '-f'): -f
Message 2 (default: '/root/.local/share/jupyter/runtime/kernel-0420eac5-b68a-4ff8-a615-67b3cc738fde.json'): 

== Creation of proofs ===
Data: [-f] Index: 3cb0c757e903e7935a37a93b9aff09cad8a900ca9233391fdf2c467c61669fab Proof: d54149491c7cef5c20600f1fd35ecb9dda92550b9e8e997cf7db865d6abaf5a2
Data: [/root/.local/share/jupyter/runtime/kernel-0420eac5-b68a-4ff8-a615-67b3cc738fde.json] Index: 29c51a86a090ddf77c962c7ab3207df875cd26280a815882c6cc7140093c5079 Proof: 25f1130a25e07b553a956b2160089b2abd034ba0585552bd4bba1a6b3b8efc65

== Verification of proofs ===
Result 1: 3cb0c757e903e7935a37a93b9aff09cad8a900ca9233391fdf2c467c61669fab
Proven
Result 2: 29c51a86a090ddf77c962c7ab3207df875cd26280a815882c6cc7140093c5079
Proven

== Interactive Mode ==
Enter additional messages to test (or 'quit' to exit):
Enter message: quit
"""