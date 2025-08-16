# =================================================================================
#   수정 금지 안내 (Do NOT modify below lines)
# ---------------------------------------------------------------------------------
# - 답안은 main.py 파일에 작성해야 합니다.
# - 아래 'DO NOT MODIFY' 부분을 절대로 수정하지 마세요.
#   수정 시, 개발 과정에 대한 평가 점수가 0점 처리됩니다.
# - Write your answer in the main.py file.
# - Do NOT modify code at the 'DO NOT MODIFY' comments.
#   If modified, you will receive a ZERO for the development process evaluation.
# =================================================================================

import answer.util.utility # DO NOT MODIFY

# =================================================================================
#   아래 영역부터 코드 작성 (Write your code below)
# =================================================================================

print("Hello, World!")

def print_asset_csv():
    try:
        # 1. CSV 파일을 읽어옵니다
        with open("assets/student_score_raw_format.csv", 'r', encoding='utf-8') as file:
            # 헤더 읽기
            headers = file.readline().strip().split(',')
            print("헤더 정보:", headers)  # 헤더 정보 출력
            print("CSV 파일 읽기 성공!")
            
            # 2. CSV 파일의 내용을 화면에 출력합니다.
            for line in file:
                values = line.strip().split(',')
                row_dict = dict(zip(headers, values))
                print(values)
                #row_dict = dict(zip(headers, values))
                #print(row_dict)
    except FileNotFoundError:
        print("CSV 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")

def get_max_final_score():
    # 1. CSV 파일을 읽어옵니다
    max_score = float('-inf')
    max_score_students = []
    
    try:
        with open("assets/student_score_raw_format.csv", 'r', encoding='utf-8') as file:
            # 헤더 읽기
            headers = file.readline().strip().split(',')
            score_index = headers.index("기말고사(100점)")
            student_id_index = headers.index('학번')
            print("CSV 파일 읽기 성공!")
            
            # 2. 기말고사 최대값을 찾고, 해당하는 학번을 저장합니다
            for line in file:
                values = line.strip().split(',')
                current_score = float(values[score_index])
                if current_score > max_score:
                    max_score = current_score
                    max_score_students = [values[student_id_index]]
                elif current_score == max_score:
                    max_score_students.append(values[student_id_index])
        
        # 3. 최대값을 가진 학번들을 리턴합니다.
        return max_score_students
    except FileNotFoundError:
        print("CSV 파일을 찾을 수 없습니다.")
        return []
    except Exception as e:
        print(f"오류 발생: {e}")
        return []

if __name__ == "__main__":
    # Example.1: CSV 파일 읽기 및 출력
    print("\nCSV 파일 읽기 및 출력:")
    print_asset_csv()

    # Example.2: 최고 점수 학생 목록 출력
    max_score_students = get_max_final_score()
    print("\n기말고사 최고점 학생 학번:")
    print(max_score_students)