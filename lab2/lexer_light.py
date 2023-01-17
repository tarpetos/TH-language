FSuccess = (True, 'Lexer')

tableOfLanguageTokens = {
    'def': 'keyword', 'end': 'keyword', 'pow': 'keyword',
    'input': 'keyword', 'print': 'keyword', 'for': 'keyword',
    'if': 'keyword', 'then': 'keyword', 'goto': 'keyword', 'true': 'boolean', 'false': 'boolean',
    'e': 'exponent', 'E': 'exponent',
    '=': 'assign_op', '.': 'dot', ' ': 'ws', '\t': 'ws', '\n': 'eol', '\r': 'eol', '-': 'add_op',
    '+': 'add_op', '*': 'mult_op', '/': 'mult_op', '^': 'mult_op', ',': 'punct', ';': 'punct', ':': 'colon',
    '"': 'quote', '(': 'bracket_op', ')': 'bracket_op', '{': 'decl_op', '}': 'decl_op',
    '==': 'rel_op', '!=': 'rel_op', '<=': 'rel_op', '>=': 'rel_op', '<': 'rel_op', '>': 'rel_op',
}

tableIdentFloatInt = {2: 'ident', 6: 'float', 9: 'int'}

state_trans_func = {
    (0, 'Letter'): 1, (1, 'Letter'): 1, (1, 'Digit'): 1, (1, 'other'): 2,
    (0, 'Digit'): 4, (4, 'Digit'): 4, (4, 'dot'): 5, (4, 'other'): 9, (5, 'Digit'): 5, (5, 'other'): 6,
    (0, ':'): 12,
    (11, 'other'): 102,
    (0, 'ws'): 0,
    (0, 'eol'): 13,
    (0, '+'): 14, (0, '-'): 14, (0, '*'): 14, (0, '/'): 14, (0, '^'): 14,
    (0, '('): 14, (0, ')'): 14, (0, '{'): 14, (0, '}'): 14,
    (0, ','): 16, (0, ';'): 16, (0, '"'): 16,
    (0, '<'): 20, (20, '='): 21,
    (20, '>'): 22,
    (20, 'other'): 23,
    (0, '>'): 30, (30, '='): 31,
    (30, 'other'): 33,
    (0, '='): 40,
    (0, 'other'): 101
}

initState = 0
F = {2, 6, 9, 12, 13, 14, 16, 101, 102, 21, 22, 23, 31, 33, 40}
F_STAR = {2, 6, 9, 23, 33}
F_ERROR = {101, 102}

tableOfId = {}
tableOfConst = {}
tableOfSymb = {}
tableOfLabel = {}

state = initState

# Open the file below lexer, parser, translator and interpreter
with open('../examples/translator_interpreter_example.thl', 'r') as file:
    source_code = file.read()

# Open the file below only for lexer and parser
# with open('../examples/translator_interpreter_example.thl', 'r') as file:
#     source_code = file.read()

source_code += ' '

lenCode = len(source_code) - 1
numLine = 1
numChar = -1
char = ''
lexeme = ''


def lex():
    global state, char, lexeme, FSuccess
    try:
        while numChar < lenCode:
            char = nextChar()
            classCh = classOfChar(char)
            state = nextState(state, classCh)
            if is_final(state):
                processing()
            elif state == 0:
                lexeme = ''
            else:
                lexeme += char
    except SystemExit as e:
        FSuccess = (False, 'Lexer')
        print('Lexer: Аварійне завершення програми з кодом {0}'.format(e))


def processing():
    global state, lexeme, numLine, numChar
    if state == 13:
        numLine += 1
        state = 0
    if state in (2, 6, 9):
        token = getToken(state, lexeme)
        if token != 'keyword':
            index = indexIdConst(state, lexeme, token)
            # print('{0:<3d} {1:<10s} {2:<10s} {3:<2d} '.format(numLine, lexeme, token, index))
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, index)
        else:
            # print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        numChar = putCharBack(numChar)
        state = 0
    if state == 12:
        lexeme += char
        token = getToken(state, lexeme)
        # print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        state = 0
    if state in (14, 16):
        lexeme += char
        token = getToken(state, lexeme)
        # print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        state = 0
    if state in (21, 22, 31, 40):
        lexeme += char
        token = getToken(state, lexeme)
        # print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        state = 0
    if state in (23, 33):
        token = getToken(state, lexeme)
        # print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        numChar = putCharBack(numChar)
        state = 0
    if state in (101, 102):
        fail()


