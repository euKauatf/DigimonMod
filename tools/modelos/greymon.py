"""
Greymon (v3: simplificado). Anatomia das folhas de modelo oficiais, montada com POUCAS peças grandes,
todas encostadas umas nas outras (jeito Cobblemon). ~30 cubos em vez de ~100.

Medidas (H = altura até o topo do capacete, sem chifres; H ~ 40 unidades = 2,5 blocos):
  cabeça: comprimento 0,42 H, altura 0,30 H, largura 0,40 H (tão larga quanto o quadril de frente);
          capacete cobre a metade de cima e o focinho; UM olho de cada lado, na quina do capacete.
  chifres: 2 laterais (para fora e para cima) e 1 de rinoceronte em cima do focinho.
  pescoço: grosso, inclinado para a frente.   tronco: inclinado, barriga redonda clara.
  braços: braço + antebraço (cotovelo dobrado) + mão com 3 garras.
  pernas: coxa grande para a frente/fora, canela para trás até o pé, pé com 3 garras e esporão.
  cauda: 3 gomos afinando, para trás e subindo; listras azuis poucas e finas.
"""
from comum import *

m = Modelo(globals().get("NOME", "greymon"), densidade=2)   # MetalGreymon reaproveita este corpo
# Cores VIVAS e LISAS (o usuário preferiu assim; o granulado "vanilla" pareceu apagado e manchado)
m.material("pele", rampa_manual("#8A300A", "#B44412", "#DA5E18", "#F2761E", "#FF8C24", "#FFA83C", "#FFC45C",
                                base=4), estilo="limpo", ruido=0.15)
m.material("barriga", rampa_manual("#C85A14", "#E8761E", "#FA8E2A", "#FFA23A", "#FFB850", "#FFCC6E", base=4),
           estilo="limpo", ruido=0.12)
m.material("listra", rampa_manual("#0C1640", "#16286A", "#2440A0", "#3A5CC8", base=2), estilo="liso",
           aresta_clara=0, aresta_escura=0, volume=0.15, oclusao=0.3)
m.material("capacete", rampa_manual("#160A04", "#2A1408", "#3E2010", "#56301A", "#704428", "#8E5E3C", "#B08060",
                                    base=3), estilo="limpo", ruido=0.2, aresta_clara=0.8)
m.material("chifre", rampa_manual("#140A06", "#26140C", "#3C2416", "#583A26", "#7A563A", "#A07A58", base=3),
           estilo="liso", aresta_clara=0.6)
m.material("chifre_nariz", rampa_manual("#140A06", "#26140C", "#3C2416", "#583A26", "#7A563A", "#A07A58", base=3),
           estilo="liso", aresta_clara=0.6)        # separado para o MetalGreymon trocar (vira metal)
m.material("garra", rampa_manual("#4E5058", "#6E727C", "#959AA4", "#BCC0C8", "#DEE1E6", "#F6F7F9", base=3),
           estilo="liso", aresta_clara=0.5, volume=0.3)
m.material("dente", rampa_manual("#B8B4B0", "#DAD6D2", "#F2F0EC", "#FFFFFF", base=2), estilo="liso", volume=0.2)
m.material("boca", rampa_manual("#2A0406", "#4A0A0E", "#701820", "#98303A", "#C04A56", base=2), estilo="liso",
           volume=0.2, aresta_clara=0, aresta_escura=0)

CORES_OLHO = globals().get("CORES_OLHO") or {"k": "#1A0606", "r": "#A80E14", "R": "#E83A30", "W": "#FFFFFF",
                                             "P": "#140202", "s": "#2A1408"}
# UM olho por lado, dobrando a quina da frente do capacete (2 colunas na frente + 4 na lateral)
OLHO_FRENTE = """
ss
kk
Wr
Pr
kk
"""
OLHO_LADO = """
ssss.
kkkks
RRrk.
PRrk.
kkk..
"""


