---
title: "Understanding Verifiable Delay Functions (with a Rust implementation)"
date: 2019-11-30T13:57:25-07:00
---

I have been reading about Verifiable Delay Functions (VDF) recently and wanted to write a short post explaining what they are and what they can be used for. This post relies mainly on the papers: [Efficient verifiable delay functions, Wesolowski](https://eprint.iacr.org/2018/623.pdf) and [A Survey of Two Verifiable Delay Functions, Boneh et al](https://crypto.stanford.edu/~dabo/pubs/papers/VDFsurvey.pdf). I also recommend [this podcast](https://www.zeroknowledge.fm/103) with Joseph Bonneau.

## Definition

A VDF is a function $f_T: \mathcal{X} \to \mathcal{Y}$ that takes a long time to compute but is fast to verify. Concretely, this means that $f_T$ takes $T$ steps to compute **regardless of the number of parallel processors**, and having computed $f(x)=y$, a prover can produce a proof $\pi$, such that a verifier can quickly check (say in time $O(\log T)$) that $f(x)=y$ using $\pi$.



At first sight, this definition looks very familiar to proof of work: given a hash function $H: \{0,1\}^* \to 2^k$, find $y$ such that $H(y)<x$. With the random oracle model, this takes on average $\frac {2^k} x$, so by setting $x=\frac {2^k} T$, we can get a PoW map running on expectation in $T$ steps. Also, PoW is easily verifiable: just give $y$ to the verifier, and they can check that $H(y)<x$.

The major problem with this approach, and something crypto miners have long figured out, is that this function is highly parallelizable: using $n$ processors yields $n$ times faster computations.

VDFs can be incredibly useful since one cannot compute them faster by buying more processors.

## Applications

### Random beacon

Randomness is hard to achieve in a blockchain. The reason is that miners can choose not to communicate a block they've found if the *randomness* in this block is at their disadvantage. The classical example is the one of a *casino* smart contract. This smart contract proposes a heads or tail game where you double your bet with probability 0.5 and lose it also with probability 0.5. A miner can cheat this contract by playing it and at the same time ignoring any new block where the coin result makes them lose their bet. What's more, people can try to bribe miners to have higher chances to win at this game. This totally breaks the point of randomness.

VDFs solve this problem in a clever way. We ask that the randomness comes not from the block itself, but from a VDF of the block! Concretely, instead of using $H(B)$ as a random value, we use $H(f_T(H(B)))$. The difference is the $T$ steps of computations necessary for $f_T$ between the latter and the former. By setting $T$ to a high enough value, we ensure that a miner trying to cheat will have to wait too long to know the *random* result of each block making it impossible to cheat without other miners being faster.

Here, we also see why VDFs need to be **functions**, i.e., have a unique output. If a VDF could have multiple possible outputs, nobody could agree on the randomness since $H(f_T(H(B)))$ would have multiple possible values.

We also see the need for fast proofs, since everybody needs to be convinced that the random values are truthful, without having to compute the slow function $f_T$.



There are other applications of VDFs, mainly in the blockchain space. See the papers cited in the intro for a survey.



## Wesolowski's construction  ([paper](https://eprint.iacr.org/2018/623.pdf))

### The function

Let $G$ be a group of **unknown** order and $H: \mathcal{X}\to G$ a hash function, then 
$$
f_T: \mathcal{X}\to G: x\mapsto H(x)^{(2^T)}
$$
is a VDF.  $f_T$ can be computed in $T$ steps by squaring $H(x)$ $T$ times sequentially. Importantly, when the order of the group is unknown, no algorithm is know that computes $f_T$ faster than that, even with many parallel processors. 

When the group has a **know order** $n$, the construction breaks since $g^{(2^T)} = g^{(2^T mod\ n)}$ can be computed by first computing $2^T mod\ n$ in $\log T$ steps, and then computing $g^{(2^T mod\ n)}$ in $O(\log n)$ steps.

Now, this construction is very simple and you may wonder why VDFs have only appeared recently. Indeed, this function was already used by Ron Rivest for his [time capsule puzzle](https://en.wikipedia.org/wiki/LCS35) in 1999. But it's only recently that protocols have been found to **verify** that the function was computed correctly.

### Verifiability

Wesolowski and [Pietrzak](https://eprint.iacr.org/2018/627) independently found protocols to verify $f_T$ in 2018. We will focus on Wesolowski's construction here.

1. The prover sends $g=H(x)$ and $y=f_T(x)=g^{(2^T)}$ to the verifier.
2. The verifier checks that these are group elements and sends a random prime $l$ from the first $2^\lambda$ primes to the prover, where $\lambda$ is a security parameter.
3.  The prover computes the Euclidean division $q,r$ such that $2^T = ql + r$, and sends $\pi=g^q$ to the verifier.
4. The verifier computes $r=2^T mod\ l$ and checks that $h = \pi^l g^r$. 

A verifier will always accept a honest prover since $g^{(2^T)}=h=\pi^lg^r=g^{ql+r}$. 

This protocol has low communication complexity since the verifier sends at most 3 group elements and the verifier sends one prime $l=O(2^\lambda)$. The verification is also fast since it only requires the verifier $O(\log T)$ group operations to compute $r, \pi^l$ and $g^r$.

The prover on the other hand needs to compute $\pi=g^q$ which can be quite costly. The paper describes an algorithm to compute it in $T/s$ steps on $s$ processors. 

### Security

The security of the protocol relies on the following assumption:

##### Adaptive root assumption (roughly)

*No efficient adversary can output an element $w\in G$ and then, given a prime $l\in P$, output $w^{1/l}$.*



If the adversary guesses $l$ beforehand, he can output $w=u^l$ and then $u$. That is why we use $|P|=2^\lambda$, in the protocol, so that an adversary has a negligible chance of guessing $l$.  

This assumption is necessary since if an adversary breaking it can make the verifier accept $wh\ne f_T(x)$ with the proof $w^{1/l}g^q$.  Indeed, 
$$
wh = (w^{1/l}g^q)^l g^r = w g^{ql + r},
$$
and the protocol is unsafe. 

### Groups of unknown orders

There are two main types of group of unknown order: RSA groups and ideal class groups. 

The first type consists of the groups $(\mathbb{Z}/N\mathbb{Z})^*$ where $N$ is a product of two unknown primes. These primes can be generated using a trusted setup, or by using RSA numbers you [find in the wild](https://en.wikipedia.org/wiki/RSA_numbers) and hoping that nobody kept the primes. 

Ideal class groups are more advanced mathematical constructions, but importantly it is believed to be hard to compute their orders under certain conditions.

Both types of groups are believed to satisfy the *adaptive root assumption* so that they can be used for VDFs.



## Rust implementation

After all this theory, we finally implement our own VDF using Rust. We use RSA groups and the [ramp](https://github.com/Aatch/ramp) library for arbitrary precision arithmetic. The full code can be found [here](https://github.com/wborgeaud/rust-vdf).

### Hashing

Let $\tilde{H}$ be your favorite traditional hash function. Mine is SHA-512. Then, we hash into the group $G= (\mathbb{Z}/N\mathbb{Z})^*$ like so:
$$
H(x) = \tilde{H}(x||0)\ || \ \dots\ ||\ \tilde{H}(x||k) \ mod \ N \in G,
$$
where $k$ is a large enough constant (we use $2|N|/|\tilde{H}|$). Here is the Rust implementation:

```rust
use ramp::Int;
use sha3::{Digest, Sha3_512};

pub fn hash(s: &str, N: &Int) -> Int {
    let mut ans = Int::zero();
    for i in 0..(2*N.bit_length()/512 + 1) {
        let mut hasher = Sha3_512::new();
        hasher.input(format!("{}{}", s, i).as_bytes());
        let arr = hasher.result();
        for x in arr.into_iter() {
            ans = (ans<<8) + Int::from(x);
        }
    }
    ans % N
}
```

**Note**: In production, we should probably check that $gcd(H(x), N) = 1$.

### The VDF

The VDF itself is very simple:

```rust
pub fn vdf(g: &Int, T: u128, N: &Int) -> Int {
    let mut ans = g.clone();
    for _ in 0..T {
        ans = ans.pow_mod(&Int::from(2), N);
    }
    ans
}
```

### Verification

Verification is also straightforward:

```rust
pub fn verify(pi: &Int, g: &Int, h: &Int, l: u64, T: u128, N: &Int) -> bool {
    if pi > N {
        return false;
    }
    let r = pow_mod(2, T, l.into());
    *h == (pi.pow_mod(&Int::from(l), &N) * g.pow_mod(&Int::from(r), &N)) % N
}
```

### Test

```rust
// Using RSA-1024 from https://en.wikipedia.org/wiki/RSA_numbers
let N = Int::from_str("135066410865995223349603216278805969938881475605667027524485143851526510604859533833940287150571909441798207282164471551373680419703964191743046496589274256239341020864383202110372958725762358509643110564073501508187510676594629205563685529475213500852879416377328533906109750544334999811150056977236890927563").expect("Cannot read string");
let T = 100000;

// Running the VDF
let g = hash(&format!("VDFs are awesome"), &N);
let res = vdf(&g, T, &N);
// Sampling the prime
let l = get_prime();
// Generate the proof pi
let pi = prove(&g, &res, &Int::from(l), T, &N);
// Verify the proof
let is_ok = verify(&pi, &g, &res, l, T, &N);
assert!(is_ok);
```

## Conclusion

This was a quick introduction to VDFs. I think these are nice cryptographic objects that are easy to understand but can have very useful applications. I encourage you to read the papers cited above to learn more about them! 
