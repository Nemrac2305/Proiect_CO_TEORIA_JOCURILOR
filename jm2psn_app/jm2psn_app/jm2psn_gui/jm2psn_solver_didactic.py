"""
===============================================================================

Rezolvare JM2PSN prin PLB (MAX) + ASP
construit peste codul didactic de PL incarcat de utilizator

Observatie:
- pentru joc fara punct sa se ataseaza PLA si PLB;
- prin conventie, aici se rezolva doar PLB cu ASP;
- solutia pentru PLA se extrage din TS final al lui PLB, folosind dualitatea;
- apoi se reconstruiesc strategiile mixte optime si valoarea jocului.

===============================================================================
"""

EPS = 1e-9


# -----------------------------------------------------------------------------
# Subprogram (procedura) afisare valoare numar real in precizia indicata
# -----------------------------------------------------------------------------

def afisare_valoare_float(v, precizie):
    print(round(v, precizie), end='')

    return


# -----------------------------------------------------------------------------
# Subprogram (procedura) afisare vector numere reale in precizia indicata
# -----------------------------------------------------------------------------

def afisare_vector_float(V, precizie):
    n = len(V)
    if n == 0:
        return

    print("[", end='')
    for i in range(n):
        print(round(V[i], precizie), end='')
        if i < n - 1:
            print(", ", end='')
        else:
            print("]")

    return


# -----------------------------------------------------------------------------
# Subprogram (procedura) afisare matrice in precizia indicata
# -----------------------------------------------------------------------------

def afisare_matrice_float(M, precizie):
    for i in range(len(M)):
        afisare_vector_float(M[i], precizie)

    return


# -----------------------------------------------------------------------------
# Subprogram (functie) creare copie "deep" vector
# -----------------------------------------------------------------------------

def copie_vector(V):
    copie_V = []
    for i in range(len(V)):
        copie_V.append(V[i])

    return copie_V


# -----------------------------------------------------------------------------
# Subprogram (functie) creare copie "deep" matrice
# -----------------------------------------------------------------------------

def copie_matrice(M):
    copie_M = []
    for i in range(len(M)):
        line = []
        for j in range(len(M[0])):
            line.append(M[i][j])
        copie_M.append(line)

    return copie_M


# -----------------------------------------------------------------------------
# Subprograme ajutatoare pentru calcule floating point
# -----------------------------------------------------------------------------

def aproape_zero(x, eps=EPS):
    return abs(x) <= eps


def aproape_egal(a, b, eps=EPS):
    return abs(a - b) <= eps


def curata_numar(x, eps=EPS):
    if abs(x) <= eps:
        return 0.0
    return x


def curata_vector(V, eps=EPS):
    W = []
    for x in V:
        if abs(x) <= eps:
            W.append(0.0)
        else:
            W.append(x)
    return W


# -----------------------------------------------------------------------------
# Subprogram (functie) testare daca PLS are solutie infinit (optim infinit)
# -----------------------------------------------------------------------------

def solutie_infinit(delta, A, opt="max"):
    m = len(A)
    if opt == "min":
        for j in range(len(A[0])):
            if delta[j] < -EPS:
                i = 0
                while i < m:
                    if A[i][j] > EPS:
                        break
                    i = i + 1
                if i >= m:
                    return True
    else:
        for j in range(len(A[0])):
            if delta[j] > EPS:
                i = 0
                while i < m:
                    if A[i][j] > EPS:
                        break
                    i = i + 1
                if i >= m:
                    return True

    return False


# -----------------------------------------------------------------------------
# Subprogram (functie) testare existenta solutii multiple
# -----------------------------------------------------------------------------

def solutii_multiple(B, delta):
    ms_list = []
    print()

    for j in range(len(delta)):
        if j not in B and aproape_zero(delta[j]):
            ms_list.append(j)

    return ms_list


# -----------------------------------------------------------------------------
# Subprogram (procedura) afisare solutie curenta PL
# -----------------------------------------------------------------------------

def prezentare_solutie(n, m, Z, B, XB, opt="max"):
    print()
    print()
    print("Obs: Solutia PL == solutia PLS pentru variabilele principale")
    print("------------------------------------------------------------")
    print()

    # daca solutia de baza are componente == 0 ==> observatie "solutie degenerata"

    for i in range(m):
        if B[i] < n and aproape_zero(XB[i]):
            print("OBS: Solutie degenerata (exista componente bazice nule) !!!")
            print("(criteriul de iesire din baza a implicat metoda perturbatiilor)")
            print()
            break

    k = len(Z) - 1

    if opt != "min":
        print(f"==> Optim gasit pentru functia obiectiv:  fmax(x*) == Z[{k}] = {Z[k]}")
    else:
        print(f"==> Optim gasit pentru functia obiectiv:  fmin(x*) == Z[{k}] = {Z[k]}")
    print("    pentru valorile optimale:  x* = (", end='')
    for j in range(n):
        if j in B:
            for i in range(m):
                if B[i] == j:
                    print(f"x{j + 1}* = ", end='')
                    afisare_valoare_float(XB[i], 2)
                    if j < n - 1:
                        print(", ", end='')
                    else:
                        print(")")
                    break
        else:
            if j < n - 1:
                print(f"x{j + 1}* = 0.0", end=", ")
            else:
                print(f"x{j + 1}* = 0.0)")

    print()

    return


# -----------------------------------------------------------------------------
# Subprogram (procedura) verificari solutie curenta PL
# -----------------------------------------------------------------------------

def verificare_solutie(n, m, Z, B, CB, XB, c, b, S, opt, tip_restrictie):
    print()
    print("Verificari solutie")
    print()

    k = len(Z) - 1

    val = 0
    for i in range(m):
        if B[i] < n:
            val = val + c[B[i]] * XB[i]

    # masura pentru evitare inadvertente datorate unor erori de calcule floating point

    val = round(val, 10)

    print("Verificare optim functie obiectiv de valorile optimale ale variabilelor:")
    print(f"f(x*) = ", end='')
    for i in range(n):
        if i > 0:
            print("+ ", end='')
        print(f"{c[i]} x x{i + 1}* ", end='')
    print(f"= {val}", end='')
    if aproape_egal(Z[k], val):
        print(f" == Z[{k}] --> Ok.")
    else:
        print(f" ??? Z[{k}] (= {Z[k]}) --> Nu se verifica.")

    # verificare b = S x XB (S de la iteratia 0)

    print()
    print("Verificare matrice S x vector XB final = b1 == b:")

    b1 = []
    for i in range(m):
        val = 0
        for j in range(m):
            val = val + S[i][B[j]] * XB[j]
        b1.append(round(val, 10))

    for i in range(m):
        print("[", end='')
        for j in range(m):
            print(f"{round(S[i][B[j]], 3)}", end='')
            if j < m - 1:
                print(", ", end='')
            else:
                print("]   ", end='')
        afisare_valoare_float(XB[i], 2)
        print("   ", end='')
        print(round(b1[i], 3), end="     ")
        print(b[i])

    ok = True
    for i in range(m):
        if not aproape_egal(b[i], b1[i]):
            ok = False
            break

    if not ok:
        print("--> Nu se verifica (S x XB = b1 != b)")
    else:
        print("--> Ok. (S x XB = b1 == b)")

    # verificare restrictii pentru valorile optimale x*

    print()
    print("Verificare restrictii pentru valorile optimale ale variabilelor:")
    for i in range(m):
        val = 0
        for j in range(n):
            for k in range(m):
                if B[k] == j:
                    val = val + S[i][j] * XB[k]
                    break

        val = round(val, 10)

        if val < b[i] - EPS:
            print(f"   {val} < {b[i]}", end='')
            if tip_restrictie[i] == 1:
                print(" --> Ok.")
            else:
                print(" --> Restrictia nu se verifica")
        elif aproape_egal(val, b[i]):
            print(f"   {val} == {b[i]} --> Ok.")
        else:
            print(f"   {val} > {b[i]}", end='')
            if tip_restrictie[i] == 2:
                print(" --> Ok.")
            else:
                print(" --> Restrictia nu se verifica")

    return


