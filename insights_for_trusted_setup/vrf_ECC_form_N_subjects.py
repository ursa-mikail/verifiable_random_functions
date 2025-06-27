import hashlib
import secrets
import os
from typing import Tuple, List, Dict

# Simple Elliptic Curve implementation for secp256k1
class Point:
    """Represents a point on the elliptic curve"""
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y
        self.infinity = (x is None and y is None)
    
    def __eq__(self, other):
        if self.infinity and other.infinity:
            return True
        return self.x == other.x and self.y == other.y
    
    def __str__(self):
        if self.infinity:
            return "O (point at infinity)"
        return f"({self.x}, {self.y})"

class EllipticCurve:
    """Simplified secp256k1 elliptic curve implementation"""
    def __init__(self):
        # secp256k1 parameters: y² = x³ + 7 (mod p)
        self.p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
        self.n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
        self.a = 0
        self.b = 7
        # Generator point G
        self.G = Point(
            0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
            0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
        )
    
    def mod_inverse(self, a, m):
        """Calculate modular inverse using extended Euclidean algorithm"""
        if a < 0:
            a = (a % m + m) % m
        g, x, _ = self.extended_gcd(a, m)
        if g != 1:
            raise Exception('Modular inverse does not exist')
        return x % m
    
    def extended_gcd(self, a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = self.extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    def point_add(self, P, Q):
        """Add two points on the elliptic curve"""
        if P.infinity:
            return Q
        if Q.infinity:
            return P
        
        if P.x == Q.x:
            if P.y == Q.y:
                # Point doubling
                s = (3 * P.x * P.x + self.a) * self.mod_inverse(2 * P.y, self.p) % self.p
            else:
                # Points are inverses
                return Point()  # Point at infinity
        else:
            # Point addition
            s = (Q.y - P.y) * self.mod_inverse(Q.x - P.x, self.p) % self.p
        
        x = (s * s - P.x - Q.x) % self.p
        y = (s * (P.x - x) - P.y) % self.p
        
        return Point(x, y)
    
    def scalar_mult(self, k, P):
        """Multiply point P by scalar k using double-and-add"""
        if k == 0:
            return Point()  # Point at infinity
        if k == 1:
            return P
        
        result = Point()  # Point at infinity
        addend = P
        
        while k:
            if k & 1:
                result = self.point_add(result, addend)
            addend = self.point_add(addend, addend)
            k >>= 1
        
        return result
    
    def hash_to_curve(self, message: bytes) -> Point:
        """Hash message to a point on the curve (simplified)"""
        # This is a simplified version - real implementations use more sophisticated methods
        hash_val = hashlib.sha256(message).digest()
        x = int.from_bytes(hash_val, 'big') % self.p
        
        # Find a valid point by trying different x values
        for i in range(1000):  # Try up to 1000 times
            y_squared = (pow(x, 3, self.p) + self.b) % self.p
            
            # Check if y_squared is a quadratic residue
            if pow(y_squared, (self.p - 1) // 2, self.p) == 1:
                y = pow(y_squared, (self.p + 1) // 4, self.p)
                return Point(x, y)
            
            x = (x + 1) % self.p
        
        # Fallback to generator point if no valid point found
        return self.G

class ECVRF:
    """Elliptic Curve VRF implementation"""
    def __init__(self):
        self.curve = EllipticCurve()
        self.private_key = secrets.randbelow(self.curve.n)
        self.public_key = self.curve.scalar_mult(self.private_key, self.curve.G)
    
    def evaluate(self, message: bytes) -> Tuple[bytes, Tuple[int, int, Point]]:
        """
        Evaluate VRF for a message
        Returns (vrf_output, proof)
        """
        # Hash message to curve point
        H = self.curve.hash_to_curve(message)
        
        # Compute VRF value: VRF = k * H
        VRF = self.curve.scalar_mult(self.private_key, H)
        
        # Generate random nonce
        r = secrets.randbelow(self.curve.n)
        
        # Compute commitments
        rG = self.curve.scalar_mult(r, self.curve.G)
        rH = self.curve.scalar_mult(r, H)
        
        # Create challenge hash
        challenge_data = (
            self.curve.G.x.to_bytes(32, 'big') +
            self.curve.G.y.to_bytes(32, 'big') +
            H.x.to_bytes(32, 'big') +
            H.y.to_bytes(32, 'big') +
            self.public_key.x.to_bytes(32, 'big') +
            self.public_key.y.to_bytes(32, 'big') +
            VRF.x.to_bytes(32, 'big') +
            VRF.y.to_bytes(32, 'big') +
            rG.x.to_bytes(32, 'big') +
            rG.y.to_bytes(32, 'big') +
            rH.x.to_bytes(32, 'big') +
            rH.y.to_bytes(32, 'big')
        )
        
        s = int.from_bytes(hashlib.sha256(challenge_data).digest(), 'big') % self.curve.n
        t = (r - s * self.private_key) % self.curve.n
        
        # VRF output is hash of VRF point
        vrf_output = hashlib.sha256(
            VRF.x.to_bytes(32, 'big') + VRF.y.to_bytes(32, 'big')
        ).digest()
        
        proof = (s, t, VRF)
        return vrf_output, proof
    
    def verify(self, message: bytes, vrf_output: bytes, proof: Tuple[int, int, Point]) -> bool:
        """Verify VRF proof"""
        try:
            s, t, VRF = proof
            
            # Hash message to curve point
            H = self.curve.hash_to_curve(message)
            
            # Recompute commitments
            tG_plus_sP = self.curve.point_add(
                self.curve.scalar_mult(t, self.curve.G),
                self.curve.scalar_mult(s, self.public_key)
            )
            
            tH_plus_sVRF = self.curve.point_add(
                self.curve.scalar_mult(t, H),
                self.curve.scalar_mult(s, VRF)
            )
            
            # Recompute challenge
            challenge_data = (
                self.curve.G.x.to_bytes(32, 'big') +
                self.curve.G.y.to_bytes(32, 'big') +
                H.x.to_bytes(32, 'big') +
                H.y.to_bytes(32, 'big') +
                self.public_key.x.to_bytes(32, 'big') +
                self.public_key.y.to_bytes(32, 'big') +
                VRF.x.to_bytes(32, 'big') +
                VRF.y.to_bytes(32, 'big') +
                tG_plus_sP.x.to_bytes(32, 'big') +
                tG_plus_sP.y.to_bytes(32, 'big') +
                tH_plus_sVRF.x.to_bytes(32, 'big') +
                tH_plus_sVRF.y.to_bytes(32, 'big')
            )
            
            expected_s = int.from_bytes(hashlib.sha256(challenge_data).digest(), 'big') % self.curve.n
            
            if s != expected_s:
                return False
            
            # Verify VRF output
            expected_output = hashlib.sha256(
                VRF.x.to_bytes(32, 'big') + VRF.y.to_bytes(32, 'big')
            ).digest()
            
            return vrf_output == expected_output
            
        except Exception:
            return False

class VRFParticipant:
    """Represents a participant in the VRF system"""
    def __init__(self, name: str):
        self.name = name
        self.messages = []
        self.vrf_outputs = []
        self.proofs = []

def generate_random_participants(num_participants: int) -> List[VRFParticipant]:
    """Generate N participants with random test data"""
    participants = []
    
    print(f"\n=== Generating {num_participants} Participants with Random Data ===")
    
    # List of sample random data types
    sample_data = [
        "secret_number_", "random_phrase_", "lucky_string_", "crypto_seed_", 
        "random_value_", "entropy_data_", "random_bits_", "test_input_",
        "participant_seed_", "random_choice_", "lottery_number_", "hash_input_"
    ]
    
    for i in range(num_participants):
        name = f"Participant_{i+1}"
        participant = VRFParticipant(name)
        
        # Generate 1-3 random messages per participant
        num_messages = secrets.randbelow(3) + 1
        
        for j in range(num_messages):
            # Create random message
            prefix = secrets.choice(sample_data)
            random_number = secrets.randbelow(1000000)
            random_suffix = secrets.token_hex(8)
            message = f"{prefix}{random_number}_{random_suffix}"
            
            participant.messages.append(message)
        
        participants.append(participant)
        print(f"✓ {name}: {len(participant.messages)} random message(s) generated")
    
    return participants

def process_vrf_for_participants(participants: List[VRFParticipant], vrf: ECVRF):
    """Process VRF evaluation for all participants"""
    print("\n=== Processing Elliptic Curve VRF for All Participants ===")
    
    all_results = []
    
    for participant in participants:
        print(f"\nProcessing {participant.name}'s submissions:")
        
        for i, message in enumerate(participant.messages):
            msg_bytes = message.encode('utf-8')
            vrf_output, proof = vrf.evaluate(msg_bytes)
            
            participant.vrf_outputs.append(vrf_output)
            participant.proofs.append(proof)
            
            print(f"  Message {i+1}: [{message}]")
            print(f"  VRF Output: {vrf_output.hex()}")
            print(f"  Proof (s, t, VRF point): ({proof[0]}, {proof[1]}, {proof[2]})")
            
            # Store for collective analysis
            all_results.append({
                'participant': participant.name,
                'message': message,
                'vrf_output': vrf_output,
                'proof': proof
            })
    
    return all_results

def verify_all_proofs(participants: List[VRFParticipant], vrf: ECVRF):
    """Verify all VRF proofs using elliptic curve verification"""
    print("\n=== Elliptic Curve VRF Verification ===")
    
    total_verified = 0
    total_messages = 0
    
    for participant in participants:
        print(f"\nVerifying {participant.name}'s EC-VRF proofs:")
        
        for i, message in enumerate(participant.messages):
            msg_bytes = message.encode('utf-8')
            vrf_output = participant.vrf_outputs[i]
            proof = participant.proofs[i]
            
            if vrf.verify(msg_bytes, vrf_output, proof):
                print(f"  ✓ Message {i+1}: [{message}] - EC-VRF PROVEN")
                total_verified += 1
            else:
                print(f"  ✗ Message {i+1}: [{message}] - EC-VRF VERIFICATION FAILED")
            
            total_messages += 1
    
    print(f"\nEC-VRF Verification Summary: {total_verified}/{total_messages} proofs verified successfully")

def analyze_collective_randomness(all_results: List[Dict]):
    """Analyze the collective randomness from all participants"""
    print("\n=== Collective Randomness Analysis (Elliptic Curve Based) ===")
    
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
    print("=== Elliptic Curve VRF Multi-Participant Demonstration ===")
    print("This demo uses proper elliptic curve cryptography (secp256k1)")
    print("and generates random test data for N participants automatically.")
    
    # Get number of participants
    while True:
        try:
            num_participants = int(input("\nHow many participants should we simulate? "))
            if num_participants > 0:
                break
            else:
                print("Please enter a positive number")
        except ValueError:
            print("Please enter a valid number")
    
    # Initialize EC-VRF system
    vrf = ECVRF()
    print(f"\n✓ Elliptic Curve VRF system initialized")
    print(f"Private key: {vrf.private_key}")
    print(f"Public key: {vrf.public_key}")
    
    # Generate participants with random data
    participants = generate_random_participants(num_participants)
    
    # Process VRF for all participants
    all_results = process_vrf_for_participants(participants, vrf)
    
    # Verify all proofs
    verify_all_proofs(participants, vrf)
    
    # Analyze collective randomness
    collective_hash = analyze_collective_randomness(all_results)
    
    # Summary
    print("\n=== Final Summary ===")
    for participant in participants:
        print(f"{participant.name}: {len(participant.messages)} message(s) processed")
    
    print(f"\nAll {len(all_results)} messages have been processed through the EC-VRF system.")
    print("Each participant's random input has been converted to a cryptographically")
    print("verifiable random output using elliptic curve operations on secp256k1.")
    print("The collective randomness combines all individual VRF outputs fairly.")

if __name__ == "__main__":
    main()

"""
=== Elliptic Curve VRF Multi-Participant Demonstration ===
This demo uses proper elliptic curve cryptography (secp256k1)
and generates random test data for N participants automatically.

How many participants should we simulate? 3

✓ Elliptic Curve VRF system initialized
Private key: 60394470308420576427611520748332333856709740995148747621934376850477287138980
Public key: (72783732828507314330349465781084942128100869027657115879812445185755803192338, 46936185045130290649163490530164132091193290121822399710437865115076776638105)

=== Generating 3 Participants with Random Data ===
✓ Participant_1: 2 random message(s) generated
✓ Participant_2: 3 random message(s) generated
✓ Participant_3: 3 random message(s) generated

=== Processing Elliptic Curve VRF for All Participants ===

Processing Participant_1's submissions:
  Message 1: [lucky_string_980644_9de4d522ef3ee271]
  VRF Output: d751c94f729b54c0f92eb61c5e59930b260a8b9d458ed0a8e580df9ad93d0684
  Proof (s, t, VRF point): (104196488733376606580785145555030499727990895731272461971906947074917388818503, 45783197640390205804883701950308207190318405959831179921270498658673810777722, (43051084883784633429215327723999755642380747738928451944823321409553533931439, 7661256417288321933619190187139688015583645337117524304897908768066951767953))
  Message 2: [crypto_seed_903951_7bf61a55bd5d266c]
  VRF Output: 0c2091c0e5d5032a2aa7fb6cd3c0592a3b87938897a042ea71a3e340b738e51d
  Proof (s, t, VRF point): (36662956072635847084567085980992056989869888229237786683429326877768781795428, 18203787133552597846117941731261917584199433761411348800686136081333202933961, (6276935036871725972179201354010678619789634352327456227095038014814484245890, 71892854145501303661958928587646394406966283844790374014905603598469045289006))

Processing Participant_2's submissions:
  Message 1: [hash_input_237766_9109d5ff753d830e]
  VRF Output: 855bfe5f7934e8d9b30207b33fa98bb241ad18ddfe53c6bd80e09c63bad6bed7
  Proof (s, t, VRF point): (56481221412307319747957537584667171781035538785561410638284359237620947369933, 66547106486151351249236928820593479536422421303648695112812926070001710655668, (85896721747464740279246691702381593761812559102007182945380192406423618734457, 80524004517009649678317985280080037037804219788175787075813144267213219799345))
  Message 2: [lottery_number_290779_d1fb5d5faa7c6a60]
  VRF Output: a384bcf2ebdbd59f9f95696c5617e6c1d8cdf164433b28777016f54864783043
  Proof (s, t, VRF point): (38786955344661709273444440036438921614772927020379645614098403261608066920702, 273678702176798457420778470322912004285976184672824423829485608654174024305, (90378339119840791137019957608018148347655768439567509439674913455887725754561, 42027519589501311695330180326449952832460097453528115714294456108532513155941))
  Message 3: [random_choice_117421_729bf7d549f8b804]
  VRF Output: 9cf6069e4654aa49c62a3b76ab72de537a881ec4bdd3356d7780e70cf7a0ba95
  Proof (s, t, VRF point): (114078419905986558834591209822496874480069173752383150168722088230868116975421, 25008755818394794276614604516900141153283063017794517251401220261325454498146, (58767612167419874732783943474431986470484948061789196937227145297227626454533, 44082611371426648189828860567619325011959172708741913867664389811061233293496))

Processing Participant_3's submissions:
  Message 1: [lottery_number_118771_56e65df40a7184ea]
  VRF Output: 1592936c7bc86d09a94d538ab06e46c1760165eab151dd77f714b3e3a77c196d
  Proof (s, t, VRF point): (61318573493488409579282525623305256945168894944457294873824120083094633974943, 12277638957212779039470473856134288444954443635049443239854828660320759466242, (25127107500937277021135495733117054795216190403903929537223731566223729863107, 67456149324106502692817745496843221410487716730853844769189997025773478101223))
  Message 2: [participant_seed_349817_008278f8c899f8c2]
  VRF Output: c8c598f9b70865ffcb900d100f6d87a008a529d79227c5b810c195f3fae413fd
  Proof (s, t, VRF point): (16827887542024639118762879877446035552917688095107449008881324377698512349441, 79357117613474523064957806254064683777642555006339151584984864647470255895360, (93824727018826153735406967666710031014319418175656820324508478135971212077276, 35661796490793105532160658297104278916849827319041693030789377756838076253510))
  Message 3: [hash_input_217776_cb027693cfe7a75e]
  VRF Output: 64b5fc855cfe31ff1cccc52cd7b6cedf1cf46d0176e42b42f1bfb59b39b9853d
  Proof (s, t, VRF point): (85023662115009949088481436427694929024429684456784857089201496703730414149458, 16322638964329213959996448250773028028012734899967520197390619103460241330351, (32281388356243821218039143540544100180363158462645157574269714535884177235945, 74474955830991896289378272035991718434441383979377855755259201459902442207426))

=== Elliptic Curve VRF Verification ===

Verifying Participant_1's EC-VRF proofs:
  ✓ Message 1: [lucky_string_980644_9de4d522ef3ee271] - EC-VRF PROVEN
  ✓ Message 2: [crypto_seed_903951_7bf61a55bd5d266c] - EC-VRF PROVEN

Verifying Participant_2's EC-VRF proofs:
  ✓ Message 1: [hash_input_237766_9109d5ff753d830e] - EC-VRF PROVEN
  ✓ Message 2: [lottery_number_290779_d1fb5d5faa7c6a60] - EC-VRF PROVEN
  ✓ Message 3: [random_choice_117421_729bf7d549f8b804] - EC-VRF PROVEN

Verifying Participant_3's EC-VRF proofs:
  ✓ Message 1: [lottery_number_118771_56e65df40a7184ea] - EC-VRF PROVEN
  ✓ Message 2: [participant_seed_349817_008278f8c899f8c2] - EC-VRF PROVEN
  ✓ Message 3: [hash_input_217776_cb027693cfe7a75e] - EC-VRF PROVEN

EC-VRF Verification Summary: 8/8 proofs verified successfully

=== Collective Randomness Analysis (Elliptic Curve Based) ===
Total participants: 3
Total messages: 8
Collective random output: d9e8742dbbecbce65409878ff578053d509b24de549df478b92a90f1744ea337
Collective random number: 15701927840602438886
Collective random (0-100): 24

=== Final Summary ===
Participant_1: 2 message(s) processed
Participant_2: 3 message(s) processed
Participant_3: 3 message(s) processed

All 8 messages have been processed through the EC-VRF system.
Each participant's random input has been converted to a cryptographically
verifiable random output using elliptic curve operations on secp256k1.
The collective randomness combines all individual VRF outputs fairly.
"""    