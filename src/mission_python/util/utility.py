# =================================================================================
#   수정 금지 안내 (Do NOT modify)
# ---------------------------------------------------------------------------------
# - 이 파일을 절대로 수정하지 마세요.
#   수정 시, 개발 과정에 대한 평가 점수가 0점 처리됩니다.
# - Do NOT modify this file.
#   If modified, you will receive a ZERO for the development process evaluation.
# =================================================================================

import os
import sys
import difflib
from datetime import datetime
from typing import List, Optional, Union
from functools import wraps

# 개발 중 평문 로그 확인을 위한 플래그 (True: log.plain 생성, False: log.encrypted 생성)
flag_plain_log_enabled = False

# '.crypto'는 현재 패키지 내의 crypto 모듈을 가져오는 상대 경로 임포트 방식입니다.
from . import crypto

def safe_file_operation(func):
    """
    파일 관련 작업을 위한 데코레이터(Decorator)입니다.
    데코레이터는 기존 함수의 코드를 수정하지 않고, 추가적인 기능을 덧씌우는 역할을 합니다.
    이 데코레이터는 파일 작업 시 발생할 수 있는 일반적인 예외(오류)들을 처리해줍니다.
    """
    # @wraps(func): 데코레이터를 사용하더라도 원본 함수의 이름이나 설명서(__doc__) 같은 메타데이터를 유지시켜주는 역할을 합니다.
    @wraps(func)
    def wrapper(*args, **kwargs):
        # try-except 블록을 사용하여 오류 발생 가능성이 있는 코드를 감쌉니다.
        try:
            # func는 데코레이터가 감싸고 있는 원본 함수(e.g., read_file_content)입니다.
            # 원본 함수를 그대로 실행하고 그 결과를 반환합니다.
            return func(*args, **kwargs)
        # FileNotFoundError: 지정된 경로에 파일이 없을 때 발생하는 오류입니다.
        except FileNotFoundError as e:
            print(f"🚫 파일을 찾을 수 없습니다: {str(e)}")
        # PermissionError: 파일을 읽거나 쓸 권한이 없을 때 발생하는 오류입니다.
        except PermissionError as e:
            print(f"🚫 파일 접근 권한이 없습니다: {str(e)}")
        # Exception: 위에서 명시한 오류 외에 다른 모든 예상치 못한 오류를 처리합니다.
        except Exception as e:
            print(f"🚫 파일 작업 중 오류 발생: {str(e)}")
        
        # 어떤 종류든 오류가 발생했을 경우, None을 반환하여 호출한 쪽에서 실패했음을 알 수 있게 합니다.
        return None
    return wrapper

# @safe_file_operation 데코레이터를 적용하여, 이 함수는 자동 예외 처리 기능을 갖게 됩니다.
@safe_file_operation
def read_file_content(file_path: str, mode: str = 'r') -> Optional[Union[str, bytes]]:
    """
    지정된 경로의 파일 내용을 읽어옵니다. 텍스트(str) 또는 바이너리(bytes) 모드를 지원합니다.
    - file_path: 읽을 파일의 경로
    - mode: 'r'(텍스트 읽기, 기본값), 'rb'(바이너리 읽기) 등 파일 열기 모드
    - 반환값: 성공 시 파일 내용(str 또는 bytes), 실패 시 None
    """
    # 'b'(바이너리) 문자가 모드에 포함되어 있지 않으면 텍스트 파일로 간주하여 'utf-8' 인코딩을 사용합니다.
    # 바이너리 모드일 경우 인코딩은 None으로 설정해야 합니다.
    encoding = 'utf-8' if 'b' not in mode else None
    
    # 'with open(...)' 구문은 파일을 열고, 블록이 끝나면 자동으로 파일을 닫아주어 안전합니다.
    with open(file_path, mode, encoding=encoding) as f:
        return f.read()

# 이 함수 역시 @safe_file_operation 데코레이터를 통해 자동 예외 처리 기능을 가집니다.
@safe_file_operation
def write_file_content(file_path: str, content: Union[str, bytes], mode: str = 'w'):
    """
    주어진 내용을 파일에 씁니다. 텍스트(str) 또는 바이너리(bytes) 모드를 지원합니다.
    - file_path: 쓸 파일의 경로
    - content: 파일에 쓸 내용 (str 또는 bytes)
    - mode: 'w'(텍스트 쓰기, 기본값), 'wb'(바이너리 쓰기), 'a'(텍스트 추가), 'ab'(바이너리 추가) 등
    """
    # 바이너리 모드가 아니고, 내용이 문자열(str)일 때만 'utf-8' 인코딩을 적용합니다.
    encoding = 'utf-8' if 'b' not in mode and isinstance(content, str) else None
    with open(file_path, mode, encoding=encoding) as f:
        f.write(content)

