import hashlib
import secrets
from typing import Tuple, List, Dict

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

class VRFParticipant:
    """Represents a participant in the VRF system"""
    
    def __init__(self, name: str):
        self.name = name
        self.messages = []
        self.vrf_outputs = []
        self.proofs = []

def collect_participant_data(num_participants: int) -> List[VRFParticipant]:
    """Collect random data from N participants"""
    participants = []
    
    print(f"\n=== Collecting Random Data from {num_participants} Participants ===")
    print("Each participant will submit their own random message/data\n")
    
    for i in range(num_participants):
        name = input(f"Participant {i+1}, enter your name: ").strip()
        if not name:
            name = f"Participant_{i+1}"
        
        participant = VRFParticipant(name)
        
        print(f"\nHello {name}! Please submit your random data:")
        while True:
            message = input(f"{name}, enter your random message: ").strip()
            if message:
                participant.messages.append(message)
                break
            else:
                print("Please enter a non-empty message!")
        
        # Ask if they want to submit more messages
        while True:
            more = input(f"{name}, do you want to submit another message? (y/n): ").strip().lower()
            if more in ['y', 'yes']:
                additional_msg = input(f"{name}, enter another random message: ").strip()
                if additional_msg:
                    participant.messages.append(additional_msg)
            elif more in ['n', 'no']:
                break
            else:
                print("Please enter 'y' for yes or 'n' for no")
        
        participants.append(participant)
        print(f"✓ {name} submitted {len(participant.messages)} message(s)")
    
    return participants

def process_vrf_for_participants(participants: List[VRFParticipant], vrf: SimpleVRF):
    """Process VRF evaluation for all participants"""
    print("\n=== Processing VRF for All Participants ===")
    
    all_results = []
    
    for participant in participants:
        print(f"\nProcessing {participant.name}'s submissions:")
        
        for i, message in enumerate(participant.messages):
            msg_bytes = message.encode('utf-8')
            hash_output, proof = vrf.evaluate(msg_bytes)
            
            participant.vrf_outputs.append(hash_output)
            participant.proofs.append(proof)
            
            print(f"  Message {i+1}: [{message}]")
            print(f"  VRF Output: {hash_output.hex()}")
            print(f"  Proof: {proof.hex()}")
            
            # Store for collective analysis
            all_results.append({
                'participant': participant.name,
                'message': message,
                'vrf_output': hash_output,
                'proof': proof
            })
    
    return all_results

def verify_all_proofs(participants: List[VRFParticipant], vrf: SimpleVRF):
    """Verify all VRF proofs"""
    print("\n=== Verification of All Proofs ===")
    
    total_verified = 0
    total_messages = 0
    
    for participant in participants:
        print(f"\nVerifying {participant.name}'s proofs:")
        
        for i, message in enumerate(participant.messages):
            msg_bytes = message.encode('utf-8')
            hash_output = participant.vrf_outputs[i]
            proof = participant.proofs[i]
            
            if vrf.verify(msg_bytes, hash_output, proof):
                print(f"  ✓ Message {i+1}: [{message}] - PROVEN")
                total_verified += 1
            else:
                print(f"  ✗ Message {i+1}: [{message}] - VERIFICATION FAILED")
            
            total_messages += 1
    
    print(f"\nVerification Summary: {total_verified}/{total_messages} proofs verified successfully")

def analyze_collective_randomness(all_results: List[Dict]):
    """Analyze the collective randomness from all participants"""
    print("\n=== Collective Randomness Analysis ===")
    
    # Combine all VRF outputs for collective randomness
    combined_output = b''
    for result in all_results:
        combined_output += result['vrf_output']
    
    # Generate collective random value
    collective_hash = hashlib.sha256(combined_output).digest()
    
    print(f"Total participants: {len(set(r['participant'] for r in all_results))}")
    print(f"Total messages: {len(all_results)}")
    print(f"Collective random output: {collective_hash.hex()}")
    
    # Convert to integer for demonstration
    collective_int = int.from_bytes(collective_hash[:8], 'big')
    print(f"Collective random number: {collective_int}")
    print(f"Collective random (0-100): {collective_int % 101}")
    
    return collective_hash

