def convert_base(number, from_base, to_base):
    # 정수와 실수 부분 나누기
    integer_part, _, fractional_part = number.partition('.')

    # 정수 부분 변환
    base10_integer = int(integer_part, from_base)

    # 실수 부분 변환
    base10_fractional = 0
    for i, digit in enumerate(fractional_part):
        base10_fractional += int(digit, from_base) * (from_base ** -(i + 1))

    # 전체 합산
    base10_number = base10_integer + base10_fractional

    # 목표 진법으로 변환
    alphabet = "0123456789ABCDEF"
    integer_result = ""
    fractional_result = ""

    # 정수 부분 변환
    while base10_integer > 0:
        integer_result = alphabet[base10_integer % to_base] + integer_result
        base10_integer //= to_base

    # 실수 부분 변환
    fractional_part = base10_fractional
    while fractional_part > 0 and len(fractional_result) < 10:  # 길이를 제한합니다.
        fractional_part *= to_base
        fractional_digit = int(fractional_part)
        fractional_result += alphabet[fractional_digit]
        fractional_part -= fractional_digit

    return integer_result or "0" + ('.' + fractional_result if fractional_result else '')

# 사용 예시
print(convert_base("19", 10, 2))  # 이진수에서 16진수로 변환