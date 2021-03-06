# -*- coding: utf-8 -*-
import unittest
from math import floor
from itertools import product
from array import array
from copy import copy
import logging

from com.github.wallberg.taocp.Backtrack import walkers_backtrack
from com.github.wallberg.taocp.Tuples import preprimes

logger = logging.getLogger('com.github.wallberg.taocp.Commafree')
#ger logger.addHandler(logging.StreamHandler())
# log.setLevel(logging.INFO)

'''
Explore Backtrack Programming from The Art of Computer Programming, Volume 4,
Fascicle 5, Mathematical Preliminaries Redux; Introduction to Backtracking;
Dancing Links, 2020

§7.2.2 Backtrack Programming - Commafree codes
'''


def exercise34(words):
    ''' Find the largest commafree subset. '''

    def S(n, level, x):
        ''' Return values at level, which hold true for x_1 to x_(level-1) '''

        if level == 1:
            return domain

        elif x[level-2] is None:
            return [None]

        # Check all words after x_(l-1) for commafreeness
        result = []
        i = domain.index(x[level-2]) + 1
        while i < n:
            # Check if domain[i] is commafree with respect to x_1 .. x_(l-1)
            if exercise35(domain[i], x[:level-1]):
                result.append(domain[i])
            i += 1

        if len(result) > 0:
            return result
        else:
            return [None]

    domain = tuple(sorted(words))
    n = len(domain)

    max_subset = []
    for cf in walkers_backtrack(n, S):
        size = cf.index(None)
        if size > len(max_subset):
            max_subset = cf[:size]

    return max_subset


def exercise35(word, words, n=None):
    '''
    Test if word is commafree with respect to the accepted words of size m
    '''

    if n is None:
        n = len(word)

    test_words = set(words + [word])
    for test1, test2 in product(test_words, test_words):
        testseq = test1 + test2

        for start in [0, 1]:
            count = 0
            for i in range(0, n):
                if testseq[start+i:start+i+n] in test_words:
                    count += 1
            if count > 1:
                return False

    return True

def is_commafree(code):
    code = list(code)
    cf = [code[0]]
    for word in code[1:]:
        if not exercise35(word, cf):
            print(f'{word=}, {cf=}')
            return False
        cf.append(word)

    return True

def cyclic_class_key(m, n):
    ''' Return a key function for sorting word lists by cyclic class. '''

    words = {}  # map words to class key

    for i, clas in enumerate(word for word, j in preprimes(m, n) if j == n):
        word = clas
        for j in range(n):
            words[word] = i*n + j

            # Cycle
            word = word[1:n] + word[0:1]

    def key(word):
        return words[word]

    return key


def commafree_classes(m, n):
    '''
    Find the largest commafree subset of m-ary tuples of length n.
    Use cyclic classes to group options which must contribute only one of their
    values.
    '''

    def S(xn, level, x):
        ''' Return values at level, which hold true for x_1 to x_(level-1) '''

        if level == 1:
            return domain

        elif x[level-2] is None:
            return [None]

        # Record the class of x_(l-1)
        x_class[level-2] = class_map[x[level-2]]
        # print(f'{x_class[:level-1]=}')

        # Check all words after x_(l-1)
        result = []
        i = domain.index(x[level-2]) + 1
        while i < len(domain):

            word = domain[i]
            # print(f'checking {word} with clas {class_map[word]}')

            # Ensure this word's class isn't included already
            if class_map[word] not in x_class[:level-1]:

                # Check if word is commafree with respect to x_1 .. x_(l-1)
                if exercise35(word, x[:level-1], n):
                    result.append(word)

            i += 1

        if len(result) > 0:
            # print(f'{level=} , {x[:level-1]=}')
            return result
        else:
            return [None]

    # Maximum length of commafree subset
    xn = (m**4 - m**2) // 4

    # classes of word cycles
    classes = list(word for word, j in preprimes(m, n) if j == n)
    # print(f'{xn=}, {classes=}')

    domain = []
    class_map = {}
    for clas in classes:
        word = clas
        for _ in range(n):
            domain.append(word)
            class_map[word] = clas
            word = word[1:n] + word[0:1]

    # Track the word class at each x_j
    x_class = [None] * xn

    # Generate all commafree subsets
    max_subset = []
    for cf in walkers_backtrack(xn, S):
        try:
            size = cf.index(None)
        except ValueError:
            size = n

        if size > len(max_subset):
            max_subset = cf[:size]

            # Stop at first subset to reach the maximum possible size
            if len(max_subset) == xn:
                break

    return max_subset

