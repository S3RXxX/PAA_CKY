# Authors: Sergi Guimerà Roig & Huilin Ni
# Pràctica de Programació i Algorísmia Avançada, PAA
# Professors: José Luis Balcázar, Jordi Delgado, Pedro Jesús Copado Méndez

import sys
from collections import deque, OrderedDict
import string

"""Intenció és fer 1 classe per la gramàtica i una classe per CKY, la classe de la gramàtica ens ajudarà a passar-la a FNC si no hi està (extensió 1)"""

class FNC:

    def __init__(self, gram):
        """inicialitzar la classe, creem el set de variables auxiliars,
         fem la crida per passar la CFG a FNC i després creem la inversa per accedir més ràpid a les regles que deriven certs simbols"""
        self.c = set(string.ascii_uppercase)  # per crear noms de símbols no terminals auxiliars
        self.gram = self.read_gram(gram)

        self.to_FNC()
        self.index = 0

        self.gram_inv = self.make_inv()
        self.keys = list(self.gram.keys())

    def make_inv(self):
        """creem la gramatica inversa
        si tenim a la gramatica el diccionari {'A': ['a', 'AX'], 'S0': ['AX', 'a'], 'X':['b']}, la gramatica inversa és
         {'a': {'A', 'S'}, 'AX': {'S0', 'A'}, 'b': {'X'}}"""
        d = dict()
        for key, itms in self.gram.items():
            for itm in itms:
                if itm in d:
                    d[itm].add(key)
                else:
                    d[itm] = {key}
        return d

    def read_gram(self, gram):
        """mètode encarregat de llegir l'string i posar les regles en un diccionari,
        si tenim una regla S0 -> AX | XB | a | b, la entrada al diccionari és:
        {'S0': ['AX', 'XB', 'a', 'b']}"""
        d = dict()
        rules = gram.split('\n')
        for rule in rules:
            a = rule.split('->')
            d[a[0].strip()] = list(map(lambda x: x.strip(), a[1].split('|')))
            if a[0].strip() in self.c:
                self.c.remove(a[0].strip())
            self.c = sorted(list(self.c))
        return d

    def __make_start_symbol(self):
        """eliminem els simbols d'inici de la dreta de les regles, per això fem un nou símbol que només estigui a l'esquerra"""
        if 'S0' not in self.gram:
            self.gram['S0'] = ['S']

    def __no_bin(self, bodies, i):
        """modificar les parts dretes de les regles amb més de 2 no terminals"""
        nom = self.c.pop()
        self.gram[nom] = [bodies[i][1:]]
        bodies[i] = bodies[i][0] + nom
        if len(self.gram[nom][0]) > 2:
            # regla no binaria
            self.__no_bin(self.gram[nom], 0)

    def __hibrid(self, bodies, i, j):
        """eliminar terminals no solitaris"""
        nom = self.c.pop()
        self.gram[nom] = [bodies[i][j]]
        bodies[i] = bodies[i][:j] + nom + bodies[i][j + 1:]

    def __unitaria(self, head, bodies, i):
        """eliminar regles amb un no terminal solitari a la dreta"""
        car = bodies.pop(i)
        if car == head:
            pass
        else:
            if car in self.gram:
                for elem in self.gram[car].copy():
                    if elem not in bodies:
                        bodies.append(elem)
                for k in range(len(bodies)):
                    if len(bodies[k]) == 1:
                        if bodies[k].isupper() or bodies[k].isnumeric():
                            self.__unitaria(head, bodies, k)
                            break

    def __eliminate_epsilon(self):
        """borrar les transicions buides menys del símbol inicial"""
        end = False
        nullables = {'e'}  # la lletra e es com representem la epsilon
        while not end:
            end = True
            b_aux = True
            for key, itm in self.gram.items():
                if key not in nullables:
                    for dre in itm:
                        for caracter in dre:
                            b_aux = True
                            if caracter not in nullables:
                                b_aux = False
                                break
                        if b_aux:
                            nullables.add(key)
                            end = False

        for key, itm in self.gram.items():
            for dre in itm:
                if dre == 'e':
                    itm.remove('e')
                else:
                    for idx, caracter in enumerate(dre):
                        if caracter in nullables:
                            new_dre = dre[:idx] + dre[idx + 1:]
                            if new_dre not in self.gram[key] and new_dre:
                                self.gram[key].append(new_dre)
        if 'S0' in nullables:
            self.gram['S0'].append("e")

    def to_FNC(self):
        """Mirem si està en FNC, en cas contrari passem a FNC"""

        self.__make_start_symbol()

        for head, bodies in self.gram.copy().items():  # regla hibrida
            for i in range(len(bodies)):
                if len(bodies[i]) > 1:
                    for j in range(len(bodies[i])):
                        if bodies[i][j].islower():
                            self.__hibrid(bodies, i, j)

        for head, bodies in self.gram.copy().items():  # regla no binaria
            for i in range(len(bodies)):
                if len(bodies[i]) > 2:
                    self.__no_bin(bodies, i)

        self.__eliminate_epsilon()  # eliminem les parts dretes que porten al buit

        for head, bodies in self.gram.copy().items():  # regla unitària
            for i in range(len(bodies)):
                if len(bodies[i]) == 1:
                    if bodies[i].isupper() or bodies[i].isnumeric():
                        self.__unitaria(head, bodies, i)
                        break

        lst_aux = []
        for head, bodies in self.gram.items():
            if len(bodies) == 0:
                lst_aux.append(head)
        for head in lst_aux:
            self.gram.pop(head)



    def __next__(self):
        """implementem next per poder fer la classe sigui iterable,
        en el nostre cas té el comportament d'un diccionari quan el crides amb .items()"""
        if self.index >= len(self.keys):
            self.index = 0
            raise StopIteration
        key = self.keys[self.index]
        value = self.gram[key]
        self.index += 1
        return key, value

    def __iter__(self):
        """implementem iter per poder fer la classe sigui iterable"""
        return self

    def __str__(self):
        """implementem el str perquè si fem un print de la instància surti la gramàtica que està utilitzant"""
        s = ''
        lst_aux = []
        for esq, dretes in self.gram.items():
            lst_aux.append(esq + ' -> ' + ' | '.join(dretes))
        s = '\n'.join(lst_aux)

        return f'{s}'


