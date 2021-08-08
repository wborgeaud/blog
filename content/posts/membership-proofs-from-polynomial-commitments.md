---
date: 2020-04-16T13:57:25-07:00
title: "Membership proofs from polynomial commitments"
description: ""
tags: [cryptography, zero-knowledge proofs]
---

$$
\def\com{\mathbf{com}}
$$



Recently, Dan Boneh, Ben Fisch, Ariel Gabizon, and Zac Williamson (BFGW) published a [writeup](https://hackmd.io/@dabo/B1U4kx8XI) showing how to create **range proofs** from polynomial commitments. As a mental exercise, I wanted to see how to use polynomial commitments to create **membership proofs** instead. Membership proofs can be seen as a generalization of range proofs, if certain homomorphic properties hold (that's something I learned first from [this](https://link.springer.com/chapter/10.1007/978-3-540-89255-7_15) article). For example for Pedersen commitments, we have:


$$
\\{g^zh^r \vert z\in [0,u^l), r\in \mathbb{F}\\} = \left\\{\prod_{i=0}^{l-1} \left(g^{u^i}\right)^{z_i}h^{r_i} \big\vert z_i\in[0,u), r_i\in \mathbb{F} \right\\},
$$


i.e., $C$ is a commitment to a value in $[0, u^l)$ if and only if it is the product of commitments $C_i$ (with base $g^{u^i}$ ) of values in the set $[0,u)$.

Since polynomial commitments are also homomorphic (at least the one from [KZG](https://www.iacr.org/archive/asiacrypt2010/6477178/6477178.pdf)), a membership proof protocol using polynomial commitments automatically yields a range proof protocol.

Note that a range proof can also be build from a set membership proof just by seeing a range $[0, 2^l)$ as a set. This is often inefficient but offers a simple solution for small $l$'s. I believe this is the way [Aztec](https://github.com/AztecProtocol/AZTEC/blob/master/AZTEC.pdf) does range proofs.

# The membership proof protocol

Let  $S\subset \mathbb{F}$. We want to build a commitment of $z\in S$ along with a zero-knowledge proof that $z\in S$. 

Let $\com_f$ be a KZG polynomial commitment of a degree 1 polynomial $f(X)$ with $f(0)=z$. Then
$$
X \ \vert \ g(X)=\prod_{r\in S} \left(f(X)-r\right).
$$
The polynomial $g(X)$ is of degree $|S|$ and can be computed either by direct calculation or by interpolation on  $|S|+1$ points. We denote $h(X)=\frac{g(X)}{X}$.

The public input is $\com_f$ and $S$. The protocol then goes as follows:

1. The Prover sends $\com_h$ to the Verifier.
2. The Verifier sends a random $\alpha \in \mathbb{F}^*$ to the Prover.
3. The Prover computes $f(\alpha), h(\alpha)$ and sends them to the Verifier along with opening proofs.
4. The Verifier checks that the openings are valid and that $\prod_{r\in S}(f(\alpha)-r) = h(\alpha)\alpha$.

##### Remarks

- $f(X)$ should be *randomly chosen* with the property that $f(0)=z$. Indeed, if $f(X)$ was easily guessable, e.g. $f(X)=X + z$, knowing $f(\alpha)$ would reveal $z$.
- The protocol is sound since by the properties of the KZG commitments and the Schwartz-Zippel lemma,  except with negligible probability, there exists polynomials $f(X), h(X)$ with $\prod_{r\in S}(f(X)-r) = h(X)X$ which implies that $f(0)\in S$, i.e., $\com_f$ is a commitment to a value in $z$. QED.
- As is, the protocol has a proof length of 3 group element: $\com_h$, $\text{open}(f(\alpha))$, $\text{open}(h(\alpha))$, and 2 field elements $f(\alpha), h(\alpha)$. The proving time is dominated by the computation of $g(X)$, and the verifier time is dominated by the product over $S$. There is maybe a way to batch the two openings to reduce the number of group elements by one.

# The derived range proof protocol

Let $z=\sum_{i=0}^{l-1}z_i2^i\in [0, 2^l)$ with $z_i\in [0,2)$ for all $i$. Using the membership proof protocol above, we get the following protocol:

1. The Prover builds linear polynomials $f_i(X)$ with $f_i(0)=z_i$ for all $i\in[0,l)$ and $\sum_{i=0}^{l-1}f_i(X)\cdot 2^i = f(X)$. He then sends $\\{\com_{f_i}\\}_{i=0}^{l-1}$ to the Verifier, and set $\com_f = \prod_{i=0}^{l-1}\com_{f_i}^{2^i}$ (where we use multiplicative notation in the group).
2. The Verifier checks that $\com_f = \prod_{i=0}^{l-1}\com_{f_i}^{2^i}$, where $\com_f$ is the public commitment to $z$. 
3. The Prover and Verifier run the membership proof protocol on $\\{\com_{f_i}\\}_{i=0}^{l-1}$ with $S=\\{0, 1\\}$.

##### Remarks

- The protocol works *mutatis mutandis* in an arbitrary base $u$. As $u$ gets larger, the Prover and Verifier time increase, but the proof length decreases.
- The proof length is $4l$ group elements and $2l$ field elements. This is very bad. In comparison, the BFGW scheme has constant proof length and Bulletproofs have logarithmic proof length. There is maybe a way to reduce the proof length to logarithmic size, but I think constant size is impossible without adding more structure (as BFGW does with roots of unity).
- The naive protocol of proving $z\in [0,u)$ by performing a membership proof on the set $[0,u)$ has constant size but very bad Prover and Verifier time. Nevertheless, if $u$ is small this might be a viable succinct range proof (but still worse than BFGW). 


*Thanks to Alin Tomescu for spotting a typo in an earlier version of this post.*
