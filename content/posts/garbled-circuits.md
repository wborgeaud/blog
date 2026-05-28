---
title: "You could have invented garbled circuits"
date: 2026-05-27
description: ""
slug: ""
tags: [ cryptography]
---

Garbled circuit is a cool protocol that solves the two-party secure computation problem, but like many cryptographic protocols, its description can look a bit mysterious.

In this post, I'll show how one can stumble upon the construction of garbled circuits from first principles.


## The problem
Alice has a private $a\in X$ and Bob has a private $b \in Y$. They want to evaluate a public function $f\colon X \times Y \to Z$ on their inputs $(a,b) \in X\times Y$, without Bob (resp. Alice) learning anything about $a$ (resp. $b$) except the result $f(a,b)$.

A classic instance is [Yao's Millionaires' problem](https://en.wikipedia.org/wiki/Yao%27s_Millionaires%27_problem):
> Alice and Bob want to know which one of them is richer without revealing their actual net worth.

This could be modeled with $X=Y=\mathbb{Z}$ and $f(x,y)=\mathbf{1}\[x\geq y\]$, where $a$ is Alice's net worth and $b$ is Bob's.

## Lookup tables
Assuming $X$ and $Y$ are finite, a function $f\colon X \times Y \to Z$ is entirely described by the finite table $\[(x,y,f(x,y))\]\_{(x,y)\in X\times Y}$. With this viewpoint, the problem becomes more approachable. For example, one can imagine a protocol where Alice sends the subtable $\[(a,y,f(a,y))\]\_{y\in Y}$ to Bob, which then just picks the element at index $b$. This obvioulsy reveals way to much information about $a$ (even if $a$ were hidden from the subtable, Bob learns all the values $f(a,y)$, not just $f(a,b)$).

So we need to uses some tricks to hide parts of the data sent to Bob. A nice way to visualize these tricks is by using a pen and paper protocol!

Here is one way to do this:

1. For all $(x,y) \in X\times Y$, Alice writes $x$, $y$, and $f(x,y)$ on three slips of paper $S^x\_{x,y},S^y\_{x,y}, S^f\_{x,y}$.
![Step 1](/images/garbled/step1.png)
2. She lays the triples face down on a table, expect the slip $S^y\_{a,y}$ for all $y\in Y$ which stay face up.
![Step 2](/images/garbled/step2.png)
3. She calls Bob into the room, and she leaves the room.
4. Among the $|Y|$ triples with a visible $S^y$, Bob takes the one with value $b$, and reveals the corresponding $S^f$ slip. He discards all the other slips and calls Alice into the room.
![Step 4](/images/garbled/step4.png)
5. When Alice enters, there is only a single slip of paper on the table, with the value of $f(a,b)$ written on it.

It's pretty clear that Alice and Bob don't learn anything except $f(a,b)$ in this protocol.

### Malicious security
It should be noted that this protocol assumes both parties follow the protocol rules and don't try to cheat. For example, Bob could learn $a$ by simply revealing the $S^x$ slips along with $S^f$ in step 4 of the protocol. Or Alice could just write wrong values of $x$, $y$, or $f(x,y)$ in some slips.

For the latter case, there is a solution to ensure Alice behaves correctly. At step 4, we could have Bob flip a coin. If head, he follows the protocol as usual. If tails, he asks Alice to reveal all the slips (after potentially shuffling the triples to make sure to hide $a$), after which Bob can make sure that there is exactly one triple for each $(x,y) \in X \times Y$ and that they are all formed correctly.

Note that there is a seemingly more optimal protocol where Alice only writes slip triples corresponding to $(a,y)$ for $y\in Y$. But in this case, she doesn't have this ability to prove she behaved correctly without also revealing $a$.

## Using cryptography
The pen and paper protocol contains the core information theoretic mechanism, but it's obvioulsy impractical for a computer implementation. That's where cryptography comes into play, to simulate the whole *putting slips face down* and *revealing slips* mechanisms.

Hiding and revealing data does sound a lot like encryption, so lets consider encryption/decryption functions $E\_K, D\_K$ with $D\_K\left(E\_K(m)\right) = m$. We also assume that $D\_K(c)$ can return a failure $\bot$ when there is no message $m$ (in the relevant space) with $E\_K(m) = c$.

Then, step 1 of the protocol can be simulated by having Alice generate random keys $\\{K\_x\\}\_{x \in X}$ and encrypt all the $f(x,y)$ with the corresponding $K\_x$ to get a table $\[E\_{K\_x}(f(x,y))\]\_{(x,y) \in X \times Y}$. We want Alice to send the table along with $K\_a$ to Bob for decryption, but then Bob could use $K\_a$ to decrypt all the $E\_{K\_a}(f(a,y))$, not just $E\_{K\_a}(f(a,b))$ as we want.

To fix this, Alice generates another set of keys $\\{K\_y\\}\_{y \in Y}$ and encrypts the table again to get the encrypted (or *garbled*) table 
$$
T = \[E\_{K\_y}\left(E\_{K\_x}\left(f(x,y)\right)\right)\]\_{(x,y) \in X \times Y}.
$$

Alice sends (a shuffled version of) $T$ along with $K\_a$ and $K\_b$ to Bob, who can try to decrypt every element $t \in T$ with $D\_{K\_a}\left(D\_{K\_b}\left(t\right)\right)$. The only element in the garbled table that doesn't decrypt to $\bot$ reveals the value of $f(a,b)$, which Bob then shares with Alice.

The careful reader will probably ask "how can Alice send $K\_b$ without knowing $b$". The answer is by using [oblivious transfer](https://en.wikipedia.org/wiki/Oblivious_transfer), a classic protocol that solves exactly this problem:
> Alice has $n$ messages $m\_1,\dots,m\_n$ and Bob has a number $k \in \[n\]$. A 1-out-of-$n$ oblivious transfer protocol allows Bob to learn $m\_k$ without Alice learning anything about $k$.

Oblivious transfer isn't too hard to construct by using public-key cryptography. Maybe it deserves its own "you could have invented oblivious transfer".

We are now ready to present the final protocol for two-party computation using lookup tables:
1. Alice generates the keys $\\{K\_x\\}\_{x \in X}$, $\\{K\_y\\}\_{y \in Y}$, and the garbled table $T$ as above. She then sends $T$ and $K\_a$ to Bob.
2. Alice and Bob do a 1-out-of-$|Y|$ oblivious transfer on Alice's $\\{K\_y\\}\_{y \in Y}$ and Bob's $b$ so that Bob learns $K\_b$ without Alice learning anything about $b$.
3. Bob computes $D\_{K\_a}\left(D\_{K\_b}\left(t\right)\right)$ for all $t\in T$ and stops once the result is not $\bot$, in which case the result is $f(a,b)$.

Assuming the encryption and OT protocols are secure, it should be clear that Alice and Bob don't learn substantial other than $f(a,b)$ in this protocol.

Note that, as with the pen and paper protocol, Alice can prove that $T$ is constructed correctly by simply sending all the keys $\\{K\_x\\}\_{x \in X}$, $\\{K\_y\\}\_{y \in Y}$ to Bob, who can then fully decrypt the table and check that it was constructed correctly.

## Complexity
This protocol for two-party computation is pretty nice, except for the fact that it is totally impractical. Both the computational and communication complexity are $O(|X|\cdot |Y|)$, which in computer science lingo is exponential in the input size, which in normal lingo is really dang slow.

For example, in Yao's Millionaires' problem with $X=Y=\[10^9-1\]$ (they are not billionaires after all), Alice has to compute and send a garbled table of length $10^{18}$, which is totally impractical. 

## Function composition
One way to make the protocol more efficient is to break down the function $f$ into smaller functions, and leverage function composition. Assume for instance that Alice's input space can be decomposed as $X = X\_0 \times X\_1$ and that there exists functions $h\colon X\_1 \times Y \to W$ and $g\colon X\_0 \times W \to Z$ such that
$$
f(x, y) = f((x\_0, x\_1), y) = g(x\_0, h(x\_1, y)), \ \forall (x,y) \in X\times Y.
$$

We apply the protocol for $g$ first, generating keys $\\{K\_{x\_0}\\}\_{x\_0 \in X\_0}, \\{K\_{w}\\}\_{w \in W}$ and the table
$$
T\_g = \left[E\_{K\_w}\left(E\_{K\_{x\_0}}\left(g(x\_0,w)\right)\right)\right]\_{(x\_0,w) \in X\_0 \times W}.
$$
Alice can send the table and the key $K\_{a\_0}$ to Bob, but how can she share the other key corresponding to $h(a\_1, b) \in W$ ?

They can simply use the lookup protocol, but for the function 
$$
h\_K(x\_1, y) = K\_{h(x\_1, y)}
$$
instead! So Alice generates keys $\\{K\_{x\_1}\\}\_{x\_1 \in X\_1}, \\{K\_{y}\\}\_{y \in y}$ and the table
$$
T\_{h\_K} = \left[E\_{K\_y}\left(E\_{K\_{x\_1}}\left(K\_{h(x\_1,y)}\right)\right)\right]\_{(x\_1,y) \in X\_1 \times Y},
$$
sends the table and the key $K\_{a\_1}$ to Bob, and they run an OT to share $K\_b$ to Bob. Bob can then get $K\_{h(a\_1, b)}$ be decrypting $T\_{h\_K}$ with $D\_{K\_{a\_1}}\circ D\_{K\_b}$, and he can then get $f(a,b)$ by decrypting $T\_g$ with $D\_{K\_{a\_0}}\circ D\_{K\_{h(a\_1, b)}}$.

What did we gain by doing this ? The tables that Alice has to compute and send have sizes $|X\_0|\cdot |W|$ and $|X\_1|\cdot |Y|$ respectively. Assuming $W$ is of size $O(|Y|)$, we get a computational and communication complexity of $O\left((|X\_0|+|X\_1|)\cdot |Y|\right)$. That's up to a square-root improvement over $O(|X| \cdot |Y|)$ if $|X\_0|=|X\_1|=\sqrt{|X|}$ !

Moreover, it's easy to see that we can use the same procedure if $Y$ can be decomposed as $Y = Y\_0 \times Y\_1$ (we just need to use 2 OT), and that this further generalizes to deeper decompositions
$$
X = X\_0 \times \cdots \times X\_n, \ Y = Y\_0 \times \cdots \times Y\_m.
$$

## Garbled circuits (finally)
The function composition framework fits perfectly in computer science, where the input/output spaces are often modeled as bits, i.e.,
$$X=\\{0,1\\}^n,Y=\\{0,1\\}^m,Z=\\{0,1\\}^k,
$$
which are fully decomposable as products of $\\{0,1\\}$. Moreover, any function 
$$
f\colon \\{0,1\\}^n \times \\{0,1\\}^m \to \\{0,1\\}^k
$$
can be written as a bunch of compositions of the function $\texttt{NAND}\colon \\{0,1\\} \times \\{0,1\\} \to \\{0,1\\}$, more commonly known as a [Boolean circuit](https://en.wikipedia.org/wiki/Boolean_circuit).

Using the function composition protocol designed above, we can solve the two-party secure computation for $f$. This involves Alice sending a table of size 4 for each $\texttt{NAND}$ function call in the circuit and one key $K\_{a\_i}$ for every bit $\\{a\_i\\}\_{i=0}^{n-1}$ of her input. Alice and Bob will also have to run $m$ 1-out-of-2 OT for each key corresponding to the bits of Bob's input $\\{b\_i\\}\_{i=0}^{m-1}$. By explicitely writing the details of the protocol, we get exactly the textbook Yao's garbled circuit protocol.

The complexity is on the order of the number of gates in the circuit. Arithmetic operations require for example $O(n+m)$ gates for addition and $O\left((n+m)\log (n+m)\right)$ gates for multiplication. 
In general, most useful functions one can think of require at most a number of gates polynomial in $n+m$. This is a massive improvement over the initial lookup table protocol which has complexity $O\left(2^{n+m}\right)$.

