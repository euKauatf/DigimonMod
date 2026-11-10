"""
Goburimon: goblin verde corcunda, cabeça grande com focinho largo e presas para cima, orelhas pontudas,
moicano vermelho, colete de couro, tanga marrom com cinto, braços compridos e porrete de madeira.
Refs: Goburimon_Model_SC / New Century / DSR. Método aprovado: esqueleto, juntas, corpo no meio-termo,
um olho por lado com pupila, dentes para fora, cores vivas e lisas, nada piscando.
"""
from comum import *

m = Modelo("goburimon", densidade=2)
m.material("pele", rampa_manual("#2E5A14", "#3E7A1C", "#52982A", "#68B238", "#86C850", "#A6DC70", base=3),
           estilo="limpo", ruido=0.12)
m.material("cabelo", rampa_manual("#6A1208", "#981E0E", "#C83218", "#E84E22", "#FF7A3A", base=3), estilo="limpo")
m.material("couro", rampa_manual("#3A2210", "#563418", "#764A24", "#966236", "#B27E4C", base=2), estilo="limpo",
           ruido=0.1)
m.material("tanga", rampa_manual("#4A3418", "#6A4C24", "#8C6834", "#A88248", "#C49E62", base=2), estilo="limpo",
           ruido=0.1)
m.material("madeira", rampa_manual("#4A2E14", "#6E4620", "#94622E", "#B8803E", "#D8A060", base=2), estilo="limpo",
           ruido=0.15)
m.material("metal", rampa_manual("#2A2C32", "#44484E", "#646A72", "#8C939C", base=2), estilo="liso",
           aresta_clara=0.6)
m.material("osso", rampa_manual("#B8B0A0", "#D6CEBE", "#EEE8DA", "#FFFCF2", base=2), estilo="liso", volume=0.2)
m.material("boca", rampa_manual("#2A0808", "#4A1010", "#6E1C1C", base=1), estilo="liso", volume=0,
           aresta_clara=0, aresta_escura=0)

CORES_OLHO = {"k": "#1A1408", "y": "#F0D040", "Y": "#FFF080", "P": "#140C04", "W": "#FFFFFF", "s": "#2E5A14"}
OLHO_FRENTE = """
sss
kkk
YWP
yPP
kkk
"""
OLHO_LADO = """
ss.
kkk
Pyk
Pyk
kk.
"""

root = m.osso("root")
corpo = m.osso("body", pivo=[0, 9, 0], pai="root")

# tronco corcunda (barriga + peito curvado para a frente), colete de couro e tanga
alca = onde(lambda c: (np.abs((c.y - 12) + c.x * 0.9) < 0.7), mat="couro")
corpo.cubo_arredondado([-4.5, 7, -3], [9, 6, 6.5], [base("pele"), onde(lambda c: c.n[2] > -0.5, mat="couro"), alca],
                       raio=1.5, arestas="verticais")                                     # barriga + colete
corpo.cubo_arredondado([-5, 12, -3.5], [10, 4.5, 7.5], [base("pele"), onde(lambda c: c.n[2] > -0.5, mat="couro"),
                       alca], raio=1.5)                                                   # peito/ombros
corpo.cubo_arredondado([-4.75, 5, -3.25], [9.5, 3, 7], [base("tanga"), onde(acima(7.25), mat="couro"),
                       onde(e_(faces("north"), lambda c: (np.abs(c.x) < 0.75) & (c.y > 7.25)), mat="metal")],
                       raio=1, arestas="verticais")                                       # cinto + tanga
for x in (-3, -0.5, 2):                                                                  # franja da tanga
    corpo.plano([x, 3.5, -3.3], [2, 1.5, 0], [base("tanga"), afinar("-y", largura_ponta=0.2)])
corpo.cubo_arredondado([3.5, 13.5, -1.5], [2.5, 2.5, 3], [base("metal")], raio=0.5)        # ombreira de metal

# cabeça grande, focinho largo, mandíbula com presas para cima
cab = m.osso("head", pivo=[0, 15.5, -2.5], pai="body")
mand = m.osso("jaw", pivo=[0, 15.5, -4], pai="head", rotacao=[5, 0, 0])
corpo.segmento([0, 13, -1], [0, 16, -2.5], 5, 5, [base("pele")], raio=1, sobra=1)         # pescoço
olhos_g = olhos(OLHO_FRENTE, OLHO_LADO, CORES_OLHO, x_quina=3.5, y=20.75, z_frente=-6)
cab.cubo_arredondado([-3.5, 16.5, -6], [7, 7, 7], [base("pele")] + olhos_g, raio=1.5, arestas="frente")
cab.cubo_arredondado([-3, 18.5, -7.5], [6, 1.5, 2], [base("pele")], raio=0.5)              # testa franzida
narinas = onde(e_(faces("north"), ou_(caixa([-1.5, 17.5, -9.5], [-0.5, 18.5, -8]), caixa([0.5, 17.5, -9.5], [1.5, 18.5, -8]))),
               mat="boca")
cab.cubo_arredondado([-2.5, 16, -9], [5, 3, 3.5], [base("pele"), narinas, so_faces("down", base("boca"))],
                     raio=1, arestas="frente")                                            # focinho
