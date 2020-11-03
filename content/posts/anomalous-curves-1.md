---
date: 2020-04-21T13:57:07-07:00
title: "Anomalous Curves Part 1: Don't be clever with your elliptic curve order"
description: ""
slug: "" 
tags: [elliptic curves, cryptography]
---

$$
\def\F{\mathbb{F}}
$$



Have you ever been confused by the numbers $p,q,r$ in a paper dealing with elliptic curves? Some paper use $q$ for the order of the elliptic curve over a field of order $p$. Conveniently, other papers use the **exact opposite notation**, while some get original and use $r$ for the field size, or the order of a subgroup of the curve, or something else...

What if I told you there are curves where $p=q=r$? We could decide to only use these curves and never have to go back on page 2 of a paper to see what are $p,q$ or $r$! 

Joke aside, these curves actually exist and go by the name of **anomalous curves**, that is, curves $E(\mathbb{F}_p)$ with $\\# E(\F_p)=p$. If you know [Hasse's Theorem](https://crypto.stanford.edu/pbc/notes/elliptic/count.html), you'll understand why these curves are also called *curves of trace one*. 

Here is an example:

```
E: y^2 = x^3 + 425706413842211054102700238164133538302169176474*x + 203362936548826936673264444982866339953265530166
p = 730750818665451459112596905638433048232067471723                                                                                                     
```

Regardless of my rant on inconsistent notations for elliptic curves, using such curves could result in more elegant notation, or even a *Nothing up my sleeve* mechanism for choosing elliptic curves. Moreover, they could be use to derive efficient *recursive proof systems* without having to use cycles of elliptic curves. 

It turns out that these curves are actually **totally worthless for cryptography.** Namely, the discrete logarithm problem can be solved in $O(\log p)$ on these curves. So these curves are secure only if their field arithmetic is intractable. Clearly not ideal.

This was discovered independently by [Smart](https://link.springer.com/article/10.1007/s001459900052) and [Semaev](https://www.ams.org/journals/mcom/1998-67-221/S0025-5718-98-00887-4/S0025-5718-98-00887-4.pdf) in 1998-99.

In a coming series of posts, I will try to explore how these attacks work. I think they use some interesting math that is not commonly used in current cryptographic schemes.

For example, in pairing-based cryptography, we regularly use a field extension $\F_p \subset \F_{p^k}$ to, for example, capture the torsion points. In Smart's attack, we use a dual of some kind; we look at a map $E(\mathbb{Q}_p) \to \tilde{E}(\F_p)$ and lift points over $\F_p$ to points over $\mathbb{Q}_p$. In the next post, I'll explain what this means and how to use it to break ECDLP.
