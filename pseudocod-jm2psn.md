# Algoritm Rezolvare Completa JM2PSN

Acest fisier este pregatit pentru GitHub astfel incat sectiunile sa poata fi legate din Word prin hyperlinkuri web.

## Algoritm rezolvare completa jm2psn

```text
ALGORITM Rezolvare_Completa_JM2PSN(Q_initial[m, n])
DESCRIERE: Calculeaza strategiile optime (X_opt, Y_opt) si valoarea jocului (v).
```

## Etapa 1 analiza strategiilor pure punct sa

```text
PENTRU i = 1 LA m:
    alpha_i[i] <- min(Q_initial[i, 1..n])

PENTRU j = 1 LA n:
    beta_j[j] <- max(Q_initial[1..m, j])

v1 <- max(alpha_i[1..m])
v2 <- min(beta_j[1..n])

DACA v1 == v2 ATUNCI
    v <- v1
    (i0, j0) <- indicii pentru care Q_initial[i0, j0] == v
    X_opt <- VectorZero(m), Y_opt <- VectorZero(n)
    X_opt[i0] <- 1, Y_opt[j0] <- 1
    RETURNEAZA (X_opt, Y_opt, v, "Solutie in strategii pure (punct sa)")
SFARSIT DACA
```

## Etapa 2 reducerea prin dominanta

```text
Q <- Copie(Q_initial)
L <- {1, 2, ..., m}, C <- {1, 2, ..., n}
MODIFICAT <- ADEVARAT

CAT TIMP MODIFICAT == ADEVARAT EXECUTA
    MODIFICAT <- FALS

    // Eliminare linii dominate (Jucatorul A vrea maximizarea castigului)
    PENTRU fiecare pereche de linii k, p ∈ L (k != p):
        DACA ∀j ∈ C: Q[k, j] >= Q[p, j] ATUNCI
            Elimina p din L; MODIFICAT <- ADEVARAT; BREAK

    // Eliminare coloane dominante (Jucatorul B vrea minimizarea pierderii)
    PENTRU fiecare pereche de coloane k, p ∈ C (k != p):
        DACA ∀i ∈ L: Q[i, k] <= Q[i, p] ATUNCI
            Elimina p din C; MODIFICAT <- ADEVARAT; BREAK
SFARSIT CAT TIMP

Q_red <- Submatrice(Q, L, C)
m_red <- Lungime(L), n_red <- Lungime(C)
```

## Etapa 3 modelare programare liniara plb

```text
K <- 0
DACA min(Q_red) <= 0 ATUNCI K <- 1 - min(Q_red)
Q_pos <- Q_red + K

// Constructie Tabel Simplex (TS) pentru problema Jucatorului B
TS <- Matrice(m_red, n_red + m_red + 1)

PENTRU i = 1 LA m_red:
    PENTRU j = 1 LA n_red:
        TS[i, j] <- Q_pos[i, j]
    TS[i, n_red + i] <- 1
    TS[i, n_red + m_red + 1] <- 1

c <- [1, 1, ..., 1, 0, 0, ..., 0]
Baza <- {n_red + 1, ..., n_red + m_red}
C_B <- [0, 0, ..., 0]
```

## Etapa 4 algoritmul simplex primal

```text
OPTIM <- FALS

CAT TIMP OPTIM == FALS EXECUTA
    // 4.1 Calcul z_j si randul diferentelor Delta_j
    PENTRU j = 1 LA (n_red + m_red):
        z_j <- 0
        PENTRU i = 1 LA m_red:
            z_j <- z_j + C_B[i] * TS[i, j]
        Delta_j[j] <- c[j] - z_j

    // 4.2 Testul de optimalitate si alegerea coloanei pivot
    q <- indexul j unde Delta_j[j] este maxim
    DACA Delta_j[q] <= EPS ATUNCI
        OPTIM <- ADEVARAT
        BREAK

    // 4.3 Alegerea liniei pivot
    p <- -1, min_raport <- INFINIT
    PENTRU i = 1 LA m_red:
        A_iq <- TS[i, q]
        DACA A_iq > EPS ATUNCI
            raport <- TS[i, n_red + m_red + 1] / A_iq
            DACA raport < min_raport ATUNCI
                min_raport <- raport
                p <- i

    DACA p == -1 ATUNCI
        RETURNEAZA "Optim infinit"

    // 4.4 Transformarea tabelului (Pivotarea Gauss-Jordan)
    Pivot <- TS[p, q]
    TS[p, :] <- TS[p, :] / Pivot

    PENTRU k = 1 LA m_red:
        DACA k != p ATUNCI
            Factor <- TS[k, q]
            TS[k, :] <- TS[k, :] - Factor * TS[p, :]

    // 4.5 Actualizare Baza
    Baza[p] <- q
    C_B[p] <- c[q]
SFARSIT CAT TIMP
```

## Etapa 5 reconstructia solutiei finale

```text
g_max <- 0
PENTRU i = 1 LA m_red:
    g_max <- g_max + C_B[i] * TS[i, n_red + m_red + 1]

V_pos <- 1 / g_max
v <- V_pos - K

// Extragere strategii mixte optime
y_aux <- VectorZero(n_red), x_aux <- VectorZero(m_red)

PENTRU i = 1 LA m_red:
    DACA Baza[i] <= n_red ATUNCI
        y_aux[Baza[i]] <- TS[i, n_red + m_red + 1]

// Solutia duala se citeste din randul diferentelor Delta_j
PENTRU j = 1 LA m_red:
    x_aux[j] <- ABS(Delta_j[n_red + j])

// Normalizare si mapare pe dimensiunile originale (m, n)
X_opt <- VectorZero(m), Y_opt <- VectorZero(n)

PENTRU i = 1 LA m_red:
    X_opt[L[i]] <- x_aux[i] * V_pos

PENTRU j = 1 LA n_red:
    Y_opt[C[j]] <- y_aux[j] * V_pos

RETURNEAZA (X_opt, Y_opt, v)
SFARSIT ALGORITM
```

## Legaturi recomandate din Word

- Analiza strategiilor pure (punctul sa) -> sectiunea **Etapa 1 analiza strategiilor pure punct sa**
- Reducerea prin dominanta -> sectiunea **Etapa 2 reducerea prin dominanta**
- Modelarea problemei de programare liniara PLB -> sectiunea **Etapa 3 modelare programare liniara plb**
- Calculul costurilor reduse (Delta_j) -> sectiunea **Etapa 4 algoritmul simplex primal**
- Testul raportului minim -> sectiunea **Etapa 4 algoritmul simplex primal**
- Regula dreptunghiului / pivotarea Gauss-Jordan -> sectiunea **Etapa 4 algoritmul simplex primal**
- Reconstructia solutiei finale / teorema ecarturilor -> sectiunea **Etapa 5 reconstructia solutiei finale**
