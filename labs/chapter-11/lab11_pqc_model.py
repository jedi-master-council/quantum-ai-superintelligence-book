"""Chapter 11 labs: protect an AI model file with post-quantum cryptography, and estimate how long
protected assets must stay secret.

Lab 11.1  Hybrid envelope protection of a model file.
          * Confidentiality: a fresh AES-256-GCM key per file, derived with HKDF-SHA256 from two shared
            secrets, one from X25519 and one from ML-KEM-768 (FIPS 203). An attacker must break both.
          * Integrity and origin: a manifest (file name, size, SHA-256, algorithms) signed with both
            Ed25519 and ML-DSA-65 (FIPS 204).
          * Baseline: RSA-3072 (OAEP key transport, PSS signature), the classical choice today.
          Measures key, ciphertext and signature sizes, operation times, and checks tamper detection.
Lab 11.2  Mosca's inequality as a Monte Carlo model: the probability that an asset with shelf life x,
          protected by a migration that takes y years, is exposed before a cryptographically relevant
          quantum computer (CRQC) arrives at year z. The CRQC date range is the author's assumption.
Tested with cryptography 50.0.1 (which provides ML-KEM and ML-DSA through OpenSSL) and numpy 2.x.
"""
import json, os, sys, time, hashlib
import numpy as np
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import x25519, ed25519, rsa, padding, mlkem, mldsa
from cryptography.exceptions import InvalidTag, InvalidSignature

OUT = sys.argv[1] if len(sys.argv) > 1 else "lab11_results.json"
REPS = 200
res = {}
RAW = serialization.Encoding.Raw, serialization.PublicFormat.Raw
DER = serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo

def timeit(fn, reps=REPS):
    t0 = time.perf_counter()
    for _ in range(reps):
        out = fn()
    return (time.perf_counter() - t0) / reps * 1e3, out          # milliseconds per call

# ---------------------------------------------------------------- key generation
print("Lab 11.1 ...")
t_kg = {}
t_kg["X25519"], x_sk = timeit(x25519.X25519PrivateKey.generate)
t_kg["ML-KEM-768"], k_sk = timeit(mlkem.MLKEM768PrivateKey.generate)
t_kg["Ed25519"], e_sk = timeit(ed25519.Ed25519PrivateKey.generate)
t_kg["ML-DSA-65"], d_sk = timeit(mldsa.MLDSA65PrivateKey.generate)
t_kg["RSA-3072"], r_sk = timeit(lambda: rsa.generate_private_key(65537, 3072), reps=10)
x_pk, k_pk, e_pk, d_pk, r_pk = x_sk.public_key(), k_sk.public_key(), e_sk.public_key(), d_sk.public_key(), r_sk.public_key()

# ---------------------------------------------------------------- hybrid key establishment
def wrap_hybrid():
    eph = x25519.X25519PrivateKey.generate()
    ss1 = eph.exchange(x_pk)
    ss2, ct = k_pk.encapsulate()
    key = HKDF(hashes.SHA256(), 32, salt=None, info=b"model-file v1 X25519+ML-KEM-768").derive(ss1 + ss2)
    return key, eph.public_key().public_bytes(*RAW), ct

def unwrap_hybrid(eph_pub, ct):
    ss1 = x_sk.exchange(x25519.X25519PublicKey.from_public_bytes(eph_pub))
    ss2 = k_sk.decapsulate(ct)
    return HKDF(hashes.SHA256(), 32, salt=None, info=b"model-file v1 X25519+ML-KEM-768").derive(ss1 + ss2)

OAEP = padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
def wrap_rsa():
    key = os.urandom(32); return key, r_pk.encrypt(key, OAEP)

t_ops = {}
t_ops["hybrid KEM: encapsulate"], (key_h, eph_pub, ct_k) = timeit(wrap_hybrid)
t_ops["hybrid KEM: decapsulate"], key_h2 = timeit(lambda: unwrap_hybrid(eph_pub, ct_k))
assert key_h == key_h2
t_ops["X25519 only: exchange"], _ = timeit(lambda: x25519.X25519PrivateKey.generate().exchange(x_pk))
t_ops["ML-KEM-768 only: encapsulate"], (ssk, ctk) = timeit(k_pk.encapsulate)
t_ops["ML-KEM-768 only: decapsulate"], _ = timeit(lambda: k_sk.decapsulate(ctk))
t_ops["RSA-3072 OAEP: encrypt key"], (key_r, ct_r) = timeit(wrap_rsa)
t_ops["RSA-3072 OAEP: decrypt key"], _ = timeit(lambda: r_sk.decrypt(ct_r, OAEP))

# ---------------------------------------------------------------- signatures over a manifest
PSS = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)
msg = b"x" * 512
t_ops["Ed25519: sign"], sig_e = timeit(lambda: e_sk.sign(msg))
t_ops["Ed25519: verify"], _ = timeit(lambda: e_pk.verify(sig_e, msg))
t_ops["ML-DSA-65: sign"], sig_d = timeit(lambda: d_sk.sign(msg))
t_ops["ML-DSA-65: verify"], _ = timeit(lambda: d_pk.verify(sig_d, msg))
t_ops["RSA-3072 PSS: sign"], sig_r = timeit(lambda: r_sk.sign(msg, PSS, hashes.SHA256()))
t_ops["RSA-3072 PSS: verify"], _ = timeit(lambda: r_pk.verify(sig_r, msg, PSS, hashes.SHA256()))

