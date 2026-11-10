"""
Garurumon: lobo quadrúpede branco-lilás com listras azul-escuras, medido nos modelos oficiais (SC de lado,
New Century de frente, DSR). Mesmo método do Agumon/Gabumon: esqueleto, juntas fechadas, poucas peças,
um olho por lado, cores vivas e lisas, desenhos legíveis em 3/4, garganta e cauda sem vão, dentes fora da
mandíbula.

Medidas (cernelha ~17 unidades; corpo ~22 de comprimento; cabeça + focinho ~14):
  cabeça: crânio 8 de largura, focinho comprido e estreito com nariz preto; olhos âmbar nas laterais
          da frente do crânio, com marca azul em cima; boca entreaberta com presas
  juba de LÂMINAS de pelo (brancas, pontas azuis): 2 orelhas-lâmina na cabeça, leque no pescoço,
          lâminas altas nos ombros e menores no quadril
  corpo: peito fundo, cintura fina, quadril; pernas da frente quase retas; de trás com jarrete
  patas com 3 garras magenta grandes; cauda longa e fina, quase horizontal, ponta azul
"""
from comum import *

m = Modelo("garurumon", densidade=2)
m.material("pelo", rampa_manual("#7A80BE", "#949ADA", "#AEB4EE", "#C8CDFA", "#DEE2FF", "#F0F2FF", base=4),
           estilo="limpo", ruido=0.12)
m.material("azul_claro", rampa_manual("#6A78C0", "#8A98DC", "#A6B4F2", "#BCC8FC", "#D2DCFF", base=3),
           estilo="limpo", ruido=0.1)
m.material("listra", rampa_manual("#140F36", "#221C50", "#312A65", "#463E86", base=2), estilo="liso",
           aresta_clara=0, aresta_escura=0, volume=0.15, oclusao=0.3)
m.material("garra", rampa_manual("#3E0818", "#5E0E26", "#7A1735", "#A02848", "#C84A6A", base=3), estilo="liso",
           aresta_clara=0.4)
m.material("dente", rampa_manual("#B8B4B0", "#DAD6D2", "#F2F0EC", "#FFFFFF", base=2), estilo="liso", volume=0.2)
m.material("boca", rampa_manual("#3A0810", "#5E141E", "#8A2430", "#B03A44", base=1), estilo="liso", volume=0,
           aresta_clara=0, aresta_escura=0)

CORES_OLHO = {"b": "#312A65", "k": "#1E1848", "A": "#FFC040", "a": "#E88A1C", "P": "#120806", "W": "#FFFFFF"}
# olho esquerdo dele (+X): 2 colunas na frente (a última encosta na quina) + 5 na lateral.
# PUPILA preta grande (2x2) com brilho branco; contorno e marca azul-escura em cima.
OLHO_FRENTE = """
bb
kk
aA
aA
aa
.k
"""
OLHO_LADO = """
bbbbb.
kkkkkk
AAWPPk
AAPPPk
aAAPAk
.aaakk
"""


def listras_pelo(eixo=(0, 0, 1), periodo=4, largura=1.1, semente=3, cond=None):
    conds = [listras_eixo(eixo, periodo, largura, ondulacao=0.9, eixo_onda=(1, 1, 0), freq_onda=0.3),
             lambda c: fbm(c.p, 3.0, 1, semente=semente) > -0.5]
    if cond is not None:
        conds.append(cond)
    return onde(e_(*conds), mat="listra")


def lamina(osso, de, ate, largura=3):
    """Mecha da juba: espinho de pelo largo (largura x 2) que afina na ponta, branco com a ponta azul-escura.
    (Plano de espessura 0 virava "palito" visto de lado.)"""
    return osso.segmento(de, ate, largura, 2.5, [base("pelo"), gradiente(1, de[1], ate[1], -0.3, 0.5),
                                                 onde(local(1, 0.62, 1.01), mat="listra"),
                                                 afinar("+y", largura_ponta=0.0, curva=1.3)], sobra=0.5)


nao_baixo = lambda c: c.n[1] > -0.5           # noqa: E731

