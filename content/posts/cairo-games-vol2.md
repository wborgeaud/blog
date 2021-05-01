---
title: "Cairo Games Vol 2: Writeup"
date: 2021-04-19
description: ""
slug: ""
tags: [ctf-writeup, cryptography, stark]
---

Here are my solutions to the second edition of the [Cairo Games](https://www.cairo-lang.org/the-cairo-games/).
- [Nu (Easy)](#nu)
- [Pakhet (Easy)](#pakhet)
- [Seth (Medium)](#seth)
- [Montu (Medium)](#montu)
- [Amun (Hard)](#amun)

# Nu
This problem was pretty straightforward. We have to find to integers `x,y<2^128` such that `x*y=17` in the prime field used by Cairo. We can easily get such a pair as follows:
```python
from sympy import divisors
    P = 2**251 + 17 * 2**192 + 1
    BOUND = 2**128
    target = P + 17

    for d in divisors(target):
        n = target // d
        if n < BOUND and d < BOUND:
            break
    ids.x = n
    ids.y = d
```

# Pakhet
We get a graph on 18 vertices as an adjacency matrix. We then have to find a path of length 18 `path` in this graph such that
- `assert [path] = [path + N_VERTICES]`: The path is a cycle,
- `check(path, aux=aux, graph=graph, n=N_VERTICES)`: This function takes the path as well as an auxiliary array `aux` and checks that `path` is a permutation of `[0, 1, ..., 17]`.

These two checks imply that `path` is a **Hamiltonian cycle** of the graph. Finding an Hamiltonian cycle is hard in general, but for such a small graph we can find one easily. I used [this implementation](https://www.geeksforgeeks.org/hamiltonian-cycle-backtracking-6/) to find the cycle:
```python
from hamiltonian import Graph

N = 18
graph = list(
    reversed(
        list(
            map(
                int,
                bin(904711815024524574246580775193158565348810842345109828206640)[
                    2:
                ].zfill(200),
            )
        )
    )
)
graph += list(
    reversed(
        list(
            map(int, bin(1662189419663012728075783146332749833)[2:].zfill(N * N - 200))
        )
    )
)

g = Graph(N)
g.graph = [graph[i * N : i * N + N] for i in range(N)]

path = g.hamCycle()
aux = [18 - path.index(i) for i in range(18)]
print(graph)
print(path + [path[0]])
print(aux)
```
Note that this problem shows that STARKs contain NP, as finding Hamiltonian cycles is an NP problem.

# Seth
Let $H: \mathbb{F}\times \mathbb{F} \to \mathbb{F}$ be the Pedersen hash function and for an array $A$ of size $N$, let $H^*(A)=H(N, H(A_0,H(A_1,...)))$ be the hash chain function. 

In this problem, we have to find an array $D$ of size 100, such that if we let $S_0 = H^*(D)$, we have for $i=0,1,...,99$:
$$D_{r_i} = 0 \text{ if } 2|i  \text{ else } H(x_i,x_i),$$

$$S_{i+1} = H(H(S_i, x_i), D_{r_i}),$$
where $r_i = S_i \wedge  (2^{128}-1) \mod 100$, $\wedge$ being the bitwise AND.

My strategy to find such an array was the following:
1. Set $D_0 = H(c,c)$ and $D_i=0$ for $0<i<100$, with any $c$ such that $r_0\ne 0$. Setting $c=0$ works.
2. Find $x_i$ such that $r_{i+1}=0$.
3. Set $x_{i+1} = c$. Then $D_{r_{i+1}}=D_0=H(x_{i+1},x_{i+1})=H(c,c)$ holds, and $S_{i+2}=H(H(S_{i+1}, c), D_0)$. Go to step 2.

Note that in Step 3, if the new seed $S_{i+2}$ is such that $r_{i+2}=0$, the process fails. In this case, we can just try another initial seed $c$. If setting $c=0$, this never occurs though.

Here is the code to find the $x_i$'s:
```python
from fast_pedersen_hash import pedersen_hash as H

def hash_chain(length, l):
    if length == 1:
        return H(length, l[0])
    h = H(l[-2], l[-1])
    for i in range(3, length + 1):
        h = H(l[-i], h)
    h = H(length, h)
    return h

def get_seed(s):
    low = s & ((1 << 128) - 1)
    r = low % 100
    if r == 0:
        raise Exception("Bad intial seed")
    for j in range(10 ** 10):
        ns = H(s, j)
        ns = H(ns, 0)
        nlow = ns & ((1 << 128) - 1)
        nr = nlow % 100
        if nr == 0:
            s = ns
            return s, j

SIZE = 100
def get(c):
    data = [0 for _ in range(SIZE)]
    h = H(c, c)
    data[0] = h

    s = hash_chain(SIZE, data)
    preims = []
    while True:
        s, j = get_seed(s)
        preims.append(j)
        preims.append(0)
        if len(preims) == SIZE:
            break
        s = H(s, 0)
        s = H(s, h)

    return data, preims

c = 0
while True:
    try:
        print(get(c))
        break
    except:
        pass
    c += 1
```

# Montu
This problem was very easy if you knew about FRI, but probably quite hard otherwise. I'll assume knowledge of FRI. A good introduction can be found [here](https://starkware.co/developers-community/stark101-onlinecourse/).

We get an array $A_0$ of 8 field elements and a field element $G$ of multiplicative order 8.
We then have to come up with a modified array $A$ such that the Hamming distance $d(A_0, A)=3$, i.e., $A$ is equal to $A_0$, except at 3 points, and such that $A$ is constant after two FRI reduction steps.
Unless we're cosmically lucky, the easiest way to achieve this is to set $A$ to be a low-degree extension of a degree 3 polynomial. In FRI jargon, we would say that we need to prove that $A_0$ is $\frac{3}{8}$-far from $RS[\langle G \rangle, \frac{1}{2}]$.

To find $A$, we iterate over all combinations of $A_0$ minus 3 points, and stop when we find one that interpolates a degree 3 polynomial:
```sage
P = 2**251 + 17 * 2**192 + 1
F = GF(P)
G = F(2804690217475462062143361339624939640984649667966511418446363596075299761851)
domain = [pow(G, i) for i in range(8)]

L = [2760163267763136926307712447289333015931143661720962520709479367174330989984,
620345510678501588305616341951109830750033614090225920347864657883483407165,
3181959697776337130511545402257206919343979808211484609881516936335798865334,
1830152343057623004121086982129442788610913917055044983876581372969127139593,
3553572895696142252358926310847411672039878792883770142922873977486098926969,
2462248735454554379268841047904517280521029943202779759148500485193601548624,
792090413233267968557021563731724001464889355006703125688313681478453789157,
1348005446214778757482455457529115254152067928062775094282398020688141612139]

R.<x> = F[]

for t in combinations(range(8), 5):
    l = [A[i] for i in t]
    d = [domain[i] for i in t]
    P = R.lagrange_polynomial(zip(d, l))
    if P.degree()==3:
        LDE = [P(x) for x in domain]
        print(LDE)
        break
```

# Amun
This problem was harder and more contrived than the others. The gist of it is as follows:
1. We are given six 48-permutations $\sigma_0,...,\sigma_5\in S_{48}$.
2. We have to find an array $A$ of length 48 that satisfies some checks $H^* (A[i_0:i_1]) = h_i$, where $H^*$ is the hash chain function already seen in Seth, and $i_0, i_1, h_i$ are given indices and hashes.
3. We have to find a word in $\sigma \in \langle \sigma_0, ..., \sigma_5\rangle$ (taken as a monoid, so inverse permutations are not allowed) such that $\sigma \cdot A = [0,...,0,1,...,1,...,5,...,5]$, i.e., the array $B$ of size 48 with $B_i = \left\lfloor{i/8}\right \rfloor$.

Step 2 can be solved by brute-forcing some of the hashes $h_i$ and using the fact that $A$ must be a permutation of $B$.

My solution to Step 3 is very brute-forcy, so I guess that there probably is a much cleaner way. Here it is anyway.
We note that $\sigma_i^4=1$ for all $0\leq i<6$ and that $\sigma_0\sigma_5=\sigma_5\sigma_0$, $\sigma_1\sigma_3=\sigma_3\sigma_1$, $\sigma_2\sigma_4=\sigma_4\sigma_2$. These relations mean that when searching for $\sigma$, we can add the following rules:
- No $\sigma_i$ appears more than three time,
- $\sigma_0$ always appear before $\sigma_5$,
- $\sigma_1$ always appear before $\sigma_3$,
- $\sigma_2$ always appear before $\sigma_4$.
These reduce the search space quite substantially. Then I used an $A^ * $-search using the following heuristic
$$h(\sigma) = d(\sigma\cdot A, B) - \alpha |\sigma|,$$
where $d$ is the Hamming distance, $|\sigma|$ is the word length of $\sigma$, i.e., the number of $\sigma_i$'s in the product to get $\sigma$, and $\alpha\in \mathbb{R^+}$ is an hyperparameter. The idea is to optimize for distance to the desired array $B$, while trying to keep the words small.

Using a grid-search on $\alpha$, I finally found a valid $\sigma$ of word length 74.

Here is my uncleaned $A^*$-search code:
```rust
use std::collections::BinaryHeap;

const DATA: [usize; 120] = [
    0, 2, 4, 6, 1, 3, 5, 7, 8, 32, 24, 16, 9, 33, 25, 17, 10, 34, 26, 18, 24, 26, 28, 30, 25, 27,
    29, 31, 4, 32, 44, 20, 3, 39, 43, 19, 2, 38, 42, 18, 16, 18, 20, 22, 17, 19, 21, 23, 6, 24, 42,
    12, 5, 31, 41, 11, 4, 30, 40, 10, 8, 10, 12, 14, 9, 11, 13, 15, 0, 16, 40, 36, 7, 23, 47, 35,
    6, 22, 46, 34, 32, 34, 36, 38, 33, 35, 37, 39, 2, 8, 46, 28, 1, 15, 45, 27, 0, 14, 44, 26, 40,
    42, 44, 46, 41, 43, 45, 47, 22, 30, 38, 14, 21, 29, 37, 13, 20, 28, 36, 12,
];

const RES: [usize; 48] = [
    5, 0, 0, 3, 3, 1, 4, 0, 4, 1, 0, 4, 0, 5, 4, 2, 3, 4, 0, 1, 5, 5, 1, 3, 2, 2, 1, 0, 1, 2, 2, 5,
    2, 4, 1, 1, 3, 2, 2, 3, 4, 4, 3, 0, 5, 5, 5, 3,
];

fn trans(s: [usize; 48], se: [usize; 48], x: usize) -> ([usize; 48], [usize; 48]) {
    let mut state = s;
    let mut seen = se;
    for inc in [0, 4, 8, 12, 16].iter() {
        let i = 20 * x + inc;
        let ds = &DATA[i..i + 4];
        let mut nstate = state;
        for j in 0..4 {
            seen[ds[j]] = 1;
            nstate[ds[j]] = state[ds[(j + 3) % 4]];
        }
        state = nstate;
    }
    (state, seen)
}

fn ev(s: [usize; 48], seen: [usize; 48]) -> usize {
    (0..48).filter(|&i| seen[i] == 1 && s[i] == (i / 8)).count()
}

fn astar(scale_len: usize) {
    let mut best = 0;
    let init = RES;
    let mut q = BinaryHeap::new();
    q.push((ev(init, [0; 48]), init, [0; 48], vec![]));

    loop {
        let (_e, s, seen, l) = q.pop().unwrap();
        for i in 0..6 {
            if l.len() > 0 {
                let ll = *l.last().unwrap();
                if ll == i {
                    continue;
                }
                if ll == 3 && i == 1 {
                    continue;
                }
                if ll == 4 && i == 2 {
                    continue;
                }
                if ll == 5 && i == 0 {
                    continue;
                }
            }
            let mut ns = s;
            let mut nseen = seen;
            for j in 1..4 {
                let r = trans(ns, nseen, i);
                ns = r.0;
                nseen = r.1;
                let ee = ev(ns, nseen);
                if best > 30 && ee < 25 {
                    continue;
                }
                if best > 40 && ee < 27 {
                    continue;
                }
                let e = ee - (scale_len * l.len()) / 10;
                let mut nl = l.clone();
                for _ in 0..j {
                    nl.push(i);
                }
                if ee == 48 {
                    println!("Sols is: {:?}", nl);
                    return;
                }
                if ee > best {
                    best = ee;
                }
                q.push((e, ns, nseen, nl));
            }
        }
    }
}

fn main() {
    astar(13);
}
```
