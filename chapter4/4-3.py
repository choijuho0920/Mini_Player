def print_pyramid(char):
    levels = 10  # 최대 10줄로 제한
    for i in range(1, levels + 1):
        print(f"{char * i:^{levels * 2}}")

# 문자 입력 받기
char = input("문자를 입력하세요: ")
print_pyramid(char)