def commit_changes():
    """
    main.py 파일의 변경사항을 추적하여 암호화된 로그로 기록하는 메인 함수입니다.
    이 함수가 호출되면 전체 변경 추적 프로세스가 시작됩니다.
    """
    try:
        # '__file__'은 현재 이 스크립트(utility.py) 파일의 절대 경로를 나타내는 내장 변수입니다.
        # sys.argv[0]보다 실행 환경에 영향을 받지 않아 훨씬 안정적으로 파일 경로를 찾을 수 있습니다.
        utility_file_path = os.path.abspath(__file__)
        
        # os.path.dirname()은 경로에서 디렉토리 부분만 추출합니다.
        # /path/to/project/mission_python/utility.py -> /path/to/project/mission_python
        util_dir = os.path.dirname(utility_file_path)
        # 한 번 더 실행하여 상위 폴더, 즉 프로젝트의 루트 폴더 경로를 얻습니다.
        # /path/to/project/mission_python -> /path/to/project
        project_root = os.path.dirname(util_dir) 

        # 프로젝트 루트 폴더를 기준으로 main.py 파일의 전체 경로를 만듭니다.
        main_py_file = os.path.join(project_root, 'main.py')
        
        # main.py 파일이 실제로 존재하는지 확인하는 방어 코드입니다.
        if not os.path.exists(main_py_file):
            raise FileNotFoundError(f"main.py를 찾을 수 없습니다: {main_py_file}")
            
        # 실제 로깅 작업을 수행하는 log_code_changes 함수를 호출합니다.
        # 이 함수가 False를 반환하면 로깅에 실패했다는 의미입니다.
        if not log_code_changes(main_py_file, project_root):
            # 실패 시, 명확한 오류를 발생시켜 문제가 있음을 알립니다.
            raise RuntimeError("코드 변경사항 암호화 기록에 실패했습니다.")
            
        # 모든 작업이 성공적으로 끝나면, 현재 시간을 포함한 성공 메시지를 출력합니다.
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n🦊 Code changes successfully logged at {timestamp} ...")

    # 이 함수 내에서 발생하는 모든 예외(오류)를 최종적으로 처리합니다.
    except Exception as e:
        # sys.stderr는 표준 오류 출력 스트림으로, 일반 출력(stdout)과 구분됩니다.
        print(f"🚫 심각한 오류 발생: {str(e)}", file=sys.stderr)
        print(f"🚫 담당 교수에게 문의하세요.")

