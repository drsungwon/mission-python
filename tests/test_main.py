# ==============================================================================
# Poetry를 사용하여 테스트 실행하는 방법 (How to Run Tests with Poetry)
# ==============================================================================
#
# 아래 명령어들은 터미널에서 프로젝트의 루트 폴더(pyproject.toml 파일이 있는 곳)에서 실행해야 합니다.
#
# --- [주요 옵션 설명] ---
# -s : 테스트 중 print() 함수의 출력을 화면에 모두 보여줍니다. (silent 모드 해제)
# -v : 어떤 테스트가 실행되는지 파일명과 함수명을 자세히 보여줍니다. (verbose 모드)
#
# tests/test_main.py           : 특정 파일만 테스트하도록 지정합니다.
# ::test_function_name         : 특정 파일 내에서 특정 함수만 테스트하도록 지정합니다.
#
# ------------------------------------------------------------------------------

### 1. 화면 출력 없는 전체 테스트 실행
# 가장 일반적인 방법으로, 프로젝트의 모든 테스트가 통과하는지만 빠르게 확인합니다.
# poetry run pytest

### 2. 화면 출력 있는 전체 테스트 실행
# `print()` 문을 포함한 테스트의 상세한 진행 과정을 모두 보고 싶을 때 사용합니다. (디버깅용)
# poetry run pytest -s -v

### 3. 화면 출력 없이 `test_main`만 실행
# 여러 테스트 파일 중 `test_main.py` 파일 하나만 골라서 테스트합니다.
# poetry run pytest tests/test_main.py

### 4. 화면 출력 있는 `test_main`만 실행
# `test_main.py` 파일의 상세한 실행 과정을 확인할 때 사용합니다.
# poetry run pytest -s -v tests/test_main.py

### 5. 화면 출력 없이 특정 함수(`test_..._success`)만 실행
# 수많은 테스트 중 `test_get_assets_sample_csv_without_header_success` 함수 하나만
# 집중해서 빠르게 테스트할 때 사용합니다.
# poetry run pytest tests/test_main.py::test_get_assets_sample_csv_without_header_success

### 6. 화면 출력 있는 특정 함수(`test_..._success`)만 실행
# 특정 함수의 모든 동작 과정을 세밀하게 디버깅하고 싶을 때 사용합니다.
# poetry run pytest -s -v tests/test_main.py::test_get_assets_sample_csv_without_header_success

# ==============================================================================

# --- 1. 필요한 모듈 가져오기 (Import) ---
# os: 파일 경로를 다루기 위해 사용합니다. (e.g., 폴더와 파일명을 합쳐 경로 생성)
# shutil: 파일이나 폴더를 삭제하기 위해 사용합니다. (e.g., 테스트 후 생성한 폴더 정리)
# pytest: 테스트 프레임워크 자체로, @pytest.fixture 같은 특별한 기능을 사용하기 위해 필요합니다.
import os
import shutil
import pytest

# 테스트하려는 실제 함수를 main.py 파일에서 가져옵니다.
# from {패키지명}.{모듈명} import {함수명} 형태로 경로를 지정합니다.
from mission_python.main import get_assets_sample_csv_without_header

# --- 2. 실제 테스트를 수행하는 함수 ---
# 테스트 함수는 항상 'test_' 라는 이름으로 시작해야 pytest가 인식할 수 있습니다.
def test_get_assets_sample_csv_without_header_success(capsys):
    """
    get_assets_sample_csv_without_header 함수가 정확한 데이터를 반환하는지 테스트합니다.
    
    - capsys: pytest의 내장 fixture로, print() 같은 표준 출력을 가로채서 테스트 중 화면이 지저분해지는 것을 막고,
              필요하다면 나중에 출력 내용을 확인할 수도 있게 해줍니다.
    """
    
    # 테스트의 성공/실패 여부를 담을 변수를 준비합니다.
    is_success = False
    
    try:
        # === [준비 - Arrange] ===
        # 이 테스트가 통과하기 위한 '기대하는 결과값'을 미리 정의합니다.
        print("[ARRANGE] 기대 결과값을 정의합니다.")
        expected_result = ['1', '컴퓨터공학부', '3', '2023000003', 'Anthony Sanchez', '0', '10.0', '39', '42', '46.30', 'B+']
        
        # === [실행 - Act] ===
        # 실제로 테스트하고 싶은 함수를 호출하여 '실제 결과값'을 얻습니다.
        print("[ACT] 테스트 대상 함수를 실행합니다.")
        actual_result = get_assets_sample_csv_without_header()
        
        # === [단언 - Assert] ===
        # 'assert'는 "이 조건이 반드시 참(True)이어야 한다"고 선언하는 명령어입니다.
        # 만약 조건이 거짓(False)이면, 테스트는 즉시 실패 처리되고 'AssertionError'가 발생합니다.
        print("[ASSERT] 실제 결과가 기대 결과와 일치하는지 확인합니다.")
        assert actual_result == expected_result
        
        # assert 문을 무사히 통과했다면 테스트는 성공한 것입니다.
        is_success = True

    finally:
        # try 블록의 코드가 성공하든, 중간에 실패하든, 이 'finally' 블록은 항상 실행됩니다.
        # 이를 이용해 테스트의 최종 결과를 화면에 명확하게 보여줄 수 있습니다.
        if is_success:
            print("\n✅ [RESULT] 테스트 성공! 함수가 기대한 값을 정확히 반환했습니다.")
        else:
            print("\n❌ [RESULT] 테스트 실패! 함수가 반환한 값이 기대와 다릅니다.")