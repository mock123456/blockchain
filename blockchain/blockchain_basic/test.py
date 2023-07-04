class wallet:
    def __init__(self):
        self.amount = 5


ls1 ={}
for i in range(5):
    ls1["wallet"+str(i)] = wallet()

print(type(ls1["wallet1"]))