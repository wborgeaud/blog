---
date: 2020-04-29T08:57:07-07:00
title: "Anomalous Curves Part 3: Formal groups"
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
\def\M{\mathcal{M}}
\def\G{\hat{\mathbb{G}}}
\def\O{\mathcal{O}}
$$



This is part three of the series on anomalous curves. Go [here]({{< ref "/anomalous-curves-1.md" >}}) for part one and [here]({{< ref "/anomalous-curves-2.md" >}}) for part two.

Today, I'll prove the two missing results from the last post:
> **Theorem (VII.2.2 in Silverman):** There is a group structure on $p\Z_p$ (that we denote $\hat{E}(p\Z_p)$) such that the map 
> $$
> E_1(\Q_p) \to \hat{E}(p\Z_p): [x:y:1] \mapsto -\frac x y
> $$
> is a group isomorphism, that also induces isomorphisms $E_n(\Q_p)\to \hat{E}(p^n\Z_p)$.

> **Theorem (IV.6.4 in Silverman):** There is a isomorphism 
> $$
> \log_\mathcal{F}\colon \hat{E}(p\Z_p)\to p\Z_p
> $$
> called the <i>formal logarithm</i>, where $p\Z_p$ on the right has the usual additive group structure. It also induces isomorphisms $\hat{E}(p^n\Z_p) \to p^n\Z_p$.

The intuition behind the first result is that $E_1(\Q_p)$ somewhat represents points *close to $\mathcal{O}$* and that this space can be *linearized* into $p\Z_p$ with *some group structure*. 

The second result has little to do with geometry. It says that the group structure we put on $p\Z_p$ can always be mapped back to the usual additive group structure. We'll start by proving this second result using the notion of formal group laws.

# Formal group laws

Let $R$ be a ring. A *formal group law* over $R$ is a power series $F\in R[[X,Y]]$ such that

1. $F(X,Y) = X + Y + \text{higher order terms}$,

2. $F(X, F(Y,Z)) = F(F(X,Y), Z)$,

3. $F(X,Y) = F(Y,X)$,

4. There exists a unique $i(T)\in R[[T]]$ such that $F(T, i(T)) = 0$,

5. $F(X, 0) =X$ and  $F(0, Y) = Y$.

Intuitively, a formal group law is a power series satisfying all the abelian groups axioms. In particular, if we have a subset $\M\subseteq R$ such that $F(x,y)$ converges and belongs to $\M$ for all $x,y\in\M$, then $F$ induces an abelian group structure on $\M$, noted $F(\M)$.

An important example of such $\M$ is if $R$ is a complete local ring (think $\Z_p$) and $\M$ is the maximal ideal of $R$ (think $p\Z_p$).  Indeed, in that case for any $f=\sum_{i=1}^\infty a_i X^i\in R[[X]]$ and $x\in \M$,  we have that $f(x) = \lim_{n\to\infty} \sum_{i=1}^n a_i x^i$ is clearly a Cauchy sequence (in $\M$) under the $\M$-adic topology, under which $R$ is assumed complete. Thus $f(x)$ converges to an element of $\M$ (since $\M$ is closed in this topology).

## Examples

Two easy examples of formal group laws are:

1. **Additive formal group law** $\hat{\mathbb{G}}_a$: $F(X,Y) = X + Y$ is clearly a formal group law. Applied to $\M$, $\G_a$ reduces to the additive group structure on $\M$.
2. **Multiplicative formal group law** $\G_m$: $F(X,Y) = X + Y + XY = (X+1)(Y+1)-1$ is a formal group law. Applied to $\M$, it reduces to the multiplicative group structure on the open set $1+\M$.

Later, we will see how to construct a formal group law from any elliptic curve!

## Formal logarithm

From calculus, we know that the power series $\log(1+X) = \sum_{n=1}^\infty (-1)^{n-1} \frac {X^n}{n}$ has some nice properties. Namely, $\log((1+X)(1+Y))=\log(1+X+Y+XY)=\log(1+X) + \log(1+Y)$. This induces an <i>isomorphism</i> of formal group laws $\G_m \to \G_a$ over fields of characteristic zero. 

A surprising and important result is that the formal logarithm generalizes to arbitrary formal group laws:

> **Theorem (IV.5.2 in Silverman):** For any formal group law $F$, there is a formal logarithm $\log_F$ that induces an isomorphism of formal group laws $F \to \G_a$ over fields of characteristic zero.

This theorem has the nice following corollary that implies the second result we mentioned in the introduction:

> **Theorem (IV.6.4 in Silverman):** Let $R=\Z_p$, $\M = p\Z_p$, and $F$ a formal group law over $R$. Then the formal logarithm $\log_F$ induces group isomorphisms
> $$
> \log_F\colon F(\M^r) \xrightarrow{\simeq} \G_a(\M^r)
> $$
> for all $r>0$.



# The Formal group law of an elliptic curve

We now see how the group structure on elliptic curves induces formal group laws.

Let $E: y^2 + a_1xy +a_3y = x^3 + a_2x^2 + a_4x + a_6$ be an elliptic curve over a field $K$. Let $K[E]\_\mathcal{O}$  be the local ring without poles at $\O$. Let $\M_\O$ be the maximal ideal of $K[E]\_{\O}$ given by functions vanishing at $\O$. Then $\M_\O=(z)$ for some <i>uniformizer</i> $z$ (which exists by properties of DVR). The completion of $K[E]\_\O$ at $\M_\O$ is isomorphic to $K[[z]]$. We want to find a characterization of the group structure on $E$ inside this ring $K[[z]]$ in terms of a formal group law.

We use the change of variable: $z = -\frac x y$, $w = -\frac 1 y$. In this coordinate system, $\O=(0,0)$ and $z$ is a uniformizer of $\M_\O$.  The Weierstrass equation becomes
$$
E: w = z^3 + a_1 zw + a_2 z^2w + a_3w^2 + a_4 zw^2 + a_6w^3 = f(z, w).
$$
The idea now is to recursively substitute the equation into itself, i.e., replace all occurrences of $w$ on the right-hand-side by the right-hand-side itself <i>ad infinitum</i>. This creates a power series $w(z) = z^3(1+...)\in \Z[a_1,...,a_6][[z]]$ satisfying $w(z) = f(z, w(z))$.[^1] 

Defining the formal group law on $K[[z]]$ is now a matter of technique. We take two points on $E$: $(z_1, w(z_1))$ and $(z_2, w(z_2))$ and formally define the line connecting them, find the intersection with the curve and invert it. This gives a power series $F(z_1, z_2)\in \Z[a_1,...,a_6][[z]] \subset K[[z]] $ that satisfies the formal group law axioms. We denote this formal group law $\hat{E}$.

Now let's go back to the case $K=\Q_p$, $R=\Z_p$, $\M = p\Z_p$. The change of coordinates for $(z,w)$ implies $x =  \frac z w$ and $y = - \frac 1 w$, so we can define Laurent series $x(z) = \frac z {w(z)}$ and $y(z) = -\frac 1 {w(z)}$. A similar argument than one above shows that for $z\in \M$, $x(z)$ and $y(z)$ converge in $K$. Thus, we can define a map
$$
\M \to E(K): z\mapsto (x(z), y(z))
$$
which is injective with inverse $(x,y)\mapsto -\frac x y$. Moreover, this map is a group homomorphism when $\M$ is endowed with the group structure $\hat{E}(\M)$ induced by the formal group law $\hat{E}$.

We are now very close to proving the first result mentioned in the introduction. Indeed, the only thing left to do is to show that the image of the above map is $E_1(K)$. This last space is defined as the set of points having valuation $ord_p(x)\leq -2$. It can be shown that $w(z)=z^3(1+...)$, thus $ord(x(z))=ord(z) - ord(w(z)) = -2ord(z)\leq -2$ since $z\in \M=p\Z_p$. So we know that the image is contained in $E_1(K)$.

Finally, to show that the map is surjective on $E_1(K)$, we show that the inverse $(x,y)\mapsto -\frac x y$ is well-defined on $E_1(K)$. For $(x,y)\in E_1(K)$, we have $ord(x)=-2r, ord(y) = -3r$ for some $r>0$. Thus, $-\frac x y$ is of order $r>0$, i.e., it belongs to $\M$. This concludes the proof of the first result.



# Conclusion

This finishes the exposition of Smart's attack on anomalous elliptic curves. Although this attack is rather simple and can be implemented in a dozen lines of Sage, the math behind it is quite deep. 

The best way to summarize it is with the following exact sequence:
$$
0 \to \M \simeq \hat{E}(\M) \simeq E_1(K) \subset E(K) \xrightarrow{\pi} \tilde{E}(k) \to 0.
$$
This exact sequence is used to break the complicated group $E(K)$ of interest to geometers into the two simpler groups $\M \simeq E_1(K)$ and $\tilde{E}(k)$ (where $k=R/\M$). 

In Smart's attack, we used a map $E(K) \to E_1(K)$ (present only for anomalous curves) to go from the group $\tilde{E}(k)$ of interest to cryptographer to the  group $\M$. This can be used to efficiently break the discrete log on $\tilde{E}(k)$.  



[^1]: Proofs for all these statements can be found in Section IV.1 of Silverman.
