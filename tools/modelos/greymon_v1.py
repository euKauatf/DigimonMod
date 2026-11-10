"""
Greymon: dinossauro laranja grande com listras azuis, capacete-crânio marrom com 2 chifres laterais
e 1 no nariz, olhos vermelhos, bocão com dentes, garras brancas. Corpo inclinado para a frente.
Refs: Greymon_Model_DSR / Encounters (Wikimon). Estilo: Cobblemon charmeleon.
"""
from comum import *

m = Modelo(globals().get("NOME", "greymon_v1"), densidade=2)   # MetalGreymon reaproveita este corpo
m.material("pele", rampa_manual("#8A300A", "#B44412", "#DA5E18", "#F2761E", "#FF8C24", "#FFA83C", "#FFC45C",
                                base=4), estilo="limpo", ruido=0.15)
m.material("barriga", rampa_manual("#D8802E", "#F09A3C", "#FDB24C", "#FFC862", "#FFDA7E", base=2),
           estilo="limpo", ruido=0.15)
m.material("listra", rampa_manual("#101C44", "#1A2C6C", "#2944A0", "#4462C0", base=2), estilo="liso",
           aresta_clara=0, aresta_escura=0, volume=0.2)
m.material("capacete", rampa_manual("#1E0E06", "#32180C", "#4A2614", "#663820", "#86502E", "#A86E44", base=3),
           estilo="limpo", ruido=0.2, aresta_clara=0.7)
m.material("chifre", rampa_manual("#1E0E06", "#32180C", "#4A2614", "#663820", "#86502E", "#A86E44", base=3),
           estilo="liso", aresta_clara=0.7)
m.material("garra", rampa_manual("#9C96A0", "#C4BEC6", "#E6E1E8", "#FAF7FA", "#FFFFFF", base=3), estilo="liso",
           aresta_clara=0.3, volume=0.25)
m.material("boca", rampa_manual("#3A0A0A", "#5E1414", "#8A2424", base=1), estilo="liso", volume=0,
           aresta_clara=0, aresta_escura=0)

CORES_OLHO = globals().get("CORES_OLHO") or {"k": "#1A0606", "r": "#B01010", "R": "#F0402A", "W": "#FFFFFF",
                                             "P": "#140202"}
OLHO_FRENTE = """
.kk
kRW
kRP
.kk
"""
OLHO_LADO = """
kkkk.
WRRrk
PPRrk
kkkk.
"""


def listras_corpo(z_tras=8, z_frente=-3):
    """Listras azuis de tigre: grossas nas costas, afinando até sumir na barriga."""
    return onde(listras(1, 4.5, 1.5, ondulacao=0.8, eixo_onda=0, freq_onda=0.3,
                        afinar=(2, z_tras, z_frente)), mat="listra")


def barriga(cy, rx, ry, cz):
    return onde(e_(lambda c: c.n[2] < -0.5, esfera([0, cy, cz], 1.0, achatar=(rx, ry, 4))), mat="barriga")


# ----------------------------------------------------------------------------- esqueleto e corpo
root = m.osso("root")
corpo = m.osso("body", pivo=[0, 18, 2], pai="root", rotacao=[15, 0, 0])
pele_corpo = [base("pele"), listras_corpo(), barriga(22, 7, 9, -5)]
corpo.cubo_arredondado([-10, 13, -5], [20, 13, 12], pele_corpo, raio=2.5)
corpo.cubo_arredondado([-8, 25, -4.5], [16, 8, 10], pele_corpo, raio=2)
corpo.cubo_arredondado([-4.5, 31, -4.5], [9, 5, 8], [base("pele"), listras_corpo(6, -2)], raio=1)

# ----------------------------------------------------------------------------- cabeça
cab = m.osso("head", pivo=[0, 34, -1], pai="body", rotacao=[-15, 0, 0])
mand = m.osso("jaw", pivo=[0, 35, -2], pai="head")
olhos_cab = olhos(OLHO_FRENTE, OLHO_LADO, CORES_OLHO, x_quina=6, y=37.5, z_frente=-8)
cab.cubo_arredondado([-6, 34, -8], [12, 7, 10], [base("pele"), listras_corpo(4, -6)] + olhos_cab,
                     raio=1, arestas="verticais")
# capacete-crânio: tampa da cabeça e do focinho, com a borda descendo sobre os olhos
borda_escura = gradiente(1, 39, 40, -0.8, 0)
cab.cubo_arredondado([-6.5, 39.5, -9], [13, 4, 12], [base("capacete"), borda_escura], raio=1, arestas="frente")
cab.cubo_arredondado([-4.5, 38, -17.5], [9, 3, 9.5], [base("capacete"), gradiente(1, 38, 39, -0.8, 0)],
                     raio=1, arestas="frente")
# focinho de baixo do capacete (pele) com a linha da boca e o céu da boca
lábio = onde(e_(abaixo(35.5), faces("north", "east", "west")), mat="boca")
cab.cubo_arredondado([-4.5, 35, -17], [9, 3.5, 9.5], [base("pele"), lábio, so_faces("down", base("boca"))],
                     raio=0.5, arestas="frente")
dentes(cab, "garra", 4.55, 35, zs_lado=(-16, -14, -12, -10), xs_frente=(-2.5, -0.5, 1.5), z_frente=-17.05)
# chifres: dois grandes saindo dos lados do capacete, para fora e para cima; um pequeno no nariz
camadas_chifre = [(3, 2.5, 3), (2.5, 2.5, 2.5), (2, 2.5, 2), (1.5, 2.5, 1.5), (1, 2, 1), (0.5, 1.5, 0.5)]
for lado in (1, -1):
    cone_empilhado(cab, [5.5 * lado, 42, 0], camadas_chifre, [base("chifre"), gradiente(1, 41, 54, -0.3, 1.5)],
                   rotacao=[-25, 0, 32 * lado])
