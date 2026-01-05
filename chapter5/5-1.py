class FourCal : #클래스 (부모)
    def __init__(self, first, second):
        self.first = first
        self.second = second
    def setdata(self, first, second):
        self.first = first
        self.second = second
    def div(self):
        result = self.first / self.second
        return result
    def add(self):
        result = self.first + self.second
        return result
    def mul(self):
        result = self.first * self.second
        return result
    def sub(self):
        result = self.first - self.second
        return result
    
    
class MoreFourCal(FourCal): #클래스의 상속 (자녀)
    def pow(self):
        result = self.first ** self.second
        return result
    
class SafeFourCal(FourCal): #매서드 오버라이딩
    def div(self):
        if self.second == 0 :
            return ""
        else:
            return self.first / self.second
    
a = SafeFourCal(4,0)

print(a.add())
print(a.sub())
print(a.mul())
print(a.div())







#다음 파일 만들기 복습용용
# with open("c:/coding/chapter5/mod1.py","w") as f:
#     f.write("#mod1.py\n")
#     f.write("def add(a,b):\n    return a + b\n")
#     f.write("def sub(a,b):\n    return a-b")



