"""bench_aes_overhead.py: Benchmark AES-256-GCM hardware/software encryption in order path."""
import time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def benchmark_crypto():
    key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(key)
    nonce = b"123456789012"
    payload = b"BUY 10.5 ETH @ 5250000 NGN ORDER_ID_987654321 TIMESTAMP_1719478560"

    N = 20000
    t0 = time.perf_counter_ns()
    for _ in range(N):
        ct = aesgcm.encrypt(nonce, payload, None)
    t_enc = (time.perf_counter_ns() - t0) / N / 1000.0

    t0 = time.perf_counter_ns()
    for _ in range(N):
        pt = aesgcm.decrypt(nonce, ct, None)
    t_dec = (time.perf_counter_ns() - t0) / N / 1000.0

    print("=== AES-256-GCM Cryptographic Latency Benchmark ===")
    print(f"Payload size: {len(payload)} bytes")
    print(f"Encryption latency: {t_enc:.3f} us | Decryption latency: {t_dec:.3f} us")
    print(f"Total round-trip crypto overhead: {t_enc + t_dec:.3f} us")
    print(f"Baseline ULLIPS engine mean: 1.451 us")
    print(f"Impact: Cryptographic verification adds {((t_enc+t_dec)/1.451)*100:.1f}% overhead to order path.")

if __name__ == '__main__':
    benchmark_crypto()
