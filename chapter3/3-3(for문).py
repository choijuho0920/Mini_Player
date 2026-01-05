# a = ["one","two","three"]
# for b in a:
#     print(b)

#continue -> 처음으로 
for a in range(2,10):
    for b in range(1, 10):
        print(a*b, end=" ")
    print(' ')
    
# print(a, end=" ") -> 한 줄 안 내리고 이어 씀 print는 기본적으로 '한줄 내려씀(\n)' 을 포함함
