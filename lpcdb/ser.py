
from typing import NewType, Generic, List, Dict, get_args, get_origin

def _fromJson(cls, obj):

    origin = get_origin(cls)
    if origin is None and issubclass(cls, Serializable):
        inst = cls()

        for field, dtype in inst.__annotations__.items():
            origin = get_origin(dtype)
            if field in obj:
                if origin and origin is list:
                    args = get_args(dtype)
                    v = [_fromJson(args[0], item) for item in obj[field]]
                    setattr(inst, field, v)
                elif origin and origin is dict:
                    args = get_args(dtype)
                    v = {_fromJson(args[0], key): _fromJson(args[1], item) for key, item in obj[field].items()}
                    setattr(inst, field, v)
                elif origin:
                    raise NotImplementedError()
                elif issubclass(dtype, Serializable):
                    setattr(inst, field, dtype.fromJson(obj[field]))
                else:
                    setattr(inst, field, obj[field])
        return inst
    else:
        return obj

def _toJson(obj):

    if isinstance(obj, list):
        return [_toJson(x) for x in obj]
    elif isinstance(obj, dict):
        return {_toJson(k):_toJson(v) for k,v in obj.items()}
    elif isinstance(obj, Serializable):
        out = {}
        for field, dtype in obj.__annotations__.items():
            attr = getattr(obj, field)
            out[field] = _toJson(attr)
        return out
    else:
        return obj

class Serializable(object):
    def __init__(self, **kwargs):
        super(Serializable, self).__init__()

        for field, value in kwargs.items():
            setattr(self, field, value)

    @classmethod
    def fromJson(cls, obj):
        return _fromJson(cls, obj)

    def toJson(self):

        return _toJson(self)

    def __str__(self):

        return repr(self.toJson())

    def __repr__(self):

        return repr(self.toJson())
def main():

    class Point(Serializable):
        x : int = 0
        y : int = 0

    class Test(Serializable):
        p1 : Point = None
        p2 : List[int] = None
        p3 : Dict[int, float] = None

    r = Test.fromJson({"p1": {"x": 2}, "p2":[1], "p3":{1:2}})

    print(r)

if __name__ == '__main__':
    main()



