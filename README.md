# 🐍 Python Mission Framework

**과제 수행 및 개발 과정 자동 추적을 위한 파이썬 프로젝트 환경** <br>
*An automated Python project environment for assignments and development process tracking.*

---

## 🚀 프로젝트 소개 (Introduction)

본 프로젝트는 파이썬 프로그래밍 과제를 수행하기 위해 설계된 표준화된 개발 환경입니다. 학생 또는 개발자는 `main.py` 파일에 주어진 문제에 대한 해결 코드를 작성하는 데만 집중할 수 있습니다.

이 프레임워크의 핵심 기능은 **자동화된 개발 과정 추적 및 시스템 환경 기록**입니다. 사용자가 코드를 실행할 때마다, 백그라운드에서 다음과 같은 작업이 자동으로 수행됩니다.

1.  **최초 실행 시 시스템 핑거프린트 생성**: 부정행위 방지를 위해 최초 실행 환경의 고유 정보를 암호화하여 기록합니다 (`signature.encrypted`).
2.  **코드 변경 이력 자동 로깅**: `main.py` 파일의 모든 변경사항을 감지하여, 마치 Git처럼 수정 내역(diff)을 암호화하여 기록합니다 (`log.encrypted`).

이를 통해 개발자는 자신의 개발 과정을 돌아볼 수 있으며, 평가자는 과제 수행 과정을 투명하게 파악할 수 있습니다.

## ✨ 주요 기능 (Key Features)

- **📝 코드 작성 집중**: 사용자는 `src/mission_python/main.py` 파일 수정에만 집중하면 됩니다.
- **🔐 자동화된 버전 관리**: 코드를 실행할 때마다 변경사항이 암호화되어 자동으로 기록됩니다.
- **💻 시스템 환경 기록**: 최초 실행 시 시스템의 고유 정보를 단 한 번만 수집하여 평가의 공정성을 확보합니다.
- **📦 의존성 관리**: `Poetry`를 사용하여 프로젝트 의존성을 명확하고 재현 가능하게 관리합니다.
- **✅ 테스트 자동화**: `Pytest`를 통해 작성된 코드의 정합성을 쉽게 검증할 수 있습니다.

## 📂 프로젝트 구조 (Project Structure)

```
.
├── LICENSE
├── README.md
├── assets
│   └── sample.csv          # (필요시 작성) 문제 풀이에 사용될 샘플 데이터 
├── poetry.lock             # Poetry 의존성 잠금 파일
├── pyproject.toml          # 프로젝트 설정 및 의존성 정의 파일
├── src
│   └── mission_python      # 메인 소스 코드 패키지
│       ├── __init__.py     # ★ 패키지 초기화 및 자동화 스크립트 실행 지점
│       ├── log             # (자동 생성) 기록 및 서명 파일 저장소
│       │   ├── log.encrypted
│       │   ├── log.temp
│       │   └── signature.json.encrypted
│       ├── main.py         # ★★★ 사용자가 코드를 작성하는 유일한 파일
│       └── util            # 자동화 및 암호화를 위한 유틸리티 모듈
│           ├── crypto.py
│           ├── geolocation.py
│           └── utility.py
└── tests
    ├── __init__.py
    └── test_main.py        # main.py 코드를 검증하기 위한 테스트 코드
```

## 🛠️ 시작하기 (Getting Started)

### 사전 요구사항 (Prerequisites)

- [Python](https://www.python.org/downloads/) (3.9 이상 권장)
- [Poetry](https://python-poetry.org/docs/#installation) (Python 패키지 및 의존성 관리 도구)

### 설치 및 설정 (Installation)

1.  **프로젝트 복제 (Clone)**

    ```bash
    git clone [your-repository-url]
    cd [repository-name]
    ```

2.  **의존성 설치 (Install Dependencies)**

    Poetry를 사용하여 `pyproject.toml`에 명시된 모든 의존성을 설치합니다.

    ```bash
    poetry install
    ```

    이 명령은 프로젝트를 위한 가상 환경을 자동으로 생성하고 필요한 라이브러리를 설치합니다.

## 💻 사용 방법 (How to Use)

### 1. 과제 코드 작성

-   `src/mission_python/main.py` 파일을 열고 `DO NOT MODIFY` 주석 아래 영역에 문제 해결을 위한 코드를 작성합니다.

### 2. 프로그램 실행

-   작성한 코드를 실행하려면 프로젝트 루트 폴더에서 다음 명령어를 입력합니다.
-   **코드를 실행할 때마다 `main.py`의 변경사항이 자동으로 기록됩니다.**

    ```bash
    poetry run python -m mission_python.main
    ```
    또는
    ```bash
    poetry run python src/mission_python/main.py
    ```


### 3. 테스트 실행

-   작성한 코드가 요구사항을 충족하는지 확인하기 위해 `pytest`를 실행합니다.

    ```bash
    poetry run pytest
    ```

## ⚙️ 자동화 동작 원리 (How It Works)

이 프레임워크의 모든 자동화 기능은 `src/mission_python/__init__.py` 파일 덕분에 가능합니다.

1.  사용자가 `poetry run python ...` 명령으로 `main.py`를 실행하면, 파이썬은 `main.py` 상단에 있는 `import` 문을 처리합니다.
2.  이 과정에서 `mission_python` 패키지를 인식하고, 가장 먼저 패키지의 초기화 파일인 `__init__.py`를 **자동으로 실행**합니다.
3.  `__init__.py`는 다음 두 가지 핵심 모듈을 순서대로 호출합니다.
    -   **`geolocation.py`**: 시스템 서명 파일(`signature.json.encrypted`)이 있는지 확인하고, 없으면 생성합니다.
    -   **`utility.py`**: `main.py`의 변경사항을 추적하고, 변경이 있으면 암호화하여 로그(`log.encrypted`)를 남깁니다.
4.  `__init__.py`의 모든 작업이 완료된 후에야 비로소 `main.py`의 메인 로직이 실행됩니다.

이러한 방식으로 사용자는 별도의 명령 없이 코드를 실행하는 것만으로 모든 개발 과정을 기록하게 됩니다.

## 📄 라이선스 (License)

이 프로젝트는 [LICENSE](LICENSE) 파일에 명시된 라이선스 정책을 따릅니다.
