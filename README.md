# ULLIPS: ultra-low latency processing on commodity hardware

Revised preprint, LaTeX source, and a recomputation of the paper's results table.

**Ultra-Low Latency Intelligent Processing System: A Software-Optimised and Machine-Learning-Augmented Architecture**
A. C. Adegboyega, K. O. Enaikele and Adeyiga, Bells University of Technology. Revised manuscript, 2026.

| File | Contents |
|---|---|
| [`paper/Adegboyega_ULLIPS_revised_2026.pdf`](paper/Adegboyega_ULLIPS_revised_2026.pdf) | The revised preprint |
| [`paper/ullips.tex`](paper/ullips.tex) | LaTeX source (compile with `tectonic ullips.tex`) |
| [`results/table1_latency_us.csv`](results/table1_latency_us.csv) | Table 1 summary statistics per workload |
| [`reproduce_table1.py`](reproduce_table1.py) | Recomputes the derived columns |
| [`check_table1.py`](check_table1.py) | Tests the paper's claims against its own table |

Both scripts use only the Python standard library: `python3 reproduce_table1.py` and `python3 check_table1.py`.

## What recomputing Table 1 shows

```
 orders  mean_us  1/mean per s  reported  max/mean  median/mean
   1000    4.027       248,324   248,324        56          9.3
   2000    3.261       306,654   306,654        80 not recorded
  10000    4.444       225,023   225,023       649 not recorded
  40000    1.451       689,180   689,180      3972 not recorded
```

- **Throughput was derived, not measured.** The reported figure equals 1 / mean latency in every row,
  so it describes one sequential pipeline, not the system under concurrent load.
- **The reported statistics for the 1,000-order run cannot all be true.** At least half of any sample
  lies at or above its median and all of it at or above its minimum, so the mean cannot be below
  (37.5 + 2.208) / 2 = 19.9 µs. The reported mean is 4.03 µs, so at least one of the three figures was
  computed on different data.
- **Larger workloads do not simply amortise a fixed cost.** A model mean(N) = c + F/N fitted to the
  1,000- and 2,000-order runs misses the 10,000-order run by +68% and the 40,000-order run by -43%.
  The paper's earlier amortisation explanation is withdrawn.
- **The tail dominates.** At 40,000 orders the maximum latency is about four thousand times the mean,
  and that single order is 9.9% of the run's total measured time.

```
$ python3 check_table1.py
1. Consistency of minimum, median and mean
   N=  1000: mean must be >= 19.85 us, reported 4.027 us -> IMPOSSIBLE

2. Fixed-cost amortisation model, fitted on the two smallest workloads
   c = 2.495 us per order, F = 1532 us fixed
   N= 10000: predicted 2.648, observed 4.444, error +68%
   N= 40000: predicted 2.533, observed 1.451, error -43%

3. Share of total measured time in the single slowest order
   N= 40000: 9.9% of total; mean without it 1.307 us
```

Section 5.4 of the paper sets out these limitations in full. The C++ engine source is not included
in this repository.

Contact: christianadegboyega@gmail.com

## Kernel Instrumentation (eBPF)
The script [](scripts/trace_socket_latency.bt) provides a  probe measuring network packet transit time from  to  to isolate Linux kernel socket queuing latency from userspace execution.
