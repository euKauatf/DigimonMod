"""
WarGreymon (v2): guerreiro de armadura, medido nos modelos oficiais (New Century, SC, Encounters, anime).
Regras do usuário: poucas peças grandes e encostadas, um olho por lado, nada que a referência não tenha,
juntas fechadas, cores VIVAS e LISAS.

Medidas (H = topo do capacete sem chifres ~ 37 unidades = 2,3 blocos):
  cabeça pequena e estreita (altura 0,2 H, largura 0,15 H): capacete de prata com máscara escura,
         protetor de focinho, olhos verdes em fenda, chifre central e 2 chifres de touro; juba vermelha
  ombreiras DOURADAS enormes (cada uma ~0,19 H de largura, ~0,27 H de altura), com espinho de ponta vermelha;
         largura total nos ombros ~0,55 H
  peito de prata em gomos com 3 cruzes vermelhas no meio e 2 faixas vermelhas nos ombros
  cinto azul-marinho e placa de prata na frente (com faixa vermelha) descendo até o meio da coxa
  braços: manopla dourada grande (Dramon Destroyer) do cotovelo ao punho e 3 garras ENORMES (~0,27 H)
  pernas: 0,47 H; coxa laranja, joelheira de prata, caneleira vermelha com placa de prata na frente e
          argolas vermelhas do lado; pé laranja grande com 3 garras brancas e esporão
  escudo (Brave Shield) nas costas: dois painéis dourados grandes, azul-marinho por dentro
  cauda laranja curta
"""
from comum import *

m = Modelo("wargreymon", densidade=2)
m.material("pele", rampa_manual("#8A300A", "#B44412", "#DA5E18", "#F2761E", "#FF8C24", "#FFA83C", "#FFC45C", base=4),
           estilo="limpo", ruido=0.12)
m.material("ouro", rampa_manual("#7A5208", "#A8780C", "#D4A010", "#F0C41C", "#FFDC40", "#FFF080", base=3),
           estilo="liso", aresta_clara=0.7, volume=0.4)
m.material("prata", rampa_manual("#2E3238", "#4A5058", "#6C7480", "#929CA8", "#B8C0CA", "#DCE2E8", "#F6F8FA", base=4),
           estilo="liso", aresta_clara=0.7, volume=0.4)
m.material("vermelho", rampa_manual("#4A0C08", "#741A10", "#A42818", "#CC3C28", "#E8604A", base=2),
           estilo="liso", aresta_clara=0.4)
m.material("marinho", rampa_manual("#0C0E1E", "#161A32", "#22284A", "#30385E", "#424C76", base=2), estilo="liso",
           aresta_clara=0.3)
m.material("cabelo", rampa_manual("#4A100A", "#741C12", "#9C2C1C", "#C2402A", "#E05A3A", base=2), estilo="limpo",
           ruido=0.1)
m.material("garra", rampa_manual("#22262C", "#3A4048", "#5A626E", "#8A929E", "#B8C0CA", "#E0E6EC", base=2),
           estilo="liso", aresta_clara=0.6, volume=0.4)
m.material("unha", rampa_manual("#9C96A0", "#C4BEC6", "#E6E1E8", "#FAF7FA", "#FFFFFF", base=3), estilo="liso",
           aresta_clara=0.3)

root = m.osso("root")
corpo = m.osso("body", pivo=[0, 17.5, 0], pai="root")

# ----------------------------------------------------------------------------- tronco
CRUZ = """
vv...vv
.vv.vv.
..vvv..
.vv.vv.
vv...vv
"""
cruzes = [decalque(CRUZ, {"v": "vermelho"}, centro=[0, y, -4], profundidade=2) for y in (29, 26, 23)]
gomos = onde(e_(lambda c: c.n[2] < -0.5, lambda c: (np.abs(c.x) < 0.25) | (np.abs((c.y - 20) % 2.5) < 0.25)),
             luz=-1.2)
corpo.cubo_arredondado([-4.5, 19.5, -3], [9, 5, 6], [base("prata"), gomos], raio=1, arestas="verticais")  # abdômen
corpo.cubo_arredondado([-5.5, 23.5, -3.5], [11, 7.5, 7], [base("prata"), gradiente(1, 23.5, 31, -0.4, 0.5), gomos]
                       + cruzes, raio=1.5, arestas="verticais")                                          # peito
corpo.cubo_arredondado([-2.5, 19.5, -3.5], [5, 4, 1], [base("prata")] + cruzes, raio=0.5)              # cruz de baixo
for lado in (1, -1):                                                        # faixas vermelhas sobre os ombros
    corpo.segmento([2.5 * lado, 30.5, -3.75], [4.5 * lado, 27, -3.75], 2, 0.5, [base("vermelho")], sobra=0.5)
corpo.cubo_arredondado([-5.5, 16.5, -3], [11, 3.5, 6], [base("marinho"), onde(listras(0, 2.5, 0.5), luz=1)],
                       raio=0.5, arestas="verticais")                                                   # cinto
