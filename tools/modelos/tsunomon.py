"""Tsunomon: bolinha peluda laranja em cima e creme na cara/barriga, um chifre preto e olhos vermelhos."""
from comum import *

m = Modelo("tsunomon", densidade=2)
m.material("pelo", rampa_manual("#8A3A0A", "#B85412", "#E0761C", "#F59A2C", "#FFBC48", "#FFD670", base=3),
           estilo="limpo", ruido=0.3)
m.material("creme", rampa_manual("#C9B8A0", "#E6D8C2", "#F6EEDF", "#FFFAF0", "#FFFFFF", base=3),
           estilo="limpo", ruido=0.15)
m.material("chifre", rampa_manual("#0E0E12", "#1E1E24", "#34343C", "#55555F", "#8A8A96", base=2),
           estilo="liso", aresta_clara=0.8)
m.material("boca", rampa_manual("#5A1010", "#8A2A2A", "#D0606A", base=1), estilo="liso", volume=0,
           aresta_clara=0, aresta_escura=0)
CORES = {"k": "#2A0606", "r": "#B01818", "R": "#E8403A", "W": "#FFFFFF", "P": "#160202"}
OLHO = """
.kkkk.
kRRWrk
kRPPrk
kRrrrk
.kkkk.
"""
BOCA = """
.b..b.
..bb..
"""


def cara_creme(c):
    """Creme na cara (frente, abaixo da linha dos olhos, em "V") e embaixo; laranja no resto."""
    frente = (c.z < -2.5) & (c.y < 4.25 + np.abs(c.x) * 0.2) & (np.abs(c.x) < 4.6)
    return frente | (c.y < 1.1)


root = m.osso("root")
corpo = m.osso("body", pivo=[0, 0, 0], pai="root")
pintura = [base("pelo"), onde(cara_creme, mat="creme"), gradiente(1, 0, 8, -0.5, 0.4)]
corpo.cubo_arredondado([-5, 0, -4.5], [10, 7.5, 9], pintura
                       + olhos_frente(OLHO, CORES, 2.5, 4.5, -4.5, profundidade=2)
                       + [decalque(BOCA, {"b": "boca"}, centro=[0, 2.5, -4.5], profundidade=2)], raio=1.5)
corpo.cubo_arredondado([-4, 7, -3.5], [8, 1.5, 7], [base("pelo"), gradiente(1, 7, 8.5, 0, 0.5)], raio=1)
# tufos de pelo nas bochechas (planos recortados apontando para fora)
for lado in (1, -1):
    x = 5 if lado > 0 else -6.5
    corpo.plano([x, 1.5, -2.5], [1.5, 2.5, 0], [base("creme"), afinar("+x" if lado > 0 else "-x", largura_ponta=0.2)])
    corpo.plano([x, 2, 0.5], [1.5, 2, 0], [base("pelo"), afinar("+x" if lado > 0 else "-x", largura_ponta=0.2)])
# chifre preto, levemente para trás
chifre = m.osso("horn", pivo=[0, 8, 0], pai="body", rotacao=[-12, 0, 0])
cone_empilhado(chifre, [0, 8, 0], [(3, 1.5, 3), (2.5, 1.5, 2.5), (2, 2, 2), (1.5, 2, 1.5), (1, 2, 1),
                                   (0.5, 1.5, 0.5)],
               [base("chifre"), gradiente(1, 8, 18.5, -0.5, 1.2)])

anims = bolinha()
anims["idle"]["bones"]["horn"] = {"rotation": onda(4, 1.6, eixo=2)}
anims["attack"]["bones"]["horn"] = {"rotation": chaves({0: [0, 0, 0], 0.15: [-25, 0, 0], 0.3: [20, 0, 0], 0.4: [0, 0, 0]}, True)}
for nome, a in anims.items():
    m.animacao(nome, a["animation_length"], a["bones"], a["loop"])

if __name__ == "__main__":
    finalizar(m, refs=("Tunomon_Model_DSR.png", "Tunomon.jpg"), zoom=None)
