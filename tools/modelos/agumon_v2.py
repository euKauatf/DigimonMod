"""
Agumon v2 — refeito a partir das referências oficiais (Wikimon: modelos 3D de DSR, Encounters, SC)
com técnicas estudadas nos modelos do Cobblemon (cubos arredondados, garras recortadas, olhos que
dobram a quina da cabeça, cor chapada em manchas).

    D:\\FerramentasMinecraft\\venv\\Scripts\\python.exe tools/modelos/agumon_v2.py

Ficha (16 unidades = 1 bloco, ~1,5 bloco de altura, olhando para -Z, +X = esquerda dele):
  - cabeça grande (~40% da altura) em "pera" vista de frente: bochechas largas embaixo, crânio
    mais estreito em cima; focinho quase da largura da cabeça, mandíbula mais estreita, boca em
    linha com sorriso que sobe atrás, dentinhos brancos pendurados no lábio de cima
  - olhos verdes grandes nas quinas da frente do crânio, virados para a frente e para fora
  - corpo em pera: barriga larga embaixo (amarelo mais claro na frente), peito mais estreito
  - braços finos e compridos, mão com 3 garras brancas grandes
  - coxas grossas, pés compridos com 3 garras na frente e 1 atrás
  - cauda grossa afinando, quase tocando o chão
Cores (paleta.py no render DSR): pele #FCAE36, barriga #FFD45A, garras #F2EEF0, olho #2E9E46.
"""
import os
import sys

sys.path.insert(0, r"D:\FerramentasMinecraft\skills\modelos-minecraft\scripts")
from mcmodel import *  # noqa: E402,F403
import numpy as np  # noqa: E402

m = Modelo("agumon", densidade=2)
# rampas montadas com as cores que paleta.py tirou do render oficial (as sombras do Agumon continuam
# laranja, não puxam para marrom/roxo)
m.material("pele", rampa_manual("#9A4E14", "#BF6A1C", "#DD8222", "#F29A2A", "#FFAF30", "#FFC23C", "#FFD450",
                                base=4), estilo="limpo", ruido=0.15)
m.material("barriga", rampa_manual("#D08426", "#EEA634", "#FFC448", "#FFD65C", "#FFE57A", base=3),
           estilo="limpo", ruido=0.2)
m.material("garra", rampa_manual("#9C96A0", "#C4BEC6", "#E6E1E8", "#FAF7FA", "#FFFFFF", base=4), estilo="liso",
           aresta_clara=0.3, volume=0.25)
m.material("boca", rampa_manual("#3A1408", "#5A2414", "#7A3420", base=1), estilo="liso", volume=0,
           aresta_clara=0, aresta_escura=0)

K = "#3A2312"       # contorno marrom-escuro (preto puro fica duro demais no laranja)
CORES_OLHO = {"k": K, "g": "#2E9E46", "G": "#78D46A", "P": "#0E1A10", "W": "#FFFFFF"}
# Olho do lado +X (o esquerdo dele, que aparece à DIREITA de quem olha de frente).
# A parte da frente tem 5 colunas e termina na quina; a lateral continua com 3 colunas.
OLHO_E_FRENTE = """
.kkkk
kWWgg
kWPPg
kgPPg
kgGGg
.kkkk
"""
OLHO_E_LADO = """
kk.
ggk
Pgk
Pgk
Ggk
kk.
"""
OLHO_D_FRENTE = """
kkkk.
WWggk
WPPgk
gPPgk
gGGgk
kkkk.
"""
OLHO_D_LADO = """
.kk
kgg
kgP
kgP
kgG
.kk
"""

# ------------------------------------------------------------------------- esqueleto
root = m.osso("root")
corpo = m.osso("body", pivo=[0, 8.5, 0], pai="root")
cab = m.osso("head", pivo=[0, 16, -1], pai="body")
mand = m.osso("jaw", pivo=[0, 16.5, -3.5], pai="head")