sorriso = onde(e_(faces("north"), lambda c: np.abs(c.y - (15.5 + np.abs(c.x) * 0.25)) < 0.3), mat="boca")
mand.cubo_arredondado([-5, 13, -9], [10, 3.5, 7], [base("pele"), sorriso, so_faces("up", base("boca"))],
                      raio=1, arestas="verticais")                                        # mandíbula larga
for lado in (1, -1):                                                                     # presas para cima
    mand.cubo([3.5 * lado - 0.75, 16.5, -8.75], [1.5, 2.5, 1.5], [base("osso"), afinar("+y", largura_ponta=0.1)])
for lado in (1, -1):                                                                     # orelhas pontudas
    cab.segmento([3.25 * lado, 20.5, -2.5], [7.5 * lado, 22, -0.5], 2.5, 1.5,
                 [base("pele"), afinar("+y", largura_ponta=0.1, curva=1.2)], sobra=0.5)
for k, (z, alto) in enumerate(((-4.5, 3), (-2.5, 4), (-0.5, 3.5), (1.5, 2.5))):          # moicano vermelho
    cone_empilhado(cab, [0, 23, z], [(2.5, 1, 2), (2, alto * 0.5, 1.5), (1, alto * 0.5, 1)],
                   [base("cabelo"), gradiente(1, 23, 27, -0.3, 0.6)], rotacao=[15, 0, 0])


def braco(nome, lado):
    om = [5 * lado, 14, -0.5]
    co = [8 * lado, 10, -1.5]
    pu = [9.5 * lado, 5.5, -3]
    b = m.osso(nome, pivo=om, pai="body")
    junta(b, om, [3.5, 3.5, 3.5], [base("pele")], raio=1)
    b.segmento(om, co, 3, 3, [base("pele")], sobra=1)
    junta(b, co, [3, 3, 3], [base("pele")], raio=1)
    b.segmento(co, pu, 3, 3, [base("pele")], sobra=1)
    b.cubo_arredondado([pu[0] - 2, pu[1] - 2.5, pu[2] - 2], [4, 3, 4], [base("pele")], raio=1)   # mão grande
    for k in (-1, 0, 1):
        x = pu[0] + k * 1.2
        b.cubo([x - 0.5, pu[1] - 4.5, pu[2] - 1.75], [1, 2, 1.25], [base("osso"),
               afinar("-y", largura_ponta=0.2, curva=1.5, apoio="-z")])
    if lado < 0:                                                                       # porrete na mão direita
        b.segmento([pu[0], pu[1] - 1, pu[2] - 1], [pu[0], pu[1] - 1, pu[2] - 7], 2, 2, [base("madeira")], sobra=0.5)
        b.cubo_arredondado([pu[0] - 2.5, pu[1] - 3.5, pu[2] - 12], [5, 5, 5.5], [base("madeira"),
                           onde(lambda c: np.abs(c.n[2]) > 0.5, mat="tanga"),
                           onde(lambda c: (np.abs(c.z - (pu[2] - 9.25)) < 0.4) & (np.abs(c.n[2]) < 0.5), mat="metal")],
                           raio=1, arestas="z")


braco("arm_left", 1)
braco("arm_right", -1)


def perna(nome, lado):
    qu = [2.5 * lado, 7, 0]
    jo = [3 * lado, 4, -1]
    ca = [3.25 * lado, 1.5, 0.5]
    p = m.osso(nome, pivo=qu, pai="root")
    p.segmento(qu, jo, 3.5, 4, [base("pele")], raio=1, sobra=1.5)
    junta(p, jo, [3.5, 3, 3.5], [base("pele")], raio=1)
    p.segmento(jo, ca, 3, 3, [base("pele")], sobra=1)
    p.cubo_arredondado([ca[0] - 2.25, 0, -4], [4.5, 2, 6], [base("pele"), gradiente(1, 0, 2, -0.5, 0.3)],
                       raio=0.5, arestas="verticais")
    for k in (-1, 0, 1):
        x = ca[0] + k * 1.5
        p.cubo([x - 0.5, 0, -5.5], [1, 1, 1.5], [base("osso"), afinar("-z", apoio="y")])


perna("leg_left", 1)
perna("leg_right", -1)

anims = bipede(peso=1.0)
for an in anims.values():
    an["bones"].pop("tail", None)
anims["idle"]["bones"]["jaw"] = {"rotation": onda(3, anims["idle"]["animation_length"], deslocamento=5)}
a = anims["attack"]["animation_length"]
anims["attack"]["bones"]["arm_right"] = {"rotation": chaves({0: [0, 0, 0], a * 0.3: [-120, 0, 15], a * 0.6: [20, 0, 0],
                                                             a: [0, 0, 0]}, True)}
for nome, an in anims.items():
    m.animacao(nome, an["animation_length"], an["bones"], an["loop"])

if __name__ == "__main__":
    finalizar(m, refs=("Goburimon_Model_SC.png", "Goburimon_newcentury_model.png", "Goburimon_Model_DSR.png"),
              estilo="0004_charmander")