# -----------------------------------------------------------------------------
# Subprogram (functie) identificare variabila intrare in baza B
# -----------------------------------------------------------------------------

def idx_var_in(delta, opt="max"):
    jj = None
    if opt != "min":  # gasire valoare pozitiva maxima delta
        for j in range(len(delta)):
            if delta[j] > EPS:
                if jj is None or delta[j] > delta[jj] + EPS:
                    jj = j
    else:  # gasire valoare negativa minima delta
        for j in range(len(delta)):
            if delta[j] < -EPS:
                if jj is None or delta[j] < delta[jj] - EPS:
                    jj = j

    return jj


# -----------------------------------------------------------------------------
# Subprogram (functie) identificare variabila iesire din baza B
# -----------------------------------------------------------------------------

def idx_var_out(A, XB, jj):
    ii = None
    minim = None

    for i in range(len(XB)):
        if A[i][jj] > EPS and XB[i] >= -EPS:
            raport = XB[i] / A[i][jj]
            if ii is None or raport < minim - EPS:
                minim = raport
                ii = i

    if ii is None:
        return None

    # tratare eventuala situatie in care exista mai multe valori == minim
    # (OBS: solutie degenerata ==> se aplica metoda perturbatiilor - CHARNES)

    for i in range(ii + 1, len(XB), 1):
        if A[i][jj] > EPS and XB[i] >= -EPS and aproape_egal(XB[i] / A[i][jj], minim):
            for k in range(len(A[0])):
                st = A[i][k] / A[i][jj]
                dr = A[ii][k] / A[ii][jj]
                if not aproape_egal(st, dr):
                    if st < dr:
                        ii = i
                    break

    return ii


# -----------------------------------------------------------------------------
# Subprogram (procedura) afisare calcule criteriu de intrare in baza B
# -----------------------------------------------------------------------------

def afisare_criteriu_intrare(delta, opt="max"):
    print()
    print("Detaliere criteriu de intrare in baza:")

    jj = idx_var_in(delta, opt)

    for j in range(len(delta)):
        print(f"   delta[a{j + 1}] = ", end='')
        afisare_valoare_float(delta[j], 4)
        if opt != "min":
            if delta[j] > EPS:
                print("  > 0  --> candidat de intrare")
            else:
                print("  <= 0 --> nu poate intra in baza")
        else:
            if delta[j] < -EPS:
                print("  < 0  --> candidat de intrare")
            else:
                print("  >= 0 --> nu poate intra in baza")

    print()
    if jj is not None:
        if opt != "min":
            print(f"==> Intra in baza variabila a{jj + 1}, deoarece are delta pozitiva maxima.")
        else:
            print(f"==> Intra in baza variabila a{jj + 1}, deoarece are delta negativa minima.")
    else:
        print("==> Nu exista variabila care sa intre in baza.")

    return jj


# -----------------------------------------------------------------------------
# Subprogram (procedura) afisare calcule criteriu de iesire din baza B
# -----------------------------------------------------------------------------

def afisare_criteriu_iesire(A, XB, B, jj):
    print()
    print("Detaliere criteriu de iesire din baza:")
    print(f"Se calculeaza rapoartele XB[i] / A[i][{jj}] numai pentru liniile cu A[i][{jj}] > 0.")

    ii = idx_var_out(A, XB, jj)

    for i in range(len(XB)):
        print(f"   Linia {i}: ", end='')
        if A[i][jj] <= EPS:
            print(f"A[{i}][{jj}] = {round(A[i][jj], 4)} <= 0 --> nu participa la criteriul raportului minim")
        elif XB[i] < -EPS:
            print(f"XB[{i}] = {round(XB[i], 4)} < 0 --> nu participa la criteriul raportului minim")
        else:
            raport = XB[i] / A[i][jj]
            print(f"XB[{i}] / A[{i}][{jj}] = {round(XB[i], 4)} / {round(A[i][jj], 4)} = {round(raport, 4)}")

    print()
    if ii is not None:
        print(f"==> Iese din baza variabila a{B[ii] + 1}, aflata pe linia {ii}, deoarece are raport minim.")
    else:
        print("==> Nu exista variabila care sa iasa din baza.")

    return ii


# -----------------------------------------------------------------------------
# Subprogram (functie) test optimalitate
# -----------------------------------------------------------------------------

def TO(delta, opt="max"):
    if opt != "min":
        for j in range(len(delta)):
            if delta[j] > EPS:
                return False
    else:
        for j in range(len(delta)):
            if delta[j] < -EPS:
                return False

    return True


# -----------------------------------------------------------------------------
# Subprogram (functie) extragere solutie principala x din baza curenta
# -----------------------------------------------------------------------------

def extrage_solutie_principala(n, B, XB):
    x = []
    for j in range(n):
        x.append(0.0)

    for i in range(len(B)):
        if B[i] < n:
            x[B[i]] = curata_numar(XB[i])

    return x


# -----------------------------------------------------------------------------
# Subprogram (functie) rezolvare PL cu ASP - varianta construita peste codul dat
# -----------------------------------------------------------------------------

