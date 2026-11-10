"""Koromon: bolinha rosa, orelhas compridas que caem para trás, olhos vermelhos e sorriso com presinhas."""
from comum import *

m = Modelo("koromon", densidade=2)
m.material("pele", rampa_manual("#C2507A", "#E07098", "#F590B0", "#FFB0C8", "#FFCCDC", "#FFE4EC", base=3),
           estilo="limpo", ruido=0.15)
m.material("boca", rampa_manual("#4A0E18", "#6E1A28", "#A0303E", base=1), estilo="liso", volume=0,
           aresta_clara=0, aresta_escura=0)
m.material("dente", rampa_manual("#C9C2CC", "#F2EEF2", "#FFFFFF", base=2), estilo="liso", volume=0)
CORES = {"k": "#3A0A10", "r": "#B0101C", "R": "#E8323A", "W": "#FFFFFF", "P": "#1A0204"}
OLHO = """
.kkk.
kRWrk
kRPrk
krrrk
.kkk.
"""
BOCA = """
b............b
.bbbbbbbbbbbb.
..d........d..
..d........d..
"""

root = m.osso("root")
corpo = m.osso("body", pivo=[0, 0, 0], pai="root")
corpo.cubo_arredondado([-5.5, 0, -4.5], [11, 6, 9], [base("pele"), gradiente(1, 0, 6, -0.6, 0.5)]
                       + olhos_frente(OLHO, CORES, 3, 3.75, -4.5, profundidade=2)
                       + [decalque(BOCA, {"b": "boca", "d": "dente"}, centro=[0, 1.75, -4.5], profundidade=2)],
                       raio=1.5)
corpo.cubo_arredondado([-4.5, 5, -3.5], [9, 2, 7], [base("pele"), gradiente(1, 5, 7, 0, 0.5)], raio=1)


def orelha(nome, lado):
    x0 = 1 if lado > 0 else -2.5
    o = m.osso(nome, pivo=[x0 + 0.75, 6.5, -0.5], pai="body", rotacao=[-25, 0, 22 * lado])
    o.cubo([x0, 6, -1], [1.5, 7.5, 1], [base("pele"), gradiente(1, 6, 13.5, -0.8, -0.2)])
    p = m.osso(nome + "_tip", pivo=[x0 + 0.75, 13.5, -0.5], pai=nome, rotacao=[-40, 0, 10 * lado])
    p.cubo([x0, 13, -1], [1.5, 6, 1], [base("pele"), afinar("+y", largura_ponta=0.3, curva=1.5),
                                       gradiente(1, 13, 19, -0.2, 0.4)])


orelha("ear_left", 1)
orelha("ear_right", -1)

anims = bolinha()
anims["idle"]["bones"]["ear_left"] = {"rotation": onda(6, 1.6, eixo=0)}
anims["idle"]["bones"]["ear_right"] = {"rotation": onda(6, 1.6, eixo=0, fase=40)}
anims["walk"]["bones"]["ear_left"] = {"rotation": onda(15, 0.6, eixo=0, fase=90)}
anims["walk"]["bones"]["ear_right"] = {"rotation": onda(15, 0.6, eixo=0, fase=90)}
anims["walk"]["bones"]["ear_left_tip"] = {"rotation": onda(12, 0.6, eixo=0, fase=150)}
anims["walk"]["bones"]["ear_right_tip"] = {"rotation": onda(12, 0.6, eixo=0, fase=150)}
for nome, a in anims.items():
    m.animacao(nome, a["animation_length"], a["bones"], a["loop"])

if __name__ == "__main__":
    finalizar(m, refs=("Koromon_Model_DSR.png", "Koromon.jpg"), zoom=None)