def listras_de(eixo, periodo=5.5, largura=1.0, so_em_cima=None, semente=3):
    """Listras azuis poucas, finas, onduladas e interrompidas (nunca na barriga)."""
    conds = [listras_eixo(eixo, periodo, largura, ondulacao=1.0, eixo_onda=(1, 0, 0), freq_onda=0.25),
             lambda c: fbm(c.p, 3.0, 1, semente=semente) > -0.35]
    if so_em_cima is not None:
        conds.append(so_em_cima)
    return onde(e_(*conds), mat="listra")


nao_frente = lambda c: c.n[2] > -0.5                       # noqa: E731


def junta(osso, centro, tam, pintura, raio=0, arestas="y"):
    """Peça na articulação: costura os dois segmentos e esconde a fresta da dobra."""
    x, y, z = centro
    w, h, d = tam
    if not raio:
        return [osso.cubo([x - w / 2, y - h / 2, z - d / 2], [w, h, d], pintura)]
    return osso.cubo_arredondado([x - w / 2, y - h / 2, z - d / 2], [w, h, d], pintura, raio=raio, arestas=arestas)
nao_baixo = lambda c: c.n[1] > -0.5                        # noqa: E731

# ----------------------------------------------------------------------------- tronco e pescoço
root = m.osso("root")
corpo = m.osso("body", pivo=[0, 18, 2], pai="root")
barriga = onde(e_(lambda c: c.n[2] < -0.35, esfera([0, 19, -7], 1.0, achatar=(7, 9.5, 6))), mat="barriga")
pele_tronco = [base("pele"), listras_de((0, 0.77, -0.64), so_em_cima=nao_frente), barriga]
corpo.cubo_arredondado([-9.5, 11.5, -8.5], [19, 13, 17], pele_tronco, raio=3.5)        # quadril/barriga
corpo.cubo_arredondado([-7.5, 20, -9.5], [15, 11, 13], pele_tronco, raio=3)              # peito
corpo.cubo_arredondado([-6.5, 26.5, -12], [13, 7, 11], [base("pele"),
                       onde(lambda c: c.n[2] < -0.4, mat="barriga", somar_luz=2)], raio=2.5)  # base do pescoço
corpo.segmento([0, 27, -8], [0, 35, -11.5], 12, 11,                                # pescoço
               [base("pele"), listras_de((0, 0.6, -0.8), 4.5, 0.9, so_em_cima=nao_frente),
                onde(lambda c: c.n[2] < -0.4, mat="barriga", somar_luz=3)], sobra=1.5)

# ----------------------------------------------------------------------------- cabeça
cab = m.osso("head", pivo=[0, 34, -11], pai="body")
mand = m.osso("jaw", pivo=[0, 34.5, -12], pai="head", rotacao=[12, 0, 0])   # boca entreaberta
olhos_cab = olhos(OLHO_FRENTE, OLHO_LADO, CORES_OLHO, x_quina=8, y=39.75, z_frente=-16)
borda_cap = onde(abaixo(37), luz=-1.2)
# capacete: crânio (frente e laterais retas, topo arredondado) + focinho mais baixo na frente
cab.cubo_arredondado([-8, 36, -16], [16, 8, 11], [base("capacete"), borda_cap,
                     gradiente(1, 36, 44, -0.6, 0.6)] + olhos_cab, raio=2, arestas="frente")
narinas = onde(e_(faces("up"), ou_(caixa([1, 41, -24.5], [2, 43, -23.5]), caixa([-2, 41, -24.5], [-1, 43, -23.5]))),
               luz=-3)
cab.cubo_arredondado([-6.5, 36, -25], [13, 6.5, 13], [base("capacete"), borda_cap, narinas,
                     gradiente(1, 36, 42.5, -0.6, 0.5)], raio=1.5, arestas="frente")
# lábio de cima (pele) logo abaixo da borda do capacete; céu da boca vermelho
cab.cubo([-6, 34.5, -24.5], [12, 2, 15], [base("pele"), so_faces("down", base("boca"))])
cab.cubo([-5.75, 31.5, -23], [11.5, 3, 11.5], [base("boca"), gradiente(2, -22.5, -11.5, 0.5, -1)])   # dentro da boca
DENTE = [base("dente"), afinar("-y", largura_ponta=0.0, curva=1.0), gradiente(1, 32, 34.5, -0.6, 0.5)]
for lado in (1, -1):
    for z in (-23.5, -20.5, -17.5, -14.5):
        cab.plano([6.05 * lado, 32, z], [0, 2.5, 2], DENTE)
