"""Punimon: gelatina vermelha com duas orelhas pontudas, olhos redondos de íris marrom e anteninhas."""
from comum import *

m = Modelo("punimon", densidade=2)
m.material("pele", rampa_manual("#6E0E12", "#9A1A1E", "#C42A2A", "#E04038", "#F2634E", "#FF8A6E", base=3),
           estilo="limpo", ruido=0.15, aresta_clara=0.5)
CORES = {"k": "#1E0606", "w": "#FFFFFF", "g": "#D8D2D2", "b": "#7A3A1E", "B": "#A8582E", "P": "#140404"}
OLHO = """
.kkkk.
kwwwwk
kwbBwk
kwbPwk
kwggwk
.kkkk.
"""

root = m.osso("root")
corpo = m.osso("body", pivo=[0, 0, 0], pai="root")
corpo.cubo_arredondado([-5, 0, -4.5], [10, 6.5, 9], [base("pele"), gradiente(1, 0, 6.5, -0.6, 0.5)]
                       + olhos_frente(OLHO, CORES, 2.5, 3.5, -4.5, profundidade=2), raio=1.5)
corpo.cubo_arredondado([-4, 5.5, -3.5], [8, 2, 7], [base("pele"), gradiente(1, 5.5, 7.5, 0, 0.5)], raio=1)
# orelhas pontudas nas quinas de cima, inclinadas para fora (a esquerda dele um pouco maior)
for lado, extra in ((1, 0.5), (-1, 0)):
    camadas = [(4, 1.5, 3.5), (3, 1.5 + extra, 2.5), (1.5, 1.5, 1.5)]
    cone_empilhado(corpo, [3 * lado, 6, -0.5], camadas, [base("pele"), gradiente(1, 6, 11, 0, 0.6)],
                   rotacao=[-6, 0, -18 * lado])

anims = bolinha()
anims["idle"]["bones"]["body"]["rotation"] = onda(2, 1.6, eixo=2)
for nome, a in anims.items():
    m.animacao(nome, a["animation_length"], a["bones"], a["loop"])

if __name__ == "__main__":
    finalizar(m, refs=("Punimon_Model_DSR.png", "Punimon_Model_Encounters.png"), zoom=None)
