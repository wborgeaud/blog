---
title: "The Walsh–Hadamard transform"
date: 2023-06-27
description: ""
slug: ""
tags: [ math, polynomials]
---

In the ZKP world, we often use the Fast Fourier Transform (FFT) to go from univariate polynomials to their evaluations on a subgroup. The FFT has a less notorious analogue for multilinear polynomials: the Walsh–Hadamard transform (WHT). In this post, I'll describe the WHT and explore its applications.

## Univariate polynomials
Let $\mathbb{F}$ be a finite field and let $H<\mathbb{F}^*$ be a multiplicative subgroup of size $n=2^v$. Given a polynomial $f\in \mathbb{F}[X]^{<n}$ of degree less than $n$, we can use the FFT to compute its evaluation on $H$:

$$
\text{FFT}(f) = [f(h)]_{h\in H}.
$$

Therefore, the FFT can be seen as a map
$$
\text{FFT} \colon \ \mathbb{F}[X]^{<n} \longrightarrow \mathbb{F}^H.
$$
The codomain of this map $\mathbb{F}^H$ has an elementary structure of $\mathbb{F}$-algebra given by pointwise addition and multiplication[^1]. On the other hand, the space $\mathbb{F}[X]^{<n}$ doesn't have an obvious $\mathbb{F}$-algebra structure. However, we can identify it with the algebra of polynomials modulo $Z_H(X)=\prod_{h\in H} \left(X-h\right)=X^n-1$ and then
$$
\text{FFT} \colon \ \mathbb{F}[X]^{<n} \cong \frac{\mathbb{F}[X]}{Z_H(X)} \longrightarrow \mathbb{F}^H.
$$
is an isomorphism of $\mathbb{F}$-algebras. In other words, for any two polynomials $f,g \in \mathbb{F}[X]^{<n}$, the following holds
$$
\text{IFFT}\left(\text{FFT}(f)\cdot\text{FFT}(g)\right) = f(X)\cdot g(X) \mod X^n=1.
$$

What does this polynomial look like? It's the polynomial with $i$-th coefficient
$$
\sum_{j+k \equiv i \mod n} f_j g_k = \sum_{j+k = i} f_j g_k + \sum_{j+k = i+n} f_j g_k.
$$
In particular, if both $f$ and $g$ have degree $<n/2$, it is exactly $f(X)g(X)$.

## Multilinear polynomials
In the multivariate world, univariate polynomials of degree $<n$ are replaced with the space of multilinear polynomials $\mathbb{F}[X_0,\dots,X_{v-1}]^{\preceq 1}$ and the group $H$ is replaced with the cube $\\{0, 1\\}^v$. So what replaces the FFT? 

It is called the Walsh–Hadamard transform
$$
\text{WHT}(f) = \left[f(\mathbf{z})\right]_{\mathbf{z} \in \\{0,1\\}^v}
$$

and it can be seen as a map

$$
\text{WHT}\colon \ \mathbb{F}[X_0,\dots,X_{v-1}]^{\preceq 1} \longrightarrow \mathbb{F}^{\\{0,1\\}^v}.
$$

As with the FFT, the codomain is an $\mathbb{F}$-algebra, but the domain doesn't have a canonical $\mathbb{F}$-algebra structure. This time we can identify it with polynomials modulo the relations $X_i^2 = X_i$ and then
$$
\text{WHT}\colon \ \mathbb{F}[X_0,\dots,X_{v-1}]^{\preceq 1} \cong \frac{\mathbb{F}[X_0,\dots,X_{v-1}]}{\left(X_0^2-X_0,\dots,X_{v-1}^2-X_{v-1}\right)} \longrightarrow \mathbb{F}^{\\{0,1\\}^v}.
$$
is an isomorphism of $\mathbb{F}$-algebras. In other words, given two polynomials $f,g \in \mathbb{F}[X_0,\dots,X_{v-1}]^{\preceq 1}$, the following holds
$$
\text{IWHT}\left(\text{WHT}(f)\cdot\text{WHT}(g)\right) = f(X)\cdot g(X) \mod X_i^2=X_i \ \forall i=0,\dots,v-1.
$$

What does this polynomial look like? Let's write 
$$
f(X_0,\dots,X_{v-1}) = \sum_{i=0}^{n-1} f_i \mathbf{X}^{\mathbf{bits}(i)}
$$
with
$$
\mathbf{X}^{\mathbf{bits}(i)} = X_0^{i_0}\cdots X_{v-1}^{i_{v-1}} \ \text{ and } \ i=\sum_{k=0}^{v-1} i_k 2^k.
$$
Then it is easy to see that 
$$
\mathbf{X}^{\mathbf{bits}(i)} \cdot \mathbf{X}^{\mathbf{bits}(j)} = \mathbf{X}^{\mathbf{bits}(i\vee j)} \mod X_i^2=X_i \ \forall i=0,\dots,v-1,
$$
where $\vee$ denotes the biwise OR operation. Therefore, $\text{IWHT}\left(\text{WHT}(f)\cdot\text{WHT}(g)\right)$ is the polynomial $h(X_0,\dots,X_{v-1})$ with
$$
h_i = \sum_{j\vee k = i} f_j g_k.
$$
So the WHT gives a way to compute convolutions using the bitwise OR operation!

