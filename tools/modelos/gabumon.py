"""
Gabumon: corpo de réptil AMARELO vestindo a pele de um lobo (branca com listras azuis). Medido nos modelos
oficiais (New Century, SC) e na arte oficial. Mesmo método do Agumon aprovado: esqueleto, juntas fechadas,
poucas peças grandes, um olho por lado, cores vivas e lisas.

Medidas (H = 24 unidades até o topo do capuz, sem o chifre):
  capuz de pele (cabeça): largura 10 (0,42 H), altura 8,5; focinho de lobo branco curto com nariz preto;
         olhos vermelhos grandes na frente, com "sobrancelha" azul; presas brancas penduradas na borda do
         capuz; queixo/mandíbula amarela embaixo (é a cara do Gabumon aparecendo)
  chifre dourado com anéis no alto do capuz (~0,25 H); orelhas compridas e moles para trás e para fora
  corpo: pera amarela, barriga larga com o emblema azul-claro e rosa; a pele cobre costas e ombros
  braços: mangas de pele COMPRIDAS (até o joelho), listradas, garras magenta
  pernas: amarelas, curtas e grossas, pé com 3 garras brancas
  cauda: amarela, grossa, para trás e subindo
"""
from comum import *

m = Modelo("gabumon", densidade=2)
m.material("pele", rampa_manual("#A87A14", "#CC9A1C", "#ECBC28", "#FFD43A", "#FFE468", "#FFF29A", base=3),
           estilo="limpo", ruido=0.15)
m.material("pelo", rampa_manual("#8088B0", "#A0A8D0", "#C0C8EE", "#D8E0FC", "#ECF0FF", "#FAFCFF", base=3),
           estilo="limpo", ruido=0.15)
m.material("listra", rampa_manual("#141C5A", "#222E86", "#2C3A9E", "#4A5CC0", base=2), estilo="liso",
           aresta_clara=0, aresta_escura=0, volume=0.15, oclusao=0.3)
m.material("garra", rampa_manual("#4A0E2C", "#6E1640", "#8E2058", "#B83A78", "#DA5C9A", base=3), estilo="liso",
           aresta_clara=0.4)
m.material("unha", rampa_manual("#9C96A0", "#C4BEC6", "#E6E1E8", "#FAF7FA", "#FFFFFF", base=4), estilo="liso",
           aresta_clara=0.3, volume=0.25)
m.material("chifre", rampa_manual("#7A5A0C", "#A8801A", "#D4A828", "#F0C840", "#FFE06A", "#FFF09C", base=3),
           estilo="liso", aresta_clara=0.6, volume=0.4)
m.material("boca", rampa_manual("#3A0810", "#5E141E", "#8A2430", base=1), estilo="liso", volume=0,
           aresta_clara=0, aresta_escura=0)

K = "#2A1018"
CORES_OLHO = {"k": K, "r": "#B8301A", "R": "#F06A3A", "P": "#1A0806", "W": "#FFFFFF", "b": "#2C3A9E"}
# olho esquerdo dele (+X): parte da frente (termina na quina) + parte da lateral; "b" = sobrancelha azul
OLHO_E_FRENTE = """
.bbbb
.kkkk
kWWrr
kWPPr
krPPr
krRRr
.kkkk
"""
OLHO_E_LADO = """
bb.
kk.
rrk
Prk
Prk
Rrk
kk.
"""
OLHO_D_FRENTE = """
bbbb.
kkkk.
WWrrk
WPPrk
rPPrk
rRRrk
kkkk.
"""
OLHO_D_LADO = """
.bb
.kk
krr
krP
krP
krR
.kk
"""
EMBLEMA = """
......kk......
....kkcckk....
...kccmmcck...
..kcmmccmmck..
.kccmcmmcmcck.
.kccmcmmcmcck.
kcccmmmmmmccck
kcccccccccccck
kcmcmmmmmmcmck
kcmmmccccmmmck
kccccmmmmcccck
kcmmmmmmmmmmck
.kcmcmmmmcmck.
.kcmmmmmmmmck.
..kkcccccckk..
....kkkkkk....
"""
CORES_EMBLEMA = {"k": "#1E5A96", "c": "#66C0F2", "m": "#C42A6A"}


def listras_pelo(eixo=(0, 1, 0), periodo=3.5, largura=1.0, semente=3, cond=None):
    """Listras azuis da pele de lobo: onduladas, interrompidas, perpendiculares ao eixo."""
    conds = [listras_eixo(eixo, periodo, largura, ondulacao=0.9, eixo_onda=(1, 0, 1), freq_onda=0.35),
             lambda c: fbm(c.p, 3.0, 1, semente=semente) > -0.55]
    if cond is not None:
        conds.append(cond)
    return onde(e_(*conds), mat="listra")


# ------------------------------------------------------------------------- esqueleto
root = m.osso("root")
corpo = m.osso("body", pivo=[0, 8.5, 0.5], pai="root")
cab = m.osso("head", pivo=[0, 15.5, -0.5], pai="body")
mand = m.osso("jaw", pivo=[0, 16, -4.5], pai="head", rotacao=[4, 0, 0])

