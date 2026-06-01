EPS = 'ϵ'
EPS_OPS = {'EPS', 'eps', 'ϵ'}

def esLit(char):
    return char not in ['|', '*', '(', ')', '.'] and char != ''

def normReg(reg):
    regN = reg
    for epsTxt in ['EPS', 'eps']:
        regN = regN.replace(epsTxt, EPS)
    return regN

def meteConcat(reg):
    regs = list(reg)
    regsCon = []
    for i in range(len(regs)):
        act = regs[i]
        regsCon.append(act)
        if i == len(regs) - 1:
            continue
        sig = regs[i + 1]
        hayIzq = esLit(act) or act == ')' or act == '*'
        hayDer = esLit(sig) or sig == '('
        if hayIzq and hayDer:
            regsCon.append('.')
    return regsCon

def regToPost(reg):
    reg = normReg(reg)
    if reg == '':
        raise ValueError('La regex vacia no se permite. Use ϵ, EPS o eps.')
    prio = {'|': 1, '.': 2, '*': 3}
    salida = []
    pilOps = []
    regsCon = meteConcat(reg)
    for tk in regsCon:
        if esLit(tk):
            salida.append(tk)
        elif tk == '(':
            pilOps.append(tk)
        elif tk == ')':
            while pilOps and pilOps[-1] != '(':
                salida.append(pilOps.pop())
            if not pilOps:
                raise ValueError('Parentesis mal puestos.')
            pilOps.pop()
        elif tk == '*':
            salida.append(tk)
        elif tk in ['|', '.']:
            while pilOps and pilOps[-1] != '(' and prio[pilOps[-1]] >= prio[tk]:
                salida.append(pilOps.pop())
            pilOps.append(tk)
        else:
            raise ValueError('Token invalido: ' + tk)
    while pilOps:
        op = pilOps.pop()
        if op in ['(', ')']:
            raise ValueError('Parentesis mal puestos.')
        salida.append(op)
    return salida

def newState(contIds):
    st = contIds[0]
    contIds[0] += 1
    return st

def addTransit(delta, ori, simb, dest):
    if ori not in delta:
        delta[ori] = {}
    if simb not in delta[ori]:
        delta[ori][simb] = set()
    delta[ori][simb].add(dest)

def uneDelta(deltaBase, deltaExt):
    for ori in deltaExt:
        for simb in deltaExt[ori]:
            for dest in deltaExt[ori][simb]:
                addTransit(deltaBase, ori, simb, dest)

def armFrag(stIni, stFin, delta):
    return {'stIni': stIni, 'stFin': stFin, 'delta': delta}

def postToNfa(postf):
    pilFrags = []
    contIds = [0]
    sigma = set()
    for tk in postf:
        if esLit(tk):
            stIni = newState(contIds)
            stFin = newState(contIds)
            delta = {}
            addTransit(delta, stIni, tk, stFin)
            if tk != EPS:
                sigma.add(tk)
            pilFrags.append(armFrag(stIni, stFin, delta))
        elif tk == '.':
            if len(pilFrags) < 2:
                raise ValueError('Concatenacion invalida.')
            fragDer = pilFrags.pop()
            fragIzq = pilFrags.pop()
            delta = {}
            uneDelta(delta, fragIzq['delta'])
            uneDelta(delta, fragDer['delta'])
            addTransit(delta, fragIzq['stFin'], EPS, fragDer['stIni'])
            pilFrags.append(armFrag(fragIzq['stIni'], fragDer['stFin'], delta))
        elif tk == '|':
            if len(pilFrags) < 2:
                raise ValueError('Union invalida.')
            fragDer = pilFrags.pop()
            fragIzq = pilFrags.pop()
            stIni = newState(contIds)
            stFin = newState(contIds)
            delta = {}
            uneDelta(delta, fragIzq['delta'])
            uneDelta(delta, fragDer['delta'])
            addTransit(delta, stIni, EPS, fragIzq['stIni'])
            addTransit(delta, stIni, EPS, fragDer['stIni'])
            addTransit(delta, fragIzq['stFin'], EPS, stFin)
            addTransit(delta, fragDer['stFin'], EPS, stFin)
            pilFrags.append(armFrag(stIni, stFin, delta))
        elif tk == '*':
            if not pilFrags:
                raise ValueError('Estrella invalida.')
            fragAct = pilFrags.pop()
            stIni = newState(contIds)
            stFin = newState(contIds)
            delta = {}
            uneDelta(delta, fragAct['delta'])
            addTransit(delta, stIni, EPS, fragAct['stIni'])
            addTransit(delta, stIni, EPS, stFin)
            addTransit(delta, fragAct['stFin'], EPS, fragAct['stIni'])
            addTransit(delta, fragAct['stFin'], EPS, stFin)
            pilFrags.append(armFrag(stIni, stFin, delta))
    if len(pilFrags) != 1:
        raise ValueError('Regex invalida.')
    fragFin = pilFrags.pop()
    qSet = {fragFin['stIni'], fragFin['stFin']}
    for ori in fragFin['delta']:
        qSet.add(ori)
        for simb in fragFin['delta'][ori]:
            qSet |= fragFin['delta'][ori][simb]
    return (qSet, sigma, fragFin['delta'], fragFin['stIni'], {fragFin['stFin']}, 'NFA')

