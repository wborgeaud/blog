---
title: "The ECFFT algorithm"
date: 2021-08-07T00:57:25-07:00
description: ""
slug: ""
tags: [math, algorithms]
---
$$
\def\F{\mathbb{F}}
$$

# The ECFFT algorithm

This post is about [a recent paper](https://arxiv.org/abs/2107.08473) by Eli Ben-Sasson, Dan Carmon, Swastik Kopparty and David Levit. In this paper the authors present an amazing new generalization of the classic FFT algorithm that works in all finite fields. This post will give an overview of the algorithm and a simple implementation in Sage. I highly recommend reading the paper for more details and background. 

## The classic FFT algorithm
Let $p$ be a prime number, $n=2^k$ with $n \mid p-1$, $\langle w \rangle = H < \F_p^*$ a subgroup of size $n$. The classic FFT algorithm can be used to evaluate a polynomial $P(X)=\sum_{i=0}^n a_i X^i$ of degree $<n$ on $H$ in $O(n\log n)$. Note that the naive algorithm of evaluating $P$ at every point of $H$ takes $O(n^2)$ operations.\
The FFT works by writing $P$ as 
$$P(X) = P_0(X^2) + XP_1(X^2)$$
where $P_0, P_1$ are the polynomials of degree $< n/2$ of even and odd coefficients of $P$. \
Thus, given the evaluation of $P_0$ and $P_1$ on $H^2$, we can recover the evaluation of $P$ on $H$ with $O(n)$ operations.

Now the crucial thing to note is that $H^2$ has half the size of $H$ since $H = -H$. Therefore, if we denote by $F$ the running time of the FFT, we have the following recurrence relation

$$ F(n) = 2F(n/2) + O(n)$$
from which we can deduce that $F(n) = O(n\log n)$.

## The ECFFT algorithm
The goal of the ECFFT algorithm is to generalize the FFT algorithm for finite fields that do not have a multiplicative subgroup of size $n$, i.e., fields $\F_p$ with $n \nmid p-1$.

The idea is both brillant and simple. Here's an overview:

1. Find an elliptic curve $E(\F_p)$ with $n \mid \\#E(\F_p)$. Let $G < E(\F_p)$ be a subgroup of size $n$, and $H$ a coset of $G$.
2. Let $\phi: E \to E'$ be an isogeny of degree $2$ such that $\phi(H)$ has half the size of $H$.
3. Use $\phi$ to decompose $P$ into two smaller polynomials $P_0,P_1$ and apply the ECFFT on $P_0,P_1$ using the elliptic curve $E'$ and the coset $\phi(H)$.

I'll now explain these steps in more details. I'll also give an implementation in Sage for the base field of the Secp256k1 curve, i.e., $\F_p$ with 

$$p = 115792089237316195423570985008687907853269984665640564039457584007908834671663.$$

```sage
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
F = GF(p)
```

### Finding a curve
We need to find a curve $E(\F_p)$ with $n \mid \\#E(\F_p)$. [This paper](https://arxiv.org/abs/1403.7887) gives algorithms to do so. Otherwise, a brute-force search also works reasonably well for small values of $n$.

Here's a script to find a curve by brute-force
```sage
def find_curve(n):
  while True:
      b = F.random_element()
      E = EllipticCurve(F, [1, b])
      if E.order() % n == 0:
        return E
n = 2^12
E = find_curve(n)
```
It can find a curve for $n=2^{12}$ in around an hour. (If someone know a faster implementation of Schoof's algorithm, please let me know!) \
Here's the curve I found

$$
E: y^2 = x^3 + x + 641632526086088189863104799840287255425991771106608433941469413117059106896
$$

### Choosing a coset
Let $G < E$ be a subgroup of size $n$. We choose a random coset[^1] $H$ of $G$.
```sage
gen = E.gens()[0]
G = (gen.order()//n) * gen
R = E.random_element()
H = [R + i*G for i in range(n)]
```
Finally, let $L$ be the projection of $H$ on $\F_p$. $L$ is going to be the set of size $n$ on which we'll be able to perform the ECFFT.
```sage
L = [h.xy()[0] for h in H]
```

### Finding an isogeny
We need an isogeny that halves the size of $H$. This is very simple to find in Sage:
```sage
def find_isogeny(E, H):
 for phi in E.isogenies_prime_degree(2):
    if len(set([phi(h) for h in H])) == len(H)//2:
      return phi
phi = find_isogeny(E, H)
```
On the $x$-coordinate of $E$, $\phi$ is given by the degree $2$ rational function $\psi(X) = u(X)/v(X)$.
```sage
psi = phi.x_rational_map()
u, v = psi.numerator(), psi.denominator()
```
From this we can get a new elliptic curve $E'$, which is the codomain of $\phi$, a new coset $\phi(H)$, and a new subset of $\F_p$ given by $\psi(L)$.

### Decomposing polynomials on $L$
Let $P$ be a polynomial of degree $<n$. Then there exist polynomials $P_0, P_1$ of degree $< n/2$ such that

$$
P(X) = (P_0(\psi(X)) + XP_1(\psi(X)))v(X)^{n/2-1}
$$
See Appendix A of the paper for a proof. The idea is to prove that the linear map $(P_0, P_1) \mapsto P$ from pairs of polynomials of degree $<n/2$ to polynomials of degree $<n$ is injective, and thus bijective since its domain and codomain have the same dimension as $\F_p$-vector spaces.

Computing the polynomials $P_0,P_1$ is not as straightforward as in the classic FFT. However, it is easy to go from the evaluation of $P$ on $L$ to the evaluations of $P_0$ and $P_1$ on $\psi(L)$, and vice versa.\
Indeed, given $s_0, s_1\in L$ with $\psi(s_0)=\psi(s_1)=t\in \psi(L)$, we have the following linear relation (letting $q=n/2 -1$)

$$
\begin{bmatrix}
P(s_0) \\\\\\
P(s_1)
\end{bmatrix} =
\begin{bmatrix}
v(s_0)^q & s_0v(s_0)^q \\\\\\
v(s_1)^q & s_1v(s_1)^q 
\end{bmatrix}
\begin{bmatrix}
P_0(t) \\\\\\
P_1(t)
\end{bmatrix} 
$$
The matrix can be seen to be inversible, therefore we can easily go from $(P(s_0),P(s_1))$ to $(P_0(t), P_1(t))$ and back. This gives the following efficient correspondance that we'll use later:

$$\text{Evaluation of $P$ on $L$ $\longleftrightarrow$ Evaluations of $P_0, P_1$ on $\psi(L)$.}$$

What's more, the matrix doesn't depend on $P$, so we can precompute it and reuse it for all instantiations of the ECFFT.
```sage
inverse_matrices = []
nn = n // 2
q = nn - 1
for j in range(nn):
    s0, s1 = L[j], L[j + nn]
    assert psi(s0) == psi(s1)
    M = Matrix(F, [[v(s0)^q,s0*v(s0)^q],[v(s1)^q, s1*v(s1)^q]])
    inverse_matrices.append(M.inverse())
```

### The EXTEND operation
The final piece of the puzzle is the EXTEND operation. Let $S, S'$ be the elements of $L$ at even and odd indices respectively, so that $L = S \cup S'$.
```sage
S = [L[i] for i in range(0, n, 2)]
S_prime = [L[i] for i in range(1, n, 2)]
```
Given the evaluation of a polynomial $Q$ of degree $<n/2 -1$ on $S$, the EXTEND operation computes the evaluation of $Q$ on $S'$. The main result of the paper is that there is an $O(n\log n)$ algorithm for EXTEND. Note that a naive algorithm that would recover the coefficients of $Q$ by Lagrange interpolation on $S$ and then evaluate on $S'$ takes $O(n^2)$.

The algorithm works as follows.\
If $\\#S = \\#S' = 1$, $Q$ is constant and the evaluation of $Q$ on $S$ and $S'$ is the same. \
Otherwise, deduce from the evaluation of $Q$ on $S$ the evaluations of $Q_0,Q_1$ on $\psi(S)$, as in the previous section. Then apply the EXTEND operation twice to get the evaluations of $Q_0,Q_1$ on $\psi(S')$. Finally, recover the evaluation of $Q$ on $S'$ as in the previous section.

```sage
def extend(Q_evals, S, S_prime, matrices, inverse_matrices):
  n = len(Q_evals)
  nn = n // 2
  if n == 1:
      return Q_evals
  Q0_evals = []
  Q1_evals = []
  q = nn - 1
  for j in range(nn):
      s0, s1 = S[j], S[j + nn]
      y0, y1 = Q_evals[j], Q_evals[j + nn]
      Mi = inverse_matrices[n][j]
      q0, q1 = Mi * vector([y0, y1])
      Q0_evals.append(q0)
      Q1_evals.append(q1)

  Q0_evals_prime = extend(Q0_evals, [psi(s) for s in S], [psi(s) for s in S_prime], matrices, inverse_matrices)
  Q1_evals_prime = extend(Q1_evals, [psi(s) for s in S], [psi(s) for s in S_prime], matrices, inverse_matrices)

  return [
    M * vector([q0, q1])
     for M, q0, q1 in zip(matrices[n], Q0_evals_prime, Q1_evals_prime)
    ]
```

The recurrence relation for the running time is the same as in the classic FFT and gives a running time of $O(n\log n)$.

### Evaluating polynomials on $L$
The algorithm for the EXTEND operation given in the last section is the building block for many efficient algorithms given in the paper.\
One of them is an algorithm for the ENTER operation, which computes the evaluation of a polynomial $P$ of degree $<n$ on $L$. This is analogous to what we did in the classic FFT.

The algorithm is very simple. Decompose $P(X)$ into its low and high coefficient $U(X) + X^{n/2}V(X)$. Call ENTER on $U$ and $V$ on $S$ to get the evaluations of $U,V$ on $S$. Then call EXTEND twice to get the evaluations of $U,V$ on $S'$. Since $L = S \cup S'$, we have the evaluation of $U,V$ on $L$ and can deduce the evaluation of $P$ on $L$.

Note that the recurrence relation for the running time is now 

$$
F(n) = 2F(n/2) + O(n\log n)
$$
since we have to call EXTEND in the recursion step. Therefore the running time $F(n) = O(n\log^2 n)$ is slightly worse than for the classic FFT.

## Running it outside of Sage
As this post (hopefully) shows, these algorithms are very simple to implement in a computer algebra system like Sage. However, Sage being awfully slow, these quick implementations are far from fast. \
The cool thing about these algorithms is that for a given field $\F_p$, we can precompute all the necessary data in Sage: all the sets $L, S, S'$ and the (inverse) matrices used in the EXTEND algorithm.\
Once we have these precomputed data, the algorithms only use basic operations on $\F_p$, i.e., additions and multiplications. 

Therefore, the actual algorithms can easily be implemeneted in fast languages like C++ or Rust, without having to implement all the elliptic curve and isogenies machinery in these languages.



[^1]: See section 4.2 of the paper for a more careful choice of the coset. A random one is fine with our parameters.