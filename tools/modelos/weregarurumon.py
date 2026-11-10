"""
WereGarurumon: lobisomem em pé, medido nos modelos oficiais (New Century de frente, SC e DSR em 3/4).
Mesmo método aprovado: esqueleto, juntas fechadas, corpo CHEIO (nada esquelético), um olho por lado
com pupila e brilho, dentes fora da mandíbula, cores vivas e lisas, desenhos só em faces lisas.

Medidas (H = 34 unidades até o topo da cabeça, sem a juba):
  cabeça de lobo ~0,2 H com focinho, nariz preto, olhos laranja com pupila e marca azul; orelhas
         pontudas; juba de mechas brancas com pontas azuis para cima e para trás
  ombros largos (~0,45 H); peito de pelo branco com cicatriz costurada; alça de couro na diagonal
         (do ombro esquerdo dele até o quadril direito); OMBREIRA de couro grande no ombro esquerdo (+X)
  braço esquerdo (+X) com manga azul-escura e tiras de couro; braço direito de pelo listrado com
         munhequeira branca; mãos de pelo com garras magenta; braços compridos (até o meio da coxa)
  cinto de couro com fivela; calça jeans azul com caveira na coxa esquerda e joelheiras de couro,
         barra desfiada; pés brancos ENORMES com 3 garras magenta grandes
  cauda branca curta e cheia
"""
from comum import *

m = Modelo("weregarurumon", densidade=2, escala=1.3)   # 30% maior (pedido do usuário)
m.material("pelo", rampa_manual("#7A80BE", "#949ADA", "#AEB4EE", "#C8CDFA", "#DEE2FF", "#F0F2FF", base=4),
           estilo="limpo", ruido=0.12)
m.material("listra", rampa_manual("#140F36", "#221C50", "#312A65", "#463E86", base=2), estilo="liso",
           aresta_clara=0, aresta_escura=0, volume=0.15, oclusao=0.3)
m.material("jeans", rampa_manual("#121E36", "#1C2E52", "#284474", "#365A96", "#4A72B4", base=3), estilo="limpo",
           ruido=0.15)
m.material("couro", rampa_manual("#3E1E06", "#5E300C", "#844616", "#A85E22", "#C87A34", "#E09A50", base=3),
           estilo="limpo", ruido=0.1, aresta_clara=0.5)
m.material("prata", rampa_manual("#3A3E46", "#5E646E", "#868E9A", "#B0B8C2", "#DCE2E8", base=3), estilo="liso",
           aresta_clara=0.7)
m.material("garra", rampa_manual("#4A0A2C", "#7A1848", "#A82866", "#D8448E", "#F07AB8", base=3), estilo="liso",
           aresta_clara=0.4)
m.material("dente", rampa_manual("#B8B4B0", "#DAD6D2", "#F2F0EC", "#FFFFFF", base=2), estilo="liso", volume=0.2)
m.material("boca", rampa_manual("#3A0810", "#5E141E", "#8A2430", "#B03A44", base=1), estilo="liso", volume=0,
           aresta_clara=0, aresta_escura=0)

CORES_OLHO = {"b": "#312A65", "k": "#1E1848", "A": "#FFB038", "a": "#E07A18", "P": "#120806", "W": "#FFFFFF"}
OLHO_FRENTE = """
bb
kk
aA
aA
aa
.k
"""
OLHO_LADO = """
bbbb.
kkkkk
AWPPk
APPAk
aAAak
.kkk.
"""
CAVEIRA = """
..wwww..
.wwwwww.
.wkwwkw.
.wwwwww.
..wkkw..
w..ww..w
.ww..ww.
w......w
"""


def listras_pelo(eixo=(0, 1, 0), periodo=4, largura=1.3, semente=3, cond=None):
    conds = [listras_eixo(eixo, periodo, largura, ondulacao=0.9, eixo_onda=(1, 0, 1), freq_onda=0.3),
             lambda c: fbm(c.p, 3.0, 1, semente=semente) > -0.4]
    if cond is not None:
        conds.append(cond)
    return onde(e_(*conds), mat="listra")


