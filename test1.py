# class Student:
#     def __init__(self, name, grade):
#         self.name = name
#         self.grade = grade

# stu = Student("Ali", "A")

# print(getattr(stu, "name"))       # خروجی: Ali
# print(getattr(stu, "grade"))      # خروجی: A
# print(getattr(stu, "age", "N/A")) # چون age وجود ندارد → خروجی: N/A




# class Student:
#     def __init__(self, name, grade):
#         self.name = name
#         self.grade = grade

# s = Student("Sara", "B")

# # تغییر ویژگی موجود
# setattr(s, "grade", "A+")
# print(s.grade)  # خروجی: A+

# # اضافه کردن ویژگی جدید
# setattr(s, "age", 20)
# print(s.age)    # خروجی: 20


class Teacher:
    def __init__(self, name):
        self.name = name

t = Teacher("Reza")

# بررسی
print(hasattr(t, "name"))  # True
print(hasattr(t, "age"))   # False




# # گرفتن
# print(getattr(t, "name"))          # Reza
# print(getattr(t, "age", "unknown"))# چون age وجود ندارد → unknown

# # تغییر یا اضافه کردن
# setattr(t, "age", 35)
# print(t.age)  # 35

# # حذف
# delattr(t, "age")
# print(hasattr(t, "age"))  # False















# class Person:
#     def __init__(self, name):
#         self.name = name

# p = Person("Ali")

# print(hasattr(p, "name"))     # True  ✅
# print("name" in p.__dict__)   # True  ✅

# print(hasattr(p, "__class__"))   # True  (attribute ارث‌بری شده از object)
# print("__class__" in p.__dict__) # False (در __dict__ مستقیم ذخیره نشده)
