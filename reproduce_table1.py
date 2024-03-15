"""Recompute the derived columns of Table 1 from the recorded per-order latencies.

Shows that the reported throughput is exactly the reciprocal of mean latency, so it
describes one sequential pipeline rather than the system under concurrent load, and
quantifies how far the tail and the median sit from the mean.
"""
import csv

rows = list(csv.DictReader(open("results/table1_latency_us.csv")))
print(f"{'orders':>7} {'mean_us':>8} {'1/mean per s':>13} {'reported':>9} {'max/mean':>9} {'median/mean':>12}")
for r in rows:
    mean, mx = float(r["mean_us"]), float(r["max_us"])
    derived = round(1 / (mean * 1e-6))
    med = f"{float(r['median_us']) / mean:.1f}" if r["median_us"] else "not recorded"
    print(f"{r['orders']:>7} {mean:8.3f} {derived:13,} {int(r['reported_throughput']):9,} {mx / mean:9.0f} {med:>12}")