def fail():
    if state == 101:
        print('у рядку ', numLine, ' неочікуваний символ ' + char)
        exit(101)
    if state == 102:
        print('у рядку ', numLine, ' очікувався символ =, а не ' + char)
        exit(102)
    else:
        print('у рядку ', numLine, ' неочікуваний символ ' + char)
        exit(111)


def is_final(state):
    if state in F:
        return True
    else:
        return False


def nextState(state, classCh):
    try:
        return state_trans_func[(state, classCh)]
    except KeyError:
        return state_trans_func[(state, 'other')]


def nextChar():
    global numChar
    numChar += 1
    return source_code[numChar]


def putCharBack(numChar):
    return numChar - 1


def classOfChar(char):
    res = ''

    if char in '.':
        res = 'dot'
    elif char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
        res = 'Letter'
    elif char in '0123456789':
        res = 'Digit'
    elif char in ' \t':
        res = 'ws'
    elif char in '\n\r':
        res = 'eol'
    elif char in ',*+-:<>=(){}!;."/^':
        res = char
    return res


def getToken(state, lexeme):
    try:
        return tableOfLanguageTokens[lexeme]
    except KeyError:
        return tableIdentFloatInt[state]


def indexIdConst(state, lexeme, token):
    indx = 0
    if state == 2:
        indx1 = tableOfId.get(lexeme)
        if indx1 is None:
            indx = len(tableOfId) + 1
            tableOfId[lexeme] = (indx, 'type_undef', 'val_undef')
    elif state in (6, 9):
        indx1 = tableOfConst.get(lexeme)
        if indx1 is None:
            indx = len(tableOfConst) + 1
            if state == 6:
                val = float(lexeme)
            elif state == 9:
                val = int(lexeme)
            tableOfConst[lexeme] = (indx, token, val)
    if not (indx1 is None):
        if len(indx1) == 2:
            indx, _ = indx1
        else:
            indx, _, _ = indx1
    return indx


def tableToPrint(Tbl):
    if Tbl == 'Symb':
        tableOfSymbToPrint()
    elif Tbl == 'Id':
        tableOfIdToPrint()
    elif Tbl == 'Const':
        tableOfConstToPrint()
    elif Tbl == 'Label':
        tableOfLabelToPrint()
    else:
        tableOfSymbToPrint()
        tableOfIdToPrint()
        tableOfConstToPrint()
        tableOfLabelToPrint()
    return True


def tableOfSymbToPrint():
    print('\n Таблиця символів')
    s1 = '{0:<10s} {1:<10s} {2:<10s} {3:<10s} {4:<5s} '
    s2 = '{0:<10d} {1:<10d} {2:<10s} {3:<10s} {4:<5s} '
    print(s1.format('numRec', 'numLine', 'lexeme', 'token', 'index'))
    for numRec in tableOfSymb:  # range(1,lns+1):
        numLine, lexeme, token, index = tableOfSymb[numRec]
        print(s2.format(numRec, numLine, lexeme, token, str(index)))


def tableOfIdToPrint():
    print('\n Таблиця ідентифікаторів')
    s1 = '{0:<10s} {1:<15s} {2:<15s} {3:<10s} '
    print(s1.format('Ident', 'Type', 'Value', 'Index'))
    s2 = '{0:<10s} {2:<15s} {3:<15s} {1:<10d} '
    for id in tableOfId:
        index, type, val = tableOfId[id]
        print(s2.format(id, index, type, str(val)))


def tableOfConstToPrint():
    print('\n Таблиця констант')
    s1 = '{0:<10s} {1:<10s} {2:<10s} {3:<10s} '
    print(s1.format('Const', 'Type', 'Value', 'Index'))
    s2 = '{0:<10s} {2:<10s} {3:<10} {1:<10d} '
    for cnst in tableOfConst:
        index, type, val = tableOfConst[cnst]
        print(s2.format(str(cnst), index, type, val))


def tableOfLabelToPrint():
    if len(tableOfLabel) == 0:
        print('\n Таблиця міток - порожня')
    else:
        s1 = '{0:<10s} {1:<10s} '
        print('\n Таблиця міток')
        print(s1.format('Label', 'Value'))
        s2 = '{0:<10s} {1:<10d} '
        for lbl in tableOfLabel:
            val = tableOfLabel[lbl]
            print(s2.format(lbl, val))


# Uncomment the code below to run lexer.
'''
if __name__ == '__main__':
    lex()

    print('-' * 30, '\n')
    print('tableOfSymb:{0}'.format(tableOfSymb), '\n')
    print('tableOfVar:{0}'.format(tableOfId), '\n')
    print('tableOfConst:{0}'.format(tableOfConst))
'''
