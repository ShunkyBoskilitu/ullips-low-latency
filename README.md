# ULLIPS: Ultra-Low Latency Order Processing on Commodity Systems

Revised preprint, LaTeX source, statistical proofs, and systems measurement artifacts.

**Ultra-Low Latency Intelligent Processing System: A Software-Optimised and Machine-Learning-Augmented Architecture**  
A. C. Adegboyega, K. O. Enaikele, and Adeyiga. Bells University of Technology / Ricardian Corp. Revised manuscript, 2026.

---

## 1. Repository Contents & Replication Harnesses

| Path | Purpose / Description |
|---|---|
| [`paper/Adegboyega_ULLIPS_revised_2026.pdf`](paper/Adegboyega_ULLIPS_revised_2026.pdf) | Revised preprint incorporating empirical audit and limitation errata |
| [`paper/ullips.tex`](paper/ullips.tex) | Complete LaTeX source (compiles with `tectonic ullips.tex`) |
| [`results/table1_latency_us.csv`](results/table1_latency_us.csv) | Table 1 raw summary latency statistics across workloads (1k to 40k orders) |
| [`reproduce_table1.py`](reproduce_table1.py) | Recomputes derived throughput metrics from raw latency statistics |
| [`check_table1.py`](check_table1.py) | Mathematical consistency proof testing Table 1 data against non-negative latency bounds |
| [`scripts/trace_socket_latency.bt`](scripts/trace_socket_latency.bt) | bpftrace (eBPF) probe measuring transit from `netif_receive_skb` to user-space `recvmsg` |
| [`scripts/p4_switch_matcher.p4`](scripts/p4_switch_matcher.p4) | P4_16 switch pipeline for NetFPGA (stateless touch validation & IEEE 1588 hardware timestamps) |
| [`scripts/llvm_profile_pass.cpp`](scripts/llvm_profile_pass.cpp) | Custom LLVM function pass profiling basic block execution frequencies and loop auto-vectorization |
| [`scripts/bench_aes_overhead.py`](scripts/bench_aes_overhead.py) | Benchmark measuring authenticated AES-256-GCM memory encryption overhead on inbound order packets |

*Note: The proprietary production execution engine core is retained under corporate non-disclosure at Ricardian Corp. This repository contains the complete open-source research replication suite, mathematical audit scripts, kernel tracing probes, compiler passes, and hardware pipeline prototypes.*

---

## 2. Table 1 Statistical Audit & Limitations

Auditing the original experimental data revealed four critical mathematical limitations:

```
 orders  mean_us  1/mean per s  reported  max/mean  median/mean
   1000    4.027       248,324   248,324        56          9.3
   2000    3.261       306,654   306,654        80 not recorded
  10000    4.444       225,023   225,023       649 not recorded
  40000    1.451       689,180   689,180      3972 not recorded
```

1. **Throughput Was Derived, Not Measured**: The reported throughput equals exactly $1 / 	ext{mean}$ in every row, reflecting single-thread sequential loop execution on an isolated core rather than server throughput under concurrent network load.
2. **Table 1 Mean Inconsistency**: At least half of any sample lies at or above its median and all of it at or above its minimum. For non-negative latencies with a median of $37.5\,\mu\text{s}$ and minimum of $2.208\,\mu\text{s}$, the arithmetic mean cannot be below $(37.5 + 2.208) / 2 = 19.85\,\mu\text{s}$. The reported mean of $4.03\,\mu\text{s}$ was computed on a different sample, prompting formal errata.
3. **Fixed-Cost Amortisation Breakdown**: A model $\text{mean}(N) = c + F/N$ fitted on the 1,000- and 2,000-order runs misses the 10,000-order run by $+68\%$ and the 40,000-order run by $-43\%$. The amortisation explanation was formally withdrawn.
4. **Tail Latency Dominance**: At 40,000 orders, the maximum latency ($5.76\,\text{ms}$) is approximately $4,000\times$ the mean, with that single order absorbing $9.9\%$ of total run time due to NUMA cache line invalidations and OS scheduler ticks.

Run the automated verification script:
```bash
python3 check_table1.py
```

---

## 3. Systems Instrumentation & Research Probes

### Kernel Socket Latency (eBPF)
```bash
# Run eBPF socket buffer latency probe
sudo bpftrace scripts/trace_socket_latency.bt
```
Traces kernel socket ingress overhead, demonstrating that socket queue buffering accounted for $71\%$ of end-to-end latency before user space was reached.

### In-Network P4 Filtering (NetFPGA)
The P4 program (`scripts/p4_switch_matcher.p4`) targets Reconfigurable Match Table (RMT) architectures. It enforces line-rate stateless touch validation and hardware PTP timestamping (IEEE 1588) while maintaining stateful book execution on the host to avoid SRAM stage latency violations.

### LLVM Function Profiling
```bash
# Compile and run LLVM basic block profiling pass
clang++ -O3 -shared -fPIC scripts/llvm_profile_pass.cpp -o libllvm_profile.so
```
Profiles basic block execution entropy in `match_limit_order` to analyze the trade-off between AVX2 vectorization on contiguous arrays and branch mispredictions on order cancellations.

### Memory Encryption Latency (AES-256-GCM)
```bash
python3 scripts/bench_aes_overhead.py
```
Measures authenticated packet decryption overhead ($6.41\,\mu\text{s}$ latency penalty) and memory bus lock contention under simulated hardware enclave boundaries.

---

**Author**: Christian Akolade Adegboyega  
**Contact**: adegboyegachristian@gmail.com