# ------------------------------------------------------------------------- corpo: pera amarela + pele nas costas
# barriga com a FRENTE LISA (quinas arredondadas só nas laterais): o emblema fica só nessa frente e não
# entorta nas quinas quando visto de lado/3-4
corpo.cubo_arredondado([-6, 4.5, -4], [12, 9, 8], [base("pele"),
                       decalque(EMBLEMA, CORES_EMBLEMA, centro=[0, 9, -4], profundidade=0.4)],
                       raio=2.5, arestas="verticais")                                               # barriga
corpo.cubo_arredondado([-5, 12, -3.5], [10, 3.5, 6.5], [base("pele")], raio=1.5)                                # peito
corpo.cubo_arredondado([-6.5, 6, -0.5], [13, 11, 6.5], [base("pelo"), listras_pelo((0, 1, 0.3), 4, 1.2)],
                       raio=2)                                                         # pele de lobo nas costas
# garganta/pescoço amarelo: liga o peito à mandíbula (sem vão embaixo da boca)
corpo.segmento([0, 12.5, 0], [0, 15.5, -2.5], 6.5, 6, [base("pele")], raio=1, sobra=1.5)

# ------------------------------------------------------------------------- cabeça (capuz de lobo)
olhos_gb = [
    decalque(OLHO_E_FRENTE, CORES_OLHO, centro=[4.25, 20.25, -5.5], direcao=(0, 0, -1), profundidade=0.3),
    decalque(OLHO_E_LADO, CORES_OLHO, centro=[5.5, 20.25, -4.75], direcao=(1, 0, 0), profundidade=0.3),
    decalque(OLHO_D_FRENTE, CORES_OLHO, centro=[-4.25, 20.25, -5.5], direcao=(0, 0, -1), profundidade=0.3),
    decalque(OLHO_D_LADO, CORES_OLHO, centro=[-5.5, 20.25, -4.75], direcao=(-1, 0, 0), profundidade=0.3),
]
listras_capuz = listras_pelo((0, 0.3, 1), 4, 1.2, semente=7, cond=lambda c: (c.n[2] > -0.5) & (c.y > 18))
cab.cubo_arredondado([-5.5, 15.5, -5.5], [11, 8.5, 9.5], [base("pelo"), listras_capuz] + olhos_gb,
                     raio=1.5, arestas="frente")                                       # capuz
# focinho de lobo branco com nariz preto
nariz = onde(e_(lambda c: c.n[1] > 0.5, caixa([-1, 19, -9.5], [1, 21, -8.5])), cor="#1A1A22")
nariz_f = onde(e_(faces("north"), caixa([-1, 18.5, -9.6], [1, 20, -9])), cor="#1A1A22")
cab.cubo_arredondado([-3, 16, -9.5], [6, 4, 4.5], [base("pelo"), nariz, nariz_f,
                     so_faces("down", base("boca"))], raio=1, arestas="frente")
cab.cubo([-2.5, 15.5, -8.5], [5, 2.5, 3.5], [base("boca")])                     # fundo da boca
# presas brancas triangulares na borda do focinho, PARA FORA da mandíbula (a mandíbula é mais estreita
# que o focinho, senão ela esconde os dentes na vista 3/4)
DENTE = [base("unha"), afinar("-y", largura_ponta=0.0, curva=1.0)]
for lado in (1, -1):
    for zd in (-8.5, -6.75):
        cab.plano([3.05 * lado, 14.5, zd], [0, 1.5, 1.5], DENTE)
for x in (-2.25, 0.75):
    cab.plano([x, 14.5, -8.55], [1.5, 1.5, 0], DENTE)
# chifre dourado com anéis
aneis = onde(lambda c: (np.abs(c.y - 25.25) < 0.3) | (np.abs(c.y - 28) < 0.3), mat="boca")
cone_empilhado(cab, [0, 23.5, -2], [(3, 2, 3), (2, 2.5, 2), (1.5, 2, 1.5), (1, 1.5, 1)], [base("chifre"), aneis, gradiente(1, 23.5, 32.5, -0.3, 0.8)],
               rotacao=[-8, 0, 0])
# orelhas compridas e moles, para trás e para fora
for lado in (1, -1):
    pontas_azuis = onde(lambda c, l=lado: np.abs(c.x) > 7.5, mat="listra")
    cab.segmento([3.5 * lado, 22.5, 0], [8 * lado, 20, 5.5], 3, 1, [base("pelo"), pontas_azuis], sobra=1)

# mandíbula/queixo amarelo do Gabumon aparecendo sob o capuz
mand.cubo_arredondado([-2.75, 14, -8.5], [5.5, 2.5, 6], [base("pele"), gradiente(1, 14, 16.5, -0.4, 0.2),
                      so_faces("up", base("boca"))], raio=0.5, arestas="frente")
