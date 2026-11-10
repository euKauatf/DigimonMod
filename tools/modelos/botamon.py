"""Botamon: bolinha preta peluda, larga embaixo, orelhinhas de gato e olhos grandes cor de âmbar."""
from comum import *

m = Modelo("botamon", densidade=2)
m.material("pelo", rampa_manual("#09080C", "#141319", "#1F1D26", "#2C2A35", "#3E3B4A", "#55516A", base=2),
           estilo="rustico", ruido=0.35, pontilhado=0.15, aresta_clara=0.8)
CORES = {"o": "#A3440A", "y": "#F28A16", "Y": "#FFC23A", "L": "#FFE38A", "W": "#FFFFFF", "P": "#3A1604"}
OLHO = """
.oooo.
oyYLWo
oYLPYo
oyPYYo
oyyYyo
.oooo.
"""

root = m.osso("root")
corpo = m.osso("body", pivo=[0, 0, 0], pai="root")
corpo.cubo_arredondado([-5.5, 0, -4.5], [11, 6.5, 9], [base("pelo"), gradiente(1, 0, 6.5, -0.8, 0.6)]
                       + olhos_frente(OLHO, CORES, 2.5, 3.5, -4.5), raio=1.5)
corpo.cubo_arredondado([-4.5, 5, -3.5], [9, 2.5, 7], [base("pelo"), gradiente(1, 5, 7.5, 0, 0.6)], raio=1)
# orelhinhas de gato nas quinas de cima, saindo do contorno da cabeça
for lado in (1, -1):
    x0 = 1.5 if lado > 0 else -5
    corpo.cubo([x0, 6, -2], [3.5, 3, 3], [base("pelo"), afinar("+y", largura_ponta=0.25, curva=0.8,
                                                              apoio="-x" if lado > 0 else "x"),
                                          gradiente(1, 6, 9, 0, 0.7)])

anims = bolinha()
anims["idle"]["bones"]["body"]["rotation"] = onda(3, 1.6, eixo=2)
for nome, a in anims.items():
    m.animacao(nome, a["animation_length"], a["bones"], a["loop"])

if __name__ == "__main__":
    finalizar(m, refs=("Botamon_Model_DSR.png", "Botamon.jpg"), zoom=None)