class CKY:

    def __init__(self, sent, gram):
        """inicialitzem la instància,
        guardem la paraula (sent) i la gramàtica un cop ens hem assegurat que és un objecte FNC"""
        self.sent = sent
        if isinstance(gram, str):
            gram = FNC(gram)
        elif isinstance(gram, FNC):
            pass
        else:
            raise Exception('cannot read ')
        self.gram = gram

    def find_rule(self, sign):
        """troba una regla per derivar el signe sign i retorna el cap de la regla"""
        s = set()
        if sign in self.gram.gram_inv:
            s = self.gram.gram_inv[sign]
        return s

    def execute(self):
        """mètode per executar el CKY que només ens diu si podem aconseguir
         una derivació que comenci amb el símbol inicial (S0)"""
        n = len(self.sent)
        if n == 0:  # en cas de que passem la string buida, ho considerem la paruala buida
            if 'e' in self.gram.gram_inv:
                return True
            else:
                return False
        self.t = [[set([]) for _ in range(n)] for _ in range(n)]  # creem la nostra taula

        for j in range(n):
            """posem si hi ha alguna regla per derivar un simbol terminal"""
            self.t[j][j] = self.find_rule(self.sent[j])

            for i in range(j, -1, -1):  # necessitem un altre index per iterar per sobre la taula 2d
                s = set()

                for k in range(i, j):  # la k serveix pels diferents splits possibles entre index
                    esq, dre = self.t[i][k], self.t[k + 1][j]
                    if esq and dre:
                        for e1 in esq:  # hem de mirar totes les regles que han arribat a les caselles prèvies
                            for e2 in dre:
                                r = self.find_rule(e1 + e2)  # busquem les regles que ens permeten derivar els simbols de les caselles prèvies
                                if r:
                                    s = s.union(r)  # unim les possibilitats amb les dels altres splits possibles

                        self.t[i][j] = s

        b = 'S0' in self.t[0][n - 1]  # si el simbol inicial està en aquesta posició de la taula, llavors la paraula es pot derivar amb la gramatica usada
        return b

    def execute_trace(self):
        """mètode similar a execute, la diferència és que ara guarem inforamció per recrear una derivació vàlida"""

        n = len(self.sent)
        if n == 0:  # en cas de que passem la string buida, ho considerem la paruala buida
            if 'e' in self.gram.gram_inv:
                return True, "S0->''"
            else:
                return False, ''
        self.t = [[OrderedDict() for _ in range(n)] for _ in range(n)] # creem la nostra taula
        # ara per la taula hem utilitzat diccionaris per guardar la info
        # les claus son els elements que guardavem en el execute en els sets

        for j in range(n):
            """posem si hi ha alguna regla per derivar un simbol terminal"""
            s = OrderedDict()
            r = self.find_rule(self.sent[j])
            for e in r:
                s[e] = (-1, self.sent[j], None, -1, -1)
            self.t[j][j] = s

            for i in range(j, -1, -1):  # necessitem un altre index per iterar per sobre la taula 2d
                s = OrderedDict()
                for k in range(i, j):  # la k serveix pels diferents splits possibles entre index

                    esq, dre = self.t[i][k], self.t[k + 1][j]
                    if esq and dre:
                        for e1 in esq:
                            for e2 in dre:
                                r = self.find_rule(e1 + e2)
                                for e in r:
                                    s[e] = (k, e1, e2, i, j)

                        self.t[i][j] = s

        b = 'S0' in self.t[0][n - 1]
        traza = ''
        if b:  # si hi ha almenys una derivacio, llavors volem veure una derivacio possible
            traza = self.trace()
        return b, traza

    def trace(self):
        """mètode encarregat de retornar una string amb una derivació possible,
         en el cas del probabilistic es retorna la més probable sense canviar res
         perquè només guardem el camí més probable per cada símbol en cada casella"""
        n = len(self.sent)
        fst = self.t[0][n - 1]['S0']
        s = 'S0'
        actual = s
        d = deque()  # utilitzem una pila pq la derivacio es faci d'esquerra a dreta
        d.append((s, fst))
        while d:
            # e[sign] = (k, e1, e2, i, j)
            sign, e = d.pop()

            if e[0] != -1:  # regla símbol no terminal
                for idx in range(len(actual)):  # actualitzem com esta la derivacio en el moment
                    if sign == actual[idx:idx + len(sign)]:
                        actual = actual[0:idx] + e[1] + e[2] + actual[idx + len(sign):]
                        break

                # afegim a la pila (si regla S -> AB, primer afegim B i després A pq surti primer A)
                d.append((e[2], self.t[e[0] + 1][e[4]][e[2]]))  # k+1 j

                d.append((e[1], self.t[e[3]][e[0]][e[1]]))  # i k

            else:  # regla simbol terminal
                for idx in range(len(actual)):  # actualitzem com esta la derivacio en el moment
                    if sign == actual[idx:idx + len(sign)]:
                        actual = actual[0:idx] + e[1] + actual[idx + len(sign):]
                        break

            s += f'->{actual}'  # actualitzem la derivacio amb com esta actualment
        return s


