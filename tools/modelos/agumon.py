"""
Agumon v3: a cara, as cores (vivas e lisas) e os olhos do Agumon aprovado, agora com o ESQUELETO medido
na folha de modelo oficial do Digimon Adventure 2020 (vista de lado e de frente) e as juntas fechadas.

Medidas (H = 24 unidades até o topo da cabeça = 1,5 bloco), tiradas de lado_2020.png:
  cabeça: comprimento 15 (0,62 H: crânio redondo + focinho comprido), altura 9,5 (0,4 H); fica um
          pouco à frente do corpo, sobre um PESCOÇO curto e grosso (o Agumon tem pescoço visível)
  olhos verdes grandes no alto, atrás da raiz do focinho; boca em sorriso; dentinhos no lábio
  tronco: em pé (quase vertical), barriga redonda clara; ombro a 0,55 H
  braços: finos e COMPRIDOS, pendurados para a frente, garras brancas chegando perto do joelho
  pernas: coxa grossa indo para a frente até o joelho, canela para trás até o calcanhar alto,
          pé enorme (~0,35 H) com 3 garras na frente e 1 atrás; pés bem afastados
  cauda: curta e grossa, saindo para trás e SUBINDO (não arrasta no chão)

    D:\\FerramentasMinecraft\\venv\\Scripts\\python.exe tools/modelos/agumon.py [--mod]
"""
from comum import *

m = Modelo("agumon", densidade=2)
# rampas com as cores que paleta.py tirou do render oficial (cores vivas e lisas, aprovadas pelo usuário)
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
corpo = m.osso("body", pivo=[0, 8.5, 0.5], pai="root")
cab = m.osso("head", pivo=[0, 15.5, -0.5], pai="body")
mand = m.osso("jaw", pivo=[0, 16.5, -4.5], pai="head", rotacao=[4, 0, 0])   # sorriso entreaberto


# ------------------------------------------------------------------------- corpo (pera em pé)
def barriga_clara():
    return onde(e_(lambda c: c.n[2] < -0.5,
                   esfera([0, 9.5, -3], 1.0, achatar=(3.6, 4.4, 3.0))), mat="barriga")


corpo.cubo_arredondado([-4.5, 5.5, -3], [9, 7.5, 7], [base("pele"), barriga_clara()], raio=1.5)   # quadril/barriga
corpo.cubo_arredondado([-3.5, 12, -2.5], [7, 4, 5.5], [base("pele"), barriga_clara()], raio=1)    # peito
# pescoço curto e grosso, garganta clara
corpo.segmento([0, 14, 0], [0, 17, -1.5], 5.5, 5, [base("pele"), onde(lambda c: c.n[2] < -0.4, mat="barriga")],
               raio=1, sobra=1.5)

# ------------------------------------------------------------------------- cabeça
olhos_ag = [
    decalque(OLHO_E_FRENTE, CORES_OLHO, centro=[3.25, 21.25, -6.5], direcao=(0, 0, -1), profundidade=0.3),
    decalque(OLHO_E_LADO, CORES_OLHO, centro=[4.5, 21.25, -5.75], direcao=(1, 0, 0), profundidade=0.3),
    decalque(OLHO_D_FRENTE, CORES_OLHO, centro=[-3.25, 21.25, -6.5], direcao=(0, 0, -1), profundidade=0.3),
    decalque(OLHO_D_LADO, CORES_OLHO, centro=[-4.5, 21.25, -5.75], direcao=(-1, 0, 0), profundidade=0.3),
]


def sorriso(c):
    """Linha da boca na lateral das bochechas: continua a do focinho e sobe num sorriso no fim."""
    y_linha = 16.75 + np.clip(c.z + 5.0, 0, None) * 0.5
    return (np.abs(c.y - y_linha) < 0.26) & (c.z < -2.5) & (abs(c.n[0]) > 0.5)


# bochechas largas embaixo + crânio redondo em cima (pera vista de frente), crânio indo até a nuca
cab.cubo_arredondado([-5, 15, -6], [10, 4.5, 7.5], [base("pele"), onde(sorriso, mat="boca"),
                     onde(lambda c: c.n[1] < -0.5, mat="barriga")], raio=1, arestas="verticais")
cab.cubo_arredondado([-4.5, 17, -6.5], [9, 7, 9], [base("pele")] + olhos_ag, raio=1.5, arestas="frente")
for lado in (1, -1):                                                    # sobrancelhas baixas
    x0 = 1.5 if lado > 0 else -4.5
    cab.cubo_arredondado([x0, 23.5, -6.5], [3, 1, 3], [base("pele")], raio=0.5, arestas="verticais")

# focinho comprido, quase da largura da cabeça; linha da boca embaixo; céu da boca
labio = onde(e_(abaixo(17.0), faces("north", "east", "west")), mat="boca")
narinas = onde(e_(faces("up"), ou_(caixa([0.75, 20.5, -12], [1.5, 21.5, -11.5]),
                                    caixa([-1.5, 20.5, -12], [-0.75, 21.5, -11.5]))), mat="boca")
cab.cubo_arredondado([-4, 16.5, -12.5], [8, 4.5, 7], [base("pele"), labio, narinas,
                     so_faces("down", base("boca"))], raio=1, arestas="frente")
cab.cubo([-3, 15.5, -12], [6, 3, 7.5], [base("boca")])                  # fundo da boca (não se vê através)
DENTE = [base("garra"), sprite("gg\ng_", {"g": "garra"})]
for lado in (1, -1):
    for zd in (-11.75, -10, -8.25):
        cab.plano([4.05 * lado, 15.5, zd], [0, 1, 1], DENTE)
    cab.plano([lado * 2 - 0.5, 15.5, -12.05], [1, 1, 0], DENTE)

