def printMenu():
   print("========메뉴========\n")
   print("1 두정수의 덧셈\n")
   print("2 화씨 온도를 섭씨 온도 변환\n")
   print("3 시그마\n")
   print("4 팩토리얼\n")
   print("5 최솟값 찾기\n")
   print("6 선택정렬\n")
   print("7 자연수 선택정렬\n")
   print("8 문자열의 크기(byte)\n")
   print("9 문자열에서 글자갯수?\n")
   print("q : 종료\n")
   
printMenu()

#1. 두 정수의 덧셈
def add(a,b):
   P = a + b 
   return P
#2 화씨 온도 변환
def f2c(fa):
      celtemp = (fa-32)*5/9
      return celtemp
#3 시그마
def sum(a,b):
       

ch = int(input())
match ch:
   case 1:
       a,b = map(int, input("두 정수를 입력하시오 :").split())
       result = add(a,b)
       print(result)
   case 2:
      fa = int(input("화씨 온도를 입력하시오:"))
      result = f2c(fa) 
      print(f"{result:.2f}")
   case 3: 
      a,b =map(int, input("시작 수와 끝 수를 입력하시오 (예: 2 10) :").split())
      result = sum(a,b)
      print(result)
   case 4:  
      