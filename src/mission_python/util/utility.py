"""
주의. 이 파일은 학생이 직접 수정하지 않습니다.
교수가 배포한 프로젝트의 일부로, main.py의 변경 사항을 자동으로
암호화하여 기록하는 역할을 합니다.
"""
import os
import sys
import difflib
from datetime import datetime
from typing import List, Optional, Union
from functools import wraps

# 내부 모듈 임포트: 암호화 로직 담당
from . import crypto

def safe_file_operation(func):
    """파일 작업 데코레이터 - 예외 처리"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            print(f"🚫 파일을 찾을 수 없습니다: {str(e)}")
        except PermissionError as e:
            print(f"🚫 파일 접근 권한이 없습니다: {str(e)}")
        except Exception as e:
            print(f"🚫 파일 작업 중 오류 발생: {str(e)}")
        return None
    return wrapper

@safe_file_operation
def read_file_content(file_path: str, mode: str = 'r') -> Optional[Union[str, bytes]]:
    """파일 내용 읽기 (텍스트 또는 바이너리)"""
    encoding = 'utf-8' if 'b' not in mode else None
    with open(file_path, mode, encoding=encoding) as f:
        return f.read()

@safe_file_operation
def write_file_content(file_path: str, content: Union[str, bytes], mode: str = 'w'):
    """파일 내용 쓰기 (텍스트 또는 바이너리)"""
    encoding = 'utf-8' if 'b' not in mode and isinstance(content, str) else None
    with open(file_path, mode, encoding=encoding) as f:
        f.write(content)

def commit_changes():
    """main.py의 변경사항을 암호화하여 로컬에 커밋(기록)합니다."""
    try:
        project_root = os.path.dirname(os.path.abspath(sys.argv[0]))
        main_py_file = os.path.join(project_root, 'main.py')
        
        if not os.path.exists(main_py_file):
            raise FileNotFoundError(f"main.py를 찾을 수 없습니다: {main_py_file}")
            
        if not log_code_changes(main_py_file, project_root):
            raise RuntimeError("코드 변경사항 암호화 기록에 실패했습니다.")
            
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n🦊 Code changes successfully encrypted and logged at {timestamp}\n")

    except Exception as e:
        print(f"🚫 심각한 오류 발생: {str(e)}", file=sys.stderr)
        print(f"🚫 담당 교수에게 문의하세요.")
        # In a real scenario, you might not want to exit, but for this utility it's okay.
        # sys.exit(1) 

# 파일: src/logger_module/utility.py

def log_code_changes(target_file: str, project_root: str) -> bool:
    """
    코드 변경사항을 암호화하여 로깅하고, 평문 백업을 유지합니다.
    (v2.0 - diff 정확도 개선 버전)
    """
    try:
        log_dir = os.path.join(project_root, 'log')
        encrypted_log_file = os.path.join(log_dir, 'history.log.encrypted')
        backup_file = os.path.join(log_dir, 'main.py.backup') # 비교를 위한 평문 백업
        
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        current_content_str = read_file_content(target_file)
        if current_content_str is None: return False
        # splitlines(True) 대신 keepends=True 사용이 표준
        current_content_lines = current_content_str.splitlines(keepends=True)

        is_first_commit = not os.path.exists(backup_file)

        if is_first_commit:
            # 최초 커밋 처리
            # 학생에게는 보이지 않을 헤더이므로 파일명은 간단하게 처리
            log_entry_text = (
                f"🦊=== Code Change Tracking Started at {timestamp} ===\n"
                f"🦊=== Initial version of {os.path.basename(target_file)} ===\n\n"
                f"{current_content_str}"
            )
            encrypted_entry = crypto.encrypt_data(log_entry_text.encode('utf-8'))
            if encrypted_entry is None: return False
            
            write_file_content(encrypted_log_file, encrypted_entry, 'wb')
            write_file_content(backup_file, current_content_str, 'w')
        else:
            # 변경사항 커밋 처리
            backup_content_str = read_file_content(backup_file)
            if backup_content_str is None: return False
            backup_content_lines = backup_content_str.splitlines(keepends=True)
            
            # --- ★★★ 핵심 개선 부분 ★★★ ---
            # 변경이 없는 경우(diff가 비어있음) 아무 작업도 하지 않고 성공 처리
            if backup_content_lines == current_content_lines:
                return True
                
            # 컨텍스트 라인(n)의 수를 두 파일의 총 라인 수 합계만큼으로 넉넉하게 설정합니다.
            # 이는 difflib이 파일 전체를 컨텍스트로 사용하여 위치를 정확하게 찾도록 보장합니다.
            context_lines = len(backup_content_lines) + len(current_content_lines)
            
            diff = list(difflib.unified_diff(
                backup_content_lines,
                current_content_lines,
                fromfile='previous version',
                tofile='current version',
                n=context_lines  # <-- 컨텍스트 라인 수를 최대로 설정
            ))
            # --------------------------------
            
            if diff:
                log_entry_text = (
                    f"\n\n🦊=== Code changes at {timestamp} ===\n"
                    f"{''.join(diff)}"
                )
                encrypted_entry = crypto.encrypt_data(log_entry_text.encode('utf-8'))
                if encrypted_entry is None: return False
                
                # 암호화된 청크를 로그 파일에 추가
                write_file_content(encrypted_log_file, encrypted_entry, 'ab')
                # 평문 백업 파일 업데이트
                write_file_content(backup_file, current_content_str, 'w')
                
        return True
    except Exception as e:
        print(f"🚫 변경사항 기록 중 예상치 못한 오류 발생: {e}")
        return False