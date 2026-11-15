🚀 Revolut reportedly cut its AI coding bill by ~90%. Here's the architecture, and how your company can copy it.

~2,000 engineers moved off hosted coding assistants onto a self-hosted open-weight model: GLM-5.3, a ~754B-parameter Mixture-of-Experts model that activates only ~40B parameters per token.

The reported setup:
🔹 56 × NVIDIA B200 GPUs = 7 nodes of 8, one model replica per node
🔹 FP4 weights (~380 GB), so a full replica fits on a single node
🔹 Context capped at 256K (the model supports 1M) to fit more users per GPU and cut time-to-first-token
🔹 KV/prefix-cache optimisation, because coding agents resend the same context over and over
🔹 A model router: text and code stay on owned GPUs, and image queries go to hosted vision models
🔹 Result: ≈ $0.30 per million tokens

What other companies can take from it:
1️⃣ Do the maths first. Self-hosting is a fixed cost and only wins at high, steady volume.
2️⃣ Pick precision before hardware. FP4 decides how many GPUs one replica needs.
3️⃣ Size context to real usage, not to the spec sheet.
4️⃣ Engineer for cache hits with sticky routing. For agent workloads this is the biggest throughput lever.
5️⃣ Route, don't rip-and-replace. Keep a hosted model for vision and edge cases.
6️⃣ Track $/M tokens, TTFT and developer happiness together.

Open-weight MoE models have turned AI inference from a growing per-token bill into infrastructure you can tune.

I put together a small open blueprint covering the architecture diagram, a serving config, a model router and a cost calculator 👇
🔗 [link to your GitHub repo]

Would your team self-host, or stay on APIs? 👇

#AI #LLM #MLOps #GPU #OpenSource #GenerativeAI #CostOptimization #NVIDIA #Fintech