sizes = {
    "X25519": dict(public_key=len(x_pk.public_bytes(*RAW)), ciphertext=32, signature=None),
    "ML-KEM-768": dict(public_key=len(k_pk.public_bytes_raw()), ciphertext=len(ctk), signature=None),
    "RSA-3072 (OAEP)": dict(public_key=len(r_pk.public_bytes(*DER)), ciphertext=len(ct_r), signature=None),
    "Ed25519": dict(public_key=len(e_pk.public_bytes(*RAW)), ciphertext=None, signature=len(sig_e)),
    "ML-DSA-65": dict(public_key=len(d_pk.public_bytes_raw()), ciphertext=None, signature=len(sig_d)),
    "RSA-3072 (PSS)": dict(public_key=len(r_pk.public_bytes(*DER)), ciphertext=None, signature=len(sig_r)),
}

# ---------------------------------------------------------------- protect model files of several sizes
def protect(blob, name):
    key, eph, ct = wrap_hybrid()
    nonce = os.urandom(12)
    manifest = json.dumps(dict(file=name, bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest(),
                               kem="X25519+ML-KEM-768", aead="AES-256-GCM", sig="Ed25519+ML-DSA-65"),
                          sort_keys=True).encode()
    enc = AESGCM(key).encrypt(nonce, blob, manifest)                    # manifest bound as associated data
    return dict(eph=eph, kem_ct=ct, nonce=nonce, enc=enc, manifest=manifest,
                sig_e=e_sk.sign(manifest), sig_d=d_sk.sign(manifest))

def open_(pkg):
    e_pk.verify(pkg["sig_e"], pkg["manifest"]); d_pk.verify(pkg["sig_d"], pkg["manifest"])
    key = unwrap_hybrid(pkg["eph"], pkg["kem_ct"])
    blob = AESGCM(key).decrypt(pkg["nonce"], pkg["enc"], pkg["manifest"])
    assert hashlib.sha256(blob).hexdigest() == json.loads(pkg["manifest"])["sha256"]
    return blob

rng = np.random.default_rng(11)
files = []
for mb in (1, 10, 100):
    blob = rng.standard_normal(mb * 2 ** 18).astype(np.float32).tobytes()   # mb MiB of float32 "weights"
    reps = 5 if mb == 100 else 20
    tp, pkg = timeit(lambda: protect(blob, f"model_{mb}MiB.bin"), reps=reps)
    to, back = timeit(lambda: open_(pkg), reps=reps)
    assert back == blob
    overhead = (len(pkg["eph"]) + len(pkg["kem_ct"]) + len(pkg["nonce"]) + (len(pkg["enc"]) - len(blob))
                + len(pkg["manifest"]) + len(pkg["sig_e"]) + len(pkg["sig_d"]))
    files.append(dict(MiB=mb, protect_ms=tp, open_ms=to, overhead_bytes=overhead))

# ---------------------------------------------------------------- tamper tests
blob = rng.standard_normal(2 ** 18).astype(np.float32).tobytes()
pkg = protect(blob, "model.bin")
tests = {}
def expect_fail(mod, name):
    p = dict(pkg); mod(p)
    try:
        open_(p); tests[name] = "NOT DETECTED"
    except (InvalidTag, InvalidSignature, ValueError) as e:
        tests[name] = "detected: " + type(e).__name__
expect_fail(lambda p: p.update(enc=p["enc"][:1000] + bytes([p["enc"][1000] ^ 1]) + p["enc"][1001:]), "one bit of the encrypted weights flipped")
expect_fail(lambda p: p.update(manifest=p["manifest"].replace(b"model.bin", b"model.bim")), "file name in the manifest changed")
expect_fail(lambda p: p.update(sig_d=bytes(len(p["sig_d"]))), "post-quantum signature replaced")
expect_fail(lambda p: p.update(kem_ct=p["kem_ct"][:-1] + bytes([p["kem_ct"][-1] ^ 1])), "ML-KEM ciphertext altered")
res["lab11_1"] = dict(keygen_ms=t_kg, ops_ms=t_ops, sizes_bytes=sizes, files=files, tamper=tests)

# ---------------------------------------------------------------- Lab 11.2: Mosca's inequality
print("Lab 11.2 ...")
S = 200_000
z_year = rng.uniform(2032, 2045, S)                 # CRQC year: author's assumption, see text
assets = {"model weights (frontier)": (2, 5), "training data with personal information": (10, 25),
          "quantum circuits and calibration data": (1, 3), "safety evaluations and red-team findings": (3, 10)}
mosca = {}
for start in (2026, 2030, 2035):
    for mig in ((2, 6),):
        y = rng.uniform(*mig, S)
        for a, (lo, hi) in assets.items():
            x = rng.uniform(lo, hi, S)
            # Mosca: data protected classically until migration completes at start + y. The last classical
            # ciphertext, recorded at start + y, must stay secret for x more years; it is exposed if a CRQC
            # exists before start + y + x.
            exposed = start + y + x > z_year
            mosca.setdefault(str(start), {})[a] = float(np.mean(exposed))
curve = {}
xs = np.arange(0, 31)
for start in (2026, 2030, 2035):
    y = rng.uniform(2, 6, S)
    curve[str(start)] = [float(np.mean(start + y + xv > z_year)) for xv in xs]
res["lab11_2_curve"] = dict(shelf_life_years=xs.tolist(), p_exposed=curve)
res["lab11_2"] = dict(assumptions=dict(crqc_year=[2032, 2045], migration_years=[2, 6], shelf_life=assets),
                      p_exposed=mosca)
json.dump(res, open(OUT, "w"), indent=1, default=float)
print(json.dumps({k: res["lab11_1"][k] for k in ("keygen_ms", "ops_ms", "sizes_bytes")}, indent=1, default=float))
