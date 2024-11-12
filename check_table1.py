"""Three checks on Table 1, using only the numbers the table reports.

1. Consistency. At least half of any sample sits at or above its median, and every
   value sits at or above its minimum, so mean >= (median + minimum) / 2. If the
   reported mean is below that bound, the three statistics cannot describe the same
   set of measurements.

2. Amortisation. If larger workloads only spread a fixed start-up cost over more
   orders, mean latency follows mean(N) = c + F / N. Fit c and F on the two smallest
   workloads and see whether the model predicts the two largest.

3. The single slowest order. How much of the total measured time one order accounts
   for, and what the mean would be without it.
"""
import csv

rows = [
    {k: (float(v) if v not in ("", None) else None) for k, v in r.items()}
    for r in csv.DictReader(open("results/table1_latency_us.csv"))
]
by_n = {int(r["orders"]): r for r in rows}

print("1. Consistency of minimum, median and mean")
for n, r in sorted(by_n.items()):
    if r.get("median_us") is None:
        continue
    bound = (r["median_us"] + r["min_us"]) / 2
    verdict = "consistent" if r["mean_us"] >= bound else "IMPOSSIBLE"
    print(f"   N={n:>6}: mean must be >= {bound:.2f} us, reported {r['mean_us']:.3f} us -> {verdict}")

print("\n2. Fixed-cost amortisation model, fitted on the two smallest workloads")
(n1, r1), (n2, r2) = sorted(by_n.items())[:2]
F = (r1["mean_us"] - r2["mean_us"]) / (1 / n1 - 1 / n2)
c = r1["mean_us"] - F / n1
print(f"   c = {c:.3f} us per order, F = {F:.0f} us fixed")
for n, r in sorted(by_n.items()):
    pred = c + F / n
    print(f"   N={n:>6}: predicted {pred:.3f}, observed {r['mean_us']:.3f}, error {100 * (r['mean_us'] - pred) / pred:+.0f}%")

print("\n3. Share of total measured time in the single slowest order")
for n, r in sorted(by_n.items()):
    total = n * r["mean_us"]
    without = (total - r["max_us"]) / (n - 1)
    print(f"   N={n:>6}: {100 * r['max_us'] / total:.1f}% of total; mean without it {without:.3f} us")
