---
title: "A simple multivariate AIR argument inspired by SuperSpartan"
date: 2023-06-22
description: ""
slug: ""
tags: [ cryptography, zero-knowledge proofs]
---

*PDF version [here](https://github.com/wborgeaud/superair-note/blob/main/SuperAIR.pdf) and HackMD [here](https://hackmd.io/@wborgeaud/HyQ-fUuPn).*

We will consider the following basic version of AIR. Let $\mathbb{F}$ be a finite field and let $F \in \mathbb{F}[X_0,\dots,X_{2C-1}]$ be a constraint polynomial. An AIR witness for this instance is a table of $C$ columns $z_0,\dots,z_{C-1}$ of size $n=2^v$ such that for all $i=0,\dots,n-2$,
$$
F(z_0[i],\dots,z_{C-1}[i],z_0[i+1],\dots,z_{C-1}[i+1])=0.
$$

## Multi-columns CCS (MCCCS)
CCS is a constraint system introduced in [STW23][^1] that generalizes common constraint systems such as R1CS, AIR, and Plonk. A CCS structure is given by 
- Matrices $M_0,\dots,M_{t-1}\in \mathbb{F}^{m\times n}$.
- Multisets $S_0,\dots,S_{q-1}$ with elements in $\{0,\dots,t-1\}$.
- Constants $c_0,\dots,c_{q-1}\in \mathbb{F}$.

A witness is a vector $z\in\mathbb{F}^n$ such that[^2]
$$
\sum_{i=0}^{q-1} c_i \cdot \bigcirc_{j\in S_i} M_j \cdot z = \mathbf{0}.
$$

We introduce a generalization, MCCCS, of CCS where the witness is structured as a table of $C$ columns. The additional information required is
- A function $c:\\{0,\dots,t-1\\} \to \\{0,\dots,C-1\\}$ assigning a column to each matrix.

A witness is then a table of $C$ columns $z_0,\dots,z_{C-1}\in \mathbb{F}^n$ such that 
$$
\sum_{i=0}^{q-1} c_i \cdot \bigcirc_{j\in S_i} M_j \cdot z_{c(j)} = \mathbf{0}.
$$

It is easy to see that MCCCS is equivalent to CCS by flattening/unflattening the columns. 

## Proving system for MCCCS

The *SuperSpartan* proving system can easily be modified to accommodate MCCCS. The only difference is that the prover commits to all MLE of the columns and these commitments are all opened at the point $r_y$ in the protocol. 

## AIR as a MCCCS
The AIR arithmetization is shown to be a special case of CCS in [STW23]. We show here that AIR can also be seen as a MCCCS with a very simple transformation.

Consider the AIR constraint polynomial $F \in \mathbb{F}[X_0,\dots,X_{2C-1}]$, let $S_0,\dots,S_{q-1}$ be multisets with values in $\{0,\dots,2C-1\}$ representing the monomials of $F$, and let $c_0,\dots,c_{q-1}$ be the coefficients of these monomials, i.e., 
$$
F(X_0,\dots,X_{2C-1}) = \sum_{i=0}^{q-1} c_i \prod_{j\in S_i}X_j.
$$

Let $I_{n-1}$ be the identity matrix of size $n-1$, let $A_0$ be the 
$n\times n$ matrix
$$ A_0 = 
\begin{bmatrix}
I_{n-1} & 0 \\\\
0 & 0      \\\\
\end{bmatrix}
$$
and let $A_1$ be the $n\times n$ matrix
$$
A_1 = 
\begin{bmatrix}
0 & I_{n-1} \\\\
0 & 0      \\\\
\end{bmatrix}
$$
Note that for $A_0$ and $A_1$ the last row is only used for padding so that the matrix is square. 

Finally, let $t=2C$, $M_j=A_{\lfloor j/C \rfloor}$, and $c(j)=j \text{ mod } C$. Then the MCCCS with these parameters is equivalent to the original AIR.

## Example 

If $C=2$ and $F = X_0 X_1^2 - X_2 - 2X_1X_3$, the MCCCS constraint will be 
$$
A_0 z_0 \circ A_0z_1 \circ A_0z_1 - A_1 z_0 -2\cdot A_0 z_1 \circ A_1z_1 = \mathbf{0}. 
$$

## Proving system for AIR

The MLE of the matrices $A_0$ and $A_1$ are simple. We have 
$$A_0[i,j] = \text{eq}(i,j)-\text{eq}(i,n-1)\cdot \text{eq}(j,n-1)$$

and 
$$A_1[i,j]=\text{next}(i,j),$$ where $\text{next}(i,j)=\text{eq}(i+1,j)$ is defined in Section 5.1 of [STW23]. Therefore the MLE of $A_0$ is 
$$\widetilde{A_0}(x,y) = \widetilde{\text{eq}}(x,y)-\widetilde{\text{eq}}(x,n-1)\cdot \widetilde{\text{eq}}(y,n-1)$$
which can be evaluated in time $O(v=\log n)$, and the MLE of $A_1$ is
$$\widetilde{A_1}(x,y) = \widetilde{\text{next}}(x,y)$$
which can also be evaluated in time $O(v)$, as shown in Theorem 2 of [SWT23].

Therefore, oracle access to $\widetilde{A_0}$ and $\widetilde{A_1}$ is not required by the verifier.

## Cyclic constraints

Some versions of AIR use *cyclic constraints*, i.e., the constraint polynomial also vanishes at $i=n-1$:
$$
F(z_0[n-1],\dots,z_{C-1}[n-1],z_0[0],\dots,z_{C-1}[0])=0.
$$
The MCCCS for AIR can be adapted to support this by using the matrices 
$$ A_0 = I_n =
\begin{bmatrix}
I_{n-1} & 0 \\\\
0 & 1      \\\\
\end{bmatrix}
$$
and
$$
A_1 = 
\begin{bmatrix}
0 & I_{n-1} \\\\
1 & 0      \\\\
\end{bmatrix}.
$$

The MLE of these matrices can also be computed in time $O(v)$ using the following identites
$$ \widetilde{A_0}(x,y) = \widetilde{\text{eq}}(x,y) $$
and
$$\widetilde{A_1}(x,y) = \widetilde{\text{next}}(x,y) + \widetilde{\text{eq}}(x,n-1)\cdot \widetilde{\text{eq}}(y,0).$$



## Handling public inputs

AIR is often used to arithmetize an execution trace. For example, zkVMs often have the structure of an AIR where the first row contains the input of the program and the last row contains the output. Each other row represents a cycle in the zkVM. 

For this reason, we might want (parts of) the first and last rows to be public inputs in the proving system. This can be achieved in the proving system for MCCCS as follows. 

Say we want the first element of column $z_i$ to be public. Instead of committing to the MLE of the full column, the prover commits to the MLE of $z'_i = (0 \ z_i[1..])$, the same column with the first element set to 0. Then, the verifier can compute the value $\widetilde{Z}_i(r_y)$ using the relation
$$\widetilde{Z}_i(r_y) = \widetilde{Z'}_i(r_y) + z_i[0]\cdot \chi_0(r_y),$$
where $\chi_0$ is the 0-th Lagrange basis multilinear polynomial, which can be evaluated in $O(v)$. 

A similar modification can be used to make the last row public.

## When the constraint is an arithmetic circuit

In applications, the constraint polynomial $F(X_0,\dots, X_{2C-1})$ is rarely given in sum-of-monomials form. Most of the time, it is given as an arithmetic circuit. The circuit representation can be much more efficient than the sum-of-monomials representation. For example, 
$$ F(X_0,\dots, X_{2C-1}) = (X_0 + \dots + X_{2C-1})^2$$
takes $2C-1$ additions and $1$ multiplication to evaluate as an arithmetic circuit, but is a sum of $2C^2+C$ monomials. So the (MC)CCS representation can be very inefficient, especially when the number of columns in the AIR is large.

However, it is easy to generalize (MC)CCS to work with arithmetic circuits. Let $\mathcal{C}$ be an arithmetic circuit[^3] with $t$ inputs $x_0,\dots,x_{t-1}$ and $1$ output $\mathcal{C}(x_0,\dots,x_{t-1})$. Then, we can modify the CCS constraint equation to be
$$
\mathcal{C}(M_0\cdot z, \dots, M_{t-1}\cdot z) = \mathbf{0},
$$
where the circuit is evaluated on the $t$ vectors entrywise.

As in the SuperSpartan proving system for CCS, it is easy to see that (except with negligible probability) this constraint is equivalent to 
$$
0 = \sum_{a \in \{0,1\}^{\log m}} \widetilde{eq}(\tau,a) \mathcal{C}\left( u_0, \dots, u_{t-1}\right), \text{ with } u_i= \sum_{y \in \{0,1\}^{\log n}} \widetilde{M_i}(a,y)\cdot \widetilde{Z}(y),
$$
where $\tau\in \mathbb{F}^{\log m}$ is a random vector. This can be proved using an instantiation of the sumcheck protocol for the inner sum, as well as $t$ instantiations of the sumcheck protocol for the values $u_i$. 

[^1]: *Customizable constraint systems for succinct arguments*, Srinath Setty and Justin Thaler and Riad Wahby, eprint.iacr.org/2023/552.
[^2]: Disregarding public inputs for now.
[^3]: Here we consider usual arithmetic circuits over the field $\mathbb{F}$ with binary addition and multiplication gates, as well as unary gates for multiplication by a constant: $\{g_c\}_{c\in \mathbb{F}}$ with $g_c(x) = cx$.

