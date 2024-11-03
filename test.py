a = str(input("Enter a string: "))

file = open('test.txt', 'a', encoding='utf-8')
file.write(a)
file.close()