def regex_to_nfa(regex):
    postf = regToPost(regex)
    return postToNfa(postf)

def ecloseSt(nfa, st):
    delta = nfa[2]
    pil = [st]
    cierre = {st}
    while pil:
        stAct = pil.pop()
        stNxt = delta.get(stAct, {}).get(EPS, set())
        for nxt in stNxt:
            if nxt not in cierre:
                cierre.add(nxt)
                pil.append(nxt)
    return cierre

def ecloseSet(nfa, stSet):
    cierreTot = set()
    for st in stSet:
        cierreTot |= ecloseSt(nfa, st)
    return cierreTot

def moveSet(nfa, stSet, simb):
    delta = nfa[2]
    stNxt = set()
    for st in stSet:
        stNxt |= delta.get(st, {}).get(simb, set())
    return stNxt

def nomSet(stSet):
    if not stSet:
        return '∅'
    return '{' + ','.join(str(st) for st in sorted(stSet)) + '}'

def nfaToDfa(nfa):
    sigma = sorted(nfa[1])
    fNfa = nfa[4]
    stIni = frozenset(ecloseSet(nfa, {nfa[3]}))
    pend = [stIni]
    vistos = {stIni}
    deltaDfa = {}
    fDfa = set()
    while pend:
        stAct = pend.pop(0)
        nomAct = nomSet(stAct)
        deltaDfa[nomAct] = {}
        if set(stAct) & set(fNfa):
            fDfa.add(nomAct)
        for simb in sigma:
            movs = moveSet(nfa, stAct, simb)
            cierre = frozenset(ecloseSet(nfa, movs))
            nomSig = nomSet(cierre)
            deltaDfa[nomAct][simb] = nomSig
            if cierre not in vistos:
                vistos.add(cierre)
                pend.append(cierre)
    qDfa = set(deltaDfa.keys())
    for ori in deltaDfa:
        for simb in deltaDfa[ori]:
            qDfa.add(deltaDfa[ori][simb])
    return (qDfa, set(sigma), deltaDfa, nomSet(stIni), fDfa, 'DFA')

def nfa_to_dfa(nfa):
    return nfaToDfa(nfa)

def normCad(cad):
    if cad in EPS_OPS:
        return ''
    return cad

def accNfa(nfa, cad):
    cad = normCad(cad)
    sigma = nfa[1]
    stAct = ecloseSet(nfa, {nfa[3]})
    for char in cad:
        if char not in sigma:
            return False
        stAct = ecloseSet(nfa, moveSet(nfa, stAct, char))
    return len(stAct & nfa[4]) > 0

def accDfa(dfa, cad):
    cad = normCad(cad)
    sigma = dfa[1]
    delta = dfa[2]
    stAct = dfa[3]
    for char in cad:
        if char not in sigma:
            return False
        stAct = delta.get(stAct, {}).get(char, '∅')
    return stAct in dfa[4]

def aceptaAuto(auto, cad):
    if auto[5] == 'DFA':
        return accDfa(auto, cad)
    return accNfa(auto, cad)

def accepts(auto, cad):
    return aceptaAuto(auto, cad)

def tabNfa(nfa):
    qSet, sigma, delta, qIni, fSet, _ = nfa
    lines = []
    lines.append('NFA = (Q, Σ, δ, q0, F)')
    lines.append('Q = ' + str(sorted(qSet)))
    lines.append('Σ = ' + str(sorted(sigma)))
    lines.append('q0 = ' + str(qIni))
    lines.append('F = ' + str(sorted(fSet)))
    lines.append('δ:')
    simbs = sorted(list(sigma) + [EPS])
    for ori in sorted(qSet):
        for simb in simbs:
            dests = delta.get(ori, {}).get(simb)
            if dests:
                lines.append('  δ(' + str(ori) + ', ' + simb + ') = ' + str(sorted(dests)))
    return '\n'.join(lines)

def tabDfa(dfa):
    qSet, sigma, delta, qIni, fSet, _ = dfa
    lines = []
    lines.append('DFA = (Q, Σ, δ, q0, F)')
    lines.append('Q = ' + str(sorted(qSet)))
    lines.append('Σ = ' + str(sorted(sigma)))
    lines.append('q0 = ' + str(qIni))
    lines.append('F = ' + str(sorted(fSet)))
    lines.append('δ:')
    for ori in sorted(qSet):
        for simb in sorted(sigma):
            if ori in delta and simb in delta[ori]:
                lines.append('  δ(' + str(ori) + ', ' + simb + ') = ' + str(delta[ori][simb]))
    return '\n'.join(lines)

def parseCase(line):
    parts = [p.strip() for p in line.split('|')]
    if len(parts) != 3:
        return None
    reg = parts[0]
    cad = parts[1]
    esp = parts[2].upper()
    return reg, cad, esp

