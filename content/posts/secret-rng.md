---
title: "Donjon CTF Writeup: Secret RNG"
date: 2020-10-31T03:57:25-07:00
description: ""
slug: ""
tags: [ctf-writeup, cryptography, z3]
---

# TLDR
This was a very nice challenge in the [Donjon CTF](https://donjon-ctf.io/). The goal was to reverse engineer the state of the PRNG `math/rand` in the Go standard library to guess the private key of a signature scheme and sign a given message. I solved this challenge by using the SMT solver [Z3](https://github.com/Z3Prover/z3) to automagically recover the RNG state.

# Description

![Challenge description](/images/ctf-challs/srng.png)

Connecting to `nc ots-sig.donjon-ctf.io 4001`, we get:
```
Public key: djX6vqVMj0fTZGIhJFgN1VHLgGgaBxWEhvxp1MzB09s=
Enter signature: test
You failed! Private key was: 8GB6ClgHLz0nGU40Zwj8eKcH/CPl6sDKQEQX5cbiy1TPVf8ccI2yjr8HiOQwpwCj4VSQmS36+bIWBgkM3HO4Ny7pBvE0yGtJY9v3sVuaYeUU5h/rqYBpMjUAXBj5jfljRnVAXl50AKQvD5IYzU5IP6F5mJV/ZgT7MQ912/j/Q0+ug8Bj9q/+T6iO8tQfsui857XR/KIw85+EP5gRhUJi09Jjl36iFC2jyvqNQdjTpdJ4cQN8PO8RIAXCJlPT7upvD5uhQ0CiL+1KQRUPgWPK77SvNwUD++IboU4SBwP1DDFDrnqOZ7GmEncgT0VkLlQW9kWdfxM1HqQvSQmNqiUwK6Xps12qXi8ib07rnYkcV4eJ0QVGho6uuk8aGXhfJoArf2fGUzqhaNZIQGjsXBaoAfG7mka+SSlM4cGzvn5xA59yZ2H9H8C72ADiTtfF5cUSniT7QsMXWUjJrrsupUbOyapRH40DJ1fTeLgDZ1ly3CzN8dXKjItxcyuNONDCd5MvfdPIBsrApCY6Uu25rbG1q91C8t5YLVM0l90GoLdpJlJLfF/02jHNmkoYsc/Jyg8PyRuwBXj47mtbD/AViomNbkX2th9gUXfEVeMPzP1QqDJ6CC7sdkmdBspuyQtF6nX/pM5pXNDAOvFYuBdwfCPvCEAonXQqKUYXkqyZ82YACNhtmXgkBjkhO4b6RiOGKHVNQDqtCUmvSuk0VNebMGHrWmBSdjrM7FXVVI+f6Z7tik8ctxHYrJyU1XFervwlmAmbvhx1FOP8OwutpS9EViIne2HxN6dNaJTvVWfyPAOrdA9su7FKAh+HyrQfvlTwPEJEYW5Md9aX5jT1f2f76IiLyIG1S/gy8G/zb+WDsVVzspLV0aLw3Ce9jgJeBaMhGvZ93b+90xt86oKSDwueAM7JTjxgeNJOL0B3pr7QzlRhMRCxDl6veUfQ7o5q9YzOr1RI7cMINeyW7oQhqkyaoXa8Am4BH6LiWzmLOjMY4SiE5QPO4RVj95EhRVYFAtrrnUDMwZAftSjqhBq3qLXGNnLXm4QSwmgjaGOJ0wXqdH6BryXKALFB/hhUAFdW0YMdZzAOd27adHH2YDvDDeGvimJpAVmHDNDG1pLDHjlgXXc4QQP8TpmvhcSqJx7wgY8v/qcj00VREI+uI3F6CJScW2N8Bsa9mSzHpiyclCYkQyM4G8MEXGdfMm0CoLzeyZLf6P2sRtRjnGdbkdp3QP7frlDVOjUAe+8gsBu2K+PhyoZ6Rn+oNOMVWuftIEsy68KkEPwgy1AIwtWAEQKD3T+yRSNmRK1rznLr2HFTQJK0RI4OuBWDvmrlf4pSqC3Ri9uDcki/DOcTpVzwejOSSTrn1zYafTmeVN9JLzTHfIkdjQxSRJiOrgFxE0Rd/9iDeioj8VFBlvFkM5WX2Op2WKZefQVCuTs4ccnHt56V49yxukM0CeA=
```
We also get a single Go script:
```go {linenos=true}
package main

import (
        "bufio"
        "crypto/sha256"
        "encoding/base64"
        "fmt"
        "io/ioutil"
        "os"
        "strings"
        "time"

        "./math/rand" // same as default implementation, with different rngCooked array
        "github.com/dchest/wots"
)

const defaultFlag string = "CTF{xxx}"

func main() {
        var message = []byte("Sign me if you can")

        // Not so secure seed, but prng internals are secret
        rng := rand.New(rand.NewSource(time.Now().UnixNano()))

        for {
                var ots = wots.NewScheme(sha256.New, rng)
                priv, pub, _ := ots.GenerateKeyPair()

                fmt.Println("Public key:", base64.StdEncoding.EncodeToString(pub))

                reader := bufio.NewReader(os.Stdin)
                fmt.Print("Enter signature: ")
                text, err := reader.ReadString('\n')
                if err != nil {
                        fmt.Println("Error occurred. Please try again later.")
                        return
                }

                text = strings.TrimSuffix(text, "\n")
                signature, err := base64.StdEncoding.DecodeString(text)
                if err != nil {
                        return
                }

                if ots.Verify(pub, message, signature) {
                        fmt.Print("Congratulations! Flag: ")

                        flag, err := ioutil.ReadFile("secret")
                        if err != nil {
                                fmt.Println(defaultFlag)
                        } else {
                                fmt.Println(string(flag))
                        }
                } else {
                        fmt.Println("You failed! Private key was:", base64.StdEncoding.EncodeToString(priv))
                        fmt.Println()
                }
        }
}
```

It is clear that the service on `ots-sig.donjon-ctf.io:4001` is the Go script. The goal of the challenge is then to find a valid signature of the message `Sign me if you can` given only the public key and possibly some previous private keys. 

The signature scheme is the [Lamport signature scheme](https://en.wikipedia.org/wiki/Lamport_signature) implemented in the [wots](https://github.com/dchest/wots) Go package. I assumed that this implementation is secure (it's a bit unethical to exploit a 0-day in an open-source project). 

# Exploit
To start, I looked at the code for generating a `PrivateKey` from a RNG. [The answer](https://github.com/dchest/wots/blob/b19125f232231228ca68fda9dfe9dfde490cc3c0/wots.go#L86) is straightforward, the private key just holds the next $N$ bytes of the RNG, where $N=B*(B+2)$ is the size of the private key, and $B$ is the size of the hash function. This challenge uses SHA256, so we have $B=32$ and $N=1088$.

So the challenge allows us to get as many subsequent private keys (from a single seed) as we want. As we have just seen, this is equivalent to being able to stream the RNG `rand.New(rand.NewSource(time.Now().UnixNano()))`. Therefore, if we break the RNG, meaning we're able to guess the following 1088 bytes given an arbitrary number or previous bytes, we win.

At this point, it is worth looking back at the challenge description and also line 13 in the Go script:
```go {linenos=true, linenostart=13}
import "./math/rand" // same as default implementation, with different rngCooked array
```
So the RNG used is the same as the standard `math/rand` but with different constants (otherwise the challenge would be straightforward since we could just bruteforce the seed). `rngCooked` and the RNG logic in general are defined [here](https://github.com/golang/go/blob/master/src/math/rand/rng.go).

After staring at this file for a while, I found the potential vulnerability[^rngvuln]. Here is the [function](https://github.com/golang/go/blob/f2ee58b6bb3d8312dad2ed7826c1a0e67aea8483/src/math/rand/rng.go#L237) to generate `uint64` (which is used to generate random bytes):
```go {linenos=true, linenostart=237}
// Uint64 returns a non-negative pseudo-random 64-bit integer as an uint64.
func (rng *rngSource) Uint64() uint64 {
    rng.tap--
    if rng.tap < 0 {
        rng.tap += rngLen
    }

    rng.feed--
    if rng.feed < 0 {
        rng.feed += rngLen
    }

    x := rng.vec[rng.feed] + rng.vec[rng.tap]
    rng.vec[rng.feed] = x
    return uint64(x)
}
```
For some context, `rng.vec` is the RNG state represented by a vector of $\texttt{rngLen}=607$ `int64` elements. `rng.tap` and `rng.feed` are two counters ranging from 0 to `rngLen` and originally set at 333 and 606 respectively. The "vulnerability" is at line 250. Every time the function is called, the state element `rng.vec[rng.feed]` is replaced by the returned value[^cast]. So after having observed `rngLen` calls to this function `Uint64`, we can deduce the RNG state and thus compute the RNG's next values, without knowing anything about the original state nor the seed. 

However, in this challenge we do not get raw `uint64` values from the RNG, but bytes. So, let's see how random bytes are generated from the RNG. This is implemented [here](https://github.com/golang/go/blob/f2ee58b6bb3d8312dad2ed7826c1a0e67aea8483/src/math/rand/rand.go#L267):
```go {linenos=true, linenostart=267}
func read(p []byte, src Source, readVal *int64, readPos *int8) (n int, err error) {
    pos := *readPos
    val := *readVal
    rng, _ := src.(*rngSource)
    for n = 0; n < len(p); n++ {
        if pos == 0 {
            if rng != nil {
                val = rng.Int63()
            } else {
                val = src.Int63()
            }
            pos = 7
        }
        p[n] = byte(val)
        val >>= 8
        pos--
    }
    *readPos = pos
    *readVal = val
    return
}
```
A few things to note:
- `rng.Int63` is just the signed version of `rng.Uint64` that we analyzed above.
- The function `read` works by iteratively generating a `Int63`, and writing the first (little-endian) 7 bytes of this value to the buffer.
- After the 7 bytes have been written, the rest is discarded, a new `Int63` is generated and the process continues.
- This means that we get back the first $7*8=56$ bits of every value generated by the RNG.

I think this is the appropriate time to introduce our good friend [Z3](https://github.com/Z3Prover/z3).

# Modelling the problem with Z3
To recapitulate:
1. After observing `7*rngLen` bytes, we can deduce the first 56 bits of every element of the RNG's state.
2. Afterwards, we can observe 56 bits of an arbitrary number of linear combinations of state elements.

The state is a vector of $\texttt{rngLen}$ `int64` elements. We can thus model them with a list of $\texttt{rngLen}$ `z3.BitVec('state_i', 65)` elements:
```python
state = [z3.BitVec(f'state_{i}', 65) for i in range(rngLen)]
```
Then, by 1., after observing `7*rngLen` bytes, I create a list `masked_state` of `rngLen` 56-bits integers and set the constraints:
```python
s = z3.Solver()
for i in range(rngLen):
    s.add(state[i] & mask == masked_state[i])
```
where `mask = (1<<56)-1` is the 56 bits mask.
Then, by 2., whenever we observe 7 bytes `seven_bytes`, we can create a (little-endian) 56-bits integer from them and do the following:
```python
x = int.from_bytes(seven_bytes, 'little')
y = state[feed] + state[tap]
s.add((y & mask) == x)
state[feed] = y
```
We can then repeat this process infinitely (by also decrementing the counters `tap` and `feed`).

It turns out that after `2*rngLen*7` observed bytes, Z3 manages to correctly recover the state. After that, it's easy to solve the challenge by generating the next 1088 bytes from the RNG, give them to the `wots` Go package to sign the message and get the flag.

# Full solution
Here is the full solution in Python:
```python {linenos=true}
from pwn import remote
import re
import base64
import z3
import subprocess

# Open socket and recover 13 private keys.
def open_socket():
    private_keys = []
    r = remote('ots-sig.donjon-ctf.io', 4001)
    r.recvuntil("Public key")
    for i in range(13):
        r.sendline('bG9sCg==')
        s = r.recvuntil("Public key")
        sk = re.findall(b'.*Private key was:\s*(.*)', s)[0]
        private_keys.append(base64.b64decode(sk))

    return private_keys, r

# Reverse the RNG state given only the RNG's first N raw bytes.
def reverse_rng(raw_bytes):
    blockSize = 1088
    rngLen = 607
    rngTap = 273

    mask = (1 << (7 * 8)) - 1

    masked_state = [0 for _ in range(rngLen)]
    feed = rngLen - rngTap - 1
    tap = rngLen - 1
    for i in range(rngLen):
        x = int.from_bytes(raw_bytes[i * 7:(i + 1) * 7], 'little')
        masked_state[feed] = x
        feed -= 1
        if feed < 0:
            feed += rngLen

    s = z3.Solver()
    state = [z3.BitVec(f'v_{i}', 65) for i in range(rngLen)]
    for i in range(rngLen):
        s.add(state[i] & mask == masked_state[i])
    for i in range(rngLen, 3 * rngLen):
        x = int.from_bytes(raw_bytes[i * 7:(i + 1) * 7], 'little')
        y = state[feed] + state[tap]
        s.add((y & mask) == x)
        state[feed] = y
        feed -= 1
        if feed < 0:
            feed += rngLen
        tap -= 1
        if tap < 0:
            tap += rngLen

    print("The Z3 model is: ", s.check())
    model = s.model()
    further_bytes = b''
    for i in range(3 * rngLen, 5 * rngLen):
        x = int.from_bytes(raw_bytes[i * 7:(i + 1) * 7], 'little')
        y = state[feed] + state[tap]
        yl = model.eval(state[feed] + state[tap]).as_long()
        further_bytes += int.to_bytes(yl & mask, 7, 'little')
        state[feed] = y
        feed -= 1
        if feed < 0:
            feed += rngLen
        tap -= 1
        if tap < 0:
            tap += rngLen
    return further_bytes[13 * blockSize - 21 * rngLen:14 * blockSize -
                         21 * rngLen]

private_keys, socket = open_socket()
raw_bytes = b''.join(private_keys)
next_private_key = reverse_rng(raw_bytes)
signature = subprocess.check_output(
    ["../go/bin/go", "run", "sol.go",
     base64.b64encode(next_private_key)])

socket.sendline(signature.strip())
socket.recvuntil("Enter signature: ")
print(socket.recvline().decode())
```
I call the following Go script on line 75 to generate the signature:
```go
package main

import (
        "crypto/sha256"
        "encoding/base64"
        "fmt"
        "github.com/dchest/wots"
        "math/rand"
        "os"
        "time"
)

func main() {
        var message = []byte("Sign me if you can")
        rng := rand.New(rand.NewSource(time.Now().UnixNano()))
        var ots = wots.NewScheme(sha256.New, rng)
        priv, _ := base64.StdEncoding.DecodeString(os.Args[1])
        s, _ := ots.Sign(priv, message)
        fmt.Println(base64.StdEncoding.EncodeToString(s))
}
```
Running the Python script then outputs the flag:
```
The Z3 model is:  sat
Congratulations! Flag: CTF{m4th_RanD_1s_s0_pr3d1cT4bl3}
```

# Conclusion
This was a really nice challenge, especially when seen as a Z3 exercise. It's also cool to reverse a real-world RNG that can probably be found in the wild if people forget to use `crypto/rand`. Also during the challenge, googling for variations of "reversing golang math/rand" didn't get me anything, so solving this challenge kind of felt like finding a 0-day, which was nice :)

[^rngvuln]: Of course this isn't a vulnerability *per se*, as the `math/rand` RNG does not pretend to be cryptographically secure.

[^cast]: Well, that last sentence isn't totally true, since we get back the `uint64`-casted value of this state element. But as we'll see, it doesn't matter.