def mecha(osso, de, ate, largura=3.5):
    """Mecha da juba: espinho largo de pelo que afina, branco com a ponta azul-escura."""
    return osso.segmento(de, ate, largura, 2.5, [base("pelo"), gradiente(1, de[1], ate[1], -0.3, 0.5),
                                                   onde(local(1, 0.62, 1.01), mat="listra"),
                                                   afinar("+y", largura_ponta=0.0, curva=1.3)], sobra=0.5)


# ----------------------------------------------------------------------------- esqueleto e tronco
root = m.osso("root")
corpo = m.osso("body", pivo=[0, 18, 0], pai="root")
alca = onde(lambda c: (np.abs((c.y - 22.5) - c.x * 0.85) < 1.0) & (c.y > 19.5), mat="couro")   # alça diagonal
# CICATRIZ costurada: corte comprido em diagonal no peito direito dele (-X) com pontos atravessados
CICATRIZ = """
k.........
kk.k......
.kkkk.k...
...k.kkkk.
.......kkk
.........k
"""
cicatriz = decalque(CICATRIZ, {"k": "#4A3C6E"}, centro=[-3.25, 26.75, -4], profundidade=0.4)
# tronco CHEIO (o usuário achou o primeiro esquelético)
corpo.cubo_arredondado([-5.5, 19.5, -3.5], [11, 6, 7], [base("pelo"), alca], raio=1.5, arestas="verticais")    # abdômen
corpo.cubo_arredondado([-7, 24.5, -4], [14, 7, 8], [base("pelo"), alca, cicatriz,
                       listras_pelo((0, 1, 0), 4, 1.1, cond=lambda c: np.abs(c.n[0]) > 0.5)],
                       raio=2, arestas="verticais")                                                 # peito largo
corpo.cubo([-1.25, 21, -4], [2.5, 2, 0.5], [base("prata")])                                     # fivela da alça
# PINGENTE: plaquinha de prata numa correntinha, logo abaixo do pescoço
corrente = onde(e_(faces("north"), lambda c: (np.abs(np.abs(c.x) - (c.y - 28) * 0.9) < 0.3) & (c.y > 28)),
                cor="#8A929E")
corpo.cubo([-1, 26.5, -4.25], [2, 2.5, 0.5], [base("prata"), gradiente(1, 26.5, 29, -0.4, 0.6)])     # plaquinha
# cinto e quadril de jeans
corpo.cubo_arredondado([-6, 15, -3.75], [12, 5.5, 7.5], [base("jeans")], raio=1.5, arestas="verticais")
corpo.cubo([-6.25, 19, -4], [12.5, 1.5, 8], [base("couro"), onde(e_(faces("north"), lambda c: np.abs(c.x) < 1.25),
           mat="prata")])                                                                        # cinto
# pescoço peludo e grosso
corpo.segmento([0, 29.5, -0.5], [0, 33, -2], 6, 7, [base("pelo"), corrente], raio=1.5, sobra=1.5)

# ----------------------------------------------------------------------------- cabeça de lobo
cab = m.osso("head", pivo=[0, 32, -1], pai="body")
mand = m.osso("jaw", pivo=[0, 32, -5], pai="head", rotacao=[8, 0, 0])
olhos_w = olhos(OLHO_FRENTE, OLHO_LADO, CORES_OLHO, x_quina=3.5, y=35.5, z_frente=-5)
marca = onde(e_(lambda c: c.n[1] > 0.5, lambda c: np.abs(c.x) < 2 - (c.z + 5) * 0.3), mat="listra")
cab.cubo_arredondado([-3.5, 31.5, -5], [7, 6.5, 7.5], [base("pelo"), marca,
                     listras_pelo((0, 0, 1), 3, 0.9, semente=9, cond=lambda c: np.abs(c.n[0]) > 0.5)] + olhos_w,
                     raio=1.5, arestas="frente")
