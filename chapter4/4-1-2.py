#함수 안에 있는 변수는 지역 변수
#함수 밖에 있는 변수는 전역 변수


# a = 1  # 전역 변수

# def x(a):  # 함수의 매개변수와 지역 변수
#     a = a + 1  # 지역 변수 a를 사용
#     return a

# result = x(a)  # 함수 호출 시 전역 변수 a를 인수로 전달
# print(result)  # 출력: 2
# print(a)  # 전역 변수 a 출력: 1




#   함수 안에서 함수 밖의 변수를 변경하는 방법
#   return , global 사용하기

# vartest_return.py
a = 1 
def vartest(a): 
    a = a +1 
    return a

a = vartest(a)
print(a)

