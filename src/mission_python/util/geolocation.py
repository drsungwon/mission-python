"""
================================================================================
geolocation.py (Encrypted Version)
================================================================================

[프로그램 설명]
이 모듈은 실행된 컴퓨터의 네트워크 및 시스템 정보를 수집하여
'디지털 서명' 또는 '시스템 핑거프린트'를 생성합니다.
수집된 정보는 JSON 형식으로 변환된 후, 암호화되어 프로젝트 루트의 'log' 폴더 아래에
`signature.encrypted` 파일로 저장됩니다.

이 모듈의 주요 기능은 외부에서 호출될 때 최초 한 번만 실행되도록 설계되었습니다.
암호화된 파일이 이미 존재하면, 추가 작업을 수행하지 않습니다.

[주요 기능 및 수집 정보]
- 호스트 이름 (컴퓨터 이름)
- 로컬 Private IP 및 공인 Public IP 주소
- Public IP 기반의 지리적 위치 정보 (국가, 도시, 좌표)
- 상세 운영체제 정보 (OS 종류, 버전 등)
- 현재 로그인된 사용자 계정 ID
- 시스템의 모든 네트워크 인터페이스 MAC 주소
- 정보 수집 시각 (타임스탬프)

[사용 방법]
이 모듈은 주로 다른 스크립트에서 import 하여 `create_signature_if_not_exists()` 함수를
호출하는 방식으로 사용됩니다. 직접 실행하여 테스트할 수도 있습니다.

================================================================================
"""

import sys
import socket
import urllib.request
import urllib.error
import requests
import json
import os
import datetime
import getpass
import psutil
import platform

# 암호화 모듈을 가져옵니다.
from mission_python.util import crypto

# ---------------------------------------------------
# 네트워크 및 시스템 정보 확인 함수들
# ---------------------------------------------------

def get_local_ip_address():
    """
    현재 시스템의 로컬(사설) IP 주소를 가져옵니다.
    """
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except socket.error:
        return "확인 불가 (네트워크 미연결)"
    finally:
        if s: s.close()

def get_public_ip_address():
    """
    외부 API 서비스를 통해 현재 네트워크의 공인 IP 주소를 가져옵니다.
    """
    ip_services = ["https://api.ipify.org", "https://ifconfig.me/ip", "https://icanhazip.com"]
    for service in ip_services:
        try:
            with urllib.request.urlopen(service, timeout=5) as response:
                return response.read().decode('utf-8').strip()
        except (urllib.error.URLError, socket.timeout):
            continue
    return "확인 불가 (인터넷 연결 또는 서비스 문제)"

def get_location_by_ip(public_ip):
    """
    공인 IP를 기반으로 지리적 위치 정보를 가져옵니다.
    """
    if public_ip.startswith("확인 불가"):
        return {"error": "공인 IP를 확인할 수 없어 위치 정보를 가져올 수 없습니다."}
    try:
        response = requests.get(f"http://ipinfo.io/{public_ip}/json")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"위치 정보 API 요청 실패: {e}"}

def get_all_mac_addresses():
    """
    psutil을 사용하여 시스템의 모든 네트워크 인터페이스와 MAC 주소를 가져옵니다.
    """
    try:
        all_interfaces = psutil.net_if_addrs()
        mac_addresses = {}
        for interface_name, addresses in all_interfaces.items():
            for addr in addresses:
                if addr.family == psutil.AF_LINK:
                    if addr.address and not addr.address.startswith('00:00:00'):
                        mac_addresses[interface_name] = addr.address
        return mac_addresses
    except Exception as e:
        return {"error": f"MAC 주소 확인 중 오류 발생: {e}"}

def get_current_user():
    """
    다양한 방법을 시도하여 현재 사용자의 이름을 안정적으로 반환합니다.
    """
    try:
        return getpass.getuser()
    except Exception:
        for var in ('USERNAME', 'USER', 'LOGNAME'):
            user = os.environ.get(var)
            if user: return user
        if sys.platform != 'win32':
            try:
                import pwd
                return pwd.getpwuid(os.getuid()).pw_name
            except (ImportError, KeyError):
                pass
    return "Unknown"

def get_hostname():
    """ 현재 컴퓨터의 호스트 이름을 반환합니다. """
    try:
        return socket.gethostname()
    except Exception as e:
        return f"호스트 이름 확인 불가: {e}"

def get_os_info():
    """ platform 모듈을 사용하여 상세한 OS 정보를 반환합니다. """
    try:
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "platform": platform.platform(),
            "processor": platform.processor()
        }
    except Exception as e:
        return {"error": f"상세 OS 정보 확인 불가: {e}"}

