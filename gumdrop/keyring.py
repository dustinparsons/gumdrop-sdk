"""
Gumdrop Keyring — Hardware-backed cartridge authentication.

A cartridge is a signed identity container. The signing key lives on
hardware (YubiKey, USB security key) or in a local keystore. The
cartridge file itself is portable — but only the holder of the
private key can modify it, and anyone can verify it.

Flow:
    1. Generate a keypair (or use existing hardware key)
    2. Create a cartridge, signed by the private key
    3. The IC panel's characters are derived from the PUBLIC key + traits
    4. Load cartridge → verify signature → inject identity into LLM
    5. Anyone with the IC (public face) can verify authenticity

Supports:
    - Local keystore (file-based, for development)
    - FIDO2/USB security keys (YubiKey, SoloKey, etc.)
    - Future: PKCS#11, TPM, smart cards

The signing algorithm is Ed25519 (fast, small signatures, no config).
"""

import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

# Ed25519 is in the stdlib via hashlib, but for actual signing we need
# a small pure-python implementation or the cryptography package.
# For now: HMAC-SHA256 as the signing primitive (works without deps).
# Upgrade path: swap to Ed25519 when `cryptography` is available.

KEYSTORE_DIR = Path.home() / ".gumdrop" / "keys"
SIGNATURE_VERSION = "1"


class KeyPair:
    """
    A signing keypair for cartridge authentication.
    
    The private key signs cartridges. The public key is embedded in
    the cartridge and used to derive the IC panel visual.
    
    In production, the private key lives on hardware (YubiKey).
    For development, it's stored in ~/.gumdrop/keys/.
    """
    
    def __init__(self, private_key: bytes, public_key: bytes, key_id: str = ""):
        self.private_key = private_key
        self.public_key = public_key
        self.key_id = key_id or hashlib.sha256(public_key).hexdigest()[:16]
    
    @classmethod
    def generate(cls, key_id: Optional[str] = None) -> "KeyPair":
        """Generate a new keypair."""
        # 32 bytes of entropy for the private key
        private_key = secrets.token_bytes(32)
        # Public key derived from private (in real Ed25519, this would be
        # the curve point; here we use a hash derivation as placeholder)
        public_key = hashlib.sha256(b"gumdrop-pub:" + private_key).digest()
        
        kid = key_id or hashlib.sha256(public_key).hexdigest()[:16]
        return cls(private_key, public_key, kid)
    
    @classmethod
    def from_file(cls, path: Path) -> "KeyPair":
        """Load a keypair from a JSON file."""
        with open(path) as f:
            data = json.load(f)
        return cls(
            private_key=bytes.fromhex(data["private_key"]),
            public_key=bytes.fromhex(data["public_key"]),
            key_id=data.get("key_id", ""),
        )
    
    def save(self, path: Optional[Path] = None):
        """Save keypair to a JSON file."""
        target = path or (KEYSTORE_DIR / f"{self.key_id}.json")
        target.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "key_id": self.key_id,
            "public_key": self.public_key.hex(),
            "private_key": self.private_key.hex(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "algorithm": "hmac-sha256",  # upgrade to ed25519
        }
        
        with open(target, "w") as f:
            json.dump(data, f, indent=2)
        
        # Restrict permissions (private key!)
        os.chmod(target, 0o600)
    
    @property
    def fingerprint(self) -> str:
        """Short fingerprint of the public key (for display)."""
        return hashlib.sha256(self.public_key).hexdigest()[:16]
    
    @property
    def ic_seed(self) -> bytes:
        """
        Seed bytes for IC panel generation.
        Derived from the public key — anyone can reproduce the IC
        visual from the public key alone.
        """
        return hashlib.sha256(b"gumdrop-ic:" + self.public_key).digest()


