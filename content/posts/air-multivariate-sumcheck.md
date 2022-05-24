---
title: "Proving AIRs with multivariate sumchecks"
date: 2022-05-21
description: ""
slug: ""
tags: [cryptography, zero-knowledge proofs]
---

*Algebraic Intermediate Representation* (AIR) is a powerful arithmetization that can be extended to *Randomized Air with Preprocessing* (RAP), which includes popular systems like PLONK. See [this great note](https://hackmd.io/@aztec-network/plonk-arithmetiization-air) by Ariel Gabizon for descriptions of these arithmetizations.

Another popular arithmetization is given by R1CS. Two categories of proving systems based on R1CS are those using multivariate techniques (e.g. [Spartan](https://eprint.iacr.org/2019/550)) and those using univariate techniques (e.g. [Marlin](https://eprint.iacr.org/2019/1047)).

To the best of my knowledge, every current AIR-based proving system uses univariate techniques. In this note, I'll discuss what a multivariate AIR-based proving system could look like.

## Differences between univariate and multivariate techniques

Before discussing AIR, let's focus on the restricted arithmetization *Trivial Air Representation* (TAR) where the next row values are not used in the constraint. 

Let $C \in \mathbb{F}[X_1,\dots,X_w]$ be a constraint polynomial, and assume we have $w$ columns of length $n$ (a power of 2) $f_1,\dots,f_w \in \mathbb{F}^n$. Every row satisfies $C\left(f_1[j],\dots,f_w[j]\right)=0$ and we want a succinct proof of this fact.  Here are examples of how one could do this using univariate or multivariate techniques.

###### Univariate techniques
Let $H < \mathbb{F}^*$ be a subgroup of order $n$. Look at the columns as functions $f_i: H \to \mathbb{F}$. Using the FFT, interpolate these functions to get polynomials $\hat{f}_i: \mathbb{F}\[X\]^{<n}$ and compute the polynomial $C(\hat{f}_1,\dots,\hat{f}_w)\in \mathbb{F}\[X\]^{<deg(C)n}$. This latter polynomial evaluates to $0$ on $H$, so we can compute its quotient $Q(X)$ with the vanishing polynomial on $H$: $Z_H(X) = X^n - 1$. 

Compute commitments of the polynomials $\hat{f}_1,\dots,\hat{f}_w,Q$ using your favorite univariate polynomial commitment scheme. Send these commitments to the verifier and receive a challenge $z \in \mathbb{F}$ in return. Send the evaluations $\hat{f}_1(z),\dots,\hat{f}_w(z),Q(z)$, along with their opening proofs, to the verifier. Finally, the verifier verifies the opening proofs and checks the equality
$$
C\left(\hat{f}_1(z),\dots,\hat{f}_w(z)\right)\stackrel{?}{=} Q(z)Z_H(z).
$$ 

###### Multivariate techniques
Let $v = \log n$, look at the columns as functions $f_i: \\{0,1\\}^v \to \mathbb{F}$ and compute the multilinear extensions $\tilde{f}_1,\dots,\tilde{f}_w \in \mathbb{F}[X_1,...,X_v]$. Let $F(x) = C\left(\tilde{f}_1(x),\dots,\tilde{f}_w(x)\right)$, by assumption the equality $F(x)=0$ holds for all $x \in \\{0,1\\}^v$. Define the polynomial 

$$
P(t) = \sum_{x \in \\{0,1\\}^v} F(x) \beta(t, x),
$$
where $\beta(t,x) = \prod _{i=1}^v (t_i x_i + (1-t_i)(1-x_i))$ is the multilinear polynomial such that $\beta(t,x)\ne 0$ iff $t=x$. $P(t)$ is a multilinear polynomial that evaluates to $0$ on $\\{0,1\\}^v$ and is therefore the zero polynomial. This is something we can prove to the verifier using the multivariate sumcheck protocol.

Commit to the polynomials $\tilde{f}_1,\dots, \tilde{f}_w$ using your favorite multivariate polynomial commitment scheme and send the commitments to the verifier. Then perform the multivariate sumcheck protocol to prove that $P(r)=0$ for a random $r\in \mathbb{F}^v$ chosen by the verifier (which implies that $P$ is the zero polynomial with high probability). In the last step of the sumcheck protocol, the verifier has to evaluate $F(z)\beta(r,z)$ for some random $z \in \mathbb{F}^v$. $\beta(r,z)$ can be evaluated in $O(v)$ and to evaluate $F(z)$, the prover opens $\tilde{f}_1(z),\dots, \tilde{f}_w(z)$ with which the verifier can compute $F(z) = C(\tilde{f}_1(z),\dots, \tilde{f}_w(z))$.


To summarize, the main differences between the univariate and multivariate techniques are
1. The columns are seen as functions from $H \subset \mathbb{F}^*$ in the univariate case and as functions from $\\{0,1\\}^v \subset \mathbb{F}^v$ in the multivariate case.
2. The columns are interpolated to polynomials of degree $<n$ in the univariate case and to multilinear polynomials in the multivariate case.
3. To check that the constraint $C$ evaluates to $0$ on every row, a quotient polynomial argument is used in the univariate case, whereas the multivariate sumcheck protocol, along with the $\beta(t,x)$ trick, is used in the multivariate case.

## Introducing *next row values*
To go from TAR to AIR, we just need to change the constraint $C$ to a $2w$-variate polynomial taking as inputs the $j$-th and $j+1$-th rows
$$
C\left(f_1[j],\dots,f_w[j], f_1[j+1],\dots,f_w[j+1]\right)=0, \forall \ 0\leq j < n,
$$
where $j+1$ is taken modulo $n$.

In the univariate setting, the proof system for TARs can be extended to AIRs as follows. Let $g\in H$ be a generator of $H$ and let the correspondence between rows and $H$ be given by $j$-th row $\leftrightarrow$ $g^j$, i.e., $f_i[j] = \hat{f}_i(g^j)$. Then, for every $h\in H$, the next row value of $\hat{f}_i(h)$ is $\hat{f}_i(gh)$. 

With that, we can modify the univariate proof system for TAR to accommodate for the next row values. The polynomial $Q(X)$ is now computed as the quotient of $C\left(\hat{f}_1(X),\dots,\hat{f}_w(X),\hat{f}_1(gX),\dots,\hat{f}_w(gX)\right)$ and $Z_H(X)$, and the column polynomials are opened at $z$ and $gz$, so that the verifier can check
$$
C\left(\hat{f}_1(z),\dots,\hat{f}_w(z),\hat{f}_1(gz),\dots,\hat{f}_w(gz)\right)\stackrel{?}{=} Q(z)Z_H(z).
$$ 

## Generalizing AIRs using endomorphisms
Let $R$ be the set of rows in a TAR and let $\sigma: R \to R$ be a function. We can extend TARs by using the constraint
$$
C\left(f_1(r),\dots,f_w(r), f_1(\sigma r),\dots,f_w(\sigma r)\right)=0, \forall  r \in R.
$$
We'll call this arithmetization an *Endomorphism AIR Representation* (EAR). 

The endomorphism $\sigma$ on $R$ induces another endomorphism, that we also call $\sigma$, on functions $f: R \to \mathbb{F}$ by setting $(\sigma f)r = f(\sigma r)$ for all $r\in R$. This endomorphism can further be extended to polynomials using interpolation on $R$, i.e., $\sigma \hat{f} = \widehat{\sigma f}$.

AIRs can be recovered in this context by setting $R = H = \langle g \rangle$ and $\sigma = \mu_g$, the multiplication by $g$. Going through the previous section with this viewpoint, we observe that the only property of $\sigma$ used in the proving system for AIR is that there is an extension $\bar{\sigma} : \mathbb{F} \to \mathbb{F}$ of $\sigma$ that is efficient to compute and such that $(\sigma \hat{f})z = \hat{f}(\bar{\sigma} z)$ for all $z\in \mathbb{F}$. In the univariate context, $\bar{\sigma}$ is also $\mu_g$, the multiplication by $g$ with domain $\mathbb{F}$.

Note that, similarly to how AIRs can also be extended to also use the $j+2$-th row values in $C$ (or in general any shifted row values), EARs can be extended to use more than one endomorphism in the definition of $C$.

Furthermore, note that this construction can also be generalized to extend RAPs.

###### How to choose $\sigma$?
The choice of $\sigma$ can dramatically impact the expressiveness of the arithmetization. For example, setting $\sigma = \mathrm{id}_R$ gives a TAR, a rather useless arithmetization, and as seen previously setting $R = H, \sigma = \mu_g$ gives a regular AIR, a very powerful arithmetization.

Assuming for the moment that $\sigma$ is a permutation, a measure of expressiveness is the size of the largest cycle of $\sigma$, when seeing the permutation as a [product of cycles](https://en.wikipedia.org/wiki/Permutation#Cycle_notation). Interpreting an AIR as the repeated application of a function, the size of the largest cycle gives the maximum number of times the function can be applied.

## Back to the multivariate setting
In the multivariate setting, the row domain is $R = \\{0, 1\\}^v$. So to get an EAR, we first need to set an endomorphism $\sigma : \\{0, 1\\}^v \to \\{0, 1\\}^v$. As noted previously, to make the proving system work, we need a $\sigma$ that can be extended to some $\bar{\sigma}: \mathbb{F}^v \to \mathbb{F}^v$ such that $(\sigma \tilde{f})z = \tilde{f}(\bar{\sigma} z)$ for all $z \in \mathbb{F}^v$ and functions $f: \\{0, 1\\}^v \to \mathbb{F}$.

A set of endomorphisms of $\mathbb{F}^v$ (which are actually permutations) satisfying this condition is given by compositions of bit-flips and coordinate permutations. Formally, they are given by
$$
L_v = \\{ \tau \theta \ \mid \ \tau \in S_v, \ \theta \in (\mathbb{Z}/2\mathbb{Z})^v \\},
$$
where $S_v$ is the symmetric group on $v$ elements acting on $\mathbb{F}^v$ by permuting coordinates and $\theta = (\theta_1,\dots,\theta_v)$ acts on $x = (x_1, \dots, x_v)$ coordinate-wise by sending $x_i$ to $x_i$ if $\theta_i = 0$ and to $1-x_i$ if $\theta_i = 1$. It is clear that every element of $L_v$ restricts to a permutation on $\\{0, 1\\}^v$ and can be efficiently computed in $O(v)$ time.

The main "result" of this note can thus be stated as follows

> For every $\sigma \in L_v$ and $C\in \mathbb{F}[X_1,\dots,X_{2w}]$, there is an efficient proving system based on the multivariate sumcheck protocol for the EAR on $n = 2^v$ rows, $w$ columns, endomorphism $\sigma$, and constraint $C$. 

Here is a description of the full protocol, using the same notations as before:
1. Commit to the multilinear polynomials $\tilde{f}_1,\dots,\tilde{f}_w$ and send the commitments to the verifier.
2. Let $F(x) = C(\tilde{f}_1(x),\dots,\tilde{f}_w(x),\sigma\tilde{f}_1(x),\dots,\sigma\tilde{f}_w(x))$ and let $r\in \mathbb{F}^v$ be a random challenge sent by the verifier. Run the sumcheck argument for $P(r) = 0$, with $P(t) = \sum\_{x \in \\{0,1\\}^v} F(x) \beta(t, x)$.
3. In the last step of the sumcheck protocol, the verifier has to compute $F(z)$. The prover sends the openings $\tilde{f}_1(z),\dots, \tilde{f}_w(z), \tilde{f}_1(\sigma z),\dots,\tilde{f}_w(\sigma z)$ along with their opening proofs. The verifier then verifies the opening proofs and computes the value of
$$
F(z) = C(\tilde{f}_1(z),\dots,\tilde{f}_w(z),\sigma\tilde{f}_1(z),\dots,\sigma\tilde{f}_w(z)) = C(\tilde{f}_1(z),\dots,\tilde{f}_w(z),\tilde{f}_1(\sigma z),\dots,\tilde{f}_w(\sigma z))
$$
to conclude the sumcheck protocol.
4. The sumcheck protocol shows that (up to reasonable soundness) $P(t)$ is the zero polynomial, which implies that $F(x)=0$ for all $x\in \\{0,1\\}^v$, which is equivalent to the EAR statement.


###### How good are these permutations?
The sad thing is that the permutations in $L_v$ are not very good, measured in terms of their maximum cycle length. Denote by $M(v)$ the maximum cycle length over elements of $L_v$ and denote by $N(v)$ the number of length $M(v)$ cycles in a permutation achieving this maximum. Experiments give the following values of $M$ and $N$:

{{<table "table table-striped table-bordered nohead">}}
| | | | | | | | | | | | 
|------|---|-|-|-|-|-|-|-|-|-|-
$v$ | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19  
$M(v)$ | 60 | 60 | 120 | 120 | 168 | 210 | 280 | 420 | 420 |  840
$N(v)$ | 12 | 30 | 24 | 48 | 72 | 108 | 216 | 216 | 540 |  432
$M(v)\cdot N(v)$ | 720 | 1800 | 2880 | 5760 | 12096 | 22680 | 60480 | 90720 | 226800 |  362880
$n=2^v$ | 1024 | 2048 | 4096 | 8192 | 16384 | 32768 | 65536 | 131072 | 263144 |  524288
||||||||||||
{{</table>}}

So the bad news is that $M(v)$ is much smaller than $n$. The silver lining is that there are a lot of cycles achvieving $M(v)$ and so the number of elements in such cycles $M(v)\cdot N(v)$ is reasonably close to $n$.

###### EARs as "parallel" AIRs?
This suggests the following construction. Let $\sigma$ be a permutation with largest cycle of length $\mu = M(v)$ and $\eta = N(v)$ such cycles with supports $\Pi_1,\dots,\Pi_\eta \subset \\{0,1\\}^v$. 

Then, the EAR with endomorphism $\sigma$ and constraint $C$ contains $\eta$ copies of an AIR with $\mu$ rows and constraint $C$. It can thus be used to compute $\eta$ AIR on the row sets $\Pi_1,\dots,\Pi_\eta$ in parallel. 

There are a few issues with this construction:
- The constraint $C$ must also hold outside $\bigcup \Pi_i$. The cycles outside this set do not have length $\mu$ which can be problematic. One solution is to add a preprocessed selector polynomial $\mathbb{1}_{\bigcup \Pi_i}$ and multiply $C$ by this polynomial to filter out smaller cycles.
- One might want to use different constraints $C_1,\dots,C_\eta$ on the different row sets $\Pi_1,\dots,\Pi_\eta$. This can also be solved by adding preprocessed polynomials. Either $\eta$ selector polynomials taking binary values or one polynomial taking values $1$ to $\eta$.
- Public inputs should be a bit annoying to work with in this model.
- If implementing PLONK in this model, only rows belonging to the same cycle can be wired together.


###### Implementation
Coming soon.
