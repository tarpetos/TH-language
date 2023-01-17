from lab2.lexer_light import lex
from lab2.lexer_light import tableOfSymb

lex()
print('-' * 30)
print('tableOfSymb:{0}'.format(tableOfSymb))
print('-' * 30)

numRow = 1

len_tableOfSymb = len(tableOfSymb)
print(('len_tableOfSymb', len_tableOfSymb))


def parseProgram():
    try:
        parseToken('def', 'keyword', '')
        parseFactor()
        parseToken(':', 'colon', '')
        parseStatementList()
        parseToken('end', 'keyword', '')

        print('Parser: Синтаксичний аналіз завершився успішно')
        return True
    except SystemExit as e:
        print('Parser: Аварійне завершення програми з кодом {0}'.format(e))


def parseToken(lexeme, token, indent):
    global numRow

    if numRow > len_tableOfSymb:
        failParse('неочікуваний кінець програми', (lexeme, token, numRow))

    numLine, lex, tok = getSymb()

    numRow += 1

    if (lex, tok) == (lexeme, token):
        print(indent + 'parseToken: В рядку {0} токен {1}'.format(numLine, (lexeme, token)))
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
    elif str == 'mismatch in BoolExpr':
        (numLine, lex, tok, expected) = tuple
        print(
            'Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). '
            '\n\t Очікувався - {3}.'.format(numLine, lex, tok, expected)
        )
        exit(4)


def parseStatementList():
    print('\t parseStatementList():')
    while parseStatement():
        pass
    return True


def parseStatement():
    print('\t\t parseStatement():')
    numLine, lex, tok = getSymb()

    if tok == 'ident':
        parseAssign()
        return True
    elif (lex, tok) == ('if', 'keyword'):
        parseIf()
        return True
    elif (lex, tok) == ('for', 'keyword'):
        parseFor()
        return True
    elif (lex, tok) == ('input', 'keyword'):
        parseInput()
        return True
    elif (lex, tok) == ('print', 'keyword'):
        parsePrint()
        return True
    elif (lex, tok) == ('pow', 'keyword'):
        parsePow()
        return True
    elif (lex, tok) == ('end', 'keyword'):
        return False
    else:
        failParse('невідповідність інструкцій', (numLine, lex, tok, 'ident'))
        return False


def parseAssign():
    global numRow
    print('\t' * 4 + 'parseAssign():')

    numLine, lex, tok = getSymb()

    numRow += 1

    print('\t' * 5 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
    if parseToken('=', 'assign_op', '\t\t\t\t\t'):
        parseExpression()
        return True
    else:
        return False


def parseExpression():
    global numRow
    print('\t' * 5 + 'parseExpression():')
    numLine, lex, tok = getSymb()
    parseTerm()
    F = True

    while F:
        numLine, lex, tok = getSymb()
        if tok in 'add_op':
            numRow += 1
            print('\t' * 6 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
            parseTerm()
        else:
            F = False
    return True


def parseTerm():
    global numRow
    print('\t' * 6 + 'parseTerm():')
    parseFactor()
    F = True

    while F:
        numLine, lex, tok = getSymb()
        if tok in ('mult_op'):
            numRow += 1
            print('\t' * 6 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
            parseFactor()
        else:
            F = False
    return True


def parseFactor():
    global numRow
    print('\t' * 7 + 'parseFactor():')
    numLine, lex, tok = getSymb()
    print('\t' * 7 + 'parseFactor():=============рядок: {0}\t (lex, tok):{1}'.format(numLine, (lex, tok)))

    if tok in ('int', 'float', 'ident', 'exponent', 'boolean'):
        numRow += 1
        print('\t' * 7 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
    elif lex == '(':
        numRow += 1
        parseExpression()
        parseToken(')', 'bracket_op', '\t' * 7)
        print('\t' * 7 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
    else:
        failParse(
            'невідповідність у Expression.Factor',
            (numLine, lex, tok, 'rel_op, int, float, exponent, ident, boolean або \'(\' Expression \')\'')
        )
    return True


def parseIf():
    global numRow
    _, lex, tok = getSymb()
    if lex == 'if' and tok == 'keyword':
        numRow += 1
        parseBoolExpr()
        parseToken('then', 'keyword', '\t' * 5)
        parseToken('goto', 'keyword', '\t' * 5)
        if not parseStatement():
            parseFactor()
        return True
    else:
        return False


def parseFor():
    global numRow
    _, lex, tok = getSymb()
    if lex == 'for' and tok == 'keyword':
        numRow += 1
        parseToken('(', 'bracket_op', '\t' * 5)
        parseAssign()
        parseToken(';', 'punct', '\t' * 5)
        parseBoolExpr()
        parseToken(';', 'punct', '\t' * 5)
        parseAssign()
        parseToken(')', 'bracket_op', '\t' * 5)
        parseToken('{', 'decl_op', '\t' * 5)
        parseStatement()
        parseToken('}', 'decl_op', '\t' * 5)
        return True
    else:
        return False


def parseInput():
    global numRow
    _, lex, tok = getSymb()
    if lex == 'input' and tok == 'keyword':
        numRow += 1
        parseToken('(', 'bracket_op', '\t' * 5)
        parseFactor()
        parseToken(')', 'bracket_op', '\t' * 5)
        return True
    else:
        return False


def parsePrint():
    global numRow
    _, lex, tok = getSymb()
    if lex == 'print' and tok == 'keyword':
        numRow += 1
        parseToken('(', 'bracket_op', '\t' * 5)
        parseToken('"', 'quote', '')
        parseFactor()
        parseToken('"', 'quote', '')
        parseToken(')', 'bracket_op', '\t' * 5)
        return True
    else:
        return False


def parsePow():
    global numRow
    _, lex, tok = getSymb()
    if lex == 'pow' and tok == 'keyword':
        numRow += 1
        parseToken('(', 'bracket_op', '\t' * 5)
        parseFactor()
        parseToken(',', 'punct', '\t' * 5)
        parseFactor()
        parseToken(')', 'bracket_op', '\t' * 5)
        return True
    else:
        return False


def parseBoolExpr():
    global numRow
    parseExpression()
    numLine, lex, tok = getSymb()
    if tok in 'rel_op':
        numRow += 1
        print('\t' * 5 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
        parseExpression()
    else:
        failParse('mismatch in BoolExpr', (numLine, lex, tok, 'rel_op'))
    return True


# Uncomment the code below to run parser.
'''
if __name__ == '__main__':
    parseProgram()
'''
