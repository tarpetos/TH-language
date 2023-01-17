from lab2.lexer_light import lex, tableToPrint
from lab2.lexer_light import tableOfSymb, tableOfId, tableOfConst, tableOfLabel, source_code
from translator import postfixTranslator, postfixCode
from stack import Stack

stack = Stack()
instrNum = 0
toView = False

commandTrack = []


def postfixInterpreter():
    global commandTrack
    FSuccess = postfixTranslator()
    if (True, 'Translator') == FSuccess:
        print('\nПостфіксний код: \n{0}'.format(postfixCode))
        commandTrack = postfixProcessing()
        print('commandTrack = {}'.format(commandTrack))

        return True
    else:
        print('Interpreter: Translator завершив роботу аварійно')
        return False


print('-' * 30)


def postfixProcessing():
    global stack, postfixCode, instrNum, commandTrack
    cyclesNumb = 0
    maxNumb = len(postfixCode)
    try:
        while instrNum < maxNumb and cyclesNumb < 100:
            cyclesNumb += 1
            lex, tok = postfixCode[instrNum]
            commandTrack.append((instrNum, lex, tok))
            if tok in ('int', 'float', 'ident', 'label', 'boolean'):
                stack.push((lex, tok))
                nextInstr = instrNum + 1
            elif tok in ('jump', 'jf', 'colon'):
                nextInstr = doJumps(tok)
            else:
                doIt(lex, tok)
                nextInstr = instrNum + 1
            if toView: configToPrint(instrNum, lex, tok, maxNumb)
            instrNum = nextInstr
        print('Загальна кількість кроків: {0}'.format(cyclesNumb))
        return commandTrack
    except SystemExit as e:
        print('RunTime: Аварійне завершення програми з кодом {0}'.format(e))
    return commandTrack


def configToPrint(step, lex, tok, maxN):
    if step == 0:
        print('=' * 30 + '\nInterpreter run\n')

    print('\nІнтерпретація інструкції №: {0}'.format(step))
    if tok in ('int', 'float'):
        print('Інструкція: {0} у таблиці констант: {1}'.format((lex, tok), lex + ':' + str(tableOfConst[lex])))
    elif tok in ('ident'):
        print('Інструкція: {0} у таблиці ідентифікаторів: {1}'.format((lex, tok), lex + ':' + str(tableOfId[lex])))
    else:
        print('Інструкція: {0}'.format((lex, tok)))

    print('-------\ntpostfixCode = {0}\n------'.format(postfixCode))
    stack.print()

    if step == maxN - 1:
        for Tbl in ('Id', 'Const', 'Label'):
            tableToPrint(Tbl)
    print('-=' * 70)
    return True


def configToPrint2(step, lex, tok, maxN):
    if step == 0:
        print('=*' * 30 + '\nInterpreter run\n')
        # tableToPrint('All')

    print('\nІнтерпретація інструкції №: {0}'.format(step))
    if tok in ('int', 'float'):
        print('Інструкція: {0} у таблиці констант: {1}'.format((lex, tok), lex + ':' + str(tableOfConst[lex])))
    elif tok in 'ident':
        print('Інструкція: {0} у таблиці ідентифікаторів: {1}'.format((lex, tok), lex + ':' + str(tableOfId[lex])))
    else:
        print('Інструкція: {0}'.format((lex, tok)))

    print('postfixCode = {0}'.format(postfixCode))
    stack.printTop3()

    if step == maxN:
        for Tbl in ('Id', 'Const', 'Label'):
            tableToPrint(Tbl)
    return True


def doIt(lex, tok):
    global stack, postfixCode, tableOfId, tableOfConst, tableOfLabel

    (lexR, tokR) = stack.pop()
    (lexL, tokL) = stack.pop()
    if (lex, tok) == ('=', 'assign_op'):
        tableOfId[lexL] = (tableOfId[lexL][0], tableOfConst[lexR][1], tableOfConst[lexR][2])
    else:
        processing_add_mult_rel_op((lexL, tokL), lex, (lexR, tokR))
    return True


def doJumps(tok):
    if tok == 'jump':
        next = processing_JUMP()
    elif tok == 'colon':
        next = processing_colon()
    elif tok == 'jf':
        next = processing_JF()
    return next


def processing_JUMP():
    global instrNum
    lexLbl, _tokLbl = stack.pop()
    next = tableOfLabel[lexLbl]
    return next