It is natural to ask if the same can be done with the bitwise AND and XOR operations. AND is easy, we can just use the fact that $j \wedge k = \\, \sim(\sim j \ \vee \sim k)$ (where $\sim$ is the bitwise NOT) and reuse the convolution for OR.

For XOR, we observe that if we evaluate the multilinear polynomials on $\\{-1,1\\}^v$ instead, the relations become $X_i^2=1 \ \forall i$, and with these relations we have
$$
\mathbf{X}^{\mathbf{bits}(i)} \cdot \mathbf{X}^{\mathbf{bits}(j)} = \mathbf{X}^{\mathbf{bits}(i\oplus j)} \mod X_i^2=1 \ \forall i=0,\dots,v-1.
$$
So we can get convolution with XOR using the _special_ WHT:  
$$\text{WHT}_s(f) = \left[f(\mathbf{z})\right] _{\mathbf{z} \in \\{-1,1\\}^v}.$$

## Computing the WHT
Computing the WHT is surpisingly simple. Let $f\in\mathbb{F}[X_0,\dots,X_{v}]^{\preceq 1}$ be a multilinear polynomial on $v+1$ variables. Write it as
$$
f(X_0,\dots,X_v) = f_l(X_0,\dots,X_{v-1}) + f_r(X_0,\dots,X_{v-1})\cdot X_v,
$$
where $f_l,f_r\in\mathbb{F}[X_0,\dots,X_{v-1}]^{\preceq 1}$ have coefficients the left half (resp. right half) of the coefficients of $f$. For $\mathbf{z}\in \\{0,1\\}^v$, we then have
$$
f(\mathbf{z}, 0) = f_l(\mathbf{z}) \ \text{ and } \ f(\mathbf{z}, 1) = f_l(\mathbf{z}) + f_r(\mathbf{z}).
$$
Since the WHT is linear, there is a matrix $\mathbf{H}_{v+1}$ such that $\text{WHT}(f) = \mathbf{H} _{v+1} \cdot f$. It is obvious that $\mathbf{H} _0=[1]$, and the previous equation shows that
$$
\mathbf{H} _{v+1} = \begin{bmatrix}
\mathbf{H}_v & 0 \\\\
\mathbf{H}_v & \mathbf{H}_v
\end{bmatrix}.
$$

$\mathbf{H} _{v+1} \cdot f$ can be computed in time $O(n\log n)$ using the recursive formula
$$
\mathbf{H} _{v+1} \cdot f = \begin{bmatrix}
\mathbf{H}_v \cdot f_l \\\\
\mathbf{H}_v \cdot (f_l + f_r)
\end{bmatrix}.
$$
The inverse of $\mathbf{H}_v$ can easily be computed with
$$
\mathbf{H} _{v+1}^{-1} = \begin{bmatrix}
\mathbf{H}_v^{-1} & 0 \\\\
\mathbf{H}_v^{-1} & \mathbf{H}_v^{-1}
\end{bmatrix}.
$$
which gives a $O(n\log n)$ algorithm for the IWHT.

The special WHT is similar; we have $\text{WHT}_s(f) = {}_s \mathbf{H}_v \cdot f$ with the recursive formula
$$
{}_s \mathbf{H} _{v+1} = \begin{bmatrix}
{}_s \mathbf{H}_v & -{}_s \mathbf{H}_v \\\\
{}_s \mathbf{H}_v & {}_s \mathbf{H}_v
\end{bmatrix}.
$$

## Programming the WHT
All this stuff is well known in the competitive programming community. The WHT can be used to solve problems such as
> Let $P$ be the set of prime numbers and let $$S(n) = \text { number of ways to write } n=\bigvee_{i=1}^{10} p_i, \ p_i\in P \ \forall i.$$
Compute $\sum_{n=0}^{10^5} S(n)$.

And here is a solution in Sage
```python
N = 10^5
N_next_pow2 = 2^int(N).bit_length()

def WHT(f):
    n = len(f)
    if n==1:
        return f
    else:
        f0 = f[:n//2]
        f1 = f[n//2:]
        s = [x+y for x,y in zip(f0,f1)]
        return WHT(f0) + WHT(s)

def IWHT(f):
    n = len(f)
    if n==1:
        return f
    else:
        f0 = f[:n//2]
        f1 = f[n//2:]
        s = [y-x for x,y in zip(f0,f1)]
        return IWHT(f0) + IWHT(s)

def or_convolution(f, g):
    return IWHT([x*y for x,y in zip(WHT(f), WHT(g))])

f = [0 for _ in range(N_next_pow2)]
for p in primes(N_next_pow2):
    f[p] = 1

F = f[:]
for _ in range(9):
    F = or_convolution(F, f)

print(sum(F[i] for i in range(N+1)))
```

[^1]: Not to be confused with the group algebra $\mathbb{F}[H]$.