corpo.cubo([-1.75, 10.5, -3.6], [3.5, 6.5, 1], [base("prata"), onde(entre(1, 12.5, 14), mat="vermelho"),
           gradiente(1, 10.5, 17, -0.5, 0.4)])                                                            # placa
# pescoço de dragão: grosso, azul-marinho em gomos, saindo do peito para cima e para a frente
corpo.segmento([0, 28.5, -0.5], [0, 33.5, -1], 5, 5, [base("marinho"), onde(listras(1, 1.5, 0.5),
               luz=1)], raio=1, sobra=1.5)

# ----------------------------------------------------------------------------- escudo nas costas
esc = m.osso("shield", pivo=[0, 26, 3.5], pai="body")
for lado in (1, -1):
    x0 = 0 if lado > 0 else -10
    dentro = onde(lambda c: c.n[2] < -0.5, mat="marinho")
    esc.cubo_arredondado([x0, 12, 3.5], [10, 21, 2], [base("ouro"), gradiente(1, 12, 33, -0.6, 0.6), dentro,
                         onde(lambda c: (np.abs(np.abs(c.x) - 7.5) < 0.3) & (c.n[2] > 0.5), luz=-1.5)],
                         raio=1, arestas="z", rotacao=[0, -20 * lado, 0], pivo=[0, 22, 4.5])

# ----------------------------------------------------------------------------- cabeça
# Capacete de CRÂNIO DE DRAGÃO (não de humano): igual ao do Greymon, mais fino. Crânio + focinho
# comprido que desce para a frente, face/mandíbula escura embaixo, um olho verde de cada lado sob a
# aba do capacete, chifre de rinoceronte no focinho, 2 chifres de touro atrás, juba vermelha caindo.
cab = m.osso("head", pivo=[0, 33.5, -1], pai="body")
OLHO_LADO = """
sss.
GGk.
"""
cores_olho = {"s": "#3A4048", "G": "#7CF080", "k": "#0C0E1E"}
olhos_cab = [decalque(OLHO_LADO, cores_olho, centro=[3, 35.75, -4.25], direcao=(1, 0, 0), profundidade=0.4),
             decalque(espelhar_arte(OLHO_LADO), cores_olho, centro=[-3, 35.75, -4.25], direcao=(-1, 0, 0),
                      profundidade=0.4)]
cab.cubo_arredondado([-3, 33.5, -5.5], [6, 5.5, 7], [base("prata"), gradiente(1, 33.5, 39, -0.5, 0.6),
                     onde(lambda c: (np.abs(c.x) < 0.25) & (c.y > 37), luz=-1.5)] + olhos_cab,
                     raio=1, arestas="frente")                                                  # crânio
cab.segmento([0, 36.5, -4.5], [0, 35.25, -9], 5, 4, [base("prata"), gradiente(2, -9, -4.5, -0.4, 0.4),
             onde(lambda c: c.n[1] < -0.5, mat="marinho")], raio=1, sobra=1)                    # focinho
cab.cubo_arredondado([-2.25, 31.5, -8.5], [4.5, 3, 5.5], [base("marinho"), gradiente(1, 31.5, 34.5, -0.6, 0.3)],
                     raio=0.5, arestas="frente")                                                # face/mandíbula
cab.cadeia([[0, 36.5, -7], [0, 39, -7], [0, 41.5, -6.25], [0, 43.5, -5.25]], [(3, 3), (2, 2), (1, 1)],
           [base("prata"), gradiente(1, 36.5, 43.5, 0, 1)], sobra=0.5)                          # chifre do focinho
for lado in (1, -1):
    aneis = onde(lambda c: np.abs(c.y - 38.5) < 0.4, mat="marinho")
    cab.cadeia([[2.5 * lado, 37.5, -0.5], [5.5 * lado, 38, 0], [6.5 * lado, 41.5, 0]], [(2, 2), (1.5, 1.5)],
               [base("prata"), gradiente(1, 37, 42, 0, 1), aneis], sobra=0.5)                   # chifres de touro
    cab.segmento([2.5 * lado, 37, 0.5], [4 * lado, 31.5, 4], 2.5, 3.5,
                 [base("cabelo"), gradiente(1, 30, 37, -0.4, 0.5)], sobra=0.5)                   # juba vermelha
cab.segmento([0, 38, 0], [0, 33.5, 4.5], 4, 2.5, [base("cabelo"), gradiente(1, 31, 38, -0.4, 0.5)], sobra=0.5)


# ----------------------------------------------------------------------------- braços
def braco(nome, lado):
    om = [7 * lado, 28.5, 0]
    co = [10.5 * lado, 21.5, 0]
    pu = [11.5 * lado, 14, -1]
    b = m.osso(nome, pivo=om, pai="body")
    xo = 5 if lado > 0 else -13
    b.cubo_arredondado([xo, 20.5, -4.5], [8, 12, 9], [base("ouro"), gradiente(1, 22, 32, -0.5, 0.6),
                       onde(lambda c: c.n[1] < -0.5, mat="marinho")], raio=2)                  # ombreira
    cone_empilhado(b, [(xo + 4 + 2 * lado), 31.5, 0], [(3, 1.5, 3), (2.5, 1.5, 2.5), (1.5, 2, 1.5), (1, 1.5, 1)],
                   [base("ouro"), onde(acima(35), mat="vermelho")], rotacao=[0, 0, 35 * lado])   # espinho p/ fora
    b.segmento(om, co, 3.5, 3.5, [base("pele")], sobra=1.5)                                     # braço
    junta_ = b.cubo_arredondado([co[0] - 2.25, co[1] - 2, co[2] - 2.25], [4.5, 4, 4.5], [base("pele")], raio=1)
    b.segmento(co, pu, 5.5, 6, [base("ouro"), onde(entre(1, 14, 15.5), mat="prata"),
               onde(e_(entre(1, 17, 18), lambda c: c.n[0] * lado > 0.5), mat="marinho")], raio=1.5, sobra=2.5)
    for k, dx in enumerate((-2, 0, 2)):                                                         # garras enormes
        raiz = [pu[0] + dx, pu[1] - 0.5, pu[2] - 0.5]
        pt = [raiz[0] + dx * 0.9 + 1.5 * lado, raiz[1] - 10, raiz[2] - 2.5]
        b.segmento(raiz, pt, 3, 2, [base("garra"), gradiente(1, pt[1], raiz[1], 1, -0.6),
                   afinar("+y", largura_ponta=0.1, curva=2.2)], sobra=0.5)


braco("arm_left", 1)
braco("arm_right", -1)


# ----------------------------------------------------------------------------- pernas
def perna(nome, lado):
    qu = [4 * lado, 17.5, 0]
    jo = [4.5 * lado, 11, -1]
    to = [4.5 * lado, 3.5, 0.5]
    p = m.osso(nome, pivo=qu, pai="root")
    p.cubo_arredondado([qu[0] - 3, 15, -3], [6, 5, 6], [base("pele")], raio=1.5)                   # quadril
    p.segmento(qu, jo, 5, 5.5, [base("pele")], raio=1, sobra=1.5)                                    # coxa
    p.cubo_arredondado([jo[0] - 2.75, jo[1] - 2.5, jo[2] - 2.75], [5.5, 5, 5.5], [base("pele")], raio=1)  # junta do joelho
    p.cubo_arredondado([jo[0] - 3, jo[1] - 2, jo[2] - 3.5], [6, 4, 4], [base("prata"),
                       gradiente(1, jo[1] - 2, jo[1] + 2, -0.4, 0.6)], raio=1)                     # joelheira
    p.segmento(jo, to, 5.5, 6, [base("vermelho"), gradiente(1, to[1], jo[1], -0.5, 0.4)], raio=1, sobra=1.5)  # caneleira
    p.cubo([to[0] - 2, 4.5, -3.5], [4, 6.5, 1], [base("prata"), gradiente(1, 4.5, 11, -0.5, 0.6)])  # placa da frente
    for k in range(3):                                                                            # argolas do lado
        p.cubo([to[0] + 2.5 * lado - (0 if lado > 0 else 1), 5 + k * 1.75, -1], [1, 1.5, 2.5], [base("vermelho")])
    p.cubo_arredondado([to[0] - 3.5, 0, -6.5], [7, 3.5, 9.5], [base("pele"), gradiente(1, 0, 3.5, -0.6, 0.3)],
                       raio=1, arestas="verticais")                                                # pé
    for k in (-1, 0, 1):
        x = to[0] + k * 2.25
        p.cubo([x - 1, 0, -10], [2, 2.5, 4], [base("unha"), afinar("-z", largura_ponta=0.0, curva=0.8, apoio="y")])
    p.cubo([to[0] - 0.75, 0, 3], [1.5, 1.5, 2.5], [base("unha"), afinar("+z", apoio="y")])


perna("leg_left", 1)
perna("leg_right", -1)

# ----------------------------------------------------------------------------- cauda
cauda = m.osso("tail", pivo=[0, 16.5, 2], pai="body")
cauda.segmento([0, 16.5, 2], [0, 13, 7.5], 4, 4, [base("pele")], raio=1, sobra=1)
ponta = m.osso("tail_tip", pivo=[0, 13, 7.5], pai="tail")
ponta.segmento([0, 13, 7.5], [0, 11.5, 11], 2.5, 2.5, [base("pele")], sobra=0.5)

anims = bipede(peso=1.2)
d = anims["idle"]["animation_length"]
anims["idle"]["bones"]["tail_tip"] = {"rotation": onda(6, d, eixo=1)}
anims["idle"]["bones"]["shield"] = {"rotation": onda(1.5, d, fase=90)}
for nome, an in anims.items():
    m.animacao(nome, an["animation_length"], an["bones"], an["loop"])

if __name__ == "__main__":
    finalizar(m, refs=("Wargreymon_newcentury_model.png", "War_Greymon_Model_SC.png", "War_Greymon_Model_Encounters.png"),
              estilo="0005_charmeleon")
