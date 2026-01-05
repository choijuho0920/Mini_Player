# def fs(box, money,b1,b3,b5):            # First salary
#     if box == 10:
#         print("money")
#     for 

# box = 0
# b1 = 175
# b3 = 400
# b5 = 700
# money = 0
# while box < 10:

#     if box == 10:
#         print("%f",money)

from itertools import combinations_with_replacement

def min_cost(box_target, costs):
    min_money = float('inf')
    best_combo = None

    # 가능한 모든 조합 탐색
    for i in range(1, box_target + 1):
        for combo in combinations_with_replacement(costs.keys(), i):
            if sum(combo) >= box_target:  # 박스 개수가 목표를 넘기면 유효한 조합
                money = sum(costs[b] for b in combo)
                
                if money < min_money:
                    min_money = money
                    best_combo = combo  # 최소 비용일 때의 조합 저장

    return min_money, best_combo

# 박스 종류와 가격 설정
costs = {1: 175, 3: 400, 5: 700}
box_target = 10

# 최소 비용과 조합 계산
min_money, best_combo = min_cost(box_target, costs)

# 결과 출력
print(f"최소 비용: {min_money:.2f} 원")
print(f"사용된 박스 조합: {best_combo}")