def rezolva_PL_cu_ASP(opt, c_init, A_init, b_init, tip_restrictie, cauta_solutii_multiple=False):
    n = len(c_init)
    m = len(A_init)

    c = copie_vector(c_init)
    A = copie_matrice(A_init)
    b = copie_vector(b_init)
    tip_restrictie = copie_vector(tip_restrictie)

    # verificare daca nu cumva suntem deja in situatia PLS

    i = 0
    while i < m:
        if tip_restrictie[i] != 3:  # "=="
            break
        i = i + 1

    # daca toate restrictiile sunt de tip "==", verificare daca exista deja o baza

    y_supl = 0
    z_art = 0
    B = []
    if i >= m:
        for i in range(m):
            for j in range(n):
                if aproape_egal(A[i][j], 1):
                    k = 0
                    while k < m:
                        if k != i and not aproape_zero(A[k][j]):
                            break
                        k = k + 1
                    if k >= m:
                        B.append(j)
                        break

    print()
    if len(B) == m:
        print("Problema este una standard (PL == PLS)")
        print("--------------------------------------")
        print()
    else:
        # daca e necesar, trecere de la PL la PLS

        print("Trecere la forma standard (PL --> PLS)")
        print("--------------------------------------")
        print()

        for i in range(m):
            if tip_restrictie[i] == 1:  # "<="
                y_supl = y_supl + 1
            elif tip_restrictie[i] == 2:  # ">="
                y_supl = y_supl + 1
                z_art = z_art + 1
            else:  # tip_restrictie[i] == 3   # "=="
                z_art = z_art + 1

        print(f"==> Numar variabile suplimentare:  y = {y_supl},  z = {z_art}")
        print()

        # completare matrice A pentru trecerea de la PL la PLS

        for i in range(m):
            for j in range(y_supl + z_art):
                A[i].append(0.0)

        j = n
        while j < n + y_supl:
            for i in range(m):
                if tip_restrictie[i] == 1:
                    A[i][j] = 1.0
                    j = j + 1
                elif tip_restrictie[i] == 2:
                    A[i][j] = -1.0
                    j = j + 1

        j = n + y_supl
        while j < n + y_supl + z_art:
            for i in range(m):
                if tip_restrictie[i] in [2, 3]:
                    A[i][j] = 1.0
                    j = j + 1

        # generare coeficienti variabile suplimentare functie obiectiv PLS
        # y = nr. variabile slack/surplus, z = nr. variabile artificiale

        for j in range(y_supl):
            c.append(0.0)
        if opt != "min":
            M = -1000.0
        else:
            M = 1000.0
        for j in range(z_art):
            c.append(M)

    print(f"Coeficientii c: {c}")
    print()

    # pastram in S o copie "deep" a lui A initial (pentru verificare finala)

    S = copie_matrice(A)

    # iteratia 0

    k = 0

    print("Start Algoritm Simplex Primal (ASP)")
    print()
    print(f"* Iteratia {k}:")
    print()
    print("Componentele initiale ale Tabelului Simplex (TS)")
    print()

    # daca nu s-a facut deja (PL == PLS), initializare baza B

    if len(B) != m:
        B = []
        j1 = 0
        for i in range(m):
            if tip_restrictie[i] in [2, 3]:
                B.append(n + y_supl + j1)  # indexul lui a preluat in B
                j1 = j1 + 1
            elif tip_restrictie[i] == 1:
                for j in range(n, n + y_supl, 1):
                    if aproape_egal(A[i][j], 1):
                        B.append(j)
                        break

    # initializare si CB si XB

    CB = []
    XB = []
    for i in range(m):
        CB.append(c[B[i]])
        XB.append(b[i])

    print("Vectorii B, CB si XB:")
    for i in range(m):
        print(f"a{B[i] + 1}", end="   ")
        print(CB[i], end="   ")
        print(XB[i])

    print()
    print("Matricea A si vectorul b:")
    for i in range(m):
        print(A[i], end='   ')
        print(b[i])

    # initializare si calcul initial z si delta

    z = []
    delta = []
    for j in range(n + y_supl + z_art):
        val = 0
        for i in range(m):
            val = val + CB[i] * A[i][j]

        # masura pentru evitare probleme datorate erorilor de calcul in virgula mobila

        val = round(val, 10)

        z.append(val)
        delta.append(round(c[j] - val, 10))

    print()
    print(f"Vectorii z si delta, iteratia {k}:")
    afisare_vector_float(z, 2)
    afisare_vector_float(delta, 2)

    # test criteriu optim infinit

    if solutie_infinit(delta, A, opt):
        print()
        if opt != "min":
            print("Obs: Criteriu de optim infinit (valori coloana matrice A <= 0 si delta > 0)")
        else:
            print("Obs: Criteriu de optim infinit (valori coloana matrice A <= 0 si delta < 0)")
        print("==> Problema de optimizare PL are solutie optim infinit")
        print()
        print("Terminare program")
        print()

        return {
            "status": "optim_infinit",
            "message": "Problema de PL are solutie optim infinit.",
            "n": n,
            "m": m,
            "y_supl": y_supl,
            "y": y_supl,
            "z_art": z_art,
            "z_artificiale": z_art,
            "B": B,
            "CB": CB,
            "XB": XB,
            "A": A,
            "S": S,
            "c": c,
            "b": b,
            "delta": delta,
            "z": z,
            "Z": []
        }

    # initializare Z (valori optime la fiecare iteratie)

    Z = []

    # calcul valoare optima la iteratia curenta

    val = 0
    for i in range(m):
        val = val + CB[i] * XB[i]

    # masura pentru evitare probleme datorate erorilor de calcul in virgula mobila

    val = round(val, 10)

    Z.append(val)

    print()
    print(f"Valoare optima la iteratia curenta ({k}):")
    print(f"==> Z[{k}] = {Z[k]}")

    sol_multiple = False

    # test optimitate solutie

    gata = TO(delta, opt)
    if gata:
        print()
        print(f"* Test optimalitate ==> \"True\" ==> Iteratia {k}: STOP")
        print()
        print("------------------------------------------------------")

        # test existenta solutie

        if z_art > 0:
            i = 0
            while i < m:
                if B[i] >= len(A[0]) - z_art and not aproape_zero(XB[i]):
                    break
                i = i + 1
            if i < m:
                print()
                print("Obs: Criteriu inexistenta solutie (variabila de penalizare PLS != 0)")
                print("==> Problema de optimizare PL nu are solutie")
                print()
                print("Terminare program")
                print()

                return {
                    "status": "fara_solutie",
                    "message": "Problema de PL nu are solutie.",
                    "n": n,
                    "m": m,
                    "y_supl": y_supl,
            "y": y_supl,
                    "z_art": z_art,
            "z_artificiale": z_art,
                    "B": B,
                    "CB": CB,
                    "XB": XB,
                    "A": A,
                    "S": S,
                    "c": c,
                    "b": b,
                    "delta": delta,
                    "z": z,
                    "Z": Z
                }

        # furnizare solutie curenta PL

        prezentare_solutie(n, m, Z, B, XB, opt)

        # verificare solutie curenta PL

        verificare_solutie(n, m, Z, B, CB, XB, c, b, S, opt, tip_restrictie)

        rezultat = {
            "status": "optim",
            "message": "Optim gasit.",
            "n": n,
            "m": m,
            "y_supl": y_supl,
            "y": y_supl,
            "z_art": z_art,
            "z_artificiale": z_art,
            "B": copie_vector(B),
            "CB": copie_vector(CB),
            "XB": curata_vector(copie_vector(XB)),
            "A": copie_matrice(A),
            "S": copie_matrice(S),
            "c": copie_vector(c),
            "b": copie_vector(b),
            "delta": curata_vector(copie_vector(delta)),
            "z": curata_vector(copie_vector(z)),
            "Z": copie_vector(Z),
            "obiectiv": Z[-1],
            "x": extrage_solutie_principala(n, B, XB)
        }

        if not cauta_solutii_multiple:
            print()
            print("Obs: Pentru utilizarea in JM2PSN ne oprim la prima solutie optima gasita.")
            print()
            print("Terminare program")
            print()
            return rezultat

        if not sol_multiple:
            ms_list = solutii_multiple(B, delta)
            print()
            if len(ms_list) > 0:
                print(f"Obs: Solutii multiple PLS (delta == 0 pt. inca {len(ms_list)} variabile non-baza)")
                k1 = 0
                sol_multiple = True
                gata = False

                # pastrare context iteratie solutii multiple pentru celelalte solutii

                B1 = copie_vector(B)
                CB1 = copie_vector(CB)
                XB1 = copie_vector(XB)
                A1 = copie_matrice(A)
            else:
                print("Obs: Solutie unica (nu exista solutii multiple)")

        print()
        print("------------------------------------------------------")
    else:
        print()
        print(f"* Test optimalitate ==> \"False\" ==> Inca o iteratie")
        print()
        print("------------------------------------------------------")

    while not gata:
        # trecere la iteratia urmatoare

        k = k + 1

        print()
        print(f"* Iteratia {k}:")

        print()
        print("Aplicare criterii identificare indecsi variabile de i/o baza B")

        # identificare variabila intrare in baza B

        if not sol_multiple:
            jj = afisare_criteriu_intrare(delta, opt)
        else:
            jj = ms_list[k1]

            if k1 > 0:
                # de la a 3-a solutie multipla, refacere context iteratie prima solutie multipla

                B = copie_vector(B1)
                CB = copie_vector(CB1)
                XB = copie_vector(XB1)
                A = copie_matrice(A1)

            print()
            print("Detaliere criteriu de intrare in baza:")
            print(f"==> Intra in baza variabila a{jj + 1}, aleasa din lista variabilelor cu delta = 0")

        if jj is None:
            gata = True
            continue

        # identificare variabila iesire din baza B

        ii = afisare_criteriu_iesire(A, XB, B, jj)
        if ii is None:
            print()
            print("Obs: Nu exista variabila de iesire din baza pentru coloana aleasa.")
            print("==> Problema de optimizare PL are solutie optim infinit")
            print()
            print("Terminare program")
            print()
            return {
                "status": "optim_infinit",
                "message": "Problema de PL are solutie optim infinit.",
                "n": n,
                "m": m,
                "y_supl": y_supl,
            "y": y_supl,
                "z_art": z_art,
            "z_artificiale": z_art,
                "B": B,
                "CB": CB,
                "XB": XB,
                "A": A,
                "S": S,
                "c": c,
                "b": b,
                "delta": delta,
                "z": z,
                "Z": Z
            }

        # stabilire pivot

        p = A[ii][jj]
        var_out = B[ii]

        print()
        print(f"==> Variabila care intra in baza: a{jj + 1}")
        print(f"==> Variabila care iese din baza: a{var_out + 1}")
        print(f"==> Pivot = A[{ii}][{jj}] = ", end='')
        afisare_valoare_float(p, 2)
        print()

        # actualizare baza B, CB

        B[ii] = jj
        CB[ii] = c[jj]

        # actualizare toti XB cu i != ii

        for i in range(m):
            if i != ii:
                XB[i] = XB[i] * p - XB[ii] * A[i][jj]
        for i in range(m):
            XB[i] = XB[i] / p

        # actualizare toti A cu i != ii si j != jj

        for i in range(m):
            if i != ii:
                for j in range(n + y_supl + z_art):
                    if j != jj:
                        A[i][j] = A[i][j] * p - A[ii][j] * A[i][jj]
        for i in range(m):
            if i != ii:
                for j in range(n + y_supl + z_art):
                    if j != jj:
                        A[i][j] = A[i][j] / p

        # actualizare linie pivot

        if not aproape_zero(p):
            for j in range(n + y_supl + z_art):
                A[ii][j] = A[ii][j] / p

        # actualizare rest coloana pivot (toti A cu i != ii si j == jj)

        for i in range(m):
            if i != ii:
                A[i][jj] = 0.0

        for i in range(m):
            XB[i] = round(curata_numar(XB[i]), 10)
        for i in range(m):
            for j in range(n + y_supl + z_art):
                A[i][j] = round(curata_numar(A[i][j]), 10)

        # actualizare z si delta

        for j in range(n + y_supl + z_art):
            val = 0
            for i in range(m):
                val = val + CB[i] * A[i][j]

            # masura pentru evitare probleme datorate erorilor de calcul in virgula mobila

            val = round(val, 10)

            z[j] = val
            delta[j] = round(c[j] - z[j], 10)

        print()
        print("Componentele Tabelului Simplex (TS) actualizat")
        print()
        print("Vectorii B, CB si XB:")
        for i in range(m):
            print(f"a{B[i] + 1}", end="   ")
            print(CB[i], end="   ")
            afisare_valoare_float(XB[i], 2)
            print()

        print()
        print("Matricea A:")
        for i in range(m):
            afisare_vector_float(A[i], 2)

        print()
        print(f"Vectorii z si delta, iteratia {k}:")
        print(f"z = ", end='')
        afisare_vector_float(z, 2)
        print(f"delta = ", end='')
        afisare_vector_float(delta, 2)

        # test criteriu "optim infinit"

        if solutie_infinit(delta, A, opt):
            print()
            if opt != "min":
                print("Obs: Criteriu de optim infinit (valori coloana matrice A <= 0 si delta > 0)")
            else:
                print("Obs: Criteriu de optim infinit (valori coloana matrice A <= 0 si delta < 0)")
            print("==> Problema de optimizare PL are solutie optim infinit")
            print()
            print("Terminare program")
            print()

            return {
                "status": "optim_infinit",
                "message": "Problema de PL are solutie optim infinit.",
                "n": n,
                "m": m,
                "y_supl": y_supl,
            "y": y_supl,
                "z_art": z_art,
            "z_artificiale": z_art,
                "B": B,
                "CB": CB,
                "XB": XB,
                "A": A,
                "S": S,
                "c": c,
                "b": b,
                "delta": delta,
                "z": z,
                "Z": Z
            }

        # calcul valoare optima la iteratia curenta

        val = 0
        for i in range(m):
            val = val + CB[i] * XB[i]

        # masura pentru evitare probleme datorate erorilor de calcul in virgula mobila

        val = round(val, 10)

        Z.append(val)

        # verificare evolutie (optimizare) valoare functie obiectiv

        print()
        print(f"Valoare optima la iteratia curenta ({k}):")
        print(f"==> Z[{k}] = {Z[k]}")
        print()
        if opt != "min" and Z[k] > Z[k - 1] + EPS:
            print(f"(Obs: Z[{k}] = {Z[k]} > Z[{k - 1}] = {Z[k - 1]} --> Ok.)")
        elif opt == "min" and Z[k] < Z[k - 1] - EPS:
            print(f"(OBS: Z[{k}] = {Z[k]} < Z[{k - 1}] = {Z[k - 1]}) --> Ok.")
        elif sol_multiple and aproape_egal(Z[k], Z[k - 1]):
            print(f"(Obs: Z[{k}] = {Z[k]} == Z[{k - 1}] = {Z[k - 1]}) --> Ok.")
        else:
            print(f"(Obs: Z[{k}] = {Z[k]} ??? Z[{k - 1}] = {Z[k - 1]}) --> Nu s-a optimizat")

        # test optimalitate solutie

        gata = TO(delta, opt)
        if gata:
            print()
            print(f"* Test optimalitate ==> \"True\" ==> Iteratia {k}: STOP")
            print()
            print("------------------------------------------------------")

            # test existenta solutie

            if z_art > 0:
                i = 0
                while i < m:
                    if B[i] >= len(A[0]) - z_art and not aproape_zero(XB[i]):
                        break
                    i = i + 1
                if i < m:
                    print()
                    print("Obs: Criteriu inexistenta solutie (variabila de penalizare PLS != 0)")
                    print("==> Problema de optimizare PL nu are solutie")
                    print()
                    print("Terminare program")
                    print()

                    return {
                        "status": "fara_solutie",
                        "message": "Problema de PL nu are solutie.",
                        "n": n,
                        "m": m,
                        "y_supl": y_supl,
            "y": y_supl,
                        "z_art": z_art,
            "z_artificiale": z_art,
                        "B": B,
                        "CB": CB,
                        "XB": XB,
                        "A": A,
                        "S": S,
                        "c": c,
                        "b": b,
                        "delta": delta,
                        "z": z,
                        "Z": Z
                    }

            # furnizare solutie curenta PL

            prezentare_solutie(n, m, Z, B, XB, opt)

            # verificare solutie curenta PL

            verificare_solutie(n, m, Z, B, CB, XB, c, b, S, opt, tip_restrictie)

            rezultat = {
                "status": "optim",
                "message": "Optim gasit.",
                "n": n,
                "m": m,
                "y_supl": y_supl,
            "y": y_supl,
                "z_art": z_art,
            "z_artificiale": z_art,
                "B": copie_vector(B),
                "CB": copie_vector(CB),
                "XB": curata_vector(copie_vector(XB)),
                "A": copie_matrice(A),
                "S": copie_matrice(S),
                "c": copie_vector(c),
                "b": copie_vector(b),
                "delta": curata_vector(copie_vector(delta)),
                "z": curata_vector(copie_vector(z)),
                "Z": copie_vector(Z),
                "obiectiv": Z[-1],
                "x": extrage_solutie_principala(n, B, XB)
            }

            if not cauta_solutii_multiple:
                print()
                print("Obs: Pentru utilizarea in JM2PSN ne oprim la prima solutie optima gasita.")
                print()
                print("Terminare program")
                print()
                return rezultat

            # asiguram obtinerea una cate una si a restului de solutii multiple (daca exista)

            if not sol_multiple:
                ms_list = solutii_multiple(B, delta)
                if len(ms_list) > 0:
                    print(f"Obs: Solutii multiple PLS (delta == 0 pt. inca {len(ms_list)} variabile non-baza)")
                    k1 = 0
                    sol_multiple = True
                    gata = False

                    # pastrare context iteratie solutii multiple pentru celelalte solutii

                    B1 = copie_vector(B)
                    CB1 = copie_vector(CB)
                    XB1 = copie_vector(XB)
                    A1 = copie_matrice(A)
                else:
                    print("Obs: Solutie unica (nu exista solutii multiple)")
            else:
                k1 = k1 + 1
                if k1 < len(ms_list):
                    gata = False

            print()
            print("------------------------------------------------------")
        else:
            print()
            print(f"* Test optimalitate ==> \"False\" ==> Inca o iteratie")
            print()
            print("------------------------------------------------------")

    print()
    print("Terminare program")
    print()

    return rezultat


