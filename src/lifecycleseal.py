#!/usr/bin/env python3
"""
LifecycleSeal — local-first full job lifecycle evidence bundler and QuantumGuard sealer.
Aggregates sealed packs from VeriQuote, FieldSeal/JobSeal, CloseSeal into one master evidence pack.
Offline. Deterministic. Compatible with QuantumGuard CONTRACT-v1.
"""
import argparse
import json
import hashlib
import base64
from datetime import datetime, timezone
from pathlib import Path

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Note: cryptography not installed. Using stub signatures. pip install cryptography for real Ed25519.")

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load_or_create_key(key_path: Path) -> tuple:
    if not CRYPTO_AVAILABLE:
        return None, "00" * 32
    if key_path.exists():
        with open(key_path, "rb") as f:
            priv = serialization.load_pem_private_key(f.read(), password=None)
        pub = priv.public_key()
        pub_bytes = pub.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        return priv, pub_bytes.hex()
    else:
        priv = Ed25519PrivateKey.generate()
        pub = priv.public_key()
        pub_bytes = pub.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        pem = priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        key_path.write_bytes(pem)
        return priv, pub_bytes.hex()

def sign_payload(priv, payload_hash_hex: str) -> str:
    if not CRYPTO_AVAILABLE or priv is None:
        return "00" * 64
    hash_bytes = bytes.fromhex(payload_hash_hex)
    sig = priv.sign(hash_bytes)
    return sig.hex()

def build_lifecycle_pack(lifecycle_data: dict, priv, pub_hex: str) -> dict:
    """Build deterministic QuantumGuard CONTRACT-v1 evidence pack for full job lifecycle."""
    payload_obj = {
        "version": "1",
        "type": "job_lifecycle",
        "job_id": lifecycle_data.get("job_id", "unknown"),
        "client": lifecycle_data.get("client", ""),
        "quote_pack_hash": lifecycle_data.get("quote_pack_hash", ""),
        "field_pack_hashes": lifecycle_data.get("field_pack_hashes", []),
        "close_pack_hash": lifecycle_data.get("close_pack_hash", ""),
        "invoice_pack_hash": lifecycle_data.get("invoice_pack_hash", ""),
        "summary": lifecycle_data.get("summary", ""),
        "status": lifecycle_data.get("status", "complete"),
        "operator": lifecycle_data.get("operator", "field-tech"),
        "bundled_at": lifecycle_data.get("bundled_at", datetime.now(timezone.utc).isoformat()),
        "notes": lifecycle_data.get("notes", "")
    }
    payload_bytes = json.dumps(payload_obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.b64encode(payload_bytes).decode("ascii")
    payload_hash = sha256_hex(payload_bytes)
    signature = sign_payload(priv, payload_hash)

    pack = {
        "version": "1",
        "payload": payload_b64,
        "payload_hash": payload_hash,
        "signature": signature,
        "public_key": pub_hex,
        "alg": "ed25519"
    }
    return pack

def demo():
    sample = {
        "job_id": "JOB-2026-LIFE-001",
        "client": "Acme HVAC Repair",
        "quote_pack_hash": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
        "field_pack_hashes": [
            "b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef12345678",
            "c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234567890"
        ],
        "close_pack_hash": "d4e5f6789012345678901234567890abcdef1234567890abcdef1234567890ab",
        "invoice_pack_hash": "e5f6789012345678901234567890abcdef1234567890abcdef1234567890abcd",
        "summary": "Quote accepted, work logged, close-out signed, invoice sealed. Full lifecycle evidence.",
        "status": "complete",
        "operator": "tech-dan",
        "notes": "All packs verified PASS with QuantumGuard before bundling."
    }
    key_path = Path.home() / ".lifecycleseal_key.pem"
    priv, pub_hex = load_or_create_key(key_path)
    pack = build_lifecycle_pack(sample, priv, pub_hex)
    print(json.dumps(pack, indent=2))
    print("\n# Verify with: qg verify <this.json>  (from QuantumGuard)")

def main():
    parser = argparse.ArgumentParser(description="LifecycleSeal — local full job lifecycle evidence bundler")
    parser.add_argument("--demo", action="store_true", help="Run demo and print sealed pack")
    parser.add_argument("--data", type=str, help="Path to lifecycle JSON file")
    parser.add_argument("--out", type=str, help="Output sealed pack path")
    parser.add_argument("--key", type=str, default=str(Path.home() / ".lifecycleseal_key.pem"), help="Private key path")
    args = parser.parse_args()

    if args.demo:
        demo()
        return

    if not args.data:
        parser.print_help()
        return

    with open(args.data) as f:
        data = json.load(f)

    key_path = Path(args.key)
    priv, pub_hex = load_or_create_key(key_path)
    pack = build_lifecycle_pack(data, priv, pub_hex)

    out_path = args.out or "sealed_lifecycle.json"
    with open(out_path, "w") as f:
        json.dump(pack, f, indent=2)
    print(f"Sealed lifecycle pack written to {out_path}")
    print(f"Payload hash: {pack['payload_hash']}")
    print("Verify with QuantumGuard: qg verify", out_path)

if __name__ == "__main__":
    main()
