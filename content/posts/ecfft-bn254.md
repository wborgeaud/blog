---
title: "ECFFT on the BN254 base field in Rust"
date: 2021-10-16T00:57:25-07:00
description: ""
slug: ""
tags: [math, algorithms, rust]
---

$$
\def\F{\mathbb{F}}
$$

**tl;dr:** A Rust implementation of the ECFFT here: [https://github.com/wborgeaud/ecfft-bn254](https://github.com/wborgeaud/ecfft-bn254).

The [last post]({{< ref "/ecfft.md" >}}) was about the ECFFT algorithm by Eli Ben-Sasson, Dan Carmon, Swastik Kopparty and David Levit. At the end of the post, I mentioned that it would be fairly straightforward to implement the ECFFT algorithms in low-level languages like Rust by doing all the mathematical precomputations in Sage.

Well I have done exactly that and implemented the EXTEND and ENTER operations in Rust for the base field of the BN254 curve. This field has order

$$
p = 21888242871839275222246405745257275088696311157297823662689037894645226208583
$$

with

$$
p-1 = 2 \times 3^2 \times 13 \times 29 \times 67 \times 229 \times 311 \times 983 \times 11003 \times 405928799 \times 11465965001 \times n
$$

so the classic FFT cannot be performed on this field. As an aside, this makes proof recursion pretty hard on this curve since most modern computational integrity proof systems use FFTs.

The Rust implementation can be found [here](https://github.com/wborgeaud/ecfft-bn254). It uses the [arkworks framework](https://github.com/arkworks-rs) for field operations[^1].

The crate contains two important objects:

- A `EcFftParameters<F: PrimeField>` trait which holds all the necessary parameters to perform the ECFFT.
- A `EcFftPrecomputation<F: PrimeField, P: EcFftParameters<F>>` struct which holds all the precomputations needed in the ECFFT algorithms.

For the BN254 base field, there is a `Bn254EcFftParameters` which implements `EcFftParameters<ark_bn254::Fq>`. The parameters used in this implementation are gotten from a Sage script `get_params.sage`.

Note that the BN254 base field was chosen for convenience, since it's already implemented in arkworks. It is quite easy to extend the implementations to an arbitrary field given a Rust implementation of this field.

### Benchmarks

Here is a comparison of the running time for the evaluation of a polynomial of degree `n-1` on a domain of `n` points using 3 algorithms:

- the naive evaluation in $O(n^2)$,
- the classic FFT (on the FFT-friendly BN254 scalar field) in $O(n\log{n})$,
- the ECFFT ENTER algorithm in $O(n\log^2{n})$.
  ![Challenge description](/images/benchmarks/ecfft-bench.svg)

[^1]: I initially wanted to work in the base field of the Secp256k1 curve as in the last post, but this field is currently not supported in arkworks (see [this issue](https://github.com/arkworks-rs/curves/issues/36)). Once it is, it will be straightforward to implement the ECFFT on this field.
