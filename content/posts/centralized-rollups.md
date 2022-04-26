---
title: "The case for centralized rollups"
date: 2022-04-25
description: ""
slug: ""
tags: [rollups]
---

Common wisdom is that rollups should be decentralized. In fact, most rollups have decentralization of sequencers/validators/provers on their roadmap. In this post, I argue that fully centralized rollups are viable and secure.

## What does a centralized rollup look like?
In a centralized rollup, a single actor controls sequencing and block production. Users send transactions directly to this actor, i.e, there is no public mempool. This actor then constructs a block with some of the transactions it has received and pushes them to L1, along with a state transition validity proof in the case of a zk-rollup. 

### Security
The security of a centralized rollup looks pretty bad at first sight, since only a single actor controls every step of the transaction lifecycle. This can be fixed by using an escape hatch, i.e., a mechanism for users to push transactions directly to L1. Then if the centralized actor goes down or acts maliciously, users can simply withdraw their funds to L1. Note that the escape hatch should allow users to make L2 transactions before withdrawal to, e.g., recover funds locked in a liquidity pool.

I will also assume that the L1 is decentralized and secure, otherwise talking about L2 security doesn’t make much sense.

## Criticisms
Here are some criticisms I’ve heard about centralized rollups.

### Censorship resistance
The main criticism of centralized systems is the lack of censorship resistance. In the case of a centralized rollup, the central actor could refuse to process transactions coming from a specific address. I don’t think this argument holds since censorship is also possible in decentralized systems. For example, good luck making an ETH transaction if the top mining pools want to censor you. 

The solution to censorship is reputation, not decentralization. If a centralized rollup starts censoring an address, it would be easy to prove it and tell the world about it. Users that care about censorship resistance (most of them hopefully) would then be able to flee the rollup using the escape hatch. Most applications building on the rollup would probably do the same which would lead to the rollup’s death. It is thus very unlikely that a centralized rollup would sacrifice its reputation and community by censoring addresses. And even if this were to happen, no funds would be lost in the process thanks to the escape hatch.



### Regulatory issues 
A centralized rollup would be more vulnerable to regulatory pressure than a decentralized system. IANAL so I don’t have clear insight on how serious this concern is. My first thought is that regulators should have enough work with all the scammy things going on in crypto before attacking legitimate use cases like rollups. In any case, centralized rollups are not bound to a given server. In case of regulatory issues, it is trivial to just change the location of the rollup server.

### Downtime 
It is inevitable that any centralized system will experience downtime at some point. Many precautions can be taken to reduce the frequency and length of such downtimes, but it wouldn’t be realistic to claim they will never happen. To me this is the only issue with centralized rollups that can’t be fixed without adding some significant overhead. Note that downtimes aren’t particularly risky for users since, as long as the L1 is up, the escape hatch would allow them to leave the L2.

## Advantages

### Performance 
There are lots of performance benefits to centralization. For example, every message needs to only be passed once, i.e., there’s no need for any gossiping. In the case of a zk-rollup, the whole sequencing-proving pipeline can be performed by a single server which makes it more efficient and parallelizable. 

Importantly, no decentralization means no need for incentives and thus no need for slashing either. So there wouldn't be any consensus- or slashing-related downtimes in a centralized rollup.

### No need for a token 
Sorry VCs but a centralized rollup doesn’t need a token. Case in point, no rollups that are live now have a token. We touched on the reason why above, i.e., there’s no need for incentives in a centralized system. The only incentive is for the centralized actor to keep things running smoothly in order to collect fees and other revenues (see below).

If you really want a token, you can always have a governance token to vote on new features for the rollup. But the fact that a token is not inherently needed is definitely a plus.

### Benevolent sequencer
The centralized rollup could vow to not extract malicious MEV, like sandwich attacks, from users. It would be easy to detect if the sequencer does perform such extraction and, as with censoring, we’d see users leave the rollup if that were the case. This is obviously not possible in a decentralized system. 
Therefore a centralized rollup could have much better UX for users, in the form of better DEX prices. 

Note that this is not only a theoretical argument, as we see users on Ethereum do similar things by sending their transactions to centralized relayers (e.g. Flashbots) to avoid getting sandwiched. 

### For-profit rollup
The last section was about malicious MEV and how a centralized rollup solves it. What about beneficial MEV like arbitrages (keeping prices efficient on the network) and liquidations (helping borrowing platforms stay solvent)? 

A centralized sequencer could easily extract such MEV and make a profit along the way. These profits wouldn’t be made on the back of users, and would actually help the network. 

Moreover, the rollups could reinvest the profits into the network by: reducing fees, public good funding, buyback+burn of tokens (if the rollup has a token), or airdropping users. How the profits are used could be decided using some governance system.

Now this MEV extraction would be totally optional. Some users might be uneasy with the rollup performing arbitrages and liquidations, and the rollup would function perfectly well without performing such extractions. It is, however, interesting to ask if the value behind such extractions would not be better used by the rollup than by some profit-seeking MEV searchers. I would argue that the average user, who probably doesn’t run an arbitrage or liquidation bot, would benefit more from the centralized actor extracting this kind of MEV and reinvesting it in the network. 

## Conclusion
It is kind of easy to just sweep every issue with centralized rollups under the escape hatch rug. In practice, having to leave a malicious centralized rollup would be a massive annoyance (note that it would also be easy to fork the rollup in such cases). But I think the upsides are significant and cannot be ignored.

Anyway, I think this is an interesting avenue to explore and I wouldn’t be surprised if a centralized rollup ends up winning the coming rollup wars. 