# ---------------------------------------------------
# 핵심 정보 수집 로직
# ---------------------------------------------------
def _collect_all_system_info():
    """
    모든 시스템 정보를 수집하여 딕셔너리 형태로 반환합니다. (내부 사용 함수)
    """
    scan_results = {}
    
    public_ip = get_public_ip_address()
    location_info = get_location_by_ip(public_ip)
    
    scan_results["hostname"] = get_hostname()
    scan_results["local_ip"] = get_local_ip_address()
    scan_results["public_ip"] = public_ip
    scan_results["location_info"] = location_info
    scan_results["os_info"] = get_os_info()
    scan_results["user_id"] = get_current_user()

    all_macs = get_all_mac_addresses()
    if isinstance(all_macs, dict) and "error" not in all_macs:
        sorted_macs = {k: v for k, v in sorted(all_macs.items())}
    else:
        sorted_macs = all_macs
    scan_results["mac_addresses"] = sorted_macs
    scan_results["scan_time"] = datetime.datetime.now().isoformat()
    
    return scan_results


# ---------------------------------------------------
# 프로그램 진입점 함수
# ---------------------------------------------------
def create_signature_if_not_exists():
    """
    프로젝트 루트의 'log' 폴더에 암호화된 서명 파일의 존재 여부를 확인하고,
    파일이 없을 때만 정보 수집 및 암호화/저장을 수행합니다.
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        log_dir = os.path.join(project_root, 'log')
        
        # 파일명을 암호화되었음을 나타내는 이름으로 지정합니다.
        signature_file = os.path.join(log_dir, 'signature.encrypted')

        # 파일이 이미 존재하는지 확인하고, 존재하면 메시지를 출력하고 종료합니다.
        if os.path.exists(signature_file):
            # print(f"ℹ️ [INFO] '{os.path.basename(signature_file)}' 파일이 이미 존재하므로, 생성을 건너뜁니다.")
            print(f"🦊 Signature already exists. Skipping creation ...")
            return False 
        
        # 파일을 쓰기 전에 log 디렉토리가 없으면 생성합니다.
        os.makedirs(log_dir, exist_ok=True)
        
        # 시스템 정보를 수집합니다.
        result_data = _collect_all_system_info()
        
        # 1. 딕셔너리 -> JSON 문자열로 변환
        json_string = json.dumps(result_data, indent=4, ensure_ascii=False)
        # 2. JSON 문자열 -> UTF-8 바이트로 인코딩
        data_bytes = json_string.encode('utf-8')
        # 3. crypto 모듈을 사용해 바이트 데이터 암호화
        encrypted_data = crypto.encrypt_data(data_bytes)
        
        # 4. 암호화 실패 시 오류 처리
        if encrypted_data is None:
            print("🚫 [Geolocation] 데이터 암호화에 실패했습니다.", file=sys.stderr)
            return False

        # 5. 암호화된 바이트 데이터를 바이너리 쓰기('wb') 모드로 파일에 저장
        with open(signature_file, 'wb') as f:
            f.write(encrypted_data)
        
        # 모든 작업이 성공적으로 끝나면, 성공 메시지를 출력합니다.
        print(f"🦊 Signature successfully created ...")
        # print(f"✅ [INFO] 시스템 서명 '{os.path.basename(signature_file)}' 파일이 암호화되어 성공적으로 생성되었습니다.")            
        return True

    except Exception as e:
        print(f"🚫 [Geolocation] Signature 파일 생성 중 심각한 오류 발생: {e}", file=sys.stderr)
        return False

# ----------------------------------------------------------------------------------
#  메인(main) 코드 블록: 이 프로그램이 시작되는 지점입니다.
# `if __name__ == "__main__":` 은 이 파이썬 파일을 직접 실행했을 때만
# 아래 코드를 동작시키라는 특별한 의미를 가지고 있어요.
#
# 실행 방법:
#  1. 프로젝트 root 폴더에서 poetry install 명령을 실행합니다.
#  2. Visual Code의 인터프리터 선택에서, 프로젝트 인터프리터에 해당하는 항목을 선택합니다.
#  3. Terminal 사용시 프로젝트 root 폴더에서 다음 명령을 중 하나를 수형합니다. 
#     - poetry run python src/mission_python/util/geolocation.py
#     - poetry run python -m mission_python.util.geolocation
# ----------------------------------------------------------------------------------

if __name__ == "__main__":
    print("geolocation.py 모듈을 직접 실행하여 테스트합니다...")
    
    _current_dir = os.path.dirname(os.path.abspath(__file__))
    _project_root = os.path.dirname(_current_dir)
    _test_signature_file = os.path.join(_project_root, 'log', 'signature.encrypted')

    try:
        os.remove(_test_signature_file)
        print(f"-> 기존 테스트 파일('{_test_signature_file}')을 삭제했습니다.")
    except FileNotFoundError:
        print("-> 기존 테스트 파일이 없어 바로 진행합니다.")

    was_created = create_signature_if_not_exists()
    
    print("\n[첫 번째 실행 결과]")
    if was_created:
        print("-> 예상대로 파일이 새로 생성되었습니다.")
    else:
        print("-> 오류! 파일 생성에 실패했습니다.")

    print("\n[두 번째 실행 결과]")
    was_created_again = create_signature_if_not_exists()
    if not was_created_again:
        print("-> 예상대로 파일이 이미 존재하므로 추가 작업을 수행하지 않았습니다.")
    else:
        print("-> 오류! 파일이 이미 있는데도 재생성되었습니다.")