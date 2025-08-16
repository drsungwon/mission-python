import os
import struct # 길이 정보를 바이트로 변환하기 위해 추가
from cryptography.hazmat.primitives.asymmetric import rsa, padding as rsa_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization, hashes, padding as aes_padding

# (PROFESSOR_PUBLIC_KEY, 상수 정의 등 이전과 동일)
PROFESSOR_PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApLrm3+PqnidkFIh8BGpY
r1MhGF7MTwzrE5h3wQfx37/X65Tw7qh62D9E3kn7WdW7ETVaKb0nRTv0Ym265Fdv
nNdtCzrFsAEnLcEfxpMcEbodEWLtQ2JFZgNYm3+QtfgVumREc3W+ojEaGPw7Vowp
OzULStvsdC1USXXKm9JYvLEuyOyosfZDF4flKSt3F59sVrbFeoXBXCKK2JFxhuvP
K0Pka6VIsoyJwAnLqmeJOWIhpakfFTvrkHxZo2YihEIJvdhlmpRjj1CSgorZwMgG
QIaS6KkIZl9JAeie9fmCGiUKsN7Me/WyeNGnd/ZAR9ScbNTQPJNIYp//ZQGBu8BF
HwIDAQAB
-----END PUBLIC KEY-----
"""
AES_KEY_SIZE = 32
AES_IV_SIZE = 16
RSA_ENCRYPTED_KEY_SIZE = 256

_public_key_cache = None

def get_public_key():
    global _public_key_cache
    if _public_key_cache is None:
        _public_key_cache = serialization.load_pem_public_key(
            PROFESSOR_PUBLIC_KEY.encode('utf-8')
        )
    return _public_key_cache

def encrypt_data(data: bytes) -> bytes | None:
    """하이브리드 방식으로 데이터를 암호화하고, [암호화된 키][데이터길이][암호화된 데이터] 형식으로 반환"""
    try:
        public_key = get_public_key()
        aes_key, iv = os.urandom(AES_KEY_SIZE), os.urandom(AES_IV_SIZE)

        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        padder = aes_padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()
        aes_encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        session_key_to_encrypt = aes_key + iv
        rsa_encrypted_key = public_key.encrypt(
            session_key_to_encrypt,
            rsa_padding.OAEP(
                mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # ★★★ 핵심 수정: 암호화된 데이터의 길이를 4바이트 정수로 추가
        aes_data_len_bytes = struct.pack('>I', len(aes_encrypted_data))

        return rsa_encrypted_key + aes_data_len_bytes + aes_encrypted_data

    except Exception as e:
        print(f"🚫 [Crypto] 데이터 암호화 중 오류 발생: {e}")
        return None