for x in (-1.75, 0.75):                                                  # dentinhos de baixo
    mand.plano([x, 16.5, -8.05], [1, 1, 0], [base("unha"), afinar("+y", largura_ponta=0.0)])


# ------------------------------------------------------------------------- braços (mangas de pele compridas)
def braco(nome, lado):
    om = [6 * lado, 13.5, -0.5]
    co = [7.75 * lado, 9.5, -1]
    pu = [8.25 * lado, 5.5, -2.5]
    b = m.osso(nome, pivo=om, pai="body")
    manga = [base("pelo"), listras_pelo((0, 1, 0), 3, 0.9, semente=11 if lado > 0 else 13)]
    junta(b, om, [4, 4, 4], manga, raio=1.5)
    b.segmento(om, co, 3.5, 3.5, manga, sobra=1)
    junta(b, co, [3.5, 3.5, 3.5], manga)
    b.segmento(co, pu, 3.5, 3.5, manga, sobra=1)
    b.cubo_arredondado([pu[0] - 2, pu[1] - 1.5, pu[2] - 2], [4, 2.5, 4], [base("pelo")], raio=1)   # punho de pelo
    for k in (-1, 0, 1):                                                 # 3 garras magenta
        x = pu[0] + k * 1.2
        b.cubo([x - 0.5, pu[1] - 4.5, pu[2] - 1.75], [1, 3, 1.5],
               [base("garra"), afinar("-y", largura_ponta=0.2, curva=1.6, apoio="-z")],
               rotacao=[-20, 0, 0], pivo=[x, pu[1] - 1.5, pu[2] - 1])


braco("arm_left", 1)
braco("arm_right", -1)


# ------------------------------------------------------------------------- pernas (amarelas, curtas e grossas)
def perna(nome, lado):
    qu = [3.5 * lado, 7.5, 1]
    jo = [4.5 * lado, 4, -1]
    ca = [5 * lado, 2, 1.5]
    p = m.osso(nome, pivo=qu, pai="root")
    p.segmento(qu, jo, 4.5, 5.5, [base("pele")], raio=1.5, arestas="y", sobra=1.5)        # coxa
    junta(p, jo, [4, 3.5, 4], [base("pele")], raio=1)                                     # joelho
    p.segmento(jo, ca, 3, 3, [base("pele")], sobra=1)                                     # canela
    p.cubo_arredondado([ca[0] - 2.5, 0, -4.5], [5, 2, 7.5], [base("pele"), gradiente(1, 0, 2, -0.5, 0.3)],
                       raio=0.5, arestas="verticais")                                      # pé
    for k in (-1, 0, 1):
        x = ca[0] + k * 1.75
        p.cubo([x - 0.75, 0, -6.5], [1.5, 1.5, 2], [base("unha"), afinar("-z", largura_ponta=0.0, curva=0.9, apoio="y")])


perna("leg_left", 1)
perna("leg_right", -1)

# ------------------------------------------------------------------------- cauda (amarela, para trás e para cima)
cauda = m.osso("tail", pivo=[0, 6.5, 3.5], pai="body")
cauda.segmento([0, 7, 1.5], [0, 7.5, 7], 6, 6, [base("pele")], raio=1.5, sobra=1.5)   # nasce dentro do corpo
ponta = m.osso("tail_tip", pivo=[0, 7.5, 7], pai="tail")
ponta.segmento([0, 7.5, 7], [0, 10, 9.5], 4, 4, [base("pele")], raio=1, sobra=1)
fim = m.osso("tail_end", pivo=[0, 10, 9.5], pai="tail_tip")
fim.segmento([0, 10, 9.5], [0, 13, 11], 2.5, 2.5, [base("pele")], sobra=0.5)

# ------------------------------------------------------------------------- animações (mesmos nomes do mod)
anims = bipede(peso=0.9)
anims["idle"]["bones"]["tail_tip"] = {"rotation": onda(6, 2.16, eixo=1, fase=60)}
anims["idle"]["bones"]["jaw"] = {"rotation": chaves({0: [4, 0, 0], 1.6: [4, 0, 0], 1.8: [10, 0, 0], 2.16: [4, 0, 0]}, True)}
anims["walk"]["bones"]["tail_tip"] = {"rotation": onda(10, 0.81, eixo=1, fase=150)}
anims["walk"]["bones"]["tail_end"] = {"rotation": onda(8, 0.81, eixo=1, fase=210)}
anims["attack"]["bones"]["jaw"] = {"rotation": chaves({0: [4, 0, 0], 0.15: [28, 0, 0], 0.35: [28, 0, 0], 0.45: [4, 0, 0]}, True)}
for nome, a in anims.items():
    m.animacao(nome, a["animation_length"], a["bones"], a["loop"])

if __name__ == "__main__":
    finalizar(m, refs=("Gabumon_newcentury_model.png", "Gabumon_Model_SC.png", "Gabumon.png"), estilo="0004_charmander")
