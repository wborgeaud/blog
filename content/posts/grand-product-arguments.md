---
title: "Grand product arguments"
date: 2023-08-28
description: ""
slug: ""
tags: [ cryptography, zero-knowledge proofs]
---


$\newcommand{\F}{\mathbb{F}}$ $\newcommand{\c}{\text{comm}}$ $\newcommand{\i}{\mathbf{i}}$ $\newcommand{\z}{\mathbf{z}}$ $\newcommand{\r}{\mathbf{r}}$ $\newcommand{\eq}{\widetilde{\text{eq}}}$

*HackMD version [here](https://hackmd.io/@wborgeaud/rk-gp0222).*

# Grand product arguments


Let $\F$ be a finite field and consider a vector $f = (f_0,\dots,f_{n-1})\in \F^n$, where $n=2^v$. 
Given some kind of commitment $\c_f$ to $f$ and a value $y\in\F$, we want to convince a verifier that the product of the elements of $f$ is $y$, $\prod f_i = y$.

In this note, I will describe different approaches to this problem using univariate polynomials as in Plonk or multivariate polynomials as in Quarks and Lasso.

## Using AIR constraints
This problem can be solved using univariate polynomials and AIR constraints. This is the approach taken in Plonk[^1].

Let $c_i=\prod_{j\leq i}f_j$ be the vector of cumulative products of $f$. The equality $\prod f_i = y$ is equivalent to $c_{n-1}=y$. Therefore, a protocol to prove this equality is to commit to both $f$ and $c$ and check the following AIR constraints

- $c_0 = f_0$,
- $c_{i+1}=c_i \cdot f_{i+1}$ for all $i<n-1$,
- $c_{n-1} = y$.

## Using GKR
This is the approach of [Tha13, 5.3.1][^2].

For $0\leq k \leq v$, we consider the vector $g_k$ of size $2^k$ given by 
$$
g_{k,i} = \prod_{i\cdot 2^{v-k}\leq j < (i+1)\cdot 2^{v-k}} f_j.
$$
Note that $g_v=f$ and $g_0$ is the constant $y$. The vector $g_k$ can be seen as the $k$-th layer in the binary multiplication tree with leaves $f$.
These  vectors satisfy the relations
$$
g_{k,i} = g_{k+1, 2i} \cdot g_{k+1, 2i+1}.
$$
Seeing $g_k$ as a function $\\{0,1\\}^k \to \F$ instead, the relations become

$$
g _k(\i) = g _{k+1}(\i, 0) \cdot g _{k+1}(\i,1).
$$

Therefore, the MLEs $\tilde{g} _k$ satisfy

$$
\tilde{g} _k(\i) = \tilde{g} _{k+1}(\i, 0) \cdot \tilde{g} _{k+1}(\i,1).
$$

and thus for any $\z \in \F^k$ we have

$$
\tilde{g} _k(\z) = \sum _{\i \in \{0,1\}^k} \eq(\z, \i) \cdot \tilde{g} _{k+1}(\i, 0) \cdot \tilde{g} _{k+1}(\i,1).
$$

The evaluation of this sum can be proved using the sumcheck protocol. At the end of the protocol, the verifier needs to evaluate $\tilde{g}_{k+1}$ at $(\r,0)$ and $(\r, 1)$ for a random $\r \in \F^k$. 

The trick to do so efficiently is to consider the degree one univariate polynomial $h(t)=\tilde{g} _{k+1}(\r, t)$ for $t\in \F$. We have 

$$
h(0) = \tilde{g} _{k+1}(\r, 0) \ \text{ and } \ h(1) = \tilde{g} _{k+1}(\r, 1)
$$

therefore to send $h$ it is sufficient to send $\tilde{g} _{k+1}(\r, 0)$ and $\tilde{g} _{k+1}(\r, 1)$ (which are anyways required by the verifier). Then the verifier sends a random $u\in \F$ and uses the sumcheck protocol to check that

$$
h(u) = \tilde{g} _{k+1}(\r, u).
$$

Therefore, proving an opening $\tilde{g} _k(\z)$ can be reduced to a sumcheck argument and an opening $\tilde{g} _{k+1}(\r, u)$.

The strategy to prove $\prod f_i = g_0 = y$ is then clear:

- Reduce the evalutation proof $g_0 = y$ to a sumcheck argument and an evaluation $\tilde{g} _1(\r_1)$.
- For $k=1,\dots, v-1$, reduce the evalutation proof $\tilde{g} _k(\r_k)$ to a sumcheck argument and an evaluation $\tilde{g} _{k+1}(\r _{k+1})$.
- The last evaluation $\tilde{g} _v(\r _v)=\tilde{f}(\r _v)$ is proved using the commitment to $f$.

### Costs 
- **Prover**: A sumcheck argument costing $O(2^k)$ for $k=0\dots v-1$ and an evaluation proof for $f$, so in total $O(n) + \text{ prover cost of evaluation proof}$. The commited polynomial is $f$ of size $n$.
- **Verifier**: A sumcheck argument costing $O(k)$ for $k=0\dots v-1$ and an evaluation proof for $f$, so in total $O(v^2) + \text{ verifier cost of evaluation proof}$.
- **Proof size**: A sumcheck argument of size $O(k)$ for $k=0\dots v-1$ and an evaluation proof for $f$, so in total $O(v^2) + \text{ size of evaluation proof}$.

## Quarks
This is the approach of [SL20, Section 5][^3].

Instead of using $v+1$ different functions $\\{g _k: \\{0,1\\}^k \to \F \\} _{k=0}^v$, we can pack them into a single function $g: \\{0,1\\}^{v+1} \to \F$ given by

$$
g(1^l, 0, x) = g _{v-l}(x) \text{  for } x\in \\{0,1\\}^{v-l},
$$

and $g(\mathbf{1})=0$. Note that $g(0, x) = g_v(x) = f(x)$ for $x\in \\{0,1\\}^v$ and $g(1^v, 0) = g_0 = y$. Furthermore, the relation between the adjacent functions $g_k$ and $g_{k+1}$ becomes
$$
g(1, x) = g(x,0)\cdot g(x, 1) \text{ for } x\in \\{0,1\\}^v.
$$
Let $h(x) = g(1,x)-g(x,0)\cdot g(x, 1)$ for $x\in \{0,1\}^v$, then $\tilde{h}$ is the zero polynomial, which we can check with the usual zero-check
$$
0 = h(\tau) = \sum_{x\in \\{0,1\\}^v} \eq(\tau, x) \left(g(1,x)-g(x,0)\cdot g(x, 1)\right),
$$
where $\tau$ is a random verifier challenge, which is proved with a sumche
Therefore, the product $\prod f = y$ can be proved by commiting to $\tilde{g}$ and 
- using the sumcheck argument to prove $h(\tau)=0$,
- prove $g(0, x) = f(x)$ by checking $\tilde{g}(0,\gamma)=\tilde{f}(\gamma)$ for a random $\gamma$,
- open $\tilde{g}(1^v, 0)= \prod f = y$.

### Costs 
- **Prover**: A sumcheck argument costing $O(n)$ and evaluation proofs for $g$ and $f$, so in total $O(n) + \text{ prover cost of evaluation proofs}$. The commited polynomials are $f$ of size $n$ and $g$ of size $2n$.
- **Verifier**: A sumcheck argument costing $O(v+1)$ and evaluation proofs for $g$ and $f$, so in total $O(v) + \text{ verifier cost of evaluation proofs}$.
- **Proof size**: A sumcheck argument of size $O(v)$ and evaluation proofs for $g$ and $f$, so in total $O(v) + \text{ size of evaluation proofs}$.

Note that compared to GKR, the verifier cost and proof size go from quadratic in $v$ to linear in $v$, at the cost of more and larger evaluation proofs.

## Hybrid approach
This is the approach of [SL20, Section 6][^3], also used in Lasso[^4].

We can get the best of both approaches by combining them. Fix a number $1\leq \ell \leq v$, we use the Quarks approach for the first $\ell+1$ layers $\{g _k\} _{k=0}^{\ell}$ and the GKR approach for the last $v-l$ layers $\{g _k\} _{k=\ell+1}^{v}$. Concretely, this means that in the Quarks protocol, we instead have $g(0,x)=g _{\ell}(x)$ for all $x\in \\{0,1\\}^{\ell}$, which we check by evalutating at a random value $\gamma$, $\tilde{g}(0,\gamma)=\tilde{g} _{\ell}(\gamma)$. 

The evaluation $\tilde{g} _{\ell}(\gamma)$ is computed using the GKR protocol, by reducing it to a sumcheck argument and an evaluation of $\tilde{g} _{\ell +1}$, and so on until an evaluation of $\tilde{g} _v = \tilde{f}$.

### Costs 
- **Prover**: $O(2^\ell)$ for Quarks + $O(\sum_{k=\ell+1}^v 2^k)$ for GKR, so $O(n)$ in total, plus commitments to $f$ of size $n$ and $g$ of size $2^{\ell+1}$.
- **Verifier**: $O(\ell)$ for Quarks + $O(\sum_{k=\ell+1}^v k)=O((v-\ell)\cdot v)$, so $O(\ell + (v-\ell)\cdot v)$ in total, plus cost of evaluation proofs.
- **Proof size**: Similarly to the verifier costs, $O(\ell + (v-\ell)\cdot v)$ in total, plus size of evaluation proofs.

For example, setting $\ell = v - 3\log v$, the proof size is $O(v - 3\log v +3v \log v) = O(3v \log v)$ which is better than the proof size of $O(v^2)$ when using only GKR for large enough $v$. This comes at the cost of commiting to $g$ of size $2^{v - 3\log v + 1} = \frac{2n}{v^3}$, which is much smaller than $2n$, the corresponding size of $g$ when using only Quarks.

[^1]: https://eprint.iacr.org/2019/953
[^2]: https://eprint.iacr.org/2013/351
[^3]: https://eprint.iacr.org/2020/1275
[^4]: https://eprint.iacr.org/2023/1216
