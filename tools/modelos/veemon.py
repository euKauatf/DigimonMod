"""
Veemon (V-mon): o rookie da linha do DemiVeemon. Medido nos modelos oficiais (SC, New Century, DSR) e
na folha de lineart do Adventure 02 / Digimon Zero-2.

Traços que identificam:
  1. cabeça grande azul (~38% da altura), com "V" AMARELO na testa e risquinho amarelo no canto de
     fora de cada olho
  2. olhos grandes vermelho-escuros com pupila preta e dois brilhos
  3. focinho BRANCO largo (mandíbula e bochechas) com boca em zigue-zague e duas presinhas;
     um chifrinho branco no nariz
  4. duas orelhas grandes que sobem do topo e dobram para trás e para fora, com pontas serrilhadas
     atrás da cabeça
  5. corpo fino em pera com barriga BRANCA comprida; braços finos e COMPRIDOS (mão abaixo do quadril)
     com 3 garras brancas
  6. pernas de lagarto: coxa para a frente, calcanhar para trás, pés grandes com 3 garras brancas
  7. cauda azul média com espinhos nas costas
Medidas (H = 24 até o topo da cabeça, sem orelhas).
"""
from comum import *

m = Modelo("veemon", densidade=2)
m.material("azul", rampa_manual("#0C4A80", "#1462A2", "#1C7EC4", "#2C98DC", "#4EB0EC", "#7EC8F4", base=3),
           estilo="limpo", ruido=0.06)
m.material("branco", rampa_manual("#B8BCCC", "#D6DAE6", "#ECEFF5", "#F8FAFD", "#FFFFFF", base=4),
           estilo="limpo", ruido=0.0, volume=0.25)
m.material("garra", rampa_manual("#A8A4B0", "#CCC8D2", "#E8E6EC", "#FAF8FC", "#FFFFFF", base=3), estilo="liso",
           aresta_clara=0.3, volume=0.25)
m.material("amarelo", rampa_manual("#8A6A08", "#B88E10", "#D8AE1C", "#F0CA34", base=2), estilo="liso", volume=0)

CORES_OLHO = {"k": "#20060E", "r": "#7E1428", "R": "#D23A52", "P": "#1A0408", "W": "#FFFFFF", "w": "#F6B4C2"}
OLHO = """
.kkkk.
kWWrrk
kWPPrk
kPPPRk
kPPPRk
krPRwk
krRRRk
.kkkk.
"""
V = """
yy......yy
.yy....yy.
..yy..yy..
...yyyy...
....yy....
"""
BOCA = """
b..............b
.b..b..bb..b..b.
..bb.bb..bb.bb..
"""

root = m.osso("root")
corpo = m.osso("body", pivo=[0, 9, 0.5], pai="root")
cab = m.osso("head", pivo=[0, 15, -0.5], pai="body")

# ----------------------------------------------------------------------------- tronco (pera, barriga branca comprida)
barriga = onde(e_(lambda c: c.n[2] < -0.4, lambda c: np.abs(c.x) < 2.9 - np.clip(c.y - 13.5, 0, None) * 0.4),
               mat="branco")
corpo.cubo_arredondado([-4, 6.5, -3], [8, 6.5, 6.5], [base("azul"), barriga], raio=2, arestas="verticais")
corpo.cubo_arredondado([-3.5, 12.5, -2.75], [7, 3.5, 5.5], [base("azul"), barriga], raio=1.5, arestas="verticais")
corpo.segmento([0, 15, 0], [0, 17, -0.5], 5, 4.5, [base("azul"), onde(lambda c: c.n[2] < -0.4, mat="branco")],
               sobra=1)                                                                  # pescoço

# ----------------------------------------------------------------------------- cabeça
# Cabeça grande e arredondada. Olhos GRANDES e redondos (vermelho com pupila e 2 brilhos); "V" amarelo
# pequeno ACIMA dos olhos (sem cobrir); a parte de baixo da frente é branca (focinho) e sai só um pouco,
# com a boca em zigue-zague; chifrinho branco no nariz.
OLHO = """
..kkkkk..
.kRRRRRk.
kRWWRRRRk
kRWWPPRRk
kRRPPPPRk
kRRPPPPRk
kRRPPPWRk
.kRRRRRk.
..kkkkk..
"""      # brilho grande em cima à esquerda nos DOIS olhos (como no desenho), sem pálpebra grossa
V = """
yy....yy
.yy..yy.
..yyyy..
...yy...
"""
olhos_v = olhos_frente(OLHO, CORES_OLHO, 2.5, 20.75, -5.5, profundidade=0.4, espelhar=False)
marcas = [decalque(V, {"y": "amarelo"}, centro=[0, 24, -5.5], profundidade=0.4)]
for lado in (1, -1):
    marcas.append(decalque("..y\n.yy\nyy.", {"y": "amarelo"}, centro=[5.5 * lado, 19.5, -3.5], direcao=(lado, 0, 0),
                           profundidade=0.4))
branco_frente = onde(e_(lambda c: c.n[2] < -0.5, abaixo(18.25), lambda c: np.abs(c.x) < 4.5 - np.clip(c.y - 17, 0, None)),
                     mat="branco")
# raio pequeno: a frente lisa precisa ser larga para os olhos grandes caberem inteiros (decalque não pinta a quina)
cab.cubo_arredondado([-5.5, 15.5, -5.5], [11, 10, 10], [base("azul"), branco_frente] + olhos_v + marcas,
                     raio=1, arestas="verticais")