# -----------------------------------------------------------------------------
# Subprograme pentru jocul matricial de 2 persoane cu suma nula
# -----------------------------------------------------------------------------

def calculeaza_alpha_beta(Q):
    m = len(Q)
    n = len(Q[0])

    alpha = []
    for i in range(m):
        minim = Q[i][0]
        for j in range(1, n):
            if Q[i][j] < minim:
                minim = Q[i][j]
        alpha.append(minim)

    beta = []
    for j in range(n):
        maxim = Q[0][j]
        for i in range(1, m):
            if Q[i][j] > maxim:
                maxim = Q[i][j]
        beta.append(maxim)

    v1 = alpha[0]
    for i in range(1, m):
        if alpha[i] > v1:
            v1 = alpha[i]

    v2 = beta[0]
    for j in range(1, n):
        if beta[j] < v2:
            v2 = beta[j]

    return alpha, beta, v1, v2



def puncte_sa(Q, alpha, beta, v):
    puncte = []
    for i in range(len(Q)):
        if aproape_egal(alpha[i], v):
            for j in range(len(Q[0])):
                if aproape_egal(beta[j], v) and aproape_egal(Q[i][j], v):
                    puncte.append((i, j))

    return puncte



def translatare_matrice_pozitiva(Q):
    minim = Q[0][0]
    for i in range(len(Q)):
        for j in range(len(Q[0])):
            if Q[i][j] < minim:
                minim = Q[i][j]

    K = 0.0
    if minim <= 0:
        K = 1 - minim

    Q1 = copie_matrice(Q)
    if K > 0:
        for i in range(len(Q1)):
            for j in range(len(Q1[0])):
                Q1[i][j] = Q1[i][j] + K

    return Q1, K



