class MyError(Exception):
    pass 


def say_nick(nick):
    if nick == "바보":
        raise MyError()
    print(nick)
    
say_nick('바보')