nariz = onde(ou_(e_(faces("north"), caixa([-1, 33.5, -11], [1, 35, -9])),
                 e_(lambda c: c.n[1] > 0.5, caixa([-1, 33.5, -10.5], [1, 35.5, -9.5]))), cor="#18141E")
cab.cubo_arredondado([-2, 32, -10.5], [4, 3, 6], [base("pelo"), nariz, so_faces("down", base("boca"))],
                     raio=1, arestas="frente")
cab.cubo([-1.5, 31, -9.5], [3, 2, 5], [base("boca")])                                       # fundo da boca
for lado in (1, -1):
    for z in (-9.5, -7.75):
        cab.plano([2.05 * lado, 30.5, z], [0, 1.5, 1.5], [base("dente"), afinar("-y", largura_ponta=0.0)])
mand.cubo_arredondado([-1.5, 30, -9.5], [3, 2, 5.5], [base("pelo"), so_faces("up", base("boca"))],
                      raio=0.5, arestas="frente")
# orelhas pontudas
for lado in (1, -1):
    cone_empilhado(cab, [2.25 * lado, 37.5, -1.5], [(2.5, 1.5, 2), (2, 1.5, 1.5), (1, 1.5, 1)],
                   [base("pelo"), onde(acima(39.5), mat="listra")], rotacao=[-10, 0, -10 * lado])
# juba: mechas para cima e para trás
for x, alto, abre in ((0, 6, 0), (-2, 5, -0.5), (2, 5, 0.5), (-3, 3, -1), (3, 3, 1)):
    mecha(cab, [x, 36, 0], [x + abre * 3.5, 36 + alto, 4.5], 3.5)
for lado in (1, -1):                                                                        # bochechas
    mecha(cab, [3 * lado, 32.5, -2], [6.5 * lado, 31.5, 1.5], 3)


# ----------------------------------------------------------------------------- braços
def braco(nome, lado):
    om = [8 * lado, 28.5, 0]
    co = [9.75 * lado, 21, 0.5]
    pu = [10.75 * lado, 14, -1]
    b = m.osso(nome, pivo=om, pai="body")
    if lado > 0:                                         # esquerdo dele: manga azul + tiras de couro + ombreira
        manga = [base("jeans")]
        antebraco = [base("jeans"), onde(ou_(entre(1, 15.5, 16.5), entre(1, 18, 19)), mat="couro")]
        b.cubo_arredondado([4.5, 25, -5], [8.5, 7.5, 10], [base("couro"), gradiente(1, 25, 32.5, -0.4, 0.6),
                           onde(lambda c: np.abs(c.y - 27) < 0.3, luz=-1.5)], raio=1)            # ombreira
    else:                                                # direito dele: pelo listrado + munhequeira
        manga = [base("pelo"), listras_pelo((0, 1, 0), 3.5, 1.1, semente=13)]
        antebraco = [base("pelo"), listras_pelo((0, 1, 0), 3.5, 1.1, semente=17),
                     onde(entre(1, 14.5, 16), cor="#F4F4F8")]
    junta(b, om, [5.5, 5.5, 5.5] if lado > 0 else [6, 6, 6], manga, raio=1.5)      # (a do lado da ombreira fica por dentro dela)
    b.segmento(om, co, 5, 5, manga, raio=1.5, sobra=1.5)
    junta(b, co, [5, 5, 5], manga, raio=1.5)
    b.segmento(co, pu, 5, 5, antebraco, raio=1.5, sobra=1.5)
    b.cubo_arredondado([pu[0] - 2.75, pu[1] - 4.5, pu[2] - 2.75], [5.5, 5, 5.5], [base("pelo")], raio=1.5)  # mão
    for k in (-1, 0, 1):                                                                       # garras
        x = pu[0] + k * 1.5
        b.cubo([x - 0.5, pu[1] - 6.5, pu[2] - 2.25], [1, 3, 1.5],
               [base("garra"), afinar("-y", largura_ponta=0.2, curva=1.6, apoio="-z")],
               rotacao=[-20, 0, 0], pivo=[x, pu[1] - 3.5, pu[2] - 1.5])