def processing_colon():
    global instrNum
    _lex, _tok = stack.pop()
    next = instrNum + 1
    return next


def processing_JF():
    global instrNum
    lexLbl, _tokLdl = stack.pop()
    lexBoolExpr, _tokLdl = stack.pop()

    if lexBoolExpr == 'false':
        next = tableOfLabel[lexLbl]
    else:
        next = instrNum + 1
    return next


def processing_add_mult_rel_op(ltL, lex, ltR):
    global stack, postfixCode, tableOfId, tableOfConst, tableOfLabel
    lexL, tokL = ltL
    lexR, tokR = ltR
    if tokL == 'ident':
        if tableOfId[lexL][1] == 'undefined' or \
                tableOfId[lexR][1] == 'assigned':
            failRunTime('неініційована змінна', (lexL, tableOfId[lexL], (lexL, tokL), lex, (lexR, tokR)))
        else:
            valL, tokL = (tableOfId[lexL][2], tableOfId[lexL][1])
    else:
        valL = tableOfConst[lexL][2]
    if tokR == 'ident':
        if tableOfId[lexR][1] == 'undefined' or \
                tableOfId[lexR][1] == 'assigned':
            failRunTime('неініційована змінна', (lexR, tableOfId[lexR], (lexL, tokL), lex, (lexR, tokR)))
        else:
            valR, tokR = (tableOfId[lexR][2], tableOfId[lexR][1])
    else:
        valR = tableOfConst[lexR][2]
    getValue((valL, lexL, tokL), lex, (valR, lexR, tokR))


def getValue(vtL, lex, vtR):
    global stack, postfixCode, tableOfId, tableOfConst, tableOfLabel
    valL, lexL, tokL = vtL
    valR, lexR, tokR = vtR
    if (tokL, tokR) in (
            ('int', 'float'), ('float', 'int'),
            ('boolean', 'float'), ('float', 'boolean'),
            ('int', 'boolean'), ('boolean', 'int')
    ):
        failRunTime('невідповідність типів', ((lexL, tokL), lex, (lexR, tokR)))
    elif lex == '+':
        value = valL + valR
    elif lex == '-':
        value = valL - valR
    elif lex == '*':
        value = valL * valR
    elif lex == '^':
        value = valL ** valR
    elif lex == '/' and valR == 0:
        failRunTime('ділення на нуль', ((lexL, tokL), lex, (lexR, tokR)))
    elif lex == '/' and tokL == 'float':
        value = valL / valR
    elif lex == '/' and tokL == 'int':
        value = int(valL / valR)
    elif lex == '<':
        value = str(valL < valR).lower()
    elif lex == '<=':
        value = str(valL <= valR).lower()
    elif lex == '>':
        value = str(valL > valR).lower()
    elif lex == '>=':
        value = str(valL >= valR).lower()
    elif lex == '=':
        value = str(valL == valR).lower()
    elif lex == '<>':
        value = str(valL != valR).lower()
    else:
        pass
    stack.push((str(value), tokL))
    toTableOfConst(value, tokL)


def toTableOfConst(val, tok):
    lexeme = str(val)
    indx1 = tableOfConst.get(lexeme)
    if indx1 is None:
        indx = len(tableOfConst) + 1
        tableOfConst[lexeme] = (indx, tok, val)


def failRunTime(str, tuple):
    if str == 'невідповідність типів':
        ((lexL, tokL), lex, (lexR, tokR)) = tuple
        print(
            'RunTime ERROR: \n\t Типи операндів відрізняються у {0} {1} {2}'.format((lexL, tokL), lex, (lexR, tokR))
        )
        exit(1)
    elif str == 'неініціалізована змінна':
        (lx, rec, (lexL, tokL), lex, (lexR, tokR)) = tuple
        print(
            'RunTime ERROR: \n\t Значення змінної {0}:{1} не визначене. '
            'Зустрілось у {2} {3} {4}'.format(lx, rec, (lexL, tokL), lex, (lexR, tokR))
        )
        exit(2)
    elif str == 'ділення на нуль':
        ((lexL, tokL), lex, (lexR, tokR)) = tuple
        print(
            'RunTime ERROR: \n\t Ділення на нуль у {0} {1} {2}. '.format((lexL, tokL), lex, (lexR, tokR))
        )
        exit(3)


if __name__ == '__main__':
    postfixInterpreter()

    for Tbl in ('Id', 'Const', 'Label'):
        tableToPrint(Tbl)