def commafree_four(m, g):
    '''
    Algorithm C. Four-letter commafree codes.

    m - alphabet size
    g - goal number of words in the code
    '''

    RED = 0
    BLUE = 1
    GREEN = 2

    DEBUG = logger.isEnabledFor(logging.DEBUG)
    INFO = logger.isEnabledFor(logging.INFO)

    def alpha(word):
        ''' Return integer representation of the code word. '''
        result = 0
        for letter in word:
            result *= m
            result += letter

        return result

    def tostring():
        ''' String representation of MEM table. '''

        nonlocal RED, BLUE, GREEN, M4, ALF, MEM, UNDO

        lists = {2:'P1', 5:'P2', 8:'P3', 11:'S1', 14:'S2', 17:'S3', 20:'CL'}

        table = []

        # Add header
        table.append('      ' + '   '.join([f'{j:-4x}' for j in range(M4)]))

        for i in range(24):
            row = [f'{i*16:-3x}']

            for j in range(M4):
                n = i*M4 + j

                if n < len(MEM):
                    if i == 0:
                        if MEM[j] == RED:
                            row.append(' RED')
                        elif MEM[j] == BLUE:
                            row.append('BLUE')
                        else:
                            row.append(' GRN')
                    else:
                        alf = MEM[n]
                        if alf == 0:
                            row.append('    ')
                        elif i % 3 == 2:
                            if MEM[n + M4] > 0:
                                tail = MEM[n + M4]
                                closed = (tail == n - 1)
                            if n < tail:
                                row.append(''.join(str(c) for c in ALF[alf]))
                            else:
                                if closed:
                                    row.append('cccc')
                                else:
                                    row.append('xxxx')
                        else:
                            row.append('{:-4x}'.format(MEM[n]))
            row.append(' ')

            if i in lists:
                row[-1] += lists[i]

            table.append(' | '.join(row))

            if (i+1) % 3 == 1:
                table.append('    |-' + '-' * (7*M4-2) + '|')

        table.append('')

        # table.append('UNDO=' + ', '.join(['{:x}:{:x}'.format(a, v) for a, v in UNDO[:u]]))

        return '\n'.join(table)

    def prefixes_suffixes(word):
        '''
        Return 6-tuple of prefixes and suffixes of word.
        Return in table order or pair order.
        '''

        p1 = alpha(word[0:1] + (0, 0, 0))
        p2 = alpha(word[0:2] + (0, 0))
        p3 = alpha(word[0:3] + (0, ))
        s1 = alpha(word[3:4] + (0, 0, 0))
        s2 = alpha(word[2:4] + (0, 0))
        s3 = alpha(word[1:4] + (0, ))

        return (p1, p2, p3, s1, s2, s3)

    def initialize_mem():

        nonlocal RED, BLUE, GREEN, M4, ALF, MEM
        nonlocal P1OFF, P2OFF, P3OFF, S1OFF, S2OFF, S3OFF, CLOFF

        # Initialize colors to RED
        for alf in range(M4):
            MEM[alf] = RED

        # Initialize the prefix and suffix lists
        ps1 = 0
        for _ in range(m):
            MEM[P1OFF+M4+ps1] = P1OFF + ps1
            MEM[S1OFF+M4+ps1] = S1OFF + ps1

            ps2 = 0
            for _ in range(m):
                MEM[P2OFF+M4+ps1+ps2] = P2OFF + ps1 + ps2
                MEM[S2OFF+M4+ps1+ps2] = S2OFF + ps1 + ps2

                ps3 = 0
                for _ in range(m):
                    MEM[P3OFF+M4+ps1+ps2+ps3] = P3OFF + ps1 + ps2 + ps3
                    MEM[S3OFF+M4+ps1+ps2+ps3] = S3OFF + ps1 + ps2 + ps3

                    ps3 += m
                ps2 += m**2
            ps1 += m**3



        # Iterate over word classes
        for cl, clas in enumerate(word for word, j in preprimes(m, 4)
                                  if j == 4):

            # Initialize the class list
            MEM[CLOFF+M4+(4*cl)] = CLOFF + (4 * cl)

            # Iterate through the 4-cycle of words in this class
            word = clas
            for _ in range(4):
                alf = alpha(word)
                ALF[alf] = word
                ALFC[alf] = cl

                # Skip 0100 and 1000 since they will generate symmetric
                # duplicates
                if word != (0, 1, 0, 0) and word != (1, 0, 0, 0):

                    MEM[alf] = BLUE

                    # Insert into 3 prefix and 3 suffix lists
                    offset = P1OFF
                    for ps in prefixes_suffixes(word):
                        tail = offset + M4 + ps
                        insert(alf, tail, offset - M4)

                        offset += 3*M4

                    # Insert into CLOFF
                    tail = CLOFF + M4 + (4 * cl)
                    insert(alf, tail, CLOFF - M4)

                # Cycle
                word = word[1:4] + word[0:1]

    def insert(alf, tail, ihead):
        ''' Insert a value into the list and the inverted list. '''

        MEM[MEM[tail]] = alf
        MEM[ihead+alf] = MEM[tail]
        MEM[tail] += 1

    def store(a, v):
        ''' Store v at MEM[a]; save original value on the UNDO stack '''

        nonlocal MEM, STAMP, UNDO, u, sigma

        # print(f'store: {a=}, {v=}, {STAMP[a]=}, {sigma=}')

        # Check if MEM[a] has been changed yet this round
        if STAMP[a] != sigma:
            # No, indicate now that is has been
            STAMP[a] = sigma
            # Save a and original value on the UNDO stack
            UNDO[u] = (a, MEM[a])
            u += 1

        MEM[a] = v

    def select_next_word():
        '''
        Select the next word from a class with the least number of blue words.
        Exercise 44.
        '''

        nonlocal M4, MEM, CLOFF, FREE, PP, POISON, x, c, DEBUG

        if DEBUG:
            logger.debug('select_next_word')

        r = 5  # number of words in a class with least blue words

        # Iterate over free classes
        # print(f'{f=}, {r=}')
        for k in range(f):
            t = FREE[k]  # a free class
            j = MEM[CLOFF + 4*t + M4] - (CLOFF + 4*t)  # size of class list
            # print(f'{k=}, {t=}, {j=}')

            # Does this class have the fewest words seen so far?
            if j < r:
                r, cl = j, t
                if r == 0:
                    x = -1
                    break

        # print(f'{r=}, {cl=}')

        if r > 0:
            # Set x to a word in the class
            x = MEM[CLOFF + 4*cl]

        if r > 1:
            # Use the poison list to find an x that maximizes the number of
            # blue words that could be killed on the other side of the prefix
            # or suffix that contains x.

            q = 0  # size of the biggest prefix/suffix list in the poison list
            p = POISON  # head of the poison list
            pp = MEM[PP]  # tail of the poison list

            # Iterate over poison prefix/suffix list pairs
            while p < pp:

                # MEM[p:p+2] is one poison prefix/suffix list pair

                y = MEM[p]  # head of poison prefix list
                z = MEM[p + 1]  # head of poison suffix list

                yp = MEM[y + M4]  # tail of poison prefix list
                zp = MEM[z + M4] # tail of poison suffix list

                # Check if either of the lists is empty
                if y == yp or z == zp:

                    # Delete entry p from the poison list
                    # (this also advances to next p)
                    pp -= 2
                    if p != pp:
                        store(p, MEM[pp])
                        store(p+1, MEM[pp+1])
                else:
                    # Get the size of each list
                    ylen = yp - y
                    zlen = zp - z

                    # print(f'{y=:x}, {yp=:x}, {z=:x}, {zp=:x}')

                    # Select a new word if either of the lists is larger than
                    # we've seen before.
                    if ylen >= zlen and ylen > q:
                        q = ylen
                        x = MEM[z]
                        cl = ALFC[x]
                        # print(f'select {x=} from {z=:x} because {ylen=}')

                    elif ylen < zlen and zlen > q:
                        q = zlen
                        x = MEM[y]
                        cl = ALFC[x]
                        # print(f'select {x=} from {y=:x} because {zlen=}')

                    # Advance to next p
                    p += 2

            # Store the new value of the the poison list
            store(PP, pp)

        c = cl

    def rem(alf, delta, omicron):
        ''' Remove an item from a list. '''

        nonlocal M4, MEM, DEBUG

        p = delta + omicron  # head pointer
        q = MEM[p + M4] - 1  # tail pointer

        if DEBUG:
            logger.debug(f'rem: {delta=:x}, {omicron=:x}, {p=:x}, {q=:x}')

        if q >= p:
            # list p isn't closed or being killed
            store(p + M4, q)
            t = MEM[alf + omicron - M4]

            # print(f'     {t=:x}, {alf=}')

            if t != q:
                y = MEM[q]
                store(t, y)
                store(y + omicron - M4, t)

    def close(delta, omicron):
        ''' Close list delta+omicron. '''

        nonlocal M4, MEM, DEBUG

        p = delta + omicron  # head of the list
        q = MEM[p + M4]  # tail of the list

        if DEBUG:
            logger.debug(f'close: {delta=:x}, {omicron=:x}, {p=:x}, {q=:x}')

        # Check if already closed
        if q != p - 1:
            # Close by setting tail to head-1
            store(p + M4, p - 1)

        # Return the head and tail
        return (p, q)

    def red(alf, c):
        ''' Make alpha RED. '''

        nonlocal RED, P1OFF, M4, ALF, DEBUG

        if DEBUG:
            logger.debug(f'red: {alf=}, {c=}')

        store(alf, RED)

        # Remove alf from all of its lists
        offset = P1OFF
        for ps in prefixes_suffixes(ALF[alf]):
            rem(alf, ps, offset)  # remove from pre- or suffix list
            offset += 3*M4
        rem(alf, 4*c, offset)  # remove from class list

    def green(alf, c):
        ''' Make alpha GREEN. '''

        nonlocal GREEN, P1OFF, CLOFF, M4, ALF, DEBUG

        if DEBUG:
            logger.debug(f'green: {alf=}, {c=}')

        store(alf, GREEN)
        # print(tostring())

        # Close all of alf's lists
        offset = P1OFF
        for ps in prefixes_suffixes(ALF[alf]):
            close(ps, offset)  # close pre- or suffix list
            offset += 3*M4
        p, q = close(4*c, CLOFF)  # close class list

        # print(f'RED words in class {c}')
        # Turn the other words in this class RED
        # print(f'{p=}, {q=}')
        for r in range(p, q):
            if MEM[r] != alf:
                red(MEM[r], c)
                # print(tostring())

    # C1. [Initialize.]
    if INFO:
        logger.info("C1.")

    assert 2 <= m <= 7

    M2 = m**2
    M4 = m**4
    L = (M4 - M2) // 4  # number of word classes (also, max possible g)
    M = floor(23.5 * M4)  # size of the main table, MEM

    assert L - m * (m - 1) <= g <= L

    MEM = array('I', [0] * M) # color, P1, P2, P3, S1, S2, S3, CL, POISON

    P1OFF = 2 * M4  # offsets into MEM for P1, P2, P3, S1, S2, S3, CL
    P2OFF = 5 * M4
    P3OFF = 8 * M4
    S1OFF = 11 * M4
    S2OFF = 14 * M4
    S3OFF = 17 * M4
    CLOFF = 20 * M4

    POISON = 22 * M4  # head of the poison list
    PP = POISON - 1  # tail of the poison list
    MEM[PP] = POISON

    level = 0  # backtrack level and index into X, C, S, U

    u = 0  # size of the UNDO stack
    U = [0] * L
    UNDO = [None] * 10000  # UNDO stack

    STAMP = [-1] * M  # store MEM[a] in UNDO only once per sigma
    sigma = 0

    x = 1  # trial word
    X = [0] * L

    c = 0  # trial word's class, simple index into the class l
    C = [0] * L

    s = L - g  # "slack"
    S = [0] * L

    f = L  # number of free classes, aka tail pointer for the free class list
    FREE = [c for c in range(L)]
    IFREE = [c for c in range(L)]

    # alpha to code word lookup table
    ALF = [0] * (16*3 * M)

    # alpha to class lookup table
    ALFC = [0] * M4

    # Fill in the main tables
    initialize_mem()

    # print(tostring())

    first = True

    # Begin the main event loop
    step = 'C2'
    while True:

        if step == 'C2':
            # [Enter level.]
            if INFO:
                logger.info(f'C2. {level=}, X={X[:level]}, {x=}, {c=}')

            if level == L:
                if INFO:
                    logger.info(f'C2. visiting {X[:level]}')
                yield tuple(ALF[alf] for alf in X[:L] if alf >= 0)
                step = 'C6'

            else:
                # Choose a candidate word x and class c
                select_next_word()
                if first:
                    # x, c = 2, 0
                    first = False

                # print(tostring())

                step = 'C3'

        elif step == 'C3':
            # [Try the candidate.]
            if INFO:
                logger.info(f'C3. {level=}, X={X[:level]}, {x=}, {c=}, {s=}')

            U[level] = u
            sigma += 1

            step = 'C4'

            if x < 0:
                if s == 0 or level == 0:
                    step = 'C6'
                else:
                    s -= 1
            else:
                # Make x green
                green(x, c)

                # Add the three prefix, suffix pairs to the poison list,
                # cross matching prefixes and suffixes
                pp = MEM[PP] + 6

                p1, p2, p3, s1, s2, s3 = prefixes_suffixes(ALF[x])
                store(pp - 6, S1OFF + p1)
                store(pp - 5, P3OFF + s3)
                store(pp - 4, S2OFF + p2)
                store(pp - 3, P2OFF + s2)
                store(pp - 2, S3OFF + p3)
                store(pp - 1, P1OFF + s1)

                p = POISON

                # print(tostring())

                # Iterate over poison prefix/suffix list pairs
                while p < pp:

                    # MEM[p:p+2] is one poison prefix/suffix list pair

                    y = MEM[p]  # head of poison prefix list
                    z = MEM[p + 1]  # head of poison suffix list

                    yp = MEM[y + M4]  # tail of poison prefix list
                    zp = MEM[z + M4] # tail of poison suffix list

                    # print(f'{p=:x}, {pp=:x}, {y=:x}, {yp=:x}, {z=:x}, {zp=:x}')

                    if y == yp or z == zp:
                        # One of the lists is empty, delete entry p from the
                        # poison list (this also advances to next p)
                        # print(f'removing {MEM[p]:x}:{MEM[p+1]:x} from poison list')

                        pp -= 2
                        if p != pp:
                            store(p, MEM[pp])
                            store(p+1, MEM[pp+1])

                    elif yp < y and zp < z:
                        # Both lists are closed which means a poisoned pair;
                        # We can't use this word, so try the next word.
                        # print(tostring())
                        step = 'C5'
                        break

                    elif yp > y and zp > z:
                        # Both lists are open, advance to next p
                        p += 2

                    else:
                        # One list is closed and one is open. Remove all BLUE
                        # words form the open list and make them RED
                        if yp < y and zp > z:
                            # Prefix list is closed and suffix list is open
                            store(z + M4, z)
                            for r in range(z, zp):
                                red(MEM[r], ALFC[MEM[r]])

                        else:  # yp > y and zp < z
                            # Suffix list is closed and prefix list is open
                            store(y + M4, y)
                            for r in range(y, yp):
                                red(MEM[r], ALFC[MEM[r]])

                        # Delete entry p from the poison list
                        # (this also advances to next p)
                        pp -= 2
                        if p != pp:
                            store(p, MEM[pp])
                            store(p+1, MEM[pp+1])

                store(PP, pp)

        elif step == 'C4':
            # [Make the move.]
            if INFO:
                logger.info(f'C4. {level=}, X={X[:level]}, {x=}, {c=}')

            X[level] = x
            C[level] = c
            S[level] = s

            # Delete class c from the active list
            p = IFREE[c]
            f -= 1

            if p != f:
                y = FREE[f]
                FREE[p] = y
                IFREE[y] = p
                FREE[f] = c
                IFREE[c] = f

            level += 1
            step = 'C2'

        elif step == 'C5':
            # [Try again.]
            if INFO:
                logger.info(f'C5. {level=}, X={X[:level]}, {x=}, {c=}')

            while u > U[level]:
                u -= 1
                a, v = UNDO[u]
                MEM[a] = v

            sigma += 1

            # make x red
            red(x, c)

            step = 'C2'

        elif step == 'C6':
            # [Backtrack.]
            if INFO:
                logger.info(f'C6. {level=}, X={X[0:level]}, {x=}, {c=}')

            level -= 1

            if level == -1:
                return

            x = X[level]
            c = C[level]
            f += 1

            if x < 0:
                step = 'C6'  # repeat this step
            else:
                s = S[level]
                step = 'C5'

        else:
            raise Exception(f'Invalid Step: {step}')