braco("arm_left", 1)
braco("arm_right", -1)


# ----------------------------------------------------------------------------- pernas (jeans)
def perna(nome, lado):
    qu = [3.5 * lado, 17, 0]
    jo = [4.25 * lado, 10, -1.5]
    to = [4.75 * lado, 4, 0.5]
    p = m.osso(nome, pivo=qu, pai="root")
    jeans = [base("jeans")]
    if lado > 0:
        jeans.append(decalque(CAVEIRA, {"w": "#F2EEE4", "k": "#18141E"}, centro=[qu[0] + 0.25, 13.5, -4],
                              profundidade=1))
    p.segmento(qu, jo, 6, 6.5, jeans, raio=1.5, sobra=1.5)                                     # coxa
    junta(p, jo, [5.5, 5.5, 6], [base("jeans")], raio=1.5)
    p.cubo_arredondado([jo[0] - 2.5, jo[1] - 2, jo[2] - 4.25], [5, 4.5, 2.5], [base("couro")], raio=0.5)  # joelheira
    p.segmento(jo, to, 5.5, 5.5, [base("jeans"), onde(abaixo(5.5), mat="pelo")], raio=1.5, sobra=1.5)  # canela
    p.cubo_arredondado([to[0] - 3, 3, to[2] - 3.5], [6, 3.5, 6], [base("pelo")], raio=1)      # tufo do tornozelo
    p.cubo_arredondado([to[0] - 3.25, 0, to[2] - 7.5], [6.5, 3.5, 10], [base("pelo"),
                       gradiente(1, 0, 3.5, -0.5, 0.3)], raio=1, arestas="verticais")             # pé enorme
    for k in (-1, 0, 1):
        x = to[0] + k * 2.1
        p.cubo([x - 1, 0, to[2] - 11], [2, 3, 4], [base("garra"),
               afinar("-z", largura_ponta=0.0, curva=0.9, apoio="y")])


perna("leg_left", 1)
perna("leg_right", -1)

# ----------------------------------------------------------------------------- cauda branca (nasce dentro)
cauda = m.osso("tail", pivo=[0, 17, 2.5], pai="body")
cauda.segmento([0, 17.5, 1.5], [0, 15.5, 5.5], 5, 5, [base("pelo")], raio=1.5, sobra=1.5)
ponta = m.osso("tail_tip", pivo=[0, 15.5, 5.5], pai="tail")
ponta.segmento([0, 15.5, 5.5], [0, 14, 7.5], 3.5, 3.5, [base("pelo"), onde(local(1, 0.5, 1.01), mat="listra")],
               raio=1, sobra=1)

# ----------------------------------------------------------------------------- animações
anims = bipede(peso=1.1)
d = anims["idle"]["animation_length"]
anims["idle"]["bones"]["tail_tip"] = {"rotation": onda(8, d, eixo=1, fase=60)}
anims["idle"]["bones"]["jaw"] = {"rotation": onda(3, d, deslocamento=8)}
a = anims["attack"]["animation_length"]
anims["attack"]["bones"]["jaw"] = {"rotation": chaves({0: [8, 0, 0], a * 0.3: [30, 0, 0], a * 0.7: [30, 0, 0],
                                                       a: [8, 0, 0]}, True)}
for nome, an in anims.items():
    m.animacao(nome, an["animation_length"], an["bones"], an["loop"])

if __name__ == "__main__":
    finalizar(m, refs=("Weregarurumon_newcentury_model.png", "Were_Garurumon_Model_SC.png",
                       "Were_Garurumon_Model_DSR.png"), estilo="0005_charmeleon")
