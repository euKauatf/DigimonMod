"""
MetalGarurumon: o Garurumon todo blindado, medido nas folhas de modelo oficiais (Adventure: "Metal Garurumon
reference art" e "MetalGarurumon.ARMS") e nos modelos 3D. Mesmo método aprovado: esqueleto de quadrúpede,
juntas fechadas, corpo no meio-termo (nem esquelético nem gordão), um olho por lado com pupila e brilho,
dentes fora da mandíbula, cores vivas e lisas.

  cabeça: capacete de metal lilás de lobo, NARIZ VERMELHO redondo, olhos vermelhos, cristas para trás;
          mandíbula branca com dentes
  peito e pescoço com placa DOURADA em gomos; ombros com disco de articulação; caixa dourada nas costas
          com 3 espinhos de metal e um míssil (cone) de cada lado apontando para a frente
  ASAS: duas lâminas douradas compridas, para cima e para trás
  cintura de MOLA escura; quadril de metal com almofada vermelha de cada lado
  pernas: armadura lilás em cima, pelo BRANCO com listras roxas embaixo, patas brancas com garras vermelhas
  cauda: haste de metal fina com lâmina dourada curva na ponta
"""
from comum import *

m = Modelo("metalgarurumon", densidade=2, escala=1.15)
m.material("metal", rampa_manual("#4A4478", "#625C98", "#7E78B6", "#9C96D0", "#BAB4E6", "#D8D4F6", "#F0EEFF", base=3),
           estilo="liso", aresta_clara=0.6, volume=0.4)
m.material("ouro", rampa_manual("#7A5A0C", "#A8801A", "#D4A828", "#F0C840", "#FFE06A", "#FFF09C", base=3),
           estilo="liso", aresta_clara=0.6, volume=0.4)
m.material("pelo", rampa_manual("#7A80BE", "#949ADA", "#AEB4EE", "#C8CDFA", "#DEE2FF", "#F0F2FF", base=4),
           estilo="limpo", ruido=0.1)
m.material("listra", rampa_manual("#3E3470", "#5A4E92", "#7468B0", "#8E84CA", base=1), estilo="liso",
           aresta_clara=0, aresta_escura=0, volume=0.15, oclusao=0.3)
m.material("vermelho", rampa_manual("#5A0A10", "#8A1418", "#C02428", "#E84A44", "#FF7A6A", base=2), estilo="liso",
           aresta_clara=0.6)
m.material("escuro", rampa_manual("#1E2026", "#30343C", "#464C56", "#5E6670", base=1), estilo="liso",
           aresta_clara=0.4)
m.material("aco", rampa_manual("#3A3E46", "#5E646E", "#868E9A", "#B0B8C2", "#DCE2E8", base=3), estilo="liso",
           aresta_clara=0.7)
m.material("dente", rampa_manual("#B8B4B0", "#DAD6D2", "#F2F0EC", "#FFFFFF", base=2), estilo="liso", volume=0.2)
m.material("boca", rampa_manual("#3A0810", "#5E141E", "#8A2430", "#B03A44", base=1), estilo="liso", volume=0,
           aresta_clara=0, aresta_escura=0)

CORES_OLHO = {"k": "#1E1A30", "R": "#FF5A3C", "r": "#C82418", "P": "#140606", "W": "#FFFFFF"}
OLHO_FRENTE = """
kk
rR
rR
kk
"""
OLHO_LADO = """
kkkkk.
RWPPrk
rPPRrk
.kkkkk
"""
listras_pata = lambda semente: onde(e_(listras_eixo((0, 1, 0), 2.5, 0.75, ondulacao=0.5, eixo_onda=(1, 0, 1)),  # noqa: E731
                                        lambda c: fbm(c.p, 3.0, 1, semente=semente) > -0.5), mat="listra")