class PFNC(FNC):

    def __init__(self, gram):
        """classe heredara de FNC, en aquest cas per gramatiques probabilistiques,
        en aquest cas la gramàtica ha d'estar en FNC abans d'entrar"""

        super(PFNC, self).__init__(gram=gram)

    def make_inv(self):
        """creem la gramatica inversa
        ara també guardem les probabilitats en format tupla"""

        d = dict()
        for key, itms in self.gram.items():
            for itm in itms:
                if itm[0] in d:
                    d[itm[0]].add((key, itm[1]))  # guardem tuples, la 2a posicio es la probabilitat
                else:
                    d[itm[0]] = {(key, itm[1])}
        return d

    def read_gram(self, gram):
        """mètode encarregat de llegir l string i posar les regles en un diccionari,
        ara els diccionaris guarden llistes de tuples (simbol, probabilitat)"""
        d = dict()
        rules = gram.split('\n')
        for rule in rules:
            a = rule.split('->')
            d[a[0].strip()] = list(map(lambda x: (x.split()[0], float(x.split()[1])), a[1].split('|')))
            if a[0].strip() in self.c:
                self.c.remove(a[0].strip())
            self.c = sorted(list(self.c))
        return d

    def to_FNC(self):
        """en aquest cas exigim que ja estigui en FNC abans de passar-la al constructor,
         per això no implementem aquest mètode"""
        pass


    def __str__(self):
        """implementem el str perquè si fem un print de la instància surti la gramàtica que està utilitzant"""
        s = ''
        lst_aux = []
        for esq, dretes in self.gram.items():
            lst_aux2 = []
            for e, p in dretes:
                lst_aux2.append(e + ' ' + str(p))
            lst_aux.append(esq + ' -> ' + ' | '.join(lst_aux2))
        s = '\n'.join(lst_aux)

        return f'{s}'




