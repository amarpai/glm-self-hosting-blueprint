# How other companies can use this architecture to cut cost

## 1. Check you have the volume
Self-hosting is a fixed cost; APIs are variable. Run `tools/cost_calculator.py` with real
usage numbers. Below roughly tens of billions of tokens a month, a frontier API usually
stays cheaper once you count the platform team.

## 2. Size the cluster to the model, not the hype
- Pick precision first: FP4 roughly halves weight memory compared with FP8, so a
  ~750B MoE fits on one 8-GPU node and each node becomes an independent replica.
- No B200s? A smaller open model (e.g. GLM-5.3-Flash, 320B total / 18B active) fits
  older or fewer GPUs and is often enough for autocomplete and simple edits.

## 3. Cap context to what users actually need
Look at your prompt-length distribution. If p99 is 120K, serving 1M wastes KV memory
and lowers concurrency. Revolut reportedly serves 256K.

## 4. Engineer for cache hits
Coding agents resend large, stable prefixes. Use sticky (session/prefix-hash) routing
and keep prefix caching on. Track cache-hit rate as a first-class metric.

## 5. Route, don't replace
Keep a router in front. Text/code goes to owned GPUs; vision, edge cases or the hardest
tasks can still go to a hosted frontier model. This also gives you a fallback.

## 6. Measure what matters
Dashboard: $/M tokens, TTFT p50/p95, tokens/s per user, cache-hit rate, GPU
utilisation, and developer satisfaction. Cost savings that slow engineers down aren't
savings.

## 7. Don't forget the hidden costs
On-call for the inference stack, model upgrades (Revolut went 5.1 → 5.3), evals,
security review of open weights, and licence terms.