def log_code_changes(target_file: str, project_root: str) -> bool:
    """
    파일의 변경사항을 이전 버전과 비교(diff)하여, 그 차이점을 암호화하고 로그 파일에 기록합니다.
    - target_file: 변경을 추적할 대상 파일 경로 (e.g., 'main.py')
    - project_root: 프로젝트의 최상위 폴더 경로
    - 반환값: 성공 시 True, 실패 시 False
    """
    try:
        # 로그 파일과 백업 파일을 저장할 'log' 디렉토리의 경로를 설정합니다.
        log_dir = os.path.join(project_root, 'log')
        # 암호화된 변경 이력이 누적될 최종 로그 파일입니다.
        encrypted_log_file = os.path.join(log_dir, 'log.encrypted')
        # flag_plain_log_enabled가 True일 때, 암호화되지 않은 평문 로그를 저장할 파일입니다.
        plain_log_file = os.path.join(log_dir, 'log.plain')
        # 현재 버전의 main.py와 비교하기 위한 직전 버전의 원본(평문)을 저장하는 임시 파일입니다.
        backup_file = os.path.join(log_dir, 'log.temp') 
        
        # 'log' 디렉토리가 없으면 생성합니다. exist_ok=True 옵션은 폴더가 이미 있어도 오류를 내지 않습니다.
        os.makedirs(log_dir, exist_ok=True)
        
        # 로그에 기록할 현재 시간을 포맷에 맞게 문자열로 만듭니다.
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 추적 대상 파일(main.py)의 현재 내용을 읽어옵니다. 파일 읽기 실패 시 None이 반환됩니다.
        current_content_str = read_file_content(target_file)
        # 안전장치: 파일 읽기에 실패했다면, 즉시 False를 반환하여 로깅을 중단합니다.
        if current_content_str is None: return False
        
        # [수정 사항] Pylance에게 이 변수가 str임을 명확히 알려줍니다.
        # 또한, 만약의 경우 bytes가 들어오면 즉시 오류를 발생시키는 안전장치 역할도 합니다.
        assert isinstance(current_content_str, str)
        
        # 파일 내용을 줄바꿈 단위로 나누어 리스트로 만듭니다.
        # keepends=True 옵션은 각 줄의 끝에 있는 줄바꿈 문자(\n)를 그대로 유지해줍니다.
        # 이는 difflib이 변경사항을 정확하게 비교하는 데 매우 중요합니다.
        current_content_lines = current_content_str.splitlines(keepends=True)

        # 백업 파일이 존재하지 않는다면, 이번이 첫 번째 커밋(기록)이라는 의미입니다.
        is_first_commit = not os.path.exists(backup_file)

        if is_first_commit:
            # 첫 커밋이므로, 변경사항(diff)이 아닌 파일 전체 내용을 로그에 기록합니다.
            log_entry_text = (
                f"🦊=== Code Change Tracking Started at {timestamp} ===\n"
                f"🦊=== Initial version of {os.path.basename(target_file)} ===\n\n"
                f"{current_content_str}"
            )

            if flag_plain_log_enabled:
                # 평문 로그 플래그가 True이면, 암호화하지 않고 log.plain 파일에 텍스트 쓰기('w') 모드로 저장합니다.
                write_file_content(plain_log_file, log_entry_text, 'w')
            else:
                # 평문 로그 플래그가 False이면, 기존 방식대로 암호화하여 로그를 기록합니다.
                # 로그 내용을 암호화하기 전에 반드시 바이트(bytes) 형태로 인코딩해야 합니다.
                encrypted_entry = crypto.encrypt_data(log_entry_text.encode('utf-8'))
                # 암호화 실패 시, 로깅을 중단합니다.
                if encrypted_entry is None: return False
                
                # 암호화된 내용을 로그 파일에 바이너리 쓰기('wb') 모드로 저장합니다.
                write_file_content(encrypted_log_file, encrypted_entry, 'wb')

            # 다음 비교를 위해 현재 파일 내용을 백업 파일에 원본 그대로 저장합니다.
            write_file_content(backup_file, current_content_str, 'w')
        else: # 첫 커밋이 아닌 경우 (백업 파일이 존재하는 경우)
            # 이전 버전의 내용이 담긴 백업 파일을 읽어옵니다.
            backup_content_str = read_file_content(backup_file)
            if backup_content_str is None: return False

            # [수정 사항] backup_content_str에 대해서도 동일하게 처리합니다.
            assert isinstance(backup_content_str, str)
            
            backup_content_lines = backup_content_str.splitlines(keepends=True)
            
            # 최적화: 만약 이전 버전과 현재 버전의 내용이 완전히 같다면, 아무 작업도 하지 않고 성공(True)을 반환합니다.
            if backup_content_lines == current_content_lines:
                return True
                
            # diff 비교 시 컨텍스트 라인 수를 최대로 설정하여 파일 전체의 차이점을 정확하게 파악합니다.
            context_lines = len(backup_content_lines) + len(current_content_lines)
            
            # difflib.unified_diff를 사용하여 두 파일 버전 간의 차이점을 생성합니다.
            # 이 결과는 git diff와 유사한 형식의 문자열 리스트로 반환됩니다.
            diff = list(difflib.unified_diff(
                backup_content_lines,    # 이전 버전
                current_content_lines,   # 현재 버전
                fromfile='previous version',
                tofile='current version',
                n=context_lines  
            ))
            
            # 변경사항이 실제로 존재할 경우에만 로그를 기록합니다.
            if diff:
                # [안정성 강화]
                # diff 리스트의 각 항목(라인)에서 혹시 모를 기존 줄바꿈 문자를 모두 제거한 후,
                # 파이썬의 표준 줄바꿈(\n)으로 다시 합쳐서 한 줄로 붙는 현상을 원천 차단합니다.
                diff_content = "\n".join(line.rstrip('\r\n') for line in diff)

                # 변경사항(diff)을 포함한 로그 엔트리를 구성합니다.
                log_entry_text = (
                    f"\n\n🦊=== Code changes at {timestamp} ===\n"
                    f"{diff_content}"
                )
                
                if flag_plain_log_enabled:
                    # 평문 로그 플래그가 True이면, 암호화하지 않고 log.plain 파일에 텍스트 추가('a') 모드를 사용합니다.
                    write_file_content(plain_log_file, log_entry_text, 'a')
                else:
                    # 평문 로그 플래그가 False이면, 기존 방식대로 암호화하여 로그를 기록합니다.
                    # 암호화를 위해 인코딩 후 암호화 함수를 호출합니다.
                    encrypted_entry = crypto.encrypt_data(log_entry_text.encode('utf-8'))
                    if encrypted_entry is None: return False
                    
                    # 기존 로그 파일에 이어서 새로운 내용을 추가하기 위해 바이너리 추가('ab') 모드를 사용합니다.
                    write_file_content(encrypted_log_file, encrypted_entry, 'ab')

                # 다음 커밋을 위해, 백업 파일을 현재 파일 내용으로 덮어쓰기('w')하여 업데이트합니다.
                write_file_content(backup_file, current_content_str, 'w')
                
        # 모든 과정이 성공적으로 완료되면 True를 반환합니다.
        return True
    # 로깅 과정에서 예상치 못한 오류가 발생할 경우를 대비한 최종 예외 처리입니다.
    except Exception as e:
        print(f"🚫 변경사항 기록 중 예상치 못한 오류 발생: {e}")
        return False