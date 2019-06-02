from django.test import TestCase

# Create your tests here.

class Person:
    city = 'ma'
    def __init__(self,name):
        self.name = name
    def run(self):
        print('run')

p = Person('ma')

val = getattr(p,"city1")
print(val)