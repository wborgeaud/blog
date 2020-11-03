---
date: 2020-04-22T13:57:07-07:00
title: "Anomalous Curves Part 2: p-adic niceties"
description: ""
slug: "" 
tags: [elliptic curves, cryptography]
---

$$
\def\F{\mathbb{F}}
$$

$$
\def\Q{\mathbb{Q}}
\def\F{\mathbb{F}}
\def\Z{\mathbb{Z}}
$$



This is part two of the series on anomalous curves. Go [here]({{< ref "/anomalous-curves-1.md" >}}) for part one.

Today, I'll give a sketch of the construction of Smart's attack. This attack combines two elliptic curve tools:

- The **reduction map** of an elliptic curve over a local field.
- The **formal group** of an elliptic curve.

I will focus on the first one, and leave the details of the second for another post.

All the content is taken from these two sources:

- *Silverman*, The Arithmetic of Elliptic Curves,
- *Monnerat*, Computation of the discrete logarithm on elliptic curves of trace one. 

# Elliptic curves over <s>local fields</s> $p$-adic numbers

Let $K$ be a local field, $R$ its ring of integers, and $k$ its residue field. If you want to continue with this level of generality, you can read Chapter VII of Silverman's book. Otherwise, we'll continue with
$$
K = \Q_p, R = \Z_p, k = \F_p.
$$
In number theory and cryptography, we start with a curve $\tilde{E}(\F_p)$ (we'll see why the $\texttt{tilde}$ later). $\F_p$ is nice and all, but kind of restricted. $\Q_p$ on the other hand is a tractable field of characteristic $0$ with some nice properties. So it is natural to ask whether we can find a curve $E(\Q_p)$ with a way to go back and forth to $\tilde{E}(\F_p)$.

It turns out there is a very simple way to do so! In particular, there exists an exact sequence of groups
$$
0 \to E_1(\Q_p) \to E(\Q_p) \xrightarrow{\pi} \tilde{E}(\F_p) \to 0.
$$
If $\tilde{E}: y^2 = x^3 + ax +b$, then $E: y^2 = x^3 + (a+O(p))x + (b+O(p))$. Now $\pi$ is rather simple. Given $[x:y:z]\in E(\Q_p)$, there exists $n$ such that $p^n x, p^n y, p^n z \in \Z_p$ and one of the three is not in $p\Z_p$. So without loss of generality, $P = [x:y:z]$ with $x,y,z\in \Z_p$ and one of them not in $p\Z_p$. Then, we use the canonical map $\Z_p\to\F_p$ to send $P$ to $\tilde{P}=[\tilde{x}, \tilde{y}, \tilde{z}]$, i.e., we just reduce all the coordinates modulo $p\Z_p$. It is easy to see that $\tilde{P} \in \tilde{E}$, and that $\pi\colon P \mapsto \tilde{P}$ is a group homomorphism.

Next, we state Hensel's lifting lemma, a great tool to work with local fields.

> **Theorem (Hensel's lemma for $\Z_p$):** Let $F(x)\in \Z_p[x]$, $n\geq 1, a\in \Z_p$ with $F(a)\in p^n\Z_p$ and  $F'(a)\notin p\Z_p$. 
>
> Then, there exists an (easily computable) $b\in \Z_p$ with $F(b)=0$ and $b - a \in p^n\Z_p$. 

This result can be thought of as an analogue of Newton's method on $\Z_p$, i.e., if we have a function $F$ that is close to zero on $a$, and has a non-zero derivative at that point, there is a root of $F$ close to $a$. 

We can now prove the main theorem of this part:

> **Theorem (VII.2.1 in Silverman):** $\pi$ is surjective. It is called the *reduction map*.
>
> *Proof*:  Let $\tilde{P}=(\tilde{x}, \tilde{y})\in \tilde{E}$. Let $y_0 = \tilde{y}$ seen as an element of $\Z_p$. Let $F(x) = x^3 + (a + O(p))x + (b+O(b)) - y_0^2\in Z_p[x]$ (this is just the equation for the curve $E$ at $y_0$). $F$ is close to zero (a.k.a in $p\Z_p$) at points $x_0$ with $\tilde{x}_0=\tilde{x}$, with a non-zero derivative (since $\tilde{E}$ is non-singular[^1]). We can thus apply Hensel's lemma and find a point $\xi\in \Z_p$ with $F(\xi)=0$ and $\tilde{\xi}=\tilde{x}$. The point $P=(\xi, y_0)$ thus belongs to $E$ and maps to $\tilde{P}$ under $\pi$. Since $\tilde{P}$ was arbitrary, we conclude that $\pi$ is surjective. 

The nice thing about this proof is that it gives a simple way to actually lift $\tilde{P}$ to $P$. In Sage, it's as simple as:

```python
tildeE = EllipticCurve(GF(p), [a, b]) # Arbitrary curve over Fp
E = EllipticCurve(Qp(p), [a, b]) # Lift of curve to Qp
tildeP = tildeE.random_point() # tildeP = tildeE(209429384434035 : 167128638250862 : 1)
P = E.lift_x(ZZ(tildeP.xy()[0])) # P = E(209429384434035 : 167128638250862 + O(p) : 1)
```

# Removing the geometry

With this lift in hand, we're close to the end of the construction! 

We define subgroups of $E(\Q_p)$ as follows:
$$
E_n(\Q_p) = \\{ P \in E(\Q_p) \ \vert \ ord_p(x(P)) \leq -2n \\} \cup \\{\mathcal{O}\\}
$$
These subgroups can be thought of as increasingly tight neighborhoods of $\\{\mathcal{O}\\}$, or as equivalents to $p^n\Z_p \subset \Z_p$. This last analogy can be made precise by observing that if $P=(x,y) = [x:y:1]\in E_n(\Q_p)$, then $\frac{x}{y}\in p^n\Z_p$[^2][^3].  In fact, this analogy can be made precise:

> **Theorem (VII.2.2 in Silverman):** There is a group structure on $p\Z_p$ (that we denote $\hat{E}(p\Z_p)$) such that the map 
> $$
> E_1(\Q_p) \to \hat{E}(p\Z_p): [x:y:1] \mapsto -\frac x y
> $$
> is a group isomorphism, that also induces isomorphisms $E_n(\Q_p)\to \hat{E}(p^n\Z_p)$.

Finally, we can *remove the geometry* using the following result:

> **Theorem (IV.6.4 in Silverman):** There is a isomorphism 
> $$
> \log_\mathcal{F}\colon \hat{E}(p\Z_p)\to p\Z_p
> $$
>  called the *formal logarithm*, where $p\Z_p$ on the right has the usual additive group structure. It also induces isomorphisms $\hat{E}(p^n\Z_p) \to p^n\Z_p$.

We will explore and prove these last two results in a coming post.

# Putting it together

Let's recap. We have our original curve $\tilde{E}(\F_p)$, a lift $E(\Q_p)$, and subgroups $E_n(\Q_p)$ where the DLP can be reduced to $p\Z_p$. Moreover, the exact sequence we showed above induces an isomorphism
$$
E(\Q_p)/E_1(\Q_p) \to \tilde{E}(\F_p).
$$
Note that we haven't used the fact that $\\#\tilde{E}(\F_p) = p$ yet, so all our previous constructions work for arbitrary curves.  We now make use of it to break the DLP on $\tilde{E}(\F_p)$! 

Since the DLP is simple in $E_1(\Q_p)$, we would win if we managed to lift points in $\tilde{E}(\F_p)$ to $E_1(\Q_p)$. But since $\\#\tilde{E}(\F_p)=p$, we have $E(\Q_p)/E_1(\Q_p) \simeq \Z/p\Z$. Thus the *multiplication by $p$ map* $[p]$ sends $E(\Q_p)$ to $E_1(\Q_p)$. 

Therefore, we have the following homomorphism
$$
\phi\colon \tilde{E}(\F_p) \xrightarrow{\text{lift}} E(\Q_p) \xrightarrow{[p]} E_1(\Q_p) \to \hat{E}(p\Z_p)\xrightarrow{\log} p\Z_p \xrightarrow{\mod p^2}\Z/p\Z.
$$
Moreover, we also have $E_1(\Q_p)/E_2(\Q_p) \simeq p\Z_p/p^2\Z_p \simeq \Z/p\Z$. So $[p]$ maps $E_1(\Q_p)$ to $E_2(\Q_p)$. 

Therefore, $\phi$ restricted to $\mathcal{O}$ maps to $0\in \Z/p\Z$:
$$
\phi\colon \mathcal{O} \xrightarrow{\text{lift}} E_1(\Q_p) \xrightarrow{[p]} E_2(\Q_p) \to \hat{E}(p^2\Z_p)\xrightarrow{\log} p^2\Z_p \xrightarrow{\mod p^2}0.
$$
And its over! Concretely, for $\tilde{P}, \tilde{Q} \in \tilde{E}(\F_p)$, with $\tilde{Q}=[m]\tilde{P}$ for an unknown $m$, we have $Q-[m]P\in E_1(\Q_p)\ (=\ker(\pi))$, so $\phi(\tilde{Q})=m\phi(\tilde{P})$ and we can solve the DLP in $\Z/p\Z$!

The nice thing is that it's also very easy to code (taken from this [post](https://crypto.stackexchange.com/questions/70454/why-smarts-attack-doesnt-work-on-this-ecdlp)):
```python
tildeE = EllipticCurve(GF(1019), [373, 837]) # Arbitrary curve over Fp
assert tildeE.order() == 1019 # The curve is anomalous
E = EllipticCurve(Qp(1019), [373, 837]) # Lift of curve to Qp
tildeP = tildeE.gens()[0]
tildeQ = 123 * tildeP
P = E.lift_x(ZZ(tildeP.xy()[0])) # Might have to take the other lift. 
Q = E.lift_x(ZZ(tildeQ.xy()[0])) # Might have to take the other lift.
p_times_P = p*P
p_times_Q = p*Q
x_P, y_P = p_times_P.xy()
x_Q, y_Q = p_times_Q.xy()
phi_P = -(x_P/y_P) # Map to Z/pZ
phi_Q = -(x_Q/y_Q) # Map to Z/pZ
k = phi_Q/phi_P # Solve the discrete log in Z/pZ (aka do a division)
print Mod(k, 1019) # Prints 123
```

The most expensive operation is the multiplication by $p$, which takes $O(\log p)$ time.

It is interesting to see where this attack fails for non-anomalous curves. The only place we used that $\\#\tilde{E}(\F_p)=p$ was to show that $[p]$ maps $E(\Q_p)$ to $E_1(\Q_p)$. So this should be wrong in general[^4]:

```python
tildeE = EllipticCurve(GF(1019), [373, 837]) # Anomalous curve over Fp
assert tildeE.order() == 1019 # The curve is anomalous
E = EllipticCurve(Qp(1019), [373, 837]) # Lift of curve to Qp
P = E.lift_x(ZZ(randint(1, p))) # Random point in E. Might fail.
print p*P # (O(p^-2) : O(p^-3) : 1) in E_1(Q_p).

tildeE = EllipticCurve(GF(1019), [373, 839]) # Arbitrary curve over Fp
assert tildeE.order() != 1019 # The curve is NOT anomalous
E = EllipticCurve(Qp(1019), [373, 839]) # Lift of curve to Qp
P = E.lift_x(ZZ(randint(1, p))) # Random point in E. Might fail.
print p*P # (O(1) : O(1) : 1) NOT in E_1(Q_p).
```

So most curves are safe against this attack.



Next time, we'll explore the concept of *formal groups* and prove the two theorems we used to *remove the geometry* from the problem.


[^1]: Actually, it could be that the derivative is zero, but then the partial derivate $\partial/\partial y$ is non-zero and we can change the proof by switching all $x$'s to $y$'s.
[^2]: Here we use the fact that $[x:y:1]\in E(\Q_p)$ are of the form $[O(p^{-2n}), O(p^{-3n}), 1]$.
[^3]: We note that $E_1(\Q_p)$ was also previously defined as the kernel of $\pi$. Using this remark, it is clear that the two definitions are equivalent.
[^4]: Note that $[p]: E_n(\Q_p) \to E_{n+1}(\Q_p)$ remains true for all curves since $E_n(\Q_p)/E_{n+1}(\Q_p) \simeq p^n\Z_p/p^{n+1}\Z_p \simeq \Z/p\Z$ is a general result.

