from lab2.lexer_light import lex, tableToPrint
from lab2.lexer_light import tableOfSymb, tableOfId, tableOfConst, tableOfLabel, source_code, FSuccess

lex()

postfixCode = []

numRow = 1

len_tableOfSymb = len(tableOfSymb)

toView = False


def postfixTranslator():
    global len_tableOfSymb, FSuccess
    lex()
    len_tableOfSymb = len(tableOfSymb)

    if (True, 'Lexer') == FSuccess:
        FSuccess = parseProgram()
        return FSuccess


def parseProgram():
    global FSuccess
    try:
        parseToken('def', 'keyword', '')
        parseFactor()
        parseToken(':', 'colon', '')
        parseStatementList()
        parseToken('end', 'keyword', '')

        print('Translator: Переклад у ПОЛІЗ та синтаксичний аналіз завершились успішно')
        FSuccess = (True, 'Translator')
        return FSuccess
    except SystemExit as e:
        print('Parser: Аварійне завершення програми з кодом {0}'.format(e))


def parseToken(lexeme, token, indent):
    global numRow

    if numRow > len_tableOfSymb:
        failParse('неочікуваний кінець програми', (lexeme, token, numRow))

    numLine, lex, tok = getSymb()

    numRow += 1

    if (lex, tok) == (lexeme, token):
        return True
    else:
        failParse('невідповідність токенів', (numLine, lex, tok, lexeme, token))
        return False


def getSymb():
    if numRow > len_tableOfSymb:
        failParse('getSymb(): неочікуваний кінець програми', numRow)
    numLine, lexeme, token, _ = tableOfSymb[numRow]
    return numLine, lexeme, token


def failParse(str, tuple):
    if str == 'неочікуваний кінець програми':
        (lexeme, token, numRow) = tuple
        print(
            'Parser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) '
            'немає запису з номером {1}. \n\t Очікувалось - {0}'.format((lexeme, token), numRow))
        exit(1001)
    if str == 'getSymb(): неочікуваний кінець програми':
        numRow = tuple
        print(
            'Parser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) '
            'немає запису з номером {0}. \n\t Останній запис - {1}'.format(numRow, tableOfSymb[numRow - 1])
        )
        exit(1002)
    elif str == 'невідповідність токенів':
        (numLine, lexeme, token, lex, tok) = tuple
        print(
            'Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). '
            '\n\t Очікувався - ({3},{4}).'.format(numLine, lexeme, token, lex, tok)
        )
        exit(1)
    elif str == 'невідповідність інструкцій':
        (numLine, lex, tok, expected) = tuple
        print(
            'Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). '
            '\n\t Очікувався - {3}.'.format(numLine, lex, tok, expected)
        )
        exit(2)
    elif str == 'невідповідність у Expression.Factor':
        (numLine, lex, tok, expected) = tuple
        print(
            'Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). '
            '\n\t Очікувався - {3}.'.format(numLine, lex, tok, expected)
        )
        exit(3)


def parseStatementList():
    while parseStatement():
        pass
    return True


def parseStatement():
    numLine, lex, tok = getSymb()
    if tok == 'ident':
        parseAssign()
        return True
    elif (lex, tok) == ('end', 'keyword'):
        return False
    else:
        failParse('невідповідність інструкцій', (numLine, lex, tok, 'ident або if'))
        return False


def createLabel():
    global tableOfLabel
    nmb = len(tableOfLabel) + 1
    lexeme = "m" + str(nmb)
    val = tableOfLabel.get(lexeme)
    if val is None:
        tableOfLabel[lexeme] = 'val_undef'
        tok = 'label'  # # #
    else:
        tok = 'Конфлікт міток'
        print(tok)
        exit(1003)
    return lexeme, tok


def setValLabel(lbl):
    global tableOfLabel
    lex, _tok = lbl
    tableOfLabel[lex] = len(postfixCode)
    return True


def parseBoolExpr():
    global numRow
    numLine, lex, tok = getSymb()
    if lex == 'true' or lex == 'false':
        numRow += 1
        postfixCode.append((lex, tok))
        return True
    else:
        parseExpression()
        numLine, lex, tok = getSymb()
        numRow += 1
        parseExpression()
    if tok in 'rel_op':
        postfixCode.append((lex, tok))
    else:
        failParse('mismatch in BoolExpr', (numLine, lex, tok, 'relop'))
    return True


def parseAssign():
    global numRow, postfixCode

    _numLine, lex, tok = getSymb()

    postfixCode.append((lex, tok))

    if toView:
        configToPrint(lex, numRow)

    numRow += 1

    if parseToken('=', 'assign_op', '\t\t\t\t\t'):
        parseExpression()

        postfixCode.append(('=', 'assign_op'))
        if toView:
            configToPrint('=', numRow)
        return True
    else:
        return False


def configToPrint(lex, numRow):
    stage = '\nКрок трансляції\n'
    stage += 'лексема: \'{0}\'\n'
    stage += 'tableOfSymb[{1}] = {2}\n'
    stage += 'postfixCode = {3}\n'
    print(stage.format(lex, numRow, str(tableOfSymb[numRow]), str(postfixCode)))


def parseExpression():
    global numRow, postfixCode
    _numLine, lex, tok = getSymb()
    parseTerm()
    F = True

    while F:
        _numLine, lex, tok = getSymb()
        if tok in 'add_op':
            numRow += 1
            parseTerm()

            postfixCode.append((lex, tok))
            if toView:
                configToPrint(lex, numRow)
        else:
            F = False
    return True


def parseTerm():
    global numRow, postfixCode
    parseFactor()
    F = True

    while F:
        _numLine, lex, tok = getSymb()
        if tok in 'mult_op':
            numRow += 1
            parseFactor()
            postfixCode.append((lex, tok))
            if toView:
                configToPrint(lex, numRow)
        else:
            F = False
    return True


def parseFactor():
    global numRow, postfixCode
    numLine, lex, tok = getSymb()

    if tok in ('int', 'float', 'boolean', 'ident'):
        postfixCode.append((lex, tok))
        if toView:
            configToPrint(lex, numRow)
        numRow += 1
    elif lex == '(':
        numRow += 1
        parseExpression()
        parseToken(')', 'bracket_op', '\t' * 7)
    else:
        failParse(
            'невідповідність у Expression.Factor',
            (numLine, lex, tok, 'rel_op, int, float, \'boolean\', ident або \'(\' Expression \')\'')
        )
    return True


# Uncomment the code below to run translator.
# If you need only interpreter leave it commented.
'''
postfixTranslator()

print('tableOfSymb:{0}'.format(tableOfSymb))
print('tableOfId:{0}'.format(tableOfId))
print('tableOfConst:{0}'.format(tableOfConst))
print('tableOfLabel:{0}'.format(tableOfLabel))

tableToPrint('All')
tableToPrint('Symb')
print('\nПочатковий код програми: \n{0}'.format(source_code))

print('\nКод програми у постфіксній формі (ПОЛІЗ): \n{0}'.format(postfixCode))
'''
