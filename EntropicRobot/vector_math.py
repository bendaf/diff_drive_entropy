class Vector2:
    def __init__(self, x=0., y=0.):
        self.x = x
        self.y = y

    def __str__(self):
        return "Vector2(%s, %s)" % (self.x, self.y)

    def __add__(self, other):
        return Vector2(self.x+other.x, self.y+other.y)

    def __sub__(self, other):
        return Vector2(self.x-other.x, self.y-other.y)

    def __mul__(self, scale_factor):
        return Vector2(self.x * scale_factor, self.y * scale_factor)

    def __truediv__(self, scale_factor):
        return Vector2(self.x / scale_factor, self.y / scale_factor)

    def length(self):
        return (self.x*self.x + self.y*self.y)**0.5

    def normal(self):
        return self/self.length()

    def as_int(self):
        return int(self.x), int(self.y)