class PCKY(CKY):

    def __init__(self, sent, gram):
        self.sent = sent
        if isinstance(gram, str):
            gram = PFNC(gram)
        elif isinstance(gram, PFNC):
            pass
        else:
            raise Exception('cannot read ')
        self.gram = gram


    def execute(self):
        """implementem directament amb traça perquè no té sentit trobar el més probable si no el mostrem"""
        pass

    def execute_trace(self):
        n = len(self.sent)
        if n == 0:  # en cas de que passem la string buida, ho considerem la paruala buida
            if 'e' in self.gram.gram_inv:
                for e in self.gram.gram['S0']:
                    if e[0] == 'e':
                        p = e[1]
                
                return True, "S0->''", p
            else:
                return False, '', 0
        self.t = [[OrderedDict() for _ in range(n)] for _ in range(n)]

        for j in range(n):
            """posem si hi ha alguna regla per derivar un sol simbol"""
            s = OrderedDict()
            r = self.find_rule(self.sent[j])
            for e, p in r:
                s[e] = (-1, self.sent[j], None, -1, -1, p)
            self.t[j][j] = s

            for i in range(j, -1, -1):
                s = OrderedDict()
                for k in range(i, j):
                    """prova per separar per diferents llocs"""

                    esq, dre = self.t[i][k], self.t[k + 1][j]
                    if esq and dre:
                        for e1 in esq:
                            for e2 in dre:
                                r = self.find_rule(e1 + e2)
                                for e, p in r:
                                    p_esq = self.t[i][k][e1][5]  # les probabilitats es guarden en la posicio 5 de la tupla
                                    p_dre = self.t[k + 1][j][e2][5]
                                    p = p * p_esq * p_dre
                                    if e in s:
                                        p_prev = s[e][5]
                                        if p_prev < p:
                                            s[e] = (k, e1, e2, i, j, p)
                                    else:
                                        s[e] = (k, e1, e2, i, j, p)

                        self.t[i][j] = s

        b = 'S0' in self.t[0][n - 1]
        traza = ''
        probabilitat = 0
        if b:
            traza = self.trace()
            probabilitat = self.t[0][n - 1]["S0"][5]
        return b, traza, probabilitat


def read_input(path):
    """llegeix el fitxer que conté la gramàtica i totes les paraules que es
    volen provar i retorna una string per la gramàtica i una llista d strings per les paraules"""
    with open(path, 'r') as f:
        a = f.read()
        splt = a.split('\n')
        p = int(splt[0])
        i = 1
        while splt[i] != '':
            i += 1
        r = '\n'.join(splt[1:i])
        word_lst = splt[i + 1:]
    return r, word_lst, p


if __name__ == '__main__':
    print('Reading the input file')
    path = sys.argv[1]
    g, word_lst, p = read_input(path)
    print('File read')
    print()

    print('The used grammar is the following:')
    print(g)
    print()
    if p:
        gram = PFNC(g)
        for w in word_lst:
            cyk = PCKY(sent=w, gram=gram)
            b, traza, probabilitat = cyk.execute_trace()
            print(f"The word {w} is {'not' * (not b)} derivable from the grammar")
            if b:
                print(f'This sequence of derivation rules has a probability of {probabilitat}')
                print('The trace is as follows:')
                print(traza)
            print()
    else:
        gram = FNC(g)
        print('The grammar in CNF is the following:')
        print(gram)
        print()
        for w in word_lst:
            cyk = CKY(sent=w, gram=gram)
            b, traza= cyk.execute_trace()
            print(f"The word {w} is {'not'*(not b)} derivable from the grammar")
            if b:
                print('The trace is as follows:'*b)
                print(traza)
            print()