cab.cubo_arredondado([-4.5, 25.5, -4.5], [9, 1, 8], [base("azul")], raio=2, arestas="verticais")      # topo
BOCA = """
b................b
.bb..bb....bb..bb.
...bb..bbbb..bb...
"""
cab.cubo_arredondado([-4, 15.5, -6.5], [8, 2.5, 1.5], [base("branco"),
                     decalque(BOCA, {"b": "#2A1A30"}, centro=[0, 16.5, -6.5], profundidade=0.4)],
                     raio=0.5, arestas="verticais")                                      # focinho (sai pouco)
cab.cubo([-0.75, 18, -6.5], [1.5, 1.5, 1.5], [base("garra"), afinar("+y", largura_ponta=0.1)])          # chifrinho
for lado in (1, -1):                                                                    # presinhas
    cab.plano([2.25 * lado - 0.5, 14.75, -6.05], [1, 1, 0], [base("garra"), afinar("-y", largura_ponta=0.0)])
# ORELHAS em lâmina larga: das quinas do topo sobem um pouco e varrem para trás; a ponta sobe num gancho
for lado in (1, -1):
    pts = [[3.75 * lado, 24.5, 0], [4.5 * lado, 26, 2], [5 * lado, 26, 6.5], [5.25 * lado, 28, 10]]
    cab.cadeia(pts, [(4, 2), (4, 1.5), (3, 1)], [base("azul"), gradiente(1, 24, 29.5, -0.2, 0.6)], sobra=0.75)
# nuca serrilhada: três espinhos para trás
for k, y in enumerate((16.5, 19, 21.5)):
    cab.segmento([0, y, 3.5], [0, y + 0.75, 6.5 - k * 0.5], 6 - k, 1.5, [base("azul"),
                 afinar("+y", largura_ponta=0.2, curva=1.2)], sobra=0.5)


# ----------------------------------------------------------------------------- braços compridos, mãos grandes
def braco(nome, lado):
    om = [4 * lado, 15, -0.5]
    co = [6.5 * lado, 11.5, -0.5]
    pu = [8 * lado, 7.5, -1.5]
    b = m.osso(nome, pivo=om, pai="body")
    junta(b, om, [3, 3, 3], [base("azul")], raio=0.75)
    b.segmento(om, co, 2.5, 2.5, [base("azul")], sobra=1)
    junta(b, co, [2.5, 2.5, 2.5], [base("azul")], raio=0.5)
    b.segmento(co, pu, 2.5, 2.5, [base("azul")], sobra=1)
    b.cubo_arredondado([pu[0] - 1.75, pu[1] - 3, pu[2] - 1.75], [3.5, 3.5, 3.5], [base("azul")], raio=1)  # mão
    for k in (-1, 0, 1):
        x = pu[0] + k * 1.1
        b.cubo([x - 0.5, pu[1] - 4.5, pu[2] - 1.25], [1, 1.5, 1], [base("garra"), afinar("-y", largura_ponta=0.1)])


braco("arm_left", 1)
braco("arm_right", -1)


# ----------------------------------------------------------------------------- pernas grossas, pés grandes
def perna(nome, lado):
    qu = [2.75 * lado, 7.5, 0.5]
    jo = [3.75 * lado, 4.5, -1.5]
    ca = [4.25 * lado, 2, 0.5]
    p = m.osso(nome, pivo=qu, pai="root")
    p.segmento(qu, jo, 4.5, 5, [base("azul")], raio=1.5, sobra=1.5)
    junta(p, jo, [3.5, 3.5, 3.5], [base("azul")], raio=1)
    p.segmento(jo, ca, 3, 3, [base("azul")], sobra=1)
    p.cubo_arredondado([ca[0] - 2.5, 0, -4.5], [5, 2.5, 7], [base("azul"), gradiente(1, 0, 2.5, -0.5, 0.3)],
                       raio=1, arestas="verticais")
    for k in (-1, 0, 1):
        x = ca[0] + k * 1.6
        p.cubo([x - 0.75, 0, -6.5], [1.5, 2, 2], [base("garra"), afinar("-z", largura_ponta=0.0, apoio="y")])


perna("leg_left", 1)
perna("leg_right", -1)

# ----------------------------------------------------------------------------- cauda com espinhos
cauda = m.osso("tail", pivo=[0, 8.5, 2.5], pai="body")
cauda.segmento([0, 8.5, 1.5], [0, 6, 7], 3.5, 3, [base("azul")], raio=1, sobra=1)
ponta = m.osso("tail_tip", pivo=[0, 6, 7], pai="tail")
ponta.segmento([0, 6, 7], [0, 7, 12], 2.5, 2, [base("azul")], sobra=0.75)
ponta.segmento([0, 7, 12], [0, 8, 14], 1.5, 1, [base("azul")], sobra=0.5)
for y, z in ((9, 4), (7.75, 6.5), (6.75, 9.5)):
    (cauda if z < 7 else ponta).segmento([0, y, z], [0, y + 1.75, z + 1], 0.5, 1.5,
                                          [base("azul"), afinar("+y", largura_ponta=0.1)])

anims = bipede(peso=0.9)
anims["idle"]["bones"]["tail_tip"] = {"rotation": onda(6, 2.16, eixo=1, fase=60)}
anims["walk"]["bones"]["tail_tip"] = {"rotation": onda(10, 0.81, eixo=1, fase=150)}
for nome, an in anims.items():
    m.animacao(nome, an["animation_length"], an["bones"], an["loop"])

if __name__ == "__main__":
    finalizar(m, refs=("V-mon_Model_SC.png", "V-mon_model_new_century.png", "V-mon_Model_DSR.png"),
              estilo="0004_charmander")