def construieste_PLB_din_joc(Q):
    # PLB:
    # max g(y) = sum y_j
    # Q * y <= 1
    # y >= 0
    n = len(Q[0])
    m = len(Q)

    c = []
    for j in range(n):
        c.append(1.0)

    A = copie_matrice(Q)

    b = []
    for i in range(m):
        b.append(1.0)

    tip = []
    for i in range(m):
        tip.append(1)   # <=

    return c, A, b, tip



def extrage_solutia_PLA_din_TS_final_PLB(rezultat_plb):
    # Pentru PLB de forma:
    #   max g(y)
    #   Q y <= 1, y >= 0
    # duala PLA este:
    #   min f(x)
    #   Q^T x >= 1, x >= 0
    #
    # In tabelul simplex final al lui PLB, pentru coloanele variabilelor slack u_i,
    # avem:
    #   delta_u_i = c_u_i - z_u_i = 0 - x_i = -x_i
    # deci:
    #   x_i = -delta_u_i

    n = rezultat_plb["n"]
    m = rezultat_plb["m"]
    y_supl = rezultat_plb["y_supl"]
    delta = rezultat_plb["delta"]

    if y_supl < m:
        raise ValueError("PLB nu a generat toate variabilele slack necesare.")

    xA = []
    for i in range(m):
        xA.append(curata_numar(-delta[n + i]))

    return xA



def normalizeaza_strategie(v):
    s = 0.0
    for x in v:
        s = s + x

    if aproape_zero(s):
        return copie_vector(v)

    w = []
    for x in v:
        y = x / s
        if y < 0 and abs(y) <= 1e-8:
            y = 0.0
        w.append(y)

    return w



def produs_vector_matrice(x, Q):
    rez = []
    for j in range(len(Q[0])):
        val = 0.0
        for i in range(len(Q)):
            val = val + x[i] * Q[i][j]
        rez.append(curata_numar(val))
    return rez