# ----------------------------------------------------------------------------- tronco
root = m.osso("root")
corpo = m.osso("body", pivo=[0, 13, 0], pai="root")
pele_corpo = [base("pelo"), listras_pelo((0, 0, 1), 5, 1.7, cond=nao_baixo)]
# corpo compacto: peito fundo, cintura, quadril (comprimento ~1,4 x altura da perna, como no SC)
corpo.cubo_arredondado([-6.5, 7.5, -10], [13, 11, 10.5], pele_corpo, raio=3.5)               # peito fundo e largo
corpo.cubo_arredondado([-5.5, 8.5, -1.5], [11, 8.5, 7], pele_corpo, raio=3)                  # barriga cheia
corpo.cubo_arredondado([-6, 8.5, 3.5], [12, 9, 8], pele_corpo, raio=3)                       # quadril largo
# JUBA volumosa em volta do pescoço e dos ombros: ela mesma é o pescoço (um segmento de pescoço por
# dentro aparecia pelas quinas arredondadas como um bloco cinza no peito)
corpo.cubo_arredondado([-6.5, 12.5, -12], [13, 9.5, 8.5], [base("pelo"), gradiente(1, 12.5, 22, -0.4, 0.5),
                       onde(lambda c: c.n[2] < -0.5, somar_luz=1.5),
                       listras_pelo((0, 0.4, 1), 3.5, 1.1, semente=31, cond=lambda c: c.n[2] > -0.5)],
                       raio=2, arestas="verticais")
# mechas grandes (pontas azuis) saindo da juba, dos ombros e do quadril (todas nascem DENTRO do corpo)
for lado in (1, -1):
    lamina(corpo, [4 * lado, 18, -9], [9.5 * lado, 22, -6], 4)          # leque do pescoço
    lamina(corpo, [4.5 * lado, 15.5, -9], [10 * lado, 16.5, -5], 4)
    lamina(corpo, [2.5 * lado, 18, -5], [4.5 * lado, 27.5, -1], 4.5)     # ombro alta
    lamina(corpo, [4 * lado, 16, -3], [8 * lado, 23, 1], 4)              # ombro baixa
    lamina(corpo, [2.5 * lado, 15.5, 6.5], [4.5 * lado, 22, 10], 3.5)    # quadril

# ----------------------------------------------------------------------------- cabeça
cab = m.osso("head", pivo=[0, 20.5, -11.5], pai="body")
mand = m.osso("jaw", pivo=[0, 19, -15], pai="head", rotacao=[10, 0, 0])
olhos_g = olhos(OLHO_FRENTE, OLHO_LADO, CORES_OLHO, x_quina=4, y=22.75, z_frente=-17.5)
marca = onde(e_(lambda c: c.n[1] > 0.5, lambda c: np.abs(c.x) < 2.5 - (c.z + 17.5) * 0.4), mat="azul_claro")
cab.cubo_arredondado([-4, 18.5, -17.5], [8, 7, 7], [base("pelo"), marca] + olhos_g, raio=1.5, arestas="frente")
# focinho: em cima azul-claro, nariz preto pequeno na ponta, céu da boca vermelho
nariz = onde(ou_(e_(faces("north"), caixa([-1.25, 21, -25], [1.25, 22.5, -23])),
                 e_(lambda c: c.n[1] > 0.5, caixa([-1.25, 21, -24.5], [1.25, 23, -23.5]))), cor="#18141E")
topo_focinho = onde(lambda c: c.n[1] > 0.5, mat="azul_claro")
cab.cubo_arredondado([-2.5, 19, -24.5], [5, 3.5, 7.5], [base("pelo"), topo_focinho, nariz,
                     so_faces("down", base("boca"))], raio=1, arestas="frente")
cab.cubo([-2, 18, -23.5], [4, 2, 7], [base("boca")])                                        # fundo da boca
DENTE = [base("dente"), afinar("-y", largura_ponta=0.0, curva=1.0)]
for lado in (1, -1):
    for z in (-23.5, -21.5, -19.5):
        cab.plano([2.55 * lado, 17.5, z], [0, 1.5, 1.5], DENTE)
# mandíbula estreita (dentes ficam para fora)
mand.cubo_arredondado([-1.75, 17, -23.5], [3.5, 2, 7.5], [base("pelo"), so_faces("up", base("boca"))],
                      raio=0.5, arestas="frente")
for z in (-23, -21):
    for lado in (1, -1):
        mand.plano([1.8 * lado, 19, z], [0, 1, 1], [base("dente"), afinar("+y", largura_ponta=0.0)])
# orelhas-mecha para cima e para trás
for lado in (1, -1):
    lamina(cab, [2.5 * lado, 24.5, -13], [4.5 * lado, 31.5, -9], 3.5)


