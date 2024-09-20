class Environment:
    def __init__(self, values) -> None:
        self.values:list[dict[str:Reference]] = [values]

    def push(self,values):
        self.values.append(values)

    def pop(self, values):
        self.values.pop()

    def lookup(self, name) -> "Reference":
        for i in range(len(self.values),0,-1):
            if name in self.values[i]:
                return self.values[i][name]
    
    def assign(self,name,value):
        for i in range(len(self.values),0,-1):
            if name in self.values[i]:
                self.values[i][name] = value

class Reference:
    def __init__(self, value) -> None:
        value = value