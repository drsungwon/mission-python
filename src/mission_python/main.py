# =================================================================================
#   수정 금지 안내 (Do NOT modify below lines)
# ---------------------------------------------------------------------------------
# - 답안은 main.py 파일에만 작성해야 합니다.
# - 아래 'DO NOT MODIFY' 부분을 절대로 수정하지 마세요.
# - main.py 파일외 프로젝트의 다른 파일들도 절대로 수정하지 않습니다.
# - 수정하지 않도록 하는 규정의 위반시, 개발 과정에 대한 평가 점수가 0점 처리됩니다.
# - Your answer must be written only in the main.py file.
# - Do NOT modify the 'DO NOT MODIFY' section below.
# - Do NOT modify any other files in the project besides main.py.
# - If these non-modification rules are violated, 
#   you will receive a ZERO for the development process evaluation.
# =================================================================================

import mission_python.util.utility # DO NOT MODIFY

# =================================================================================
#   아래 영역부터 코드 작성 (Write your code below)
# =================================================================================

def get_assets_sample_csv_without_header():
    """
    assets/sample.csv 파일을 읽어, 헤더를 제외한 첫 번째 데이터 행을 리스트 형태로 반환합니다.
    
    이 함수는 다음과 같은 과정을 통해 동작해요.
    1. CSV 파일을 안전하게 엽니다.
    2. 파일의 첫 줄(헤더)을 읽고 정보를 출력합니다.
    3. 파일의 두 번째 줄(첫 번째 데이터)을 읽어 반환합니다.
    4. 파일이 없거나, 비어있거나, 권한이 없는 등 다양한 오류 상황을 처리합니다.
    """
    
    # --- 학생들을 위한 안내 ---
    # `try...except` 구문은 혹시 모를 오류에 대비하는 안전장치와 같아요.
    # 파일을 읽는 도중 문제가 발생해도 프로그램이 갑자기 멈추지 않고,
    # `except` 블록에 작성된 코드를 실행하여 문제를 알려주고 안전하게 마무리할 수 있답니다.
    try:
        # --- 1. CSV 파일 열기 ---
        # 'with open(...) as file:' 구문은 파일을 열고, 작업이 끝나면 자동으로 닫아주는 아주 편리한 방법이에요.
        # 이렇게 하면 파일을 깜빡하고 닫지 않는 실수를 방지할 수 있습니다.
        #
        # encoding='utf-8-sig'는 파일을 UTF-8 형식으로 열겠다는 의미예요.
        # 여기서 '-sig'는 눈에 보이지 않는 특별한 코드(BOM, \ufeff)가 파일 맨 앞에 있어도
        # 똑똑하게 인식하고 자동으로 제거해준답니다. 훨씬 안정적이죠!
        #
        # ℹ️ 참고로 open() 함수에서 assets 폴더의 위치가, src 폴더와 동등한 레벨임을 기억합니다.
        with open("assets/sample.csv", 'r', encoding='utf-8-sig') as file:
            
            # --- 2. 헤더(첫 번째 줄) 읽기 및 처리 ---
            # file.readline()은 파일에서 한 줄을 통째로 읽어오는 명령어예요.
            header_line = file.readline()

            # 만약 파일이 완전히 비어있다면, readline()은 빈 문자열('')을 반환해요.
            # `if not header_line:` 은 header_line이 비어있는지 확인하는 코드랍니다.
            if not header_line:
                print("❌ [ERROR] CSV 파일이 비어 있습니다.")
                return [] # 내용이 없으므로 빈 리스트를 반환하고 함수를 종료해요.

            # .strip()은 줄 끝의 보이지 않는 공백이나 줄바꿈 문자(\n)를 제거해줘요.
            # .split(',')은 쉼표(,)를 기준으로 문자열을 잘라서 리스트로 만들어줍니다.
            headers = header_line.strip().split(',')
            print(f"✅ [INFO] 헤더를 성공적으로 읽었습니다.")
            print(f"-> {headers}")
            
            # --- 3. 본문(두 번째 줄) 읽기 및 처리 ---
            # 이제 헤더 다음 줄, 즉 첫 번째 데이터가 담긴 본문을 읽어볼 차례예요.
            first_body_line = file.readline()

            # 만약 파일에 헤더만 있고 데이터가 없다면, 이 부분은 빈 문자열이 될 거예요.
            # 여기서도 `strip()`을 사용해 공백만 있는 줄도 비어있는 것으로 처리합니다.
            if not first_body_line.strip():
                print("ℹ️ [INFO] 파일에 헤더만 있고, 본문 데이터는 없습니다.")
                return [] # 본문이 없으니 빈 리스트를 반환해요.

            # 헤더와 마찬가지로, 공백을 제거하고 쉼표로 분리하여 리스트로 만듭니다.
            values = first_body_line.strip().split(',')
            
            # --- 4. 성공 및 결과 반환 ---
            # 모든 과정이 성공적으로 끝났어요!
            return values

    # --- 오류/예외 처리 블록 ---
    # 이제부터는 `try` 블록에서 문제가 발생했을 때 실행될 부분이에요.

    # FileNotFoundError: 지정된 경로에 파일이 존재하지 않을 때 발생하는 오류입니다.
    except FileNotFoundError:
        print("❌ [ERROR] 'assets/sample.csv' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
        return []

    # PermissionError: 파일을 읽을 권한이 없을 때 발생하는 오류입니다.
    except PermissionError:
        print("❌ [ERROR] 'assets.sample.csv' 파일을 읽을 권한이 없습니다.")
        return []
    
    # UnicodeDecodeError: 파일이 'utf-8-sig' 형식으로 저장되지 않았을 때 발생할 수 있는 오류입니다.
    # 예를 들어, 다른 인코딩(euc-kr 등)으로 저장된 파일을 열려고 할 때 발생해요.
    except UnicodeDecodeError:
        print("❌ [ERROR] 파일 인코딩이 UTF-8이 아닌 것 같습니다. 파일을 UTF-8로 저장해주세요.")
        return []

    # Exception: 위에서 예상하지 못한 다른 모든 종류의 오류를 처리합니다.
    # 어떤 오류인지 `e`에 담아서 보여주기 때문에, 문제를 해결하는 데 큰 도움이 됩니다.
    except Exception as e:
        print(f"🛑 [CRITICAL] 예기치 않은 오류가 발생했습니다: {e}")
        return []
    
# ----------------------------------------------------------------------------------
#  메인(main) 코드 블록: 이 프로그램이 시작되는 지점입니다.
# `if __name__ == "__main__":` 은 이 파이썬 파일을 직접 실행했을 때만
# 아래 코드를 동작시키라는 특별한 의미를 가지고 있어요.
#
# 실행 방법:
#  1. 프로젝트 root 폴더에서 poetry install 명령을 실행합니다.
#  2. Visual Code의 인터프리터 선택에서, 프로젝트 인터프리터에 해당하는 항목을 선택합니다.
#  3. Terminal 사용시 프로젝트 root 폴더에서 다음 명령을 중 하나를 수형합니다. 
#     - poetry run python src/mission_python/main.py
#     - poetry run python -m mission_python.main
# ----------------------------------------------------------------------------------    

if __name__ == "__main__":
    
    print("\n🚀 CSV 파일에서 첫 번째 데이터 읽기 작업을 시작합니다...")
    print("==================================================")
    
    # --- 1. 위에서 정의한 함수를 호출해서 결과를 `res` 변수에 저장합니다.
    # 함수 내부에서 작업 진행 상황이 출력됩니다.
    res = get_assets_sample_csv_without_header()

    print("==================================================")
    print("✨ 최종 결과 ✨")
    
    # --- 2. 함수로부터 받은 결과(리턴 값)를 화면에 출력하기 ---
    # res 변수에 내용이 있는지 (빈 리스트가 아닌지) 확인합니다.
    if res:
        print("✅ [INFO] 성공적으로 첫 번째 본문 데이터를 가져왔습니다.")
        print(f"-> {res}")
    else:
        # res가 빈 리스트([])인 경우, 파일 읽기에 실패했거나 데이터가 없다는 의미입니다.
        # 구체적인 원인은 함수 내부에서 이미 출력되었습니다.
        print("ℹ️ 처리할 데이터가 없거나 파일을 읽는 중 오류가 발생했습니다.")
        
    print("==================================================")
    print("🎉 모든 작업이 완료되었습니다.")