class Vector(tuple):
    def __new__(cls, it): return tuple.__new__(cls, it)
    x = property(lambda s: s[0]); y = property(lambda s: s[1]); z = property(lambda s: s[2])
    def __add__(s, o): return Vector(a + b for a, b in zip(s, o))
    def __sub__(s, o): return Vector(a - b for a, b in zip(s, o))
    def __mul__(s, k): return Vector(a * k for a in s)
    __rmul__ = __mul__
    @property
    def length(s): return sum(a * a for a in s) ** 0.5
    def normalized(s):
        l = s.length or 1.0; return Vector(a / l for a in s)