for x in (-4.5, -1, 2.5):
    cab.plano([x, 32, -24.6], [2, 2.5, 0], DENTE)
# chifres: 2 laterais (2 gomos + ponta) e o de rinoceronte (1 gomo + ponta), todos saindo DE DENTRO do capacete
for lado in (1, -1):
    pts = [[6 * lado, 41.5, -9], [12 * lado, 43, -8.5], [14.5 * lado, 48.5, -8]]
    cab.cadeia(pts, [(3, 3), (2.5, 2.5)], [base("chifre"), gradiente(1, 41, 49, -0.4, 1.0)], sobra=1)
    cab.segmento(pts[-1], [15 * lado, 51.5, -7.5], 1.5, 1.5, [base("chifre"), gradiente(1, 48.5, 52, 0.6, 1.4)],
                 sobra=0.5)                                         # ponta fina sem recorte (recorte em peça fina gira e vira "garfo")
# chifre do nariz: cone que afina e deita para trás (lido como chifre, não como "toco")
cone_empilhado(cab, [0, 41.5, -21], [(4, 1.5, 4.5), (3, 1.5, 3.5), (2, 1.5, 2.5), (1, 1.5, 1.5)],
               [base("chifre_nariz"), gradiente(1, 41.5, 47.5, -0.4, 1.2)], rotacao=[-30, 0, 0])
# mandíbula: grossa, clara embaixo, boca vermelha em cima, 3 dentes de cada lado
mand.cubo_arredondado([-5.5, 30, -23.5], [11, 4.5, 14], [base("pele"), onde(lambda c: c.n[1] < -0.5, mat="barriga",
                      somar_luz=1.5), gradiente(1, 30, 34.5, -0.4, 0.3), so_faces("up", base("boca"))],
                      raio=1, arestas="frente")
DENTE_BAIXO = [base("dente"), afinar("+y", largura_ponta=0.0, curva=1.0)]
for lado in (1, -1):
    for z in (-22, -19, -16):
        mand.plano([5.55 * lado, 34, z], [0, 2, 2], DENTE_BAIXO)


# ----------------------------------------------------------------------------- braços
def braco(nome, lado):
    om = [7 * lado, 29, -6]
    co = [10.5 * lado, 24, -6]
    pu = [11 * lado, 22.5, -11.5]
    b = m.osso(nome, pivo=om, pai="body")
    junta(b, [om[0] - 0.5 * lado, om[1], om[2]], [6, 6.5, 7], [base("pele")], raio=1.5)          # ombro
    b.segmento(om, co, 4.5, 4.5, [base("pele"), listras_de((0, 1, 0), 4, 0.8, so_em_cima=nao_frente)], sobra=1.5)
    junta(b, co, [5, 5, 5], [base("pele")])                                                     # cotovelo
    b.segmento(co, pu, 4, 4, [base("pele")], sobra=2)
    b.cubo([pu[0] - 2.5, pu[1] - 2, pu[2] - 3], [5, 3.5, 5.5], [base("pele"), gradiente(1, pu[1] - 2, pu[1] + 1.5, -0.4, 0.4)])
    for k in (-1, 0, 1):          # 3 garras saindo da mão, curvando para baixo
        x = pu[0] + k * 1.6
        b.cubo([x - 0.75, pu[1] - 4.5, pu[2] - 3], [1.5, 3, 2],
               [base("garra"), afinar("-y", largura_ponta=0.15, curva=0.6, apoio="-z")],
               rotacao=[-20, 0, 0], pivo=[x, pu[1] - 1.5, pu[2] - 2])


braco("arm_left", 1)
braco("arm_right", -1)


