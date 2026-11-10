"""
Gotsumon: boneco de PEDRA cinza feito de blocos (combina muito com o Minecraft). Cabeça grande quadrada com
uma orelha/chifre de pedra de cada lado, olhos amarelos com pupila, boca larga em zigue-zague, corpo de
blocos empilhados, braços e pernas finos de pedra.
Refs: Gottsumon_Model_DSR / Encounters. Mesmo método aprovado.
"""
from comum import *

m = Modelo("gotsumon", densidade=2)
m.material("pedra", rampa_manual("#3E4146", "#555960", "#6E737A", "#8A8F96", "#A6ABB1", "#C4C8CC", base=3),
           estilo="limpo", ruido=0.1)
m.material("rachadura", rampa_manual("#16181C", "#24272C", "#33373D", base=1), estilo="liso", volume=0,
           aresta_clara=0, aresta_escura=0)
m.material("boca", rampa_manual("#0E0E12", "#18181E", "#24242C", base=1), estilo="liso", volume=0,
           aresta_clara=0, aresta_escura=0)

CORES_OLHO = {"k": "#14141A", "y": "#E8B820", "Y": "#FFE060", "P": "#140C04", "W": "#FFFFFF"}
OLHO = """
.kkkk.
kYYWyk
kYPPyk
kyPPyk
.kkkk.
"""
BOCA = """
bbbbbbbbbbbbbb
b..bb..bb..b.b
bbbbbbbbbbbbbb
bbbbbbbbbbbbbb
bb.bb..bb..bbb
.bbbbbbbbbbbb.
"""
# pedras: manchas grandes de tom (mais claras/mais escuras), sem pontinhos (o usuário não gosta de "spray")
juntas_pedra = onde(lambda c: fbm(c.p, 3.5, 1, semente=5) > 0.25, somar_luz=-1)


root = m.osso("root")
corpo = m.osso("body", pivo=[0, 8, 0], pai="root")
corpo.cubo_arredondado([-3, 5.5, -2.5], [6, 4.5, 5], [base("pedra"), juntas_pedra], raio=1, arestas="verticais")
corpo.cubo_arredondado([-4, 9.5, -3], [8, 4.5, 6], [base("pedra"), juntas_pedra], raio=1, arestas="verticais")
corpo.segmento([0, 13, -0.25], [0, 15, -0.5], 4, 4, [base("pedra")], sobra=1)          # pescoço

cab = m.osso("head", pivo=[0, 14.5, -0.5], pai="body")
cab.cubo_arredondado([-5, 14.5, -5], [10, 9.5, 9], [base("pedra"), juntas_pedra,
                     *olhos_frente(OLHO, CORES_OLHO, 2.5, 20.75, -5),
                     decalque(BOCA, {"b": "boca"}, centro=[0, 17, -5], profundidade=0.4)],
                     raio=1, arestas="verticais")
cab.cubo_arredondado([-5.5, 21.75, -6], [11, 1.5, 2], [base("pedra")], raio=0.5)        # sobrancelha de pedra
for lado in (1, -1):                                                                    # orelhas de pedra
    cab.cubo_arredondado([4.5 * lado - 2.5, 22.5, -1.5], [5, 5, 2.5], [base("pedra"), juntas_pedra], raio=1,
                         arestas="z", rotacao=[0, 0, 15 * lado], pivo=[4.5 * lado, 22.5, -0.25])


def braco(nome, lado):
    om = [4.5 * lado, 12.5, 0]
    co = [6 * lado, 9, -0.5]
    pu = [6.5 * lado, 5.5, -1]
    b = m.osso(nome, pivo=om, pai="body")
    junta(b, om, [3, 3, 3], [base("pedra")])
    b.segmento(om, co, 2.5, 2.5, [base("pedra")], sobra=1)
    junta(b, co, [2.5, 2.5, 2.5], [base("pedra")])
    b.segmento(co, pu, 2.5, 2.5, [base("pedra")], sobra=1)
    b.cubo([pu[0] - 1.75, pu[1] - 3, pu[2] - 1.75], [3.5, 3, 3.5], [base("pedra"), juntas_pedra])          # mão
    for k in (-1, 0, 1):
        b.cubo([pu[0] + k * 1.1 - 0.5, pu[1] - 4.5, pu[2] - 1.5], [1, 1.5, 1], [base("pedra")])


braco("arm_left", 1)
braco("arm_right", -1)


def perna(nome, lado):
    qu = [2.25 * lado, 6, 0]
    jo = [2.5 * lado, 3.5, -0.5]
    ca = [2.5 * lado, 1.5, 0]
    p = m.osso(nome, pivo=qu, pai="root")
    p.segmento(qu, jo, 3, 3, [base("pedra")], sobra=1)
    junta(p, jo, [3, 2.5, 3], [base("pedra")])
    p.segmento(jo, ca, 3, 3, [base("pedra")], sobra=1)
    p.cubo([ca[0] - 2, 0, -3.5], [4, 2, 5], [base("pedra"), juntas_pedra])                          # pé de bloco
    for k in (-1, 0, 1):
        p.cubo([ca[0] + k * 1.25 - 0.5, 0, -4.5], [1, 1, 1], [base("pedra")])


perna("leg_left", 1)
perna("leg_right", -1)

anims = bipede(peso=1.1)
for an in anims.values():
    an["bones"].pop("tail", None)
for nome, an in anims.items():
    m.animacao(nome, an["animation_length"], an["bones"], an["loop"])

if __name__ == "__main__":
    finalizar(m, refs=("Gottsumon_Model_DSR.png", "Gottsumon_Model_Encounters.png"), estilo="0004_charmander")
