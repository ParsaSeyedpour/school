class Rectangle:
    def __init__(self, length, width):
        self.length = length
        self.width = width
    
    @property
    def area(self):
        return self.length * self.width

 
rect = Rectangle(5, 3)
print(rect.area)  



class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius
    
    @property
    def fahrenheit(self):
        return (self.celsius * 9/5) + 32

# استفاده
temp = Temperature(25)
print(temp.fahrenheit)  
temp.celsius = 30
print(temp.fahrenheit) 