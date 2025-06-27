package main

import (
	"fmt"
	"os"

	"github.com/google/keytransparency/core/crypto/vrf/p256"
)

func main() {

	k, pk := p256.GenerateKey()

	d1 := "This is a test"
	d2 := "This is not a test"

	argCount := len(os.Args[1:])
	if argCount > 0 {
		d1 = os.Args[1]
	}
	if argCount > 1 {
		d2 = os.Args[2]
	}

	m1 := []byte(d1)
	m2 := []byte(d2)

	index1, proof1 := k.Evaluate(m1)
	index2, proof2 := k.Evaluate(m2)

	fmt.Printf("== Creation of proofs ===\n")
	fmt.Printf("Data: [%s] Index: %x Proof: %x\n", m1, index1, proof1)
	fmt.Printf("Data: [%s] Index: %x Proof: %x\n", m2, index2, proof2)

	fmt.Printf("\n== Verfication of proofs ===\n")
	newindex1, _ := pk.ProofToHash(m1, proof1)
	fmt.Printf("Result 1: %x\n", newindex1)
	if index1 == newindex1 {
		fmt.Printf("Proven\n")
	}

	newindex2, _ := pk.ProofToHash(m2, proof2)
	fmt.Printf("Result 2: %x\n", newindex2)
	if index2 == newindex2 {
		fmt.Printf("Proven\n")
	}

}

/*
% go mod tidy
% go run main.go
== Creation of proofs ===
Data: [This is a test] Index: fda2caa22a249af9faef800633fd76d57fab14dddf3d561509fd0177944455d0 Proof: a08f238f115de243ee860cd525736f046302db6db799673796749ee838b84e6423e62b9991b31797e76c4e38d693c29f514e3dbeccb386df395086e21380feba04d7b3e30bb9c079e435406b9c9192ae4b1883c6f0d8d24cd2079147dec6b8a88faed7a948c121b955dd4aa670fd268a9763d74d637f7ccde25ecaab5d6cadd0ee
Data: [This is not a test] Index: 6eff2ec1e19ea8b069bbd16950b9df1f580bdeea3687a1eab1faa7d7f4634e83 Proof: 2ea7a7aa6386a91a3d2ae79b1408d4ece29b5e2276acb83c3df6579d7496774db11e462ead3db482ac7c720a2858e8400dc325338d29b70de6dd95f74a4aafbe04faeb19b683c8b3ade2ace248d29739335f39cfa814a42d4552421e87fcfa8edb28b0f896c6c68f656be678fb432ea4b8f1c35ad17814cfaf5f3f48ec508850d3

== Verfication of proofs ===
Result 1: fda2caa22a249af9faef800633fd76d57fab14dddf3d561509fd0177944455d0
Proven
Result 2: 6eff2ec1e19ea8b069bbd16950b9df1f580bdeea3687a1eab1faa7d7f4634e83
Proven

*/