# mandíbula: mais estreita e curta que o focinho; abre no ataque
mand.cubo_arredondado([-3.5, 14.5, -11.5], [7, 2, 7.5], [base("pele"), onde(lambda c: c.n[1] < -0.5, mat="barriga"),
                      gradiente(1, 14.5, 16.5, -0.3, 0.2), so_faces("up", base("boca"))], raio=0.5, arestas="frente")


# ------------------------------------------------------------------------- braços (compridos, para a frente)
def braco(nome, lado):
    om = [4.25 * lado, 13, -0.5]        # ombro
    co = [5.75 * lado, 9.5, -1.5]       # cotovelo (braço abre um pouco, como na referência de frente)
    pu = [6 * lado, 6.5, -4]            # pulso
    b = m.osso(nome, pivo=om, pai="body")
    junta(b, om, [3, 3, 3], [base("pele")], raio=1)
    b.segmento(om, co, 2.5, 2.5, [base("pele")], sobra=1)
    junta(b, co, [2.5, 2.5, 2.5], [base("pele")])
    b.segmento(co, pu, 2.5, 2.5, [base("pele")], sobra=1)
    b.cubo_arredondado([pu[0] - 1.75, pu[1] - 1.5, pu[2] - 2], [3.5, 2.5, 3], [base("pele")], raio=0.5)   # mão
    for k in (-1, 0, 1):                                                 # 3 garras brancas grandes
        x = pu[0] + k * 1.1
        b.cubo([x - 0.5, pu[1] - 4, pu[2] - 2], [1, 3, 1.5],
               [base("garra"), afinar("-y", largura_ponta=0.2, curva=1.6, apoio="-z")],
               rotacao=[-25, 0, 0], pivo=[x, pu[1] - 1, pu[2] - 1.25])


braco("arm_left", 1)
braco("arm_right", -1)


# ------------------------------------------------------------------------- pernas (coxa para a frente, pé grande)
def perna(nome, lado):
    qu = [3 * lado, 8, 1.5]             # quadril
    jo = [4.25 * lado, 4.5, -1]         # joelho (para a frente e para fora)
    ca = [4.75 * lado, 2, 2]            # calcanhar alto (para trás); pés bem afastados
    p = m.osso(nome, pivo=qu, pai="root")
    p.segmento(qu, jo, 4.5, 5.5, [base("pele")], raio=1.5, arestas="y", sobra=1.5)           # coxa
    junta(p, jo, [4, 3.5, 4], [base("pele")], raio=1)                                         # joelho
    p.segmento(jo, ca, 3, 3, [base("pele")], sobra=1)                                         # canela
    p.cubo_arredondado([ca[0] - 3, 0, -5], [6, 2, 8.5], [base("pele"), gradiente(1, 0, 2, -0.5, 0.3)],
                       raio=0.5, arestas="verticais")                                          # pé enorme
    for k in (-1, 0, 1):
        x = ca[0] + k * 2
        p.cubo([x - 0.75, 0, -7], [1.5, 1.5, 2], [base("garra"), afinar("-z", largura_ponta=0.0, curva=0.9, apoio="y")])
    p.cubo([ca[0] - 0.5, 0, 3.5], [1, 1, 1.5], [base("garra"), afinar("+z", curva=0.9, apoio="y")])


perna("leg_left", 1)
perna("leg_right", -1)

# ------------------------------------------------------------------------- cauda (curta, para trás e para cima)
cauda = m.osso("tail", pivo=[0, 7.5, 3], pai="body")
cauda.segmento([0, 7.5, 2.5], [0, 8.5, 6], 6, 5.5, [base("pele")], raio=1.5, sobra=1.5)
ponta = m.osso("tail_tip", pivo=[0, 8.5, 6], pai="tail")
ponta.segmento([0, 8.5, 6], [0, 10.5, 8.5], 4, 4, [base("pele")], raio=1, sobra=1)
fim = m.osso("tail_end", pivo=[0, 10.5, 8.5], pai="tail_tip")
fim.segmento([0, 10.5, 8.5], [0, 12.5, 10], 2.5, 2.5, [base("pele")], sobra=0.5)

# ------------------------------------------------------------------------- animações (mesmos nomes do mod)
anims = bipede(peso=0.9)
anims["idle"]["bones"]["tail_tip"] = {"rotation": onda(6, 2.16, eixo=1, fase=60)}
anims["idle"]["bones"]["jaw"] = {"rotation": chaves({0: [4, 0, 0], 1.6: [4, 0, 0], 1.8: [10, 0, 0], 2.16: [4, 0, 0]}, True)}
anims["walk"]["bones"]["tail_tip"] = {"rotation": onda(10, 0.81, eixo=1, fase=150)}
anims["walk"]["bones"]["tail_end"] = {"rotation": onda(8, 0.81, eixo=1, fase=210)}
anims["attack"]["bones"]["jaw"] = {"rotation": chaves({0: [4, 0, 0], 0.15: [30, 0, 0], 0.35: [30, 0, 0], 0.45: [4, 0, 0]}, True)}
for nome, a in anims.items():
    m.animacao(nome, a["animation_length"], a["bones"], a["loop"])

if __name__ == "__main__":
    finalizar(m, refs=("Agumon_Model_DSR.png", "frente_2020.png", "lado_2020.png"), estilo="0004_charmander")
