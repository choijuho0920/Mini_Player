# while
# 나무찍기 = 10
# while 나무찍기 > 0 :
#     나무찍기 -= 1  
#     print('도끼의 내구도가%d번 남았습니다다.' % 나무찍기)
#     if 나무찍기 == 0:
#         print("도끼가 깨졌습니다다.")

# prompt = """
# 1.Add
# 2.Del
# 3.List
# 4.Quit
# Enter number:"""

# number = 0
# while number !=1234:
#     print(prompt)
#     number = int(input())
# else :
#     ptint("성공")


# 커피지판기
# coffee = 10
# coin = 100
# if coin < 100 :
#     print("잔액부족입니다.")
# while coin >= 100 :
#     coin = coin -100
#     print("커피 나오는 중")
#     coffee = coffee -1
#     print("남은 커피의 양은 %d개 입니다" % coffee)
#     print("남은 금액액은 %d입니다" % coin)
    
#     if coffee == 0 : 
#         print("커피 부족입니다.")
#         break
#     if coin < 100 :
#         print("잔액부족 입니다.")
#         break

#무한루프
# while True:
#     print(1)
#     print(2)
#     print(3)
#     break


for i in range(3):
    for j in range(2):
        print(f"i: {i}, j: {j}")




        
        