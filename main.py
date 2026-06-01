from funciones import regex_to_nfa, nfaToDfa, aceptaAuto, tabNfa, tabDfa, EPS_OPS

def leeCads():
    cads = []
    print('Escriba una cadena por linea. Use EPS para epsilon. Enter vacio para terminar.')
    while True:
        cad = input('> ').strip()
        if cad == '':
            break
        if cad in EPS_OPS:
            cad = ''
        cads.append(cad)
    return cads

def showMenu():
    print('\n=== Conversor de automatas Regex ↔ NFA ↔ DFA ===')
    print('1. Cargar regex')
    print('2. Construir NFA')
    print('3. Construir DFA')
    print('4. Probar cadenas')
    print('5. Ver tabla del NFA')
    print('6. Ver tabla del DFA')
    print('7. Salir')

def main():
    regAct = ''
    nfaAct = None
    dfaAct = None
    while True:
        showMenu()
        opc = input('Opcion: ').strip()
        if opc == '1':
            reg = input('Regex: ').strip()
            try:
                nfaPrev = regex_to_nfa(reg)
                regAct = reg
                nfaAct = None
                dfaAct = None
                print('Regex cargada bien.')
                print('Alfabeto detectado:', sorted(nfaPrev[1]))
            except Exception as err:
                print('Error con la regex:', err)
        elif opc == '2':
            if regAct == '':
                print('Primero cargue una regex.')
                continue
            try:
                nfaAct = regex_to_nfa(regAct)
                dfaAct = None
                print('NFA construido.')
            except Exception as err:
                print('No se pudo construir el NFA:', err)
        elif opc == '3':
            if nfaAct is None:
                print('Primero construya el NFA.')
                continue
            try:
                dfaAct = nfaToDfa(nfaAct)
                print('DFA construido.')
            except Exception as err:
                print('No se pudo construir el DFA:', err)
        elif opc == '4':
            autoAct = dfaAct if dfaAct is not None else nfaAct
            if autoAct is None:
                print('Primero construya al menos el NFA.')
                continue
            cads = leeCads()
            for cad in cads:
                cadTxt = 'EPS' if cad == '' else cad
                res = 'ACCEPT' if aceptaAuto(autoAct, cad) else 'REJECT'
                print(cadTxt, '->', res)
        elif opc == '5':
            if nfaAct is None:
                print('Primero construya el NFA.')
                continue
            print(tabNfa(nfaAct))
        elif opc == '6':
            if dfaAct is None:
                print('Primero construya el DFA.')
                continue
            print(tabDfa(dfaAct))
        elif opc == '7':
            print('Saliendo.')
            break
        else:
            print('Opcion invalida.')

if __name__ == '__main__':
    main()
