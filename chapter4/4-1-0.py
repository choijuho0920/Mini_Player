# def a(a,b):
#     print(a**b) 
#             #a,b는 매개변수(=인수,파라미터) 

# a(3,4)
#             # c = a(3,4) #3,4는 인자

# def a(*args):
#     result = 0
#     for i in args:
#         result = result + i
#     return result

# def a(*t):
#     b = 0
#     for i in t:
#         b = b + i
#     return b

# print(a(1,2,3,4,5,6,7,8,9,10))

def add_mul(choice, *args): 
     if choice == "add":   # 매개변수 choice에 "add"를 입력받았을 때
         result = 0 
         for i in args: 
             result = result + i 
     elif choice == "mul":   # 매개변수 choice에 "mul"을 입력받았을 때
         result = 1 
         for i in args: 
             result = result * i 
     return result 

result1 = add_mul('add',1,2,3) 
result2 = add_mul('mul',1,2,3)
 


print(result1,result2)


