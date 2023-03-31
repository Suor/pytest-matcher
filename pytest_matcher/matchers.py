import re


class MatcherRegex:
    """Special class to eq by matching regex"""
    def __init__(self, pattern, flags=0):
        self.regex = re.compile(pattern, flags)

    def __repr__(self):
        flags = self.regex.flags & ~32  # 32 is default
        if flags:
            return f"M.re(r'{self.regex.pattern}', {flags})"
        else:
            return f"r'{self.regex.pattern}'"

    def __eq__(self, other):
        return self.regex.search(other)


class MatcherDict:
    """Special class to eq by matching only presented dict keys"""
    # NOTE: can't inherit from dict because that makes D() == M.dict() to not call our __eq__,
    #       if D is a subclass of a dict
    def __init__(self, __d=None, **keys):
        self.d = __d or {}
        if keys:
            self.d = self.d.copy()
            self.d.update(keys)

    def __repr__(self):
        return f"M.dict({', '.join(f'{k}={repr(v)}' for k, v in self.d.items())})"

    def __len__(self):
        return len(self.d)

    def __eq__(self, other):
        missing = object()
        return all(other.get(name, missing) == v for name, v in self.d.items())


class MatcherAny:
    """Equals to anything, a way to ignore parts of data structures on comparison"""
    def __repr__(self):
        return "M.any"

    def __eq__(self, other):
        return True


class MatcherAnyOf:
    def __init__(self, *items):
        self.items = items

    def __repr__(self) -> str:
        inner = ", ".join(map(repr, self.items))
        return f"M.any_of({inner})"

    def __eq__(self, other: object) -> bool:
        return other in self.items


class MatcherUnordered:
    """Compare list contents, but do not care about ordering. (E.g. sort lists first,
    then compare.) If you care about ordering, then just compare lists directly."""
    def __init__(self, items):
        self.items = sorted(items)

    def __repr__(self):
        inner = ", ".join(map(repr, self.items))
        return f"M.unordered({inner})"

    def __eq__(self, other):
        return self.items == sorted(other)


class MatcherIsa:
    def __init__(self, *types):
        assert all(isinstance(t, type) for t in types)
        self.types = types

    def __repr__(self):
        inner = ", ".join(t.__name__ for t in self.types)
        return f"M.isa({inner})"

    def __eq__(self, other):
        return isinstance(other, self.types)


class Matcher:
    """Special class to eq by existing attrs. Also provides contructors for other types of matching:
        - regex
        - dict
        - unordered sequence
        - by class
        - "any of"
        - any wildcard

    The purpose is to simplify asserts containing objects and nested data structures, i.e.:

        assert result.errors == [
            M(message=M.re("^Smth went wrong:"), extensions=M.dict(code=523)),
            M(message=M.any, tags=M.unordered("one", "two")),
        ]

    Here all the structures like lists and dicts are followed as usual both outside and inside
    a mather object. These could be freely intermixed.
    """
    def __init__(self, **attrs):
        self.attrs = attrs

    def __repr__(self):
        name = "M"
        attrs = self.attrs
        if "__class__" in attrs:
            name += "." + attrs["__class__"].__name__
            attrs = {k: v for k, v in attrs.items() if k != "__class__"}
        return f"{name}({', '.join(f'{k}={repr(v)}' for k, v in attrs.items())})"

    def __eq__(self, other):
        # Unforturnately this doesn't work with classes with slots
        # self.__class__ = other.__class__
        missing = object()
        return all(getattr(other, name, missing) == v for name, v in self.attrs.items())

    any = MatcherAny()

    @staticmethod
    def any_of(*items):
        return MatcherAnyOf(*items)

    @staticmethod
    def re(pattern, flags=0):
        return MatcherRegex(pattern, flags)

    @staticmethod
    def dict(_d=None, **keys):
        return MatcherDict(_d, **keys)

    @staticmethod
    def unordered(*elems):
        return MatcherUnordered(elems)

    @staticmethod
    def isa(*elems):
        return MatcherIsa(*elems)

    def approx(expected, rel=None, abs=None, nan_ok=False):
        from .approx import approx  # Requires pytest

        return approx(expected, rel=rel, abs=abs, nan_ok=nan_ok)
