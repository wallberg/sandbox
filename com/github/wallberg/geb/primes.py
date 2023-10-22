# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Any

from queue import PriorityQueue

''' Recursively enumerate primes, GEB Chapter 3.'''


@dataclass(order=True)
class PrioritizedItem:
    priority: int
    data: Any=field(compare=False)


@dataclass(frozen=True)
class P:
    x: int


@dataclass(frozen=True)
class DND:
    x: int
    y: int


@dataclass(frozen=True)
class DF:
    x: int
    y: int


theorems = set()  # Set of seen theorems
q = PriorityQueue()  # Priority queue of new theorems to process


def add(t, *s):
    ''' Indicate that t has been derived from s. '''

    # # Print to screen if this is the first derivation of t
    # if not s:
    #     print(t)
    # else:
    #     print('{0} <-- {1}'.format(t, ' + '.join(str(x) for x in s)))

    priority = t.x + t.y
    q.put(PrioritizedItem(priority, t))


def axiom_schema():
    x = 2
    while True:
        for y in range(1, x):
            yield DND(x, y)
        x += 1


# Axioms
print(P(2))

asc = axiom_schema()

# Add next Axiom from Schema
add(next(asc))

# Iterate over the queue
while item := q.get():

    s = item.data

    if s not in theorems:
        theorems.add(s)

        # Rules
        if isinstance(s, DND):

            # Rule: xDNDy --> xDNDxy
            add(DND(s.x, s.x+s.y), s)

            # Rule: --DNDz --> zDF--
            if s.x == 2:
                add(DF(s.y, 2), s)

            # Rule: zDFx and x-DNDz --> zDFx-
            if (u := DF(s.y, s.x-1)) in theorems:
                add(DF(s.y, s.x), u, s)

        elif isinstance(s, DF):

            # Rule: zDFx and x-DNDz --> zDFx-
            if (u := DND(s.y+1, s.x)) in theorems:
                add(DF(s.x, s.y+1), s, u)

            # Rule: x-DFx --> Px-
            if s.x == s.y+1:
                p = P(s.x)
                print(p)

    # Add next Axiom from Schema
    add(next(asc))