# ------------------------------------------------------------------------- corpo (pera atarracada)
def barriga_clara():
    return onde(e_(lambda c: c.n[2] < -0.5,
                   esfera([0, 11, -4], 1.0, achatar=(3.9, 4.6, 3.0))), mat="barriga")


corpo.cubo_arredondado([-5, 7, -4], [10, 7, 7.5], [base("pele"), barriga_clara()], raio=1.5)
corpo.cubo_arredondado([-4, 13, -3.5], [8, 3.5, 6.5], [base("pele"), barriga_clara()], raio=1)

# ------------------------------------------------------------------------- cabeça (~40% da altura)
olhos = [
    decalque(OLHO_E_FRENTE, CORES_OLHO, centro=[3.25, 21.5, -5], direcao=(0, 0, -1), profundidade=0.3),
    decalque(OLHO_E_LADO, CORES_OLHO, centro=[4.5, 21.5, -4.25], direcao=(1, 0, 0), profundidade=0.3),
    decalque(OLHO_D_FRENTE, CORES_OLHO, centro=[-3.25, 21.5, -5], direcao=(0, 0, -1), profundidade=0.3),
    decalque(OLHO_D_LADO, CORES_OLHO, centro=[-4.5, 21.5, -4.25], direcao=(-1, 0, 0), profundidade=0.3),
]


def sorriso(c):
    """Linha da boca na lateral das bochechas: continua a do focinho e sobe num sorriso no fim."""
    y_linha = 16.75 + np.clip(c.z + 3.5, 0, None) * 0.5
    return (np.abs(c.y - y_linha) < 0.26) & (c.z < -1.4) & (abs(c.n[0]) > 0.5)


# cabeça em "pera" vista de frente: bochechas largas embaixo, crânio um pouco mais estreito em cima
# (com os olhos nas quinas), como nos modelos oficiais
cab.cubo_arredondado([-5, 15, -4.5], [10, 4.5, 6.5], [base("pele"), onde(sorriso, mat="boca")],
                     raio=1, arestas="verticais")
cab.cubo_arredondado([-4.5, 17, -5], [9, 7, 7], [base("pele")] + olhos, raio=1, arestas="frente")

# focinho de cima: quase da largura da cabeça e comprido; linha da boca embaixo; céu da boca
lábio = onde(e_(abaixo(17.0), faces("north", "east", "west")), mat="boca")
narinas = onde(e_(faces("up"), ou_(caixa([0.75, 19.5, -10.25], [1.5, 20.5, -9.75]),
                                    caixa([-1.5, 19.5, -10.25], [-0.75, 20.5, -9.75]))), mat="boca")
cab.cubo_arredondado([-4, 16.5, -10.5], [8, 3.5, 6], [base("pele"), lábio, narinas,
                     so_faces("down", base("boca"))], raio=0.5, arestas="frente")

# dentes: planos pendurados no lábio, para fora da mandíbula; cada um é uma presinha de 2x2 texels
# em "L" (o jeito clássico de pixel art fazer dente pequeno)
DENTE = [base("garra"), sprite("gg\ng_", {"g": "garra"})]
for lado in (1, -1):
    xd = 4.05 * lado
    for zd in (-9.75, -8, -6.25):
        cab.plano([xd, 15.5, zd], [0, 1, 1], DENTE)
    cab.plano([lado * 2 - 0.5, 15.5, -10.55], [1, 1, 0], DENTE)

# mandíbula: mais estreita e curta que o focinho; abre no ataque
mand.cubo_arredondado([-3.5, 14.5, -10], [7, 2, 6], [base("pele"), gradiente(1, 14.5, 16.5, -0.4, 0.2),
                      so_faces("up", base("boca"))], raio=0.5, arestas="frente")


