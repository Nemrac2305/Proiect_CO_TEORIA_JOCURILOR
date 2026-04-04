Aplicatie JM2PSN (CustomTkinter)

Scop:
- rezolvarea jocurilor matriciale de 2 persoane cu suma nula;
- interfata inspirata din simplex_app;
- solverul folosit este jm2psn_solver_didactic.

Rulare:
1. Instaleaza Python 3.11+.
2. Instaleaza dependintele:
   pip install -r requirements.txt
3. Porneste aplicatia:
   python app.py

Ce face aplicatia:
- permite definirea matricei jocului Q;
- incarca exemple rapide;
- afiseaza valoarea jocului si strategiile mixte optime;
- afiseaza logul didactic complet generat de solver;
- salveaza / incarca jocuri in format JSON;
- exporta raport text.
- permite navigarea rapida intre celulele matricei cu tastele ← → ↑ ↓ si PgUp / PgDn.

- foloseste o tema vizuala revizuita, cu contrast mai bun si accente albastre mai placute vizual.
