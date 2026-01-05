# def greet(name, greeting="Hello"):
#     print(f"{greeting}, {name}!")

# greet("Alice")
# greet("Bob", greeting="Hi")

#kwargs는 그냥 딕셔너리 형태로 출력하는 함수

def say_nick(nick): 
    if nick == "바보": 
        return print("사용할 수 없는 이름입니다.")
    print(f"나의 별명은 {nick}입니다.")
   
    
say_nick("바보") 