def produs_matrice_vector(Q, y):
    rez = []
    for i in range(len(Q)):
        val = 0.0
        for j in range(len(Q[0])):
            val = val + Q[i][j] * y[j]
        rez.append(curata_numar(val))
    return rez



def produs_bilinear(x, Q, y):
    val = 0.0
    for i in range(len(Q)):
        for j in range(len(Q[0])):
            val = val + x[i] * Q[i][j] * y[j]
    return curata_numar(val)





# -----------------------------------------------------------------------------
# Subprograme suplimentare pentru reduceri prin strategii dominate
# -----------------------------------------------------------------------------

def linie_domina(Q, k, p):
    mai_mare_strict = False
    for j in range(len(Q[0])):
        if Q[k][j] < Q[p][j] - EPS:
            return False
        if Q[k][j] > Q[p][j] + EPS:
            mai_mare_strict = True

    return mai_mare_strict



def coloana_domina(Q, k, p):
    mai_mica_strict = False
    for i in range(len(Q)):
        if Q[i][k] > Q[i][p] + EPS:
            return False
        if Q[i][k] < Q[i][p] - EPS:
            mai_mica_strict = True

    return mai_mica_strict



def reconstruieste_strategie(v_redus, idx_pastrati, dim_totala):
    v = []
    for _ in range(dim_totala):
        v.append(0.0)

    for i in range(len(v_redus)):
        v[idx_pastrati[i]] = curata_numar(v_redus[i])

    return v



def afisare_indecsi_pastrati(idx, prefix):
    print('[', end='')
    for i in range(len(idx)):
        print(f"{prefix}{idx[i] + 1}", end='')
        if i < len(idx) - 1:
            print(', ', end='')
        else:
            print(']')

    return



def reduce_strategii_dominante_didactic(Q):
    Q_redus = copie_matrice(Q)
    idx_linii = []
    idx_coloane = []
    for i in range(len(Q)):
        idx_linii.append(i)
    for j in range(len(Q[0])):
        idx_coloane.append(j)

    jurnal = []

    print('Etapa suplimentara. Reducere de linii / coloane dominate')
    print('--------------------------------------------------------')
    print()
    print('Obs: Se aplica iterativ regulile RA si RB pentru strategii pure dominate.')
    print('Matricea de plecare pentru reducere:')
    afisare_matrice_float(Q_redus, 3)
    print()

    pas = 1
    modificat = True
    while modificat:
        modificat = False

        # RA - reducere linii
        for p in range(len(Q_redus)):
            if modificat:
                break
            for k in range(len(Q_redus)):
                if k == p:
                    continue
                if linie_domina(Q_redus, k, p):
                    jurnal.append(("linie", idx_linii[k], idx_linii[p]))
                    print(f"* Reducerea #{pas}: RA (reducere de linii)")
                    print(f"Linia L{k + 1} din jocul curent domina linia L{p + 1} din jocul curent.")
                    print(f"Adica strategia A{idx_linii[k] + 1} domina strategia A{idx_linii[p] + 1} din jocul initial.")
                    print(f"==> Se elimina linia dominata: L{p + 1} (coresp. A{idx_linii[p] + 1}).")
                    print()
                    Q_nou = []
                    idx_linii_noi = []
                    for i in range(len(Q_redus)):
                        if i != p:
                            Q_nou.append(copie_vector(Q_redus[i]))
                            idx_linii_noi.append(idx_linii[i])
                    Q_redus = Q_nou
                    idx_linii = idx_linii_noi
                    print('Matricea jocului dupa reducerea curenta:')
                    afisare_matrice_float(Q_redus, 3)
                    print('Liniile pastrate din jocul initial: ', end='')
                    afisare_indecsi_pastrati(idx_linii, 'A')
                    print('Coloanele pastrate din jocul initial: ', end='')
                    afisare_indecsi_pastrati(idx_coloane, 'B')
                    print()
                    pas = pas + 1
                    modificat = True
                    break

        if modificat:
            continue

        # RB - reducere coloane
        for p in range(len(Q_redus[0])):
            if modificat:
                break
            for k in range(len(Q_redus[0])):
                if k == p:
                    continue
                if coloana_domina(Q_redus, k, p):
                    jurnal.append(("coloana", idx_coloane[k], idx_coloane[p]))
                    print(f"* Reducerea #{pas}: RB (reducere de coloane)")
                    print(f"Coloana C{k + 1} din jocul curent domina coloana C{p + 1} din jocul curent.")
                    print(f"Adica strategia B{idx_coloane[k] + 1} domina strategia B{idx_coloane[p] + 1} din jocul initial.")
                    print(f"==> Se elimina coloana dominata: C{p + 1} (coresp. B{idx_coloane[p] + 1}).")
                    print()
                    Q_nou = []
                    for i in range(len(Q_redus)):
                        linie = []
                        for j in range(len(Q_redus[0])):
                            if j != p:
                                linie.append(Q_redus[i][j])
                        Q_nou.append(linie)
                    idx_coloane_noi = []
                    for j in range(len(idx_coloane)):
                        if j != p:
                            idx_coloane_noi.append(idx_coloane[j])
                    Q_redus = Q_nou
                    idx_coloane = idx_coloane_noi
                    print('Matricea jocului dupa reducerea curenta:')
                    afisare_matrice_float(Q_redus, 3)
                    print('Liniile pastrate din jocul initial: ', end='')
                    afisare_indecsi_pastrati(idx_linii, 'A')
                    print('Coloanele pastrate din jocul initial: ', end='')
                    afisare_indecsi_pastrati(idx_coloane, 'B')
                    print()
                    pas = pas + 1
                    modificat = True
                    break

    if len(jurnal) == 0:
        print('Obs: Nu s-au gasit strategii pure dominate care sa permita reducerea jocului.')
    else:
        print('Obs: Nu se mai pot face alte reduceri prin strategiile pure dominate.')
    print()
    print('Matricea redusa finala:')
    afisare_matrice_float(Q_redus, 3)
    print('Liniile pastrate din jocul initial: ', end='')
    afisare_indecsi_pastrati(idx_linii, 'A')
    print('Coloanele pastrate din jocul initial: ', end='')
    afisare_indecsi_pastrati(idx_coloane, 'B')
    print()

    return Q_redus, idx_linii, idx_coloane, jurnal