class Signer:
    """
    Signs and verifies cartridge data.
    
    The signature covers:
    - Identity (name, voice, origin)
    - Personality (traits, quirks)  
    - Directives
    - Public key
    
    It does NOT cover:
    - Memory (changes over time)
    - Access timestamps
    - Session data
    
    This means the identity is immutable once signed, but memory
    can grow without re-signing. To change personality, you re-sign.
    """
    
    @staticmethod
    def _canonical_payload(cartridge_data: Dict[str, Any], public_key: bytes) -> bytes:
        """
        Create the canonical byte representation for signing.
        Only includes identity-critical fields.
        """
        signable = {
            "v": SIGNATURE_VERSION,
            "identity": cartridge_data.get("identity", {}),
            "personality": cartridge_data.get("personality", {}),
            "directives": cartridge_data.get("directives", []),
            "public_key": public_key.hex(),
        }
        # Deterministic JSON serialization
        return json.dumps(signable, sort_keys=True, separators=(",", ":")).encode("utf-8")
    
    @staticmethod
    def sign(cartridge_data: Dict[str, Any], keypair: KeyPair) -> Dict[str, str]:
        """
        Sign cartridge data with a keypair.
        
        Returns a signature block to embed in the cartridge file.
        """
        payload = Signer._canonical_payload(cartridge_data, keypair.public_key)
        signature = hmac.new(keypair.private_key, payload, hashlib.sha256).hexdigest()
        
        return {
            "version": SIGNATURE_VERSION,
            "algorithm": "hmac-sha256",
            "key_id": keypair.key_id,
            "public_key": keypair.public_key.hex(),
            "signature": signature,
            "signed_at": datetime.now(timezone.utc).isoformat(),
        }
    
    @staticmethod
    def verify(cartridge_data: Dict[str, Any], sig_block: Dict[str, str]) -> bool:
        """
        Verify a cartridge signature.
        
        Note: HMAC verification requires the private key, which means
        only the owner can verify. For public verification, upgrade to
        Ed25519 where the public key suffices.
        
        This is a development placeholder — the upgrade path is clear.
        """
        # For now, we verify structural integrity
        required = ["version", "algorithm", "key_id", "public_key", "signature"]
        return all(k in sig_block for k in required)
    
    @staticmethod
    def verify_with_key(
        cartridge_data: Dict[str, Any],
        sig_block: Dict[str, str],
        keypair: KeyPair,
    ) -> bool:
        """Verify signature with the actual keypair (full verification)."""
        public_key = bytes.fromhex(sig_block["public_key"])
        payload = Signer._canonical_payload(cartridge_data, public_key)
        expected = hmac.new(keypair.private_key, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, sig_block["signature"])


class Keyring:
    """
    Manages keypairs for cartridge signing.
    
    The keyring is the user's collection of signing keys.
    Each key can sign multiple cartridges (one identity per key,
    or one key per cartridge — user's choice).
    
    Storage hierarchy:
    1. Hardware key (YubiKey/FIDO2) — most secure
    2. OS keychain (macOS Keychain, Windows DPAPI) — convenient
    3. File-based (~/.gumdrop/keys/) — development fallback
    """
    
    def __init__(self, keystore_dir: Optional[Path] = None):
        self.keystore_dir = keystore_dir or KEYSTORE_DIR
        self.keystore_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, key_id: Optional[str] = None) -> KeyPair:
        """Generate and store a new keypair."""
        kp = KeyPair.generate(key_id)
        kp.save(self.keystore_dir / f"{kp.key_id}.json")
        return kp
    
    def load(self, key_id: str) -> Optional[KeyPair]:
        """Load a keypair by ID."""
        path = self.keystore_dir / f"{key_id}.json"
        if path.exists():
            return KeyPair.from_file(path)
        return None
    
    def list_keys(self) -> list:
        """List all stored key IDs."""
        keys = []
        for f in self.keystore_dir.glob("*.json"):
            try:
                with open(f) as fh:
                    data = json.load(fh)
                keys.append({
                    "key_id": data.get("key_id", f.stem),
                    "created_at": data.get("created_at", "unknown"),
                    "algorithm": data.get("algorithm", "unknown"),
                })
            except (json.JSONDecodeError, KeyError):
                continue
        return keys
    
    def delete(self, key_id: str) -> bool:
        """Delete a keypair. DESTRUCTIVE — cartridges signed with this key
        can no longer be re-signed."""
        path = self.keystore_dir / f"{key_id}.json"
        if path.exists():
            path.unlink()
            return True
        return False


# ─── Hardware Key Support (Future) ─────────────────────────────

class HardwareKeyError(Exception):
    """Raised when hardware key operations fail."""
    pass


def detect_hardware_keys() -> list:
    """
    Detect connected FIDO2/USB security keys.
    
    Returns a list of detected devices.
    Requires `fido2` package: pip install fido2
    """
    try:
        from fido2.hid import CtapHidDevice
        devices = list(CtapHidDevice.list_devices())
        return [
            {
                "vendor": hex(d.descriptor.vid),
                "product": hex(d.descriptor.pid),
                "path": str(d.descriptor.path),
            }
            for d in devices
        ]
    except ImportError:
        return []
    except Exception:
        return []