# ----------------------------------------------------------------------------- tronco
root = m.osso("root")
corpo = m.osso("body", pivo=[0, 13, 0], pai="root")
# TRONCO DOURADO (peito, barriga e pescoço amarelos, como no modelo oficial); a armadura lilás fica só
# nos ombros, no quadril e nas pernas
gomos = onde(lambda c: np.abs((c.y - 10.5) % 2) < 0.3, luz=-1.5)
corpo.cubo_arredondado([-6, 8, -10.5], [12, 10, 10.5], [base("ouro"), gradiente(1, 8, 18, -0.4, 0.4)], raio=2.5)  # peito
corpo.cubo_arredondado([-6.5, 10.5, -11.5], [13, 8.5, 6], [base("ouro"), gomos], raio=2)            # placa em gomos
corpo.cubo_arredondado([-4, 10, -1], [8, 6.5, 4.5], [base("escuro"), onde(listras(2, 1.5, 0.6), luz=1.5)],
                       raio=2, arestas="z")                                                      # cintura de mola
corpo.cubo_arredondado([-5.5, 9, 2.5], [11, 8.5, 8], [base("metal")], raio=2.5)                     # quadril
for lado in (1, -1):
    x0 = 5.25 if lado > 0 else -6
    corpo.cubo([x0, 10.5, 4.5], [0.75, 5, 3], [base("vermelho"), gradiente(1, 10.5, 15.5, -0.4, 0.5)])     # almofada vermelha
# caixa dourada nas costas com 3 espinhos e mísseis para a frente
corpo.cubo_arredondado([-3, 17, -7], [6, 3, 6.5], [base("ouro"), gomos], raio=0.5)
for x in (-1.5, 0, 1.5):
    cone_empilhado(corpo, [x, 20, -4], [(1.5, 1, 1.5), (1, 1.5, 1), (0.5, 1, 0.5)], [base("aco")])
for lado in (1, -1):
    corpo.segmento([3.25 * lado, 18.5, -5], [3.25 * lado, 18.5, -10.5], 2.5, 2.5,
                   [base("aco"), gradiente(2, -10.5, -5, 0.8, -0.3), afinar("+y", largura_ponta=0.1)], sobra=0.5)

# ----------------------------------------------------------------------------- cabeça
# Cabeça de lobo de metal em CUNHA: crânio baixo que continua direto no focinho comprido (uma forma só,
# sem degrau), nariz vermelho embutido na ponta, mandíbula branca, disco preto atrás do olho, cristas.
pescoco_dourado = [base("ouro"), onde(lambda c: np.abs((c.y - 14) % 1.75) < 0.3, luz=-1.5)]
corpo.segmento([0, 14, -8], [0, 19, -11.5], 7, 6.5, pescoco_dourado, raio=1.5, sobra=1.5)        # pescoço dourado
cab = m.osso("head", pivo=[0, 19, -11.5], pai="body")
mand = m.osso("jaw", pivo=[0, 18, -14], pai="head", rotacao=[10, 0, 0])
OLHO_SO_LADO = """
kkkkk.
kRWPrk
kRPPrk
.kkkk.
"""
olhos_m = [decalque(OLHO_SO_LADO, CORES_OLHO, centro=[3.5, 21, -15], direcao=(1, 0, 0), profundidade=0.4),
           decalque(espelhar_arte(OLHO_SO_LADO), CORES_OLHO, centro=[-3.5, 21, -15], direcao=(-1, 0, 0),
                    profundidade=0.4)]
cab.cubo_arredondado([-3.5, 18, -17], [7, 5, 7.5], [base("metal"), gradiente(1, 18, 23, -0.4, 0.5)] + olhos_m,
                     raio=1.5, arestas="frente")                                                  # crânio
cab.segmento([0, 20.25, -15], [0, 19.75, -24], 5.5, 4, [base("metal"), gradiente(2, -24, -15, 0.3, -0.2)],
             raio=0.5, sobra=0.5)                                                                 # focinho
cab.cubo([-1, 20, -25], [2, 1.5, 1.5], [base("vermelho"), gradiente(1, 20.5, 22, -0.3, 0.6)])  # nariz
cab.cubo_arredondado([-4, 18.5, -12.5], [8, 3.5, 3.5], [base("escuro"),
                     onde(lambda c: np.abs(c.n[0]) > 0.5, luz=1)], raio=1, arestas="x")          # disco preto
cab.cubo([-2, 17.25, -23], [4, 1.5, 9], [base("boca")])                                           # fundo da boca
for lado in (1, -1):
    for z in (-23, -21, -19):
        cab.plano([2.8 * lado, 16.75, z], [0, 1.5, 1.5], [base("dente"), afinar("-y", largura_ponta=0.0)])
mand.cubo_arredondado([-2.25, 15.75, -23], [4.5, 2, 9], [base("pelo"), gradiente(1, 15.75, 17.75, -0.4, 0.3),
                      so_faces("up", base("boca"))], raio=0.5, arestas="frente")                 # mandíbula branca
for lado in (1, -1):                                                                             # cristas para trás
    cab.segmento([2 * lado, 22.25, -14.5], [3.5 * lado, 24.5, -9.5], 2, 1, [base("metal"),
                 gradiente(1, 22, 24.5, 0, 0.8)], sobra=0.5)
    cab.segmento([3.25 * lado, 21, -13], [5 * lado, 21.5, -9], 1.5, 1, [base("metal")], sobra=0.5)


# ----------------------------------------------------------------------------- pernas
def perna_frente(nome, lado):
    om = [4.75 * lado, 11, -6]
    co = [5 * lado, 6.5, -6]
    pu = [5 * lado, 2.5, -6.5]
    p = m.osso(nome, pivo=om, pai="body")
    p.cubo_arredondado([om[0] - 1 + 1.25 * lado, 9.5, -9], [2, 6, 6], [base("metal"),
                       onde(lambda c: np.hypot(c.y - 12.5, c.z + 6) < 1.4, mat="escuro")], raio=1.5, arestas="x")  # disco
    junta(p, om, [5.5, 6, 6], [base("metal")], raio=1.5)
    p.segmento(om, co, 5, 5.5, [base("metal")], raio=1.5, sobra=1.5)
    junta(p, co, [4.5, 4.5, 4.5], [base("escuro")], raio=1)
    p.segmento(co, pu, 4.5, 4.5, [base("pelo"), listras_pata(3 + lado)], raio=1, sobra=1.5)
    p.cubo_arredondado([pu[0] - 3, 0, pu[2] - 3.5], [6, 2.5, 6], [base("pelo")], raio=1, arestas="verticais")
    for k in (-1, 0, 1):
        x = pu[0] + k * 2
        p.cubo([x - 0.75, 0, pu[2] - 6], [1.5, 2, 2.5], [base("vermelho"), afinar("-z", largura_ponta=0.0, apoio="y")])


def perna_tras(nome, lado):
    qu = [4.75 * lado, 12, 7]
    jo = [5 * lado, 7.5, 5]
    ja = [5 * lado, 4, 8.5]
    pe = [5 * lado, 2.5, 7]
    p = m.osso(nome, pivo=qu, pai="body")
    junta(p, [qu[0], qu[1] - 0.5, qu[2]], [6.5, 7.5, 8], [base("metal")], raio=2)                 # coxa blindada
    p.segmento(qu, jo, 5.5, 6.5, [base("metal")], raio=1.5, sobra=1.5)
    junta(p, jo, [4.5, 4.5, 4.5], [base("escuro")], raio=1)
    p.segmento(jo, ja, 4.5, 4.5, [base("pelo"), listras_pata(7 + lado)], raio=1, sobra=1.5)
    p.segmento(ja, pe, 4, 4, [base("pelo")], raio=1, sobra=1.5)
    p.cubo_arredondado([pe[0] - 3, 0, pe[2] - 4.5], [6, 2.5, 6], [base("pelo")], raio=1, arestas="verticais")
    for k in (-1, 0, 1):
        x = pe[0] + k * 2
        p.cubo([x - 0.75, 0, pe[2] - 7], [1.5, 2, 2.5], [base("vermelho"), afinar("-z", largura_ponta=0.0, apoio="y")])


perna_frente("leg_front_left", 1)
perna_frente("leg_front_right", -1)
perna_tras("leg_back_left", 1)
perna_tras("leg_back_right", -1)


# ----------------------------------------------------------------------------- asas (lâminas douradas)
def asa(lado):
    nome = "wing_left" if lado > 0 else "wing_right"
    w = m.osso(nome, pivo=[2.5 * lado, 18.5, -4], pai="body")
    cot = [6 * lado, 24, 0]
    w.segmento([2.5 * lado, 18, -4.5], cot, 2.5, 2, [base("ouro"), gomos], sobra=1)
    meio = [7.5 * lado, 26.5, 8.5]
    w.segmento(cot, meio, 3, 1, [base("ouro"), gradiente(2, 0, 9, -0.3, 0.4)], sobra=0.5)         # lâmina
    w.segmento(meio, [8.5 * lado, 27.5, 14], 2, 1, [base("ouro"), gradiente(2, 8, 14, 0.3, 1)], sobra=0.5)  # ponta


asa(1)
asa(-1)

# ----------------------------------------------------------------------------- cauda
cauda = m.osso("tail", pivo=[0, 14.5, 9.5], pai="body")
cauda.segmento([0, 14.5, 9], [0, 16, 17], 1.5, 1.5, [base("aco")], sobra=1)
ponta = m.osso("tail_tip", pivo=[0, 16, 17], pai="tail")
furos = onde(lambda c: (np.abs(c.n[0]) > 0.5) & ((np.abs(c.z - 19.5) < 0.4) | (np.abs(c.z - 20.75) < 0.4) |
                                                  (np.abs(c.z - 22) < 0.4)) & (np.abs(c.y - 17.5) < 0.6), mat="escuro")
ponta.segmento([0, 16, 17], [0, 18, 22.5], 1, 3.5, [base("ouro"), furos], sobra=0.5)              # lâmina dourada
ponta.segmento([0, 18, 22.5], [0, 20.5, 25.5], 1, 2, [base("ouro"), gradiente(1, 18, 20.5, 0.2, 1)], sobra=0.5)

# ----------------------------------------------------------------------------- animações
anims = quadrupede(peso=1.2)
d = anims["idle"]["animation_length"]
w = anims["walk"]["animation_length"]
anims["idle"]["bones"]["wing_left"] = {"rotation": onda(4, d, eixo=2)}
anims["idle"]["bones"]["wing_right"] = {"rotation": onda(4, d, eixo=2, fase=180)}
anims["walk"]["bones"]["wing_left"] = {"rotation": onda(8, w, eixo=2)}
anims["walk"]["bones"]["wing_right"] = {"rotation": onda(8, w, eixo=2, fase=180)}
anims["idle"]["bones"]["jaw"] = {"rotation": onda(3, d, deslocamento=10)}
a = anims["attack"]["animation_length"]
anims["attack"]["bones"]["jaw"] = {"rotation": chaves({0: [10, 0, 0], a * 0.3: [35, 0, 0], a * 0.7: [35, 0, 0],
                                                       a: [10, 0, 0]}, True)}
for nome, an in anims.items():
    m.animacao(nome, an["animation_length"], an["bones"], an["loop"])

if __name__ == "__main__":
    finalizar(m, refs=("Metal_Garurumon_Model_DSR.png", "Metalgarurumon_newcentury_model.png",
                       "Metal_Garurumon_Model_SC.png"), estilo="0004_charmander")