def main():
    print("=== Multi-Participant VRF Demonstration ===")
    print("This demo allows N people to submit their own random data")
    print("and generates verifiable random functions for all submissions.")
    
    # Get number of participants
    while True:
        try:
            num_participants = int(input("\nHow many participants will submit random data? "))
            if num_participants > 0:
                break
            else:
                print("Please enter a positive number")
        except ValueError:
            print("Please enter a valid number")
    
    # Initialize VRF system
    vrf = SimpleVRF()
    print(f"\n✓ VRF system initialized with private key: {vrf.private_key}")
    
    # Collect data from all participants
    participants = collect_participant_data(num_participants)
    
    # Process VRF for all participants
    all_results = process_vrf_for_participants(participants, vrf)
    
    # Verify all proofs
    verify_all_proofs(participants, vrf)
    
    # Analyze collective randomness
    collective_hash = analyze_collective_randomness(all_results)
    
    # Summary
    print("\n=== Final Summary ===")
    for participant in participants:
        print(f"{participant.name}: {len(participant.messages)} message(s) submitted")
    
    print(f"\nAll {len(all_results)} messages have been processed through the VRF system.")
    print("Each participant's random input has been converted to a verifiable random output.")
    print("The collective randomness can be used for fair random selection or other applications.")

if __name__ == "__main__":
    main()

 """
 === Multi-Participant VRF Demonstration ===
This demo allows N people to submit their own random data
and generates verifiable random functions for all submissions.

How many participants will submit random data? 3

✓ VRF system initialized with private key: 16112315459542929928104962902756340377153042494361108864836960541212845688974

=== Collecting Random Data from 3 Participants ===
Each participant will submit their own random message/data

Participant 1, enter your name: 00

Hello 00! Please submit your random data:
00, enter your random message: 00
00, do you want to submit another message? (y/n): n
✓ 00 submitted 1 message(s)
Participant 2, enter your name: 11

Hello 11! Please submit your random data:
11, enter your random message: 11
11, do you want to submit another message? (y/n): n
✓ 11 submitted 1 message(s)
Participant 3, enter your name: 22

Hello 22! Please submit your random data:
22, enter your random message: 22
22, do you want to submit another message? (y/n): n
✓ 22 submitted 1 message(s)

=== Processing VRF for All Participants ===

Processing 00's submissions:
  Message 1: [00]
  VRF Output: c6a35562ab54adf843b8200dae64b09b246c9b03896fab06dbd735ecd54f40e7
  Proof: db5004b76c80eabd4f2edb58fdd57e4d42ce07040e8b7bccde4b33f69080f8b2

Processing 11's submissions:
  Message 1: [11]
  VRF Output: 9f84cba91639bbd18df608cc09fc14a5b9aa4a24020bc8bfa68917c38df7b093
  Proof: 77b19f6e5bf8c0a43393512b4e5a36412376851afada883ef0e9d6c53e934c42

Processing 22's submissions:
  Message 1: [22]
  VRF Output: 387469ed495dba99fbf7991145c39123770c5232d28a1a1094f0a0b4b1fc33ca
  Proof: e892c28ec088e84ada3ad0c9501ebbd23cd9884f0223560d127d3fdbf0db6eae

=== Verification of All Proofs ===

Verifying 00's proofs:
  ✓ Message 1: [00] - PROVEN

Verifying 11's proofs:
  ✓ Message 1: [11] - PROVEN

Verifying 22's proofs:
  ✓ Message 1: [22] - PROVEN

Verification Summary: 3/3 proofs verified successfully

=== Collective Randomness Analysis ===
Total participants: 3
Total messages: 3
Collective random output: 8f23dcfcd63f07471b6c2de8204315ee28e7114800e49a2a72b4bfc9e525b037
Collective random number: 10314330550092891975
Collective random (0-100): 6

=== Final Summary ===
00: 1 message(s) submitted
11: 1 message(s) submitted
22: 1 message(s) submitted

All 3 messages have been processed through the VRF system.
Each participant's random input has been converted to a verifiable random output.
The collective randomness can be used for fair random selection or other applications.
 """   