# ------------------------------------------------------------------------- braços (abertos, garras grandes)
def braco(nome, lado):
    x_omb = 4 * lado
    b = m.osso(nome, pivo=[x_omb, 15, -1.5], pai="body", rotacao=[-15, 0, -12 * lado])
    xb = 4 if lado > 0 else -6
    b.cubo_arredondado([xb, 9.5, -2.5], [2, 6, 2], [base("pele")], raio=0.5, arestas="verticais")
    b.cubo_arredondado([xb - 0.5, 8, -3], [3, 2.5, 3], [base("pele")], raio=0.5)
    for k in range(3):
        b.cubo([xb - 0.5 + k * 1.0, 5, -3], [1, 3, 1.5],
               [base("garra"), afinar("-y", largura_ponta=0.3, curva=0.5, apoio="-z")],
               rotacao=[-12, 0, (k - 1) * 6 * lado], pivo=[xb + k * 1.0, 8, -2])


braco("arm_left", 1)
braco("arm_right", -1)


# ------------------------------------------------------------------------- pernas (coxas grossas, pé grande)
def perna(nome, lado):
    x0 = 0.75 if lado > 0 else -5.25
    p = m.osso(nome, pivo=[x0 + 2.25, 8, 0], pai="root")
    xc = 0.5 if lado > 0 else -5.5
    p.cubo_arredondado([xc, 2.5, -2.75], [5, 6.5, 5.5], [base("pele")], raio=1.5)              # coxa
    p.cubo_arredondado([x0 + 0.75, 0.5, -1.5], [3, 2.5, 3], [base("pele")], raio=0.5, arestas="verticais")
    p.cubo_arredondado([x0, 0, -4.5], [4.5, 1.5, 6], [base("pele"), gradiente(1, 0, 1.5, -0.5, 0.3)],
                       raio=0.5, arestas="verticais")                                      # pé
    for k in range(3):
        p.cubo([x0 + 0.25 + k * 1.5, 0, -6.5], [1, 1.5, 2],
               [base("garra"), afinar("-z", largura_ponta=0.0, curva=0.9, apoio="y")])
    p.cubo([x0 + 1.75, 0, 1.5], [1, 1, 1.5], [base("garra"), afinar("+z", curva=0.9, apoio="y")])


perna("leg_left", 1)
perna("leg_right", -1)

# ------------------------------------------------------------------------- cauda
cauda = m.osso("tail", pivo=[0, 8.5, 3], pai="body", rotacao=[-22, 0, 0])
cauda.cubo_arredondado([-2.5, 6, 2.5], [5, 5, 5], [base("pele")], raio=1, arestas="z")
ponta = m.osso("tail_tip", pivo=[0, 8.5, 7], pai="tail", rotacao=[-14, 0, 0])
ponta.cubo_arredondado([-2, 6.5, 7], [4, 4, 4.5], [base("pele")], raio=1, arestas="z")
fim = m.osso("tail_end", pivo=[0, 8.5, 11], pai="tail_tip", rotacao=[-10, 0, 0])
fim.cubo_arredondado([-1.5, 7, 11], [3, 3, 3], [base("pele")], raio=0.5, arestas="z")

# ------------------------------------------------------------------------- animações
anims = bipede(peso=0.9)
anims["idle"]["bones"]["tail_tip"] = {"rotation": onda(6, 2.16, eixo=1, fase=60)}
anims["idle"]["bones"]["jaw"] = {"rotation": chaves({0: [0, 0, 0], 1.6: [0, 0, 0], 1.8: [6, 0, 0], 2.16: [0, 0, 0]}, True)}
anims["walk"]["bones"]["tail_tip"] = {"rotation": onda(10, 0.81, eixo=1, fase=150)}
anims["walk"]["bones"]["tail_end"] = {"rotation": onda(8, 0.81, eixo=1, fase=210)}
anims["attack"]["bones"]["jaw"] = {"rotation": chaves({0: [0, 0, 0], 0.15: [30, 0, 0], 0.35: [30, 0, 0], 0.45: [0, 0, 0]}, True)}
for nome, a in anims.items():
    m.animacao(nome, a["animation_length"], a["bones"], a["loop"])

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from comum import finalizar
    finalizar(m, refs=("Agumon_Model_SC.png", "Agumon_Model_DSR.png"), estilo="0004_charmander")