def rezolva_JM2PSN_prin_PLB_ASP(Q):
    print()
    print("----------------------------------------------------------")
    print("Rezolvare JM2PSN prin PLB (MAX) + ASP")
    print("----------------------------------------------------------")
    print()

    print("Matricea jocului Q:")
    afisare_matrice_float(Q, 3)
    print()

    # Pasul 1. Calcul alpha, beta, v1, v2

    print("Pasul 1. Calcul valori alpha_i, beta_j, v1, v2")
    print("-----------------------------------------------")
    print()

    alpha, beta, v1, v2 = calculeaza_alpha_beta(Q)

    print("alpha = min pe linii:")
    afisare_vector_float(alpha, 3)
    print("beta = max pe coloane:")
    afisare_vector_float(beta, 3)
    print(f"v1 = max(alpha) = {round(v1, 6)}")
    print(f"v2 = min(beta)  = {round(v2, 6)}")
    print()

    if aproape_egal(v1, v2):
        print("Obs: Jocul are punct sa (punct de echilibru in strategii pure)")
        print()
        puncte = puncte_sa(Q, alpha, beta, v1)
        if len(puncte) == 0:
            puncte = [(alpha.index(v1), beta.index(v2))]

        x_opt = []
        for i in range(len(Q)):
            x_opt.append(0.0)
        y_opt = []
        for j in range(len(Q[0])):
            y_opt.append(0.0)

        i0, j0 = puncte[0]
        x_opt[i0] = 1.0
        y_opt[j0] = 1.0

        print(f"Alegeam un punct sa, de exemplu: ({i0 + 1}, {j0 + 1})")
        print(f"Valoarea jocului: V = {round(v1, 6)}")
        print("Strategia optima a lui A:")
        afisare_vector_float(x_opt, 6)
        print("Strategia optima a lui B:")
        afisare_vector_float(y_opt, 6)
        print()

        return {
            "status": "punct_sa",
            "message": "Joc cu punct sa.",
            "alpha": alpha,
            "beta": beta,
            "v1": v1,
            "v2": v2,
            "V": v1,
            "K": 0.0,
            "Q_shift": copie_matrice(Q),
            "Q_redus": copie_matrice(Q),
            "idx_linii_pastrate": [i for i in range(len(Q))],
            "idx_coloane_pastrate": [j for j in range(len(Q[0]))],
            "y_B": y_opt,
            "x_A": x_opt,
            "x_opt": x_opt,
            "y_opt": y_opt,
            "plb": None,
            "puncte_sa": puncte,
            "col_payoffs": produs_vector_matrice(x_opt, Q),
            "row_payoffs": produs_matrice_vector(Q, y_opt),
            "bilinear": produs_bilinear(x_opt, Q, y_opt)
        }

    print("Obs: Jocul NU are punct sa. Se foloseste modelarea prin PL.")
    print()

    # Etapa suplimentara. Reducere de linii si coloane dominate

    Q_redus, idx_linii_pastrate, idx_coloane_pastrate, jurnal_reduceri = reduce_strategii_dominante_didactic(Q)

    print("Verificare suplimentara dupa reducere")
    print("-------------------------------------")
    print()

    alpha_red, beta_red, v1_red, v2_red = calculeaza_alpha_beta(Q_redus)

    print("alpha_redus = min pe linii:")
    afisare_vector_float(alpha_red, 3)
    print("beta_redus = max pe coloane:")
    afisare_vector_float(beta_red, 3)
    print(f"v1_redus = max(alpha_redus) = {round(v1_red, 6)}")
    print(f"v2_redus = min(beta_redus)  = {round(v2_red, 6)}")
    print()

    if aproape_egal(v1_red, v2_red):
        print("Obs: Jocul redus are punct sa (punct de echilibru in strategii pure)")
        print()
        puncte_red = puncte_sa(Q_redus, alpha_red, beta_red, v1_red)
        if len(puncte_red) == 0:
            puncte_red = [(alpha_red.index(v1_red), beta_red.index(v2_red))]

        x_opt_red = []
        for i in range(len(Q_redus)):
            x_opt_red.append(0.0)
        y_opt_red = []
        for j in range(len(Q_redus[0])):
            y_opt_red.append(0.0)

        i0, j0 = puncte_red[0]
        x_opt_red[i0] = 1.0
        y_opt_red[j0] = 1.0

        x_opt = reconstruieste_strategie(x_opt_red, idx_linii_pastrate, len(Q))
        y_opt = reconstruieste_strategie(y_opt_red, idx_coloane_pastrate, len(Q[0]))

        print(f"Alegeam un punct sa in jocul redus, de exemplu: ({i0 + 1}, {j0 + 1})")
        print(f"Valoarea jocului: V = {round(v1_red, 6)}")
        print("Strategia optima a lui A in jocul redus:")
        afisare_vector_float(x_opt_red, 6)
        print("Strategia optima a lui B in jocul redus:")
        afisare_vector_float(y_opt_red, 6)
        print()
        print("Strategia optima a lui A in jocul initial (cu 0 pe strategiile eliminate):")
        afisare_vector_float(x_opt, 6)
        print("Strategia optima a lui B in jocul initial (cu 0 pe strategiile eliminate):")
        afisare_vector_float(y_opt, 6)
        print()

        return {
            "status": "punct_sa",
            "message": "Joc redus la un joc cu punct sa.",
            "alpha": alpha,
            "beta": beta,
            "v1": v1,
            "v2": v2,
            "alpha_red": alpha_red,
            "beta_red": beta_red,
            "v1_red": v1_red,
            "v2_red": v2_red,
            "V": v1_red,
            "K": 0.0,
            "Q_shift": copie_matrice(Q_redus),
            "Q_redus": copie_matrice(Q_redus),
            "idx_linii_pastrate": copie_vector(idx_linii_pastrate),
            "idx_coloane_pastrate": copie_vector(idx_coloane_pastrate),
            "jurnal_reduceri": jurnal_reduceri,
            "y_B": y_opt_red,
            "x_A": x_opt_red,
            "x_opt": x_opt,
            "y_opt": y_opt,
            "plb": None,
            "puncte_sa": puncte_red,
            "col_payoffs": produs_vector_matrice(x_opt, Q),
            "row_payoffs": produs_matrice_vector(Q, y_opt),
            "bilinear": produs_bilinear(x_opt, Q, y_opt)
        }

    print("Obs: In continuare, pasii deja existenti ai programului se aplica pe jocul redus.")
    print("Strategiile eliminate vor primi probabilitatea 0 in jocul initial.")
    print()

    Q_lucru = copie_matrice(Q_redus)

    # Pasul 2. Daca e necesar, translatare la matrice strict pozitiva

    print("Pasul 2. Trecere la matrice strict pozitiva (daca este necesar)")
    print("--------------------------------------------------------------")
    print()

    Q1, K = translatare_matrice_pozitiva(Q_lucru)
    if K > 0:
        print(f"S-a aplicat translatarea: Q1 = Q + {K}")
        print("Matricea noua Q1:")
        afisare_matrice_float(Q1, 3)
        print()
    else:
        print("Nu este necesara translatarea; toate elementele sunt deja strict pozitive.")
        print()

    # Pasul 3. Construire PLB

    print("Pasul 3. Construire PLB")
    print("-----------------------")
    print()

    c, A, b, tip = construieste_PLB_din_joc(Q1)

    print("PLB asociata jocului este:")
    print("   max g(y) = y1 + y2 + ... + yn")
    print("   cu restrictiile: Q1 * y <= 1, y >= 0")
    print()
    print("Coeficientii functiei obiectiv:")
    afisare_vector_float(c, 3)
    print("Matricea A a restrictiilor:")
    afisare_matrice_float(A, 3)
    print("Vectorul b:")
    afisare_vector_float(b, 3)
    print()

    # Pasul 4. Rezolvare PLB prin ASP

    print("Pasul 4. Rezolvare PLB prin ASP")
    print("-------------------------------")
    rezultat_plb = rezolva_PL_cu_ASP("max", c, A, b, tip, cauta_solutii_multiple=False)

    if rezultat_plb["status"] != "optim":
        print("PLB nu a putut fi rezolvata pana la o solutie optima finita.")
        return {
            "status": rezultat_plb["status"],
            "message": rezultat_plb["message"],
            "alpha": alpha,
            "beta": beta,
            "v1": v1,
            "v2": v2,
            "alpha_red": alpha_red,
            "beta_red": beta_red,
            "v1_red": v1_red,
            "v2_red": v2_red,
            "V": None,
            "K": K,
            "Q_shift": Q1,
            "Q_redus": Q_redus,
            "idx_linii_pastrate": idx_linii_pastrate,
            "idx_coloane_pastrate": idx_coloane_pastrate,
            "jurnal_reduceri": jurnal_reduceri,
            "y_B": None,
            "x_A": None,
            "x_opt": None,
            "y_opt": None,
            "plb": rezultat_plb,
            "puncte_sa": [],
            "col_payoffs": None,
            "row_payoffs": None,
            "bilinear": None
        }

    # Pasul 5. Extragere solutii auxiliare x_A, y_B si valoarea V

    print("Pasul 5. Extragere solutiilor auxiliare PLA/PLB si a valorii jocului")
    print("-------------------------------------------------------------------")
    print()

    y_B = copie_vector(rezultat_plb["x"])
    x_A = extrage_solutia_PLA_din_TS_final_PLB(rezultat_plb)

    g_max = rezultat_plb["obiectiv"]
    if aproape_zero(g_max):
        raise ZeroDivisionError("g_max este 0; nu se poate calcula valoarea jocului.")

    V1 = 1.0 / g_max          # valoarea jocului translatat
    V = V1 - K                # valoarea jocului initial

    x_opt_red = []
    for i in range(len(x_A)):
        x_opt_red.append(V1 * x_A[i])

    y_opt_red = []
    for j in range(len(y_B)):
        y_opt_red.append(V1 * y_B[j])

    x_opt_red = normalizeaza_strategie(curata_vector(x_opt_red))
    y_opt_red = normalizeaza_strategie(curata_vector(y_opt_red))

    x_opt = reconstruieste_strategie(x_opt_red, idx_linii_pastrate, len(Q))
    y_opt = reconstruieste_strategie(y_opt_red, idx_coloane_pastrate, len(Q[0]))

    print("Solutia auxiliara PLB:")
    print("y_B = ", end='')
    afisare_vector_float(y_B, 6)
    print(f"g_max = {round(g_max, 10)}")
    print()

    print("Solutia auxiliara PLA extrasa din TS final al lui PLB:")
    print("x_A = ", end='')
    afisare_vector_float(x_A, 6)
    print()

    print(f"Valoarea jocului translatat: V1 = 1 / g_max = {round(V1, 10)}")
    if K > 0:
        print(f"Valoarea jocului initial:   V = V1 - K = {round(V, 10)}")
    else:
        print(f"Valoarea jocului initial:   V = {round(V, 10)}")
    print()

    print("Strategiile mixte optime in jocul redus:")
    print("x_opt_red = V1 * x_A = ", end='')
    afisare_vector_float(x_opt_red, 6)
    print("y_opt_red = V1 * y_B = ", end='')
    afisare_vector_float(y_opt_red, 6)
    print()

    print("Strategiile mixte optime ale jocului initial:")
    print("x_opt = V1 * x_A = ", end='')
    afisare_vector_float(x_opt, 6)
    print("y_opt = V1 * y_B = ", end='')
    afisare_vector_float(y_opt, 6)
    print()

    # Pasul 6. Verificare

    print("Pasul 6. Verificare solutie joc")
    print("-------------------------------")
    print()

    col_payoffs = produs_vector_matrice(x_opt, Q)
    row_payoffs = produs_matrice_vector(Q, y_opt)
    bilinear = produs_bilinear(x_opt, Q, y_opt)

    print("Verificare sume probabilitati:")
    print(f"sum(x_opt) = {round(sum(x_opt), 10)}")
    print(f"sum(y_opt) = {round(sum(y_opt), 10)}")
    print()

    print(f"Verificare biliniara: x_opt * Q * y_opt = {round(bilinear, 10)}")
    print(f"Valoarea jocului V = {round(V, 10)}")
    print()

    return {
        "status": "optim",
        "message": "Joc rezolvat prin PLB + ASP.",
        "alpha": alpha,
        "beta": beta,
        "v1": v1,
        "v2": v2,
        "alpha_red": alpha_red,
        "beta_red": beta_red,
        "v1_red": v1_red,
        "v2_red": v2_red,
        "V": V,
        "V1": V1,
        "K": K,
        "Q_shift": Q1,
        "Q_redus": Q_redus,
        "idx_linii_pastrate": idx_linii_pastrate,
        "idx_coloane_pastrate": idx_coloane_pastrate,
        "jurnal_reduceri": jurnal_reduceri,
        "y_B": y_B,
        "x_A": x_A,
        "x_opt_red": x_opt_red,
        "y_opt_red": y_opt_red,
        "x_opt": x_opt,
        "y_opt": y_opt,
        "plb": rezultat_plb,
        "puncte_sa": [],
        "col_payoffs": col_payoffs,
        "row_payoffs": row_payoffs,
        "bilinear": bilinear
    }


