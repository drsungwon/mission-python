# =================================================================================
#   수정 금지 안내 (Do NOT modify)
# ---------------------------------------------------------------------------------
# - 이 파일을 절대로 수정하지 마세요.
#   수정 시, 개발 과정에 대한 평가 점수가 0점 처리됩니다.
# - Do NOT modify this file.
#   If modified, you will receive a ZERO for the development process evaluation.
# =================================================================================

# ==============================================================================
# Log Encryption Utility (v1.0)
# ------------------------------------------------------------------------------

import os
import struct
# cryptography 라이브러리에서 필요한 암호화 관련 모듈들을 가져옵니다.
# rsa, padding: RSA 비대칭키 암호화 및 패딩 방식에 사용됩니다.
from cryptography.hazmat.primitives.asymmetric import rsa, padding as rsa_padding
# Cipher, algorithms, modes: AES 대칭키 암호화 방식(알고리즘, 운영 모드 등)에 사용됩니다.
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
# serialization: 키를 파일이나 메모리에서 읽을 수 있는 형태로 변환합니다.
# hashes: 해시 함수(SHA256 등)를 사용합니다.
# padding: AES 암호화 시 블록 크기를 맞추기 위한 패딩에 사용됩니다.
from cryptography.hazmat.primitives import serialization, hashes, padding as aes_padding

# 평가자의 RSA 공개키입니다. 이 키로 암호화된 데이터는 대응되는 개인키로만 복호화할 수 있습니다.
# 학생의 코드 변경 기록을 안전하게 보호하는 데 사용됩니다.
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
# --- 암호화에 사용될 상수 정의 ---
AES_KEY_SIZE = 32  # AES-256을 의미합니다 (32 bytes * 8 bits/byte = 256 bits).
AES_IV_SIZE = 16   # AES 블록 크기와 같은 16 bytes(128 bits) IV(Initialization Vector)를 사용합니다.
RSA_ENCRYPTED_KEY_SIZE = 256  # 2048비트 RSA 키로 암호화된 AES 키의 결과 크기입니다 (2048 bits / 8 = 256 bytes).

# 공개키 객체를 메모리에 한 번만 로드하기 위한 캐시 변수입니다.
_public_key_cache = None

def get_public_key():
    """
    문자열 형태의 PEM 공개키를 cryptography 라이브러리에서 사용할 수 있는 객체로 변환합니다.
    효율성을 위해, 한 번 변환된 키 객체는 `_public_key_cache`에 저장하여 재사용합니다.
    """
    global _public_key_cache
    # 캐시가 비어 있을 경우에만 키 로딩 작업을 수행합니다.
    if _public_key_cache is None:
        # load_pem_public_key 함수는 PEM 형식의 키 문자열을 파싱하여 키 객체를 생성합니다.
        # 함수에 전달하기 전에 문자열을 바이트(bytes) 형태로 인코딩해야 합니다.
        _public_key_cache = serialization.load_pem_public_key(
            PROFESSOR_PUBLIC_KEY.encode('utf-8')
        )
    return _public_key_cache

def encrypt_data(data: bytes) -> bytes | None:
    """
    하이브리드 암호화(Hybrid Encryption) 방식으로 데이터를 암호화합니다.
    - 하이브리드 방식: 빠른 대칭키(AES)로 대용량 데이터를 암호화하고, 이 AES 키를 안전한 비대칭키(RSA)로 다시 암호화하는 방식.
                      속도와 보안을 모두 만족시키는 효율적인 방법입니다.
    - 최종 결과물 포맷: [RSA로 암호화된 AES키+IV (256바이트)][암호화된 데이터의 길이 (4바이트)][AES로 암호화된 데이터]
    - data: 암호화할 원본 데이터 (바이트 형태)
    - 반환값: 암호화된 전체 데이터(바이트), 실패 시 None
    """
    try:
        # --- 1단계: 암호화에 필요한 키 준비 ---
        # 평가자의 RSA 공개키 객체를 가져옵니다.
        public_key = get_public_key()
        # os.urandom: 암호학적으로 안전한(예측 불가능한) 난수를 생성하여 AES 키와 IV를 만듭니다.
        # AES 키와 IV는 매번 암호화할 때마다 새로 생성해야 보안성이 높아집니다.
        aes_key, iv = os.urandom(AES_KEY_SIZE), os.urandom(AES_IV_SIZE)

        # --- 2단계: 대칭키(AES)로 원본 데이터 암호화 ---
        # Cipher 객체 생성: AES 알고리즘과 CBC(Cipher Block Chaining) 운영 모드를 지정합니다.
        # CBC 모드는 각 데이터 블록을 암호화할 때 이전 블록의 암호화 결과에 영향을 받게 하여 보안성을 높입니다. IV는 첫 블록에 사용됩니다.
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        encryptor = cipher.encryptor() # 암호화 작업을 수행할 객체 생성

        # PKCS7 패딩 적용: AES는 정해진 블록 단위(16바이트)로 데이터를 처리하기 때문에,
        # 원본 데이터의 마지막 블록이 16바이트가 아닐 경우, 부족한 부분을 특정 규칙으로 채워주는 '패딩'이 필요합니다.
        padder = aes_padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize() # 데이터에 패딩 추가
        # 패딩된 데이터를 최종적으로 암호화합니다.
        aes_encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        # --- 3단계: 비대칭키(RSA)로 AES 키 암호화 ---
        # AES 키와 IV를 하나로 합쳐서 RSA로 암호화할 세션키를 만듭니다.
        # 복호화 시에도 이 두 값을 모두 알아야 하기 때문입니다.
        session_key_to_encrypt = aes_key + iv
        # 공개키를 사용하여 세션키(AES키+IV)를 암호화합니다.
        rsa_encrypted_key = public_key.encrypt(
            session_key_to_encrypt,
            # OAEP: RSA 암호화 시 사용되는 안전한 패딩 스킴입니다. 무차별 대입 공격 등을 방지해줍니다.
            # 여기서는 해시 함수로 SHA256을 사용하도록 지정합니다.
            rsa_padding.OAEP(
                mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # --- 4단계: 결과물 조합 ---
        # 암호화된 데이터의 길이를 4바이트의 빅엔디안(big-endian, >) 부호 없는 정수(I) 형식으로 패킹합니다.
        # 복호화 시 어디까지가 데이터 부분인지 정확히 알기 위해 필요합니다.
        aes_data_len_bytes = struct.pack('>I', len(aes_encrypted_data))

        # [암호화된 세션키] + [데이터 길이] + [암호화된 데이터] 순서로 모든 부분을 합쳐 최종 결과물을 반환합니다.
        return rsa_encrypted_key + aes_data_len_bytes + aes_encrypted_data

    # 암호화 과정에서 어떤 종류의 오류든 발생하면, 오류 메시지를 출력하고 None을 반환합니다.
    except Exception as e:
        print(f"🚫 [Crypto] 데이터 암호화 중 오류 발생: {e}")
        return None