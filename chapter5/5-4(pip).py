from faker import Faker
fake = Faker('ko-KR')

fake.name()

fake.address()

fake.text()

print(fake.name())
print(fake.address())

