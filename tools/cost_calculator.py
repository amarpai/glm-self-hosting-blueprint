#!/usr/bin/env python3
"""Compare self-hosted GPU inference cost against per-token API pricing.

Every default is an assumption: replace with your own quotes and usage data.
"""
import argparse


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--engineers", type=int, default=2000)
    p.add_argument("--tokens-per-engineer-day", type=float, default=2_000_000,
                   help="input+output tokens per engineer per working day (agents use a lot)")
    p.add_argument("--work-days", type=int, default=21, help="working days per month")
    p.add_argument("--api-price-per-m", type=float, default=3.00,
                   help="blended API $ per 1M tokens (after cache discounts)")
    p.add_argument("--gpus", type=int, default=56)
    p.add_argument("--gpu-hour-cost", type=float, default=3.50,
                   help="$ per GPU-hour (reserved cloud, or amortised capex + power)")
    p.add_argument("--ops-monthly", type=float, default=40_000,
                   help="$ per month for the platform team, storage, networking")
    a = p.parse_args()

    monthly_tokens = a.engineers * a.tokens_per_engineer_day * a.work_days
    api_cost = monthly_tokens / 1e6 * a.api_price_per_m
    gpu_cost = a.gpus * a.gpu_hour_cost * 24 * 30
    self_cost = gpu_cost + a.ops_monthly
    self_per_m = self_cost / (monthly_tokens / 1e6)

    print(f"Monthly tokens         : {monthly_tokens / 1e9:,.1f} B")
    print(f"API cost / month       : ${api_cost:,.0f}  (${a.api_price_per_m:.2f}/M)")
    print(f"Self-hosted / month    : ${self_cost:,.0f}  (${self_per_m:.2f}/M)")
    print(f"  GPUs                 : ${gpu_cost:,.0f}  ({a.gpus} GPUs)")
    print(f"  Ops & platform       : ${a.ops_monthly:,.0f}")
    saving = 1 - self_cost / api_cost if api_cost else 0
    print(f"Saving vs API          : {saving:.0%}")
    breakeven = self_cost / a.api_price_per_m * 1e6
    print(f"Break-even volume      : {breakeven / 1e9:,.1f} B tokens/month")
    if saving <= 0:
        print("-> At this volume, stay on the API. Self-hosting pays off only at scale.")
    print("\nNote: assumes your cluster can actually serve this volume. Load-test first.")


if __name__ == "__main__":
    main()