# ----------------------------------------------------------------------------- pernas
def perna(nome, lado):
    qu = [7 * lado, 17, 2.5]            # quadril
    jo = [9.5 * lado, 10, -3]           # joelho para a frente e para fora
    to = [9 * lado, 3, 1]               # tornozelo, em cima do pé
    p = m.osso(nome, pivo=qu, pai="root")
    pele_coxa = [base("pele"), listras_de((0, 1, 0), 5.5, 0.9, so_em_cima=nao_frente, semente=5)]
    junta(p, [qu[0] + 0.5 * lado, qu[1] - 1, qu[2] - 0.5], [9, 9, 10], pele_coxa, raio=2.5)     # quadril
    p.segmento(qu, jo, 9, 10.5, pele_coxa, raio=2.5, arestas="y", sobra=2)                     # coxa
    junta(p, jo, [7, 7, 7], [base("pele")], raio=1.5)                                           # joelho
    p.segmento(jo, to, 5.5, 5.5, [base("pele")], sobra=1.5)                                    # canela
    junta(p, [to[0], to[1] + 0.5, to[2]], [5.5, 4, 5.5], [base("pele")])                       # tornozelo
    p.cubo_arredondado([to[0] - 3.5, 0, to[2] - 9], [7, 3, 11], [base("pele"),
                       gradiente(1, 0, 3, -0.6, 0.3)], raio=1, arestas="verticais")        # pé
    for k in (-1, 0, 1):
        x = to[0] + k * 2.3
        p.cubo([x - 1, 0, to[2] - 12], [2, 2.5, 3.5], [base("garra"),
               afinar("-z", largura_ponta=0.0, curva=0.8, apoio="y")])
    p.cubo([to[0] - 0.75, 0, to[2] + 2], [1.5, 1.5, 2.5], [base("garra"), afinar("+z", apoio="y")])


perna("leg_left", 1)
perna("leg_right", -1)

# ----------------------------------------------------------------------------- cauda (3 gomos + ponta)
lis_cauda = listras_de((0, 0, 1), 4.8, 1.0, so_em_cima=nao_baixo, semente=9)
cauda = m.osso("tail", pivo=[0, 17, 6], pai="body")
cauda.segmento([0, 17, 6], [0, 17, 15], 12, 11, [base("pele"), lis_cauda,
               onde(lambda c: c.n[1] < -0.6, mat="barriga")], raio=2.5, arestas="y", sobra=1.5)
ponta = m.osso("tail_tip", pivo=[0, 17, 15], pai="tail")
ponta.segmento([0, 17, 15], [0, 20.5, 24], 8.5, 8, [base("pele"), lis_cauda], raio=1.5, arestas="y", sobra=1.5)
fim = m.osso("tail_end", pivo=[0, 20.5, 24], pai="tail_tip")
fim.segmento([0, 20.5, 24], [0, 26, 31], 5.5, 5, [base("pele"), lis_cauda], sobra=1.5)
fim.segmento([0, 26, 31], [0, 29.5, 34.5], 3.5, 3.5, [base("pele")], sobra=0.5)     # ponta (sem recorte: não vira "garfo")

# ----------------------------------------------------------------------------- animações
anims = bipede(peso=1.4)
d = anims["idle"]["animation_length"]
anims["idle"]["bones"]["tail_tip"] = {"rotation": onda(4, d, eixo=1, fase=60)}
anims["idle"]["bones"]["tail_end"] = {"rotation": onda(5, d, eixo=1, fase=120)}
anims["idle"]["bones"]["jaw"] = {"rotation": onda(3, d, deslocamento=3)}
w = anims["walk"]["animation_length"]
anims["walk"]["bones"]["tail_tip"] = {"rotation": onda(7, w, eixo=1, fase=150)}
anims["walk"]["bones"]["tail_end"] = {"rotation": onda(8, w, eixo=1, fase=210)}
a = anims["attack"]["animation_length"]
anims["attack"]["bones"]["jaw"] = {"rotation": chaves({0: [0, 0, 0], a * 0.3: [30, 0, 0], a * 0.7: [30, 0, 0],
                                                       a: [0, 0, 0]}, True)}
for nome, an in anims.items():
    m.animacao(nome, an["animation_length"], an["bones"], an["loop"])

if __name__ == "__main__":
    finalizar(m, refs=("Greymon_Model_DSR.png", "Greymon_front.png", "lado_movie_ereto.png"),
              estilo="0005_charmeleon")