cone_empilhado(cab, [0, 40.5, -14.5], [(2, 1.5, 2), (1.5, 1.5, 1.5), (1, 1, 1)],
               [base("chifre"), gradiente(1, 40.5, 44.5, 0, 1.2)], rotacao=[-20, 0, 0])
# mandíbula
mand.cubo_arredondado([-4, 32.5, -16], [8, 2.5, 9.5], [base("barriga"), gradiente(1, 32.5, 35, -0.5, 0.3),
                      so_faces("up", base("boca"))], raio=0.5, arestas="frente")


# ----------------------------------------------------------------------------- braços
def braco(nome, lado):
    xs = 8 * lado
    b = m.osso(nome, pivo=[xs, 31, -2], pai="body", rotacao=[-35, 0, -12 * lado])
    xb = 7.5 if lado > 0 else -11
    pele_braco = [base("pele"), onde(listras(1, 4, 1, afinar=(2, 0, -6)), mat="listra")]
    b.cubo_arredondado([xb, 23, -3.75], [3.5, 9, 3.5], pele_braco, raio=0.5, arestas="verticais")
    b.cubo_arredondado([xb - 0.25, 16.5, -4], [4, 7, 4], pele_braco, raio=0.5, arestas="verticais")
    b.cubo_arredondado([xb - 0.75, 14, -4.5], [5, 3, 5], [base("pele")], raio=0.5)
    garras(b, "garra", xb - 0.75, 14.5, -4.25, n=3, larg=1.5, comp=4, prof=2, passo=1.75)


braco("arm_left", 1)
braco("arm_right", -1)


# ----------------------------------------------------------------------------- pernas
def perna(nome, lado):
    x0 = 3 if lado > 0 else -11
    p = m.osso(nome, pivo=[x0 + 4, 18, 1], pai="root")
    pele_perna = [base("pele"), onde(listras(1, 4.5, 1.5, ondulacao=0.6, eixo_onda=2, afinar=(2, 6, -4)),
                                     mat="listra")]
    p.cubo_arredondado([x0 - 0.5, 9, -4], [9, 11, 10], pele_perna, raio=2)                # coxa
    p.cubo_arredondado([x0 + 1, 2.5, -1.5], [5, 8, 5], pele_perna, raio=1, arestas="verticais")
    p.cubo_arredondado([x0 - 0.5, 0, -7.5], [8, 3, 11], [base("pele"), gradiente(1, 0, 3, -0.5, 0.3)],
                       raio=1, arestas="verticais")                                        # pé
    garras(p, "garra", x0, 0, -7.5, n=3, larg=1.5, prof=2, comp=3, passo=2.5, ponta="-z")
    p.cubo([x0 + 3, 0, 3.5], [1.5, 1.5, 2.5], [base("garra"), afinar("+z", apoio="y")])


perna("leg_left", 1)
perna("leg_right", -1)

# ----------------------------------------------------------------------------- cauda
listra_cauda = onde(listras(2, 4, 1.5, afinar=(1, 23, 15)), mat="listra")
cauda = m.osso("tail", pivo=[0, 19, 6], pai="body", rotacao=[-30, 0, 0])
cauda.cubo_arredondado([-4.5, 14.5, 5], [9, 8, 9], [base("pele"), listra_cauda], raio=1.5, arestas="z")
ponta = m.osso("tail_tip", pivo=[0, 18.5, 13.5], pai="tail", rotacao=[-12, 0, 0])
ponta.cubo_arredondado([-3.5, 15, 13.5], [7, 6, 8.5], [base("pele"), listra_cauda], raio=1, arestas="z")
fim = m.osso("tail_end", pivo=[0, 18, 21.5], pai="tail_tip", rotacao=[-10, 0, 0])
fim.cubo_arredondado([-2.5, 15.5, 21.5], [5, 4, 7], [base("pele"), listra_cauda], raio=1, arestas="z")
fim.cubo([-1.5, 16, 28], [3, 3, 3], [base("pele"), afinar("+z", largura_ponta=0.2)])

# ----------------------------------------------------------------------------- animações
anims = bipede(peso=1.4)
d = anims["idle"]["animation_length"]
anims["idle"]["bones"]["tail_tip"] = {"rotation": onda(5, d, eixo=1, fase=60)}
anims["idle"]["bones"]["jaw"] = {"rotation": chaves({0: [0, 0, 0], d * 0.7: [0, 0, 0], d * 0.8: [8, 0, 0],
                                                     d: [0, 0, 0]}, True)}
w = anims["walk"]["animation_length"]
anims["walk"]["bones"]["tail_tip"] = {"rotation": onda(8, w, eixo=1, fase=150)}
anims["walk"]["bones"]["tail_end"] = {"rotation": onda(8, w, eixo=1, fase=210)}
a = anims["attack"]["animation_length"]
anims["attack"]["bones"]["jaw"] = {"rotation": chaves({0: [0, 0, 0], a * 0.3: [35, 0, 0], a * 0.7: [35, 0, 0],
                                                       a: [0, 0, 0]}, True)}
for nome, an in anims.items():
    m.animacao(nome, an["animation_length"], an["bones"], an["loop"])

if __name__ == "__main__":
    finalizar(m, refs=("Greymon_Model_DSR.png", "Greymon_Model_Encounters.png"), estilo="0005_charmeleon")