class Test(unittest.TestCase):

    def test_exercise34(self):

        words = ['aced', 'babe', 'bade', 'bead', 'beef', 'cafe', 'cede',
                 'dada', 'dead', 'deaf', 'face', 'fade', 'feed']

        self.assertEqual(exercise34(words),
                         ('aced', 'babe', 'bade', 'bead', 'beef', 'cafe',
                          'cede', 'dead', 'deaf', 'fade', 'feed'))

    def test_exercise35(self):

        words = ['aced', 'babe', 'bade', 'bead', 'beef', 'cafe', 'cede',
                 'dada', 'dead', 'deaf', 'face', 'feed']

        self.assertTrue(exercise35('abcd', []))
        self.assertTrue(exercise35('abcd', ['efgh']))

        self.assertFalse(exercise35('cefa', words))
        self.assertFalse(exercise35('cece', ['cece']))
        self.assertFalse(exercise35('zzzz', []))

    def test_commafree_classes(self):
        result = commafree_classes(2, 4)
        self.assertEqual(result, ((0, 0, 0, 1), (0, 0, 1, 1), (0, 1, 1, 1)))

        result = commafree_classes(3, 3)
        self.assertEqual(result, ((0, 0, 1), (0, 0, 2), (1, 1, 0), (2, 0, 1),
                                  (2, 1, 0), (2, 0, 2), (1, 1, 2), (2, 1, 2)))

    def test_commafree_four_2_3(self):
        codes = sorted([sorted(code) for code in commafree_four(2, 3)])
        codes = [[''.join(str(c) for c in word) for word in code]
                 for code in codes]

        self.assertEqual(codes, [['0001', '0011', '0111'],
                                 ['0001', '0110', '0111'],
                                 ['0001', '0110', '1110'],
                                 ['0001', '0111', '1001'],
                                 ['0001', '1001', '1011'],
                                 ['0001', '1001', '1101'],
                                 ['0001', '1001', '1110'],
                                 ['0001', '1100', '1101'],
                                 ['0010', '0011', '1011'],
                                 ['0010', '0011', '1101'],
                                 ['0010', '0011', '1110'],
                                 ['0010', '0110', '0111'],
                                 ['0010', '0110', '1110'],
                                 ['0010', '1100', '1101'],
                                ])

    def test_commafree_four_3_18(self):

        codes = [set([''.join(str(c) for c in word) for word in code])
                 for code in commafree_four(3, 18)]

        self.assertEqual(len(codes), 72)

        for code in codes:
            self.assertTrue(is_commafree(code))

        a = ['0001', '0002', '1001', '1002', '1102', '2001', '2002', '2011',
             '2012', '2102', '2112']
        for b in [['2122'], ['2212']]:
            for c in [['0102','1011','1012'], ['2010','1101','2101']]:
                for d in [['1202','2202','2111'], ['2021','2022','1112']]:
                    answer = set(a + b + c + d)

                    self.assertTrue(answer in codes)

        a = ['0001', '0020', '0021', '0022', '1001', '1020', '1021', '1022',
             '1201', '1202', '1221', '2001', '2201', '2202']
        for b in [['1121'], ['1211']]:
            for c in [['1011','1012','2221'], ['1101','2101','1222']]:
                answer = set(a + b + c)

                self.assertTrue(answer in codes)

    def test_long_commafree_four_4_57(self):
        ''' Very long, currently takes 68m on my MacBook. '''

        codes = [set([''.join(str(c) for c in word) for word in code])
                 for code in commafree_four(4, 57)]

        self.assertEqual(len(codes), 1152)

        for code in codes:
            self.assertTrue(is_commafree(code))

        answer1 = {'0001', '0002', '0003', '0201', '0203', '1001', '1002',
                   '1003', '1011', '1013', '1021', '1022', '1023', '1031',
                   '1032', '1033', '1201', '1203', '1211', '1213', '1221',
                   '1223', '1231', '1232', '1233', '1311', '1321', '1323',
                   '1331', '2001', '2002', '2003', '2021', '2022', '2023',
                   '2201', '2203', '2221', '2223', '3001', '3002', '3003',
                   '3011', '3013', '3021', '3022', '3023', '3031', '3032',
                   '3033', '3201', '3203', '3221', '3223', '3321', '3323',
                   '3331'}

        answer2 = {'0010', '0020', '0030', '0110', '0112', '0113', '0120',
                   '0121', '0122', '0130', '0131', '0132', '0133', '0210',
                   '0212', '0213', '0220', '0222', '0230', '0310', '0312',
                   '0313', '0320', '0322', '0330', '0332', '0333', '1110',
                   '1112', '1113', '2010', '2030', '2110', '2112', '2113',
                   '2210', '2212', '2213', '2230', '2310', '2312', '2313',
                   '2320', '2322', '2330', '2332', '2333', '3110', '3112',
                   '3113', '3210', '3212', '3213', '3230', '3310', '3312',
                   '3313'}

        self.assertTrue(answer1 in codes)
        self.assertTrue(answer2 in codes)


if __name__ == '__main__':
    unittest.main(exit=False)

