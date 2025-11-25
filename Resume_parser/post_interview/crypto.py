"""Cryptographic utilities for transcript encryption and integrity.

This module provides secure encryption, hashing, and signing capabilities
for interview transcripts to ensure confidentiality and tamper detection.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from typing import Dict, Optional, Tuple

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from .models import TranscriptData


class TranscriptCrypto:
    """Handles encryption and decryption of interview transcripts."""
    
    def __init__(self, master_key: Optional[bytes] = None):
        """Initialize crypto manager with optional master key."""
        if master_key is None:
            # Generate a proper Fernet key directly
            self.fernet = Fernet(Fernet.generate_key())
            self.master_key = None
        else:
            # Use provided key (must be 32 bytes for Fernet)
            if len(master_key) == 32:
                self.fernet = Fernet(base64.urlsafe_b64encode(master_key))
                self.master_key = master_key
            else:
                # Generate a Fernet key from provided key
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=b'"eureka_salt"',
                    iterations=100000,
                )
                derived_key = kdf.derive(master_key)
                self.fernet = Fernet(base64.urlsafe_b64encode(derived_key))
                self.master_key = derived_key
    
    def _derive_key(self, password: bytes, salt: Optional[bytes] = None) -> bytes:
        """Derive encryption key from password using PBKDF2."""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password)
    
    def encrypt_transcript(self, transcript: Dict) -> Tuple[str, str]:
        """Encrypt transcript data and return encrypted content with salt."""
        transcript_json = json.dumps(transcript, separators=(',', ':'))
        encrypted_data = self.fernet.encrypt(transcript_json.encode('utf-8'))
        return encrypted_data.decode('utf-8'), ""
    
    def decrypt_transcript(self, encrypted_content: str) -> Dict:
        """Decrypt transcript data."""
        try:
            decrypted_data = self.fernet.decrypt(encrypted_content.encode('utf-8'))
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            raise ValueError(f"Failed to decrypt transcript: {str(e)}")
    
    @staticmethod
    def generate_rsa_keypair() -> Tuple[str, str]:
        """Generate RSA key pair for asymmetric encryption."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        private_pem = private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption()
        )
        
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem.decode('utf-8'), public_pem.decode('utf-8')


class TranscriptHasher:
    """Handles hashing and integrity verification of transcripts."""
    
    @staticmethod
    def compute_content_hash(content: str) -> str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    @staticmethod
    def compute_transcript_hash(transcript: Dict) -> str:
        """Compute hash of transcript dictionary."""
        # Sort keys to ensure consistent hashing
        normalized = json.dumps(transcript, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    
    @staticmethod
    def verify_integrity(content: str, expected_hash: str) -> bool:
        """Verify content integrity against expected hash."""
        actual_hash = TranscriptHasher.compute_content_hash(content)
        return hmac.compare_digest(actual_hash, expected_hash)
    
    @staticmethod
    def create_hmac_signature(content: str, secret_key: str) -> str:
        """Create HMAC signature for content."""
        return hmac.new(
            secret_key.encode('utf-8'),
            content.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def verify_hmac_signature(content: str, signature: str, secret_key: str) -> bool:
        """Verify HMAC signature."""
        expected_signature = TranscriptHasher.create_hmac_signature(content, secret_key)
        return hmac.compare_digest(signature, expected_signature)


class TranscriptProcessor:
    """High-level processor for transcript security operations."""
    
    def __init__(self, crypto: TranscriptCrypto, hasher: TranscriptHasher, 
                 secret_key: Optional[str] = None):
        self.crypto = crypto
        self.hasher = hasher
        self.secret_key = secret_key or os.urandom(32).hex()
    
    def process_transcript(self, transcript: Dict, session_id: str, 
                          candidate_id: str, job_id: str, 
                          interview_type: str, duration_minutes: int) -> TranscriptData:
        """Process and secure transcript data."""
        # Encrypt content
        encrypted_content, _ = self.crypto.encrypt_transcript(transcript)
        
        # Compute hash
        content_hash = self.hasher.compute_content_hash(encrypted_content)
        
        # Create signature
        signature = self.hasher.create_hmac_signature(encrypted_content, self.secret_key)
        
        return TranscriptData(
            session_id=session_id,
            candidate_id=candidate_id,
            job_id=job_id,
            interview_type=interview_type,
            duration_minutes=duration_minutes,
            encrypted_content=encrypted_content,
            content_hash=content_hash,
            signature=signature
        )
    
    def verify_transcript(self, transcript_data: TranscriptData) -> bool:
        """Verify transcript integrity and authenticity."""
        # Verify hash
        if not self.hasher.verify_integrity(
            transcript_data.encrypted_content, 
            transcript_data.content_hash
        ):
            return False
        
        # Verify signature
        if transcript_data.signature:
            if not self.hasher.verify_hmac_signature(
                transcript_data.encrypted_content,
                transcript_data.signature,
                self.secret_key
            ):
                return False
        
        return True
    
    def decrypt_and_validate(self, transcript_data: TranscriptData) -> Dict:
        """Decrypt transcript and validate integrity."""
        if not self.verify_transcript(transcript_data):
            raise ValueError("Transcript integrity verification failed")
        
        return self.crypto.decrypt_transcript(transcript_data.encrypted_content)