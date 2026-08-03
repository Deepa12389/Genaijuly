num1=int(input("Enter first number: "))
num2=int(input("Enter second number: "))
num3=input("Enter operator (+, -, *, /): ")
print("Result: ", end="")
if num3 == "+":
    print(num1 + num2)
elif num3 == "-":
    print(num1 - num2)
elif num3 == "*":
    print(num1 * num2)
elif num3 == "/":
    print(num1 / num2)