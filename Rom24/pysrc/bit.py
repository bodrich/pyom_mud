import json
from collections import OrderedDict
import logging
logger = logging.getLogger()

import game_utils
import state_checks
import tables


class Bit:
    """
    The Bit() class is meant to be a drop-in replacement for the old
    DikuMUD style 'bitflag' variable.  Because DikuMUD was written on
    limited hardware, many techniques were used to try and fit as much
    data as possible into a small amount of memory.

    Rather than using distinct variables, 32 boolean values were
    crammed into a single integer, with each bit being assigned a
    use.  #define'd macros were created to make it somewhat eaasier
    to check, set, and clear them.  And, in Rom and later derivatives,
    functions were made to convert them to and from textual names, so
    they could be stored in area files without worrying about architecture
    changes screwing up the order.

    This class reimplements that concept, but in a more useful way.  You
    can directly use a set of names to set, clear, or check a bit.  You can
    use a list of names to do this for multiples at a time.  You can get back
    the name OR numerical value, and you can still use the numbers if you
    like.
    """
    def __init__(self, default: int=0, flags: OrderedDict=None):
        """
        The constructor allows you to specify the default value, as
        well as providing an ordered dict which will be used for
        bit position/name to number mapping.

        :param default: An integer of the starting bit values, usually 0.
        :type default: int
        :param flags: An ordered dict holding the name/number mappings used.
        :type flags: OrderedDict
        :return:
        :rtype:
        """
        self.bits = default
        self._flags = flags

    def __add__(self, other):
        """
        This implements addition between integers and Bit() objects.

        :param other: An integer value to be numerically added to self.bits.
        :type other: int
        :return: A new Bit() object with the value added.
        :rtype: Bit
        """
        return Bit(self.bits + self.from_name(other), self.flags)

    def __radd__(self, other):
        return Bit(self.from_name(other) + self.bits, self.flags)

    def __iadd__(self, other):
        self.bits += self.from_name(other)
        return self

    def __sub__(self, other):
        return Bit(self.bits - self.from_name(other), self.flags)

    def __rsub__(self, other):
        return Bit(self.from_name(other) - self.bits, self.flags)

    def __isub__(self, other):
        self.bits -= self.from_name(other)
        return self

    def __mul__(self, other):
        if isinstance(other, int):
            return Bit(self.bits * other, self.flags)
        raise TypeError('You can only multiply a Bit() value by an integer, not a ' + repr(other))

    def __rmul__(self, other):
        if isinstance(other, int):
            return Bit(other * self.bits, self.flags)
        raise TypeError('You can only multiply a Bit() value by an integer, not a ' + repr(other))

    def __imul__(self, other):
        if isinstance(other, int):
            self.bits *= other
            return self
        raise TypeError('You can only multiply a Bit() value by an integer, not a ' + repr(other))

    def __truediv__(self, other):
        if isinstance(other, int):
            return Bit(self.bits // other, self.flags)
        raise TypeError('You can only divide a Bit() value by an integer, not a ' + repr(other))

    def __rtruediv__(self, other):
        if isinstance(other, int):
            return Bit(other // self.bits, self.flags)
        raise TypeError('You can only divide a Bit() value by an integer, not a ' + repr(other))

    def __itruediv__(self, other):
        if isinstance(other, int):
            self.bits //= other
            return self
        raise TypeError('You can only divide a Bit() value by an integer, not a ' + repr(other))

    def __floordiv__(self, other):
        if isinstance(other, int):
            return Bit(self.bits // other, self.flags)
        raise TypeError('You can only divide a Bit() value by an integer, not a ' + repr(other))

    def __rfloordiv__(self, other):
        if isinstance(other, int):
            return Bit(other // self.bits, self.flags)
        raise TypeError('You can only divide a Bit() value by an integer, not a ' + repr(other))

    def __ifloordiv__(self, other):
        if isinstance(other, int):
            self.bits //= other
            return self
        raise TypeError('You can only divide a Bit() value by an integer, not a ' + repr(other))

    def __mod__(self, other):
        if isinstance(other, int):
            return Bit(self.bits % other, self.flags)
        raise TypeError('You can only get the integer modulo of a Bit() value, not a ' + repr(other))

    def __rmod__(self, other):
        if isinstance(other, int):
            return Bit(other % self.bits, self.flags)
        raise TypeError('You can only get the integer modulo of a Bit() value, not a ' + repr(other))

    def __imod__(self, other):
        if isinstance(other, int):
            self.bits %= other
            return self
        raise TypeError('You can only get the integer modulo of a Bit() value, not a ' + repr(other))

    def __pow__(self, power, modulo=None):
        if isinstance(power, int):
            return Bit(self.bits ** power, self.flags)
        raise TypeError('You can only raise a Bit() value to an integer power, not a ' + repr(power))

    def __rpow__(self, power, modulo=None):
        if isinstance(power, int):
            return Bit(power ** self.bits, self.flags)
        raise TypeError('You can only raise a Bit() value to an integer power, not a ' + repr(power))

    def __ipow__(self, power, modulo=None):
        if isinstance(power, int):
            self.bits **= power
            return self
        raise TypeError('You can only raise a Bit() value to an integer power, not a ' + repr(power))

    def __lshift__(self, other):
        if isinstance(other, int):
            return Bit(self.bits << other, self.flags)
        raise TypeError('You can only shift a Bit() value by an integer, not a ' + repr(other))

    def __rlshift__(self, other):
        if isinstance(other, int):
            return Bit(other << self.bits, self.flags)
        raise TypeError('You can only shift a Bit() value by an integer, not a ' + repr(other))

    def __ilshift__(self, other):
        if isinstance(other, int):
            self.bits <<= other
            return self
        raise TypeError('You can only shift a Bit() value by an integer, not a ' + repr(other))

    def __rshift__(self, other):
        if isinstance(other, int):
            return Bit(self.bits >> other, self.flags)
        raise TypeError('You can only shift a Bit() value by an integer, not a ' + repr(other))

    def __rrshift__(self, other):
        if isinstance(other, int):
            return Bit(other >> self.bits, self.flags)
        raise TypeError('You can only shift a Bit() value by an integer, not a ' + repr(other))

    def __irshift__(self, other):
        if isinstance(other, int):
            self.bits >>= other
            return self
        raise TypeError('You can only shift a Bit() value by an integer, not a ' + repr(other))

    def __and__(self, other):
        return Bit(self.bits & self.from_name(other), self.flags)

    def __rand__(self, other):
        return Bit(self.from_name(other) & self.bits, self.flags)

    def __iand__(self, other):
        self.bits &= self.from_name(other)
        return self

    def __xor__(self, other):
        return Bit(self.bits ^ self.from_name(other), self.flags)

    def __rxor__(self, other):
        return Bit(self.from_name(other) ^ self.bits, self.flags)

    def __ixor__(self, other):
        self.bits ^= self.from_name(other)
        return self

    def __or__(self, other):
        return Bit(self.bits | self.from_name(other), self.flags)

    def __ror__(self, other):
        return Bit(self.from_name(other) | self.bits, self.flags)

    def __ior__(self, other):
        self.bits |= self.from_name(other)
        return self

    def __bool__(self):
        return True if self.bits else False

    def __neg__(self):
        return Bit(-self.bits, self.flags)

    def __pos__(self):
        return Bit(+self.bits, self.flags)

    def __abs__(self):
        return Bit(abs(self.bits), self.flags)

    def __int__(self):
        return self.bits

    def __getattr__(self, name):
        if not name.startswith('is_'):
            raise AttributeError
        flags = self.flags
        flag = state_checks.name_lookup(flags, name[3:])
        if not flag:
            raise AttributeError
        return self.is_set(flags[flag].bit)

    @property
    def flags(self):
        flags = OrderedDict()
        if type(self._flags) == list:
            for d in self._flags:
                for k, v in d.items():
                    flags[k] = v
        else:
            flags = self._flags
        return flags

    def set_bit(self, bit):
        self.bits |= self.from_name(bit)

    def clear_bit(self, bit):
        self.bits &= ~self.from_name(bit)

    def rem_bit(self, bit):
        self.bits &= ~self.from_name(bit)

    def is_set(self, bit):
        return self.bits & self.from_name(bit)

    def read_bits(self, area, default=0):
        area, bits = game_utils.read_flags(area)
        self.set_bit(bits)
        self.set_bit(default)
        return area

    #lets you chose the flag table. so act/plr flags will save correctly.
    def print_flags(self, flags):
        holder = self._flags
        self._flags = flags
        as_str = repr(self)
        self._flags = holder
        return as_str

    def from_name(self, name):
        if type(name) is int:
            return name
        elif type(name) is list or type(name) is tuple:
            bitstring = name
        elif isinstance(name, Bit):
            bitstring = repr(name)
        else:
            name = name.strip()
            bitstring = name.split(' ')
        bits = 0
        flags = self.flags
        for tok in flags.values():
            if tok.name in bitstring:
                bits += tok.bit
        return bits

    def __repr__(self):
        buf = ""
        if not self.flags:
            return buf
        flags = self.flags
        for k, fl in flags.items():
            if self.is_set(fl.bit):
                buf += " %s" % fl.name
        return buf


def to_json(b):
    """
    A Bit() object can be serialized to json data by
    js = json.dumps(b, default=bit.to_json)

    :param b:
    :return:
    """
    if isinstance(b, Bit):
        return {'__Bit__': True, 'flags': b.flags, 'bits': b.bits}
    raise TypeError(repr(b) + " is not JSON serializable")


def from_json(js):
    """
    A Bit() object can be reconstructed from json data by
    b = json.loads(js, object_pairs_hook=bit.from_json)

    :param js:
    :return:
    """
    ok = False
    for i in js:
        if i[0] == '__Bit__':
            ok = True
    if ok:
        d_bits = 0
        for i in js:
            if i[0] == '__Bit__':
                continue
            elif i[0] == 'bits':
                d_bits = i[1]
            elif i[0] == 'flags':
                d_flags = OrderedDict()
                for j in i[1]:
                    k = j[0]
                    v = j[1]
                    d_flags[k] = tables.flag_type._make(v)
                b = Bit(flags=d_flags)
                b.set_bit(d_bits)
                return b
            else:
                raise TypeError(repr(js) + " is not a valid Bit serialization")
    return js