# ----------------------------------------------------------------------------- pernas
def perna_frente(nome, lado):
    om = [4.5 * lado, 11, -5.5]
    co = [4.75 * lado, 6.5, -5]
    pu = [4.75 * lado, 2.5, -5.5]
    p = m.osso(nome, pivo=om, pai="body")
    lis = listras_pelo((0, 1, 0), 3.5, 1.1, semente=7 + lado, cond=lambda c: c.n[2] > -0.5)
    junta(p, om, [6.5, 7, 7.5], [base("pelo"), lis], raio=2)                       # ombro gordo
    p.segmento(om, co, 5.5, 6, [base("pelo"), lis], raio=1.5, sobra=1.5)
    junta(p, co, [5, 4.5, 5], [base("pelo")], raio=1)
    p.segmento(co, pu, 4.5, 4.5, [base("azul_claro"), lis], raio=1, sobra=1.5)
    p.cubo_arredondado([pu[0] - 3, 0, pu[2] - 3.5], [6, 2.5, 6], [base("pelo")], raio=1, arestas="verticais")
    for k in (-1, 0, 1):
        x = pu[0] + k * 2
        p.cubo([x - 0.75, 0, pu[2] - 5.5], [1.5, 2, 2.5], [base("garra"),
               afinar("-z", largura_ponta=0.0, curva=0.9, apoio="y")])


def perna_tras(nome, lado):
    qu = [4.5 * lado, 12, 7]
    jo = [4.75 * lado, 7.5, 5]      # joelho para a frente
    ja = [4.75 * lado, 4, 8.5]      # jarrete para trás
    pe = [4.75 * lado, 2.5, 7]
    p = m.osso(nome, pivo=qu, pai="body")
    lis = listras_pelo((0, 1, 0), 3.5, 1.1, semente=11 + lado, cond=lambda c: c.n[2] < 0.5)
    junta(p, [qu[0], qu[1] - 0.5, qu[2]], [7, 8, 8.5], [base("pelo"), lis], raio=2.5)   # coxa gorda
    p.segmento(qu, jo, 6, 7, [base("pelo"), lis], raio=2, sobra=1.5)
    junta(p, jo, [5, 4.5, 5], [base("pelo")], raio=1)
    p.segmento(jo, ja, 4.5, 4.5, [base("pelo"), lis], raio=1, sobra=1.5)
    p.segmento(ja, pe, 4, 4, [base("azul_claro")], raio=1, sobra=1.5)
    p.cubo_arredondado([pe[0] - 3, 0, pe[2] - 4.5], [6, 2.5, 6], [base("pelo")], raio=1, arestas="verticais")
    for k in (-1, 0, 1):
        x = pe[0] + k * 2
        p.cubo([x - 0.75, 0, pe[2] - 6.5], [1.5, 2, 2.5], [base("garra"),
               afinar("-z", largura_ponta=0.0, curva=0.9, apoio="y")])


perna_frente("leg_front_left", 1)
perna_frente("leg_front_right", -1)
perna_tras("leg_back_left", 1)
perna_tras("leg_back_right", -1)

# ----------------------------------------------------------------------------- cauda (nasce dentro do quadril)
lis_cauda = listras_pelo((0, 0, 1), 3, 1, semente=21)
cauda = m.osso("tail", pivo=[0, 15, 9], pai="body")
cauda.segmento([0, 15, 8.5], [0, 16, 16.5], 3, 3, [base("pelo"), lis_cauda], sobra=1.5)
ponta = m.osso("tail_tip", pivo=[0, 16, 16.5], pai="tail")
ponta.segmento([0, 16, 16.5], [0, 16.5, 21.5], 2, 2, [base("pelo"), lis_cauda], sobra=1)
ponta.segmento([0, 16.5, 21.5], [0, 16.5, 24.5], 1.5, 1.5, [base("listra")], sobra=0.5)

# ----------------------------------------------------------------------------- animações
anims = quadrupede(peso=1.1)
d = anims["idle"]["animation_length"]
anims["idle"]["bones"]["tail_tip"] = {"rotation": onda(8, d, eixo=1, fase=60)}
anims["idle"]["bones"]["jaw"] = {"rotation": onda(3, d, deslocamento=10)}
w = anims["walk"]["animation_length"]
anims["walk"]["bones"]["tail_tip"] = {"rotation": onda(12, w, eixo=1, fase=120)}
a = anims["attack"]["animation_length"]
anims["attack"]["bones"]["jaw"] = {"rotation": chaves({0: [10, 0, 0], a * 0.3: [35, 0, 0], a * 0.7: [35, 0, 0],
                                                       a: [10, 0, 0]}, True)}
for nome, an in anims.items():
    m.animacao(nome, an["animation_length"], an["bones"], an["loop"])

if __name__ == "__main__":
    finalizar(m, refs=("Garurumon_Model_SC.png", "Garurumon_newcentury_model.png", "Garurumon_Model_DSR.png"),
              estilo="0004_charmander")