# -----------------------------------------------------------------------------
# Program principal - citire joc matricial si rezolvare JM2PSN
# -----------------------------------------------------------------------------

def main():
    print()
    print("----------------------------------------------------------")
    print("Definire joc matricial de 2 persoane cu suma nula")
    print("Rezolvare prin PLB (MAX) si ASP")
    print("----------------------------------------------------------")
    print()

    m = int(input("Numar strategii pure ale jucatorului A (numar linii)? m = "))
    print()
    n = int(input("Numar strategii pure ale jucatorului B (numar coloane)? n = "))
    print()

    Q = []
    print("Introducere elemente matrice Q (castigurile lui A):")
    for i in range(m):
        linie = []
        print(f"Linia {i + 1}:")
        for j in range(n):
            linie.append(float(input(f"   q[{i + 1}][{j + 1}] = ")))
        Q.append(linie)
        print()

    rezultat = rezolva_JM2PSN_prin_PLB_ASP(Q)

    print("----------------------------------------------------------")
    print("Rezumat final")
    print("----------------------------------------------------------")
    print()
    print(f"Status: {rezultat['status']}")
    print(f"Mesaj : {rezultat['message']}")
    print()

    if rezultat["status"] in ["optim", "punct_sa"]:
        print("Strategia optima a lui A:")
        afisare_vector_float(rezultat["x_opt"], 6)
        print("Strategia optima a lui B:")
        afisare_vector_float(rezultat["y_opt"], 6)
        print(f"Valoarea jocului V = {round(rezultat['V'], 10)}")
        print()

    return


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()

# -----------------------------------------------------------------------------
