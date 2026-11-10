"""
Numemon: lesma verde (gosma) com base larga que escorre no chão, BOCA enorme cheia de dentes e língua
rosa para fora, dois olhos em antenas no alto, manchas roxas e dois bracinhos pontudos.
Refs: Numemon_newcentury_model / SC / DSR. Mesmo método aprovado (sem faces piscando, cores vivas).
Ossos que o mod usa: root, body, eyes, arm_left, arm_right.
"""
from comum import *

m = Modelo("numemon", densidade=2)
m.material("gosma", rampa_manual("#3E6A10", "#58901A", "#78B424", "#98D030", "#B4E24A", "#D0F078", base=3),
           estilo="limpo", ruido=0.12)
m.material("mancha", rampa_manual("#2A1A5A", "#3E287E", "#5238A0", "#6A4EBE", base=2), estilo="limpo")
m.material("boca", rampa_manual("#3A0814", "#5E1022", "#861C34", "#A8304A", base=1), estilo="liso", volume=0.2,
           aresta_clara=0, aresta_escura=0)
m.material("lingua", rampa_manual("#8A1240", "#B8205A", "#E03A7A", "#F86A9E", "#FF9CC0", base=2), estilo="liso")
m.material("dente", rampa_manual("#B8B4B0", "#DAD6D2", "#F2F0EC", "#FFFFFF", base=2), estilo="liso", volume=0.2)
m.material("olho", rampa_manual("#B8B4C0", "#DCD8E2", "#F4F2F8", "#FFFFFF", base=2), estilo="liso", volume=0.3)

manchas_roxas = onde(e_(lambda c: c.n[2] > -0.6, lambda c: fbm(c.p, 3.0, 1, semente=4) > 0.38), mat="mancha")

root = m.osso("root")
corpo = m.osso("body", pivo=[0, 0, 0], pai="root")
# base escorrida, larga e baixa
corpo.cubo_arredondado([-9, 0, -6], [18, 2.5, 13], [base("gosma"), manchas_roxas], raio=3, arestas="verticais")
# corpo em gota: largo embaixo, afinando para cima, com a boca enorme na frente
corpo.cubo_arredondado([-7, 2, -5], [14, 6, 11], [base("gosma"), manchas_roxas], raio=2.5, arestas="verticais")
corpo.cubo_arredondado([-6, 7.5, -4.5], [12, 5, 9.5], [base("gosma"), manchas_roxas], raio=2, arestas="verticais")
corpo.cubo_arredondado([-4.5, 12, -3.5], [9, 3, 7.5], [base("gosma"), manchas_roxas], raio=1.5)     # topo
# boca: buraco escuro (peça encostada na frente, sem plano em comum), dentes em cima e embaixo, língua
corpo.cubo([-5, 3.5, -5.25], [10, 8, 0.5], [base("boca"), gradiente(1, 3.5, 11.5, -0.8, 0.4)])
for x in (-4.5, -2.5, -0.5, 1.5, 3.5):
    corpo.cubo([x - 0.75, 10, -5.5], [1.75, 1.5, 0.5], [base("dente")])                  # dentes de cima
for x in (-3.5, -1.5, 0.5, 2.5):
    corpo.cubo([x - 0.75, 3.5, -5.5], [1.5, 1.25, 0.5], [base("dente")])                 # dentes de baixo
corpo.segmento([0.5, 5.5, -5.25], [1, 4, -7.5], 3.5, 1.5, [base("lingua")], sobra=0.5)   # língua saindo
corpo.segmento([1, 4, -7.5], [1.5, 1, -8], 3, 1.5, [base("lingua"), onde(lambda c: (np.abs(c.x - 1.2) < 0.3) &
               (c.n[2] < -0.5), mat="boca")], sobra=0.5)                                 # e caindo por cima

# olhos em antenas
olhos_o = m.osso("eyes", pivo=[0, 15, 0], pai="body")
PUPILA = """
.rrr.
rrPPr
rPPWr
rrPPr
.rrr.
"""
for lado in (1, -1):
    olhos_o.segmento([1.75 * lado, 15, 0], [2.75 * lado, 21, -0.5], 1.5, 1.5, [base("gosma")], sobra=1)
    cx = 2.75 * lado
    olhos_o.cubo_arredondado([cx - 2.5, 20.5, -2.5], [5, 5, 5], [base("olho"),
                             decalque(PUPILA, {"r": "#C02028", "P": "#140606", "W": "#FFFFFF"},
                                      centro=[cx, 22.75, -2.5], profundidade=0.4)], raio=1)


def braco(nome, lado):
    b = m.osso(nome, pivo=[6 * lado, 6, 0], pai="body")
    b.cubo_arredondado([5.5 * lado - 2, 5, -2], [4, 3.5, 4], [base("gosma")], raio=1)
    b.segmento([7 * lado, 6.75, -0.5], [11.5 * lado, 7.5, -1], 3.5, 2.5, [base("gosma")], sobra=0.5)
    b.segmento([11.5 * lado, 7.5, -1], [13.5 * lado, 8, -1], 2, 1.5, [base("gosma")], sobra=0.5)   # ponta


braco("arm_left", 1)
braco("arm_right", -1)

anims = bolinha()
anims["idle"]["bones"]["eyes"] = {"rotation": onda(5, 1.6, eixo=2)}
anims["walk"]["bones"]["eyes"] = {"rotation": onda(8, 0.6, eixo=0, fase=90)}
anims["idle"]["bones"]["arm_left"] = {"rotation": onda(8, 1.6, eixo=2)}
anims["idle"]["bones"]["arm_right"] = {"rotation": onda(8, 1.6, eixo=2, fase=180)}
for nome, an in anims.items():
    m.animacao(nome, an["animation_length"], an["bones"], an["loop"])

if __name__ == "__main__":
    finalizar(m, refs=("Numemon_newcentury_model.png", "Numemon_Model_SC.png", "Numemon_Model_DSR.png"), zoom=None,
              estilo="0004_charmander")
