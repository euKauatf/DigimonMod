"""
Imperialdramon Dragon Mode: mega da linha do Veemon (DNA de Paildramon). Medido na folha de modelo oficial
(Imperialdramon_DM_reference_art.jpg) e nos modelos 3D (SC, DSR, New Century).

Traços que identificam:
  1. dragão de QUATRO patas, baixo na frente: braços da frente ENORMES de armadura preta com friso dourado,
     lâmina dourada saindo do antebraço para trás, mãos com 4 garras douradas grandes
  2. cabeça: elmo BRANCO com um chifre grande branco para cima e chifres laterais; faixa VERMELHA nos olhos
     e no focinho; boca aberta com dentes; juba BRANCA de cabelo para trás
  3. corpo de armadura preta, peito/barriga branco, parte de baixo azul
  4. CANHÃO preto nas costas com boca dourada apontando para a frente; espinhos dourados nas costas
  5. pernas de trás menores, pretas, com tornozeleira dourada e garras douradas
  6. asas VERMELHAS enormes de morcego com a borda serrilhada; cauda azul
Medidas (tamanho base, o modelo sai com escala 1.3): altura das costas ~24, comprimento ~48 sem cauda.
"""
from comum import *

m = Modelo("imperialdramon", densidade=2, escala=1.3)
m.material("preto", rampa_manual("#0E0E14", "#1A1A24", "#282834", "#3A3A48", "#52525F", base=2),
           estilo="liso", aresta_clara=0.5)
m.material("ouro", rampa_manual("#7A5A0A", "#A8820E", "#D2A81E", "#EECB3E", "#FCE47A", base=3), estilo="liso",
           aresta_clara=0.6)
m.material("branco", rampa_manual("#A8ACBC", "#C8CCD8", "#E2E5EE", "#F4F6FA", "#FFFFFF", base=3),
           estilo="limpo", ruido=0.0, volume=0.25)
m.material("vermelho", rampa_manual("#5A1608", "#882410", "#B83A18", "#DC5626", "#F27A44", base=3),
           estilo="liso", aresta_clara=0.5)
m.material("azul", rampa_manual("#0C4A80", "#1462A2", "#1C7EC4", "#2C98DC", "#4EB0EC", "#7EC8F4", base=3),
           estilo="limpo", ruido=0.05)
m.material("asa", rampa_manual("#4A1006", "#6E1A0A", "#962A12", "#BC3E1C", "#DA5A2E", base=3), estilo="limpo",
           ruido=0.0, aresta_clara=0, aresta_escura=0, volume=0.25, oclusao=0.3)
m.material("osso_asa", rampa_manual("#3A0C04", "#5A1408", "#7E200E", "#A23016", base=2), estilo="liso")
m.material("boca", rampa_manual("#3A0810", "#5E1220", "#882034", "#B03048", base=2), estilo="liso")
m.material("dente", rampa_manual("#B8B8C4", "#DCDCE4", "#F4F4F8", "#FFFFFF", base=3), estilo="liso", volume=0)

CORES_OLHO = {"k": "#1A0406", "R": "#E01E2A", "Y": "#FFD84A"}
OLHO = """
kkkk
kRRY
.kkk
"""

root = m.osso("root")
corpo = m.osso("body", pivo=[0, 16, 0], pai="root")

# ----------------------------------------------------------------------------- tronco
# corpo AZUL por baixo; a armadura preta cobre só a parte de cima (costas, ombros) como uma sela
barriga = onde(lambda c: (c.n[2] < -0.5) & (c.y < 18) & (np.abs(c.x) < 5), mat="branco")
armadura = onde(lambda c: (c.y > 16.5 - np.abs(c.z + 5) * 0.08) & (c.n[1] > -0.4), mat="preto")
friso = onde(lambda c: (c.n[1] > -0.4) & (np.abs(c.y - 16.75) < 0.35), mat="ouro")
corpo.cubo_arredondado([-8, 9, -12], [16, 14, 13], [base("azul"), armadura, friso, barriga], raio=3)  # peito
sela = onde(lambda c: (c.y > 16.5) & (c.n[1] > -0.4), mat="preto")
corpo.cubo_arredondado([-7, 10, 0], [14, 11.5, 12], [base("azul"), sela,
                       onde(lambda c: (c.n[1] > -0.4) & (np.abs(c.y - 16.75) < 0.35), mat="ouro")], raio=3)  # quadril
corpo.segmento([0, 17, -10], [0, 19, -14.5], 8, 7, [base("branco"), gradiente(1, 15, 22, -0.4, 0.4)],
               raio=2, sobra=1.5)                                                                   # pescoço
# juba branca de cabelo no pescoço e atrás da cabeça
for lado in (1, -1):
    for de, ate, larg in (([2.5 * lado, 21, -14], [6 * lado, 25, -9], 4), ([3 * lado, 19, -13], [7 * lado, 20, -8], 3.5),
                          ([1 * lado, 22, -12], [2.5 * lado, 26, -6], 3.5)):
        corpo.segmento(de, ate, larg, 2, [base("branco"), gradiente(1, de[1], ate[1], -0.3, 0.5),
                                          afinar("+y", largura_ponta=0.0, curva=1.2)], sobra=0.5)
# espinhos dourados dos dois lados do canhão
for lado in (1, -1):
    for z, h in ((-5, 3.5), (1, 3)):
        corpo.segmento([4.5 * lado, 21.5, z], [5 * lado, 21.5 + h, z + 2], 2.5, 2.5,
                       [base("ouro"), afinar("+y", largura_ponta=0.1)], sobra=0.5)
# canhão nas costas (Positron Laser): tubo preto CENTRALIZADO, boca dourada para a frente
corpo.segmento([0, 23.5, 7], [0, 25.5, -8], 5.5, 5.5, [base("preto"), gradiente(2, -8, 7, 0.3, -0.3)],
               raio=1.5, sobra=1.5)
boca_canhao = onde(lambda c: (c.n[2] < -0.5) & (np.hypot(c.x, c.y - 25.5) < 1.6), cor="#140E06")
corpo.cubo_arredondado([-3.25, 22.25, -10.5], [6.5, 6.5, 2.5], [base("ouro"), boca_canhao], raio=1, arestas="z")

# ----------------------------------------------------------------------------- cabeça
cab = m.osso("head", pivo=[0, 19, -14], pai="body")
mand = m.osso("jaw", pivo=[0, 17.5, -19], pai="head", rotacao=[12, 0, 0])
faixa = onde(lambda c: (c.y > 19.5) & (c.y < 21.75) & (c.n[1] < 0.5), mat="vermelho")
olhos_l = [decalque(OLHO if lado > 0 else espelhar_arte(OLHO), CORES_OLHO, centro=[4 * lado, 20.75, -18.5],
                    direcao=(lado, 0, 0), profundidade=0.4) for lado in (1, -1)]
cab.cubo_arredondado([-4, 17.5, -21], [8, 7, 7], [base("branco"), faixa] + olhos_l, raio=1, arestas="frente")
# focinho vermelho (bico de cima) e céu da boca
cab.cubo_arredondado([-3, 18.5, -26.5], [6, 3, 6], [base("vermelho"), gradiente(2, -26.5, -20.5, 0.4, -0.2),
                     so_faces("down", base("boca"))], raio=1, arestas="frente")
cab.cubo([-2.5, 17.5, -25.5], [5, 1.5, 5], [base("boca")])
for lado in (1, -1):
    for z in (-25.5, -23.5, -21.5):
        cab.plano([2.55 * lado, 16.5, z], [0, 1.5, 1.5], [base("dente"), afinar("-y", largura_ponta=0.0)])
mand.cubo_arredondado([-2.75, 15.5, -25.5], [5.5, 2.5, 8], [base("branco"), so_faces("up", base("boca"))], raio=0.75,
                      arestas="frente")
for lado in (1, -1):
    for z in (-24.5, -22.5):
        mand.plano([2.3 * lado, 17, z], [0, 1.25, 1.25], [base("dente"), afinar("+y", largura_ponta=0.0)])
# chifre grande branco para cima e chifres laterais
cab.cadeia([[0, 23.5, -18.5], [0, 28, -19.5], [0, 31.5, -20.5], [0, 34, -20]], [(3, 4), (2.5, 3), (1.5, 2)],
           [base("branco"), gradiente(1, 23, 35, 0.3, 0.9)], sobra=0.5)
for lado in (1, -1):
    cab.segmento([3.5 * lado, 22.5, -18], [8 * lado, 25.5, -14], 2.5, 1.5, [base("branco"),
                 afinar("+y", largura_ponta=0.1)], sobra=0.5)


# ----------------------------------------------------------------------------- patas da frente enormes
def perna_frente(nome, lado):
    om = [8 * lado, 15, -7]
    co = [9.5 * lado, 8, -9]
    pu = [9.5 * lado, 2.5, -12]
    p = m.osso(nome, pivo=om, pai="body")
    junta(p, om, [7, 8, 8], [base("preto"), onde(lambda c: c.y < 12.5, mat="azul")], raio=2)                                         # ombro
    p.segmento(om, co, 6, 6.5, [base("azul")], raio=1.5, sobra=1.5)
    friso_b = onde(lambda c: np.abs(c.y - 7) < 0.4, mat="ouro")
    p.segmento(co, pu, 7.5, 7.5, [base("preto"), friso_b], raio=2, sobra=2)                   # antebraço grosso
    p.segmento([co[0] + 2.5 * lado, co[1] + 1, co[2] + 1], [co[0] + 4 * lado, co[1] + 7, co[2] + 9], 2.5, 1.5,
               [base("ouro"), afinar("+y", largura_ponta=0.05, curva=1.2)], sobra=0.5)       # lâmina dourada
    p.cubo_arredondado([pu[0] - 4, 0, pu[2] - 5], [8, 3.5, 8], [base("preto"),
                       onde(lambda c: c.n[2] < -0.5, mat="ouro")], raio=1.5, arestas="verticais")  # mão
    for k in (-1.5, -0.5, 0.5, 1.5):                                                         # 4 garras douradas
        x = pu[0] + k * 2
        p.segmento([x, 1.75, pu[2] - 4], [x + k * 1.5, 0.5, pu[2] - 11], 2, 2.5,
                   [base("ouro"), afinar("+y", largura_ponta=0.1)], sobra=0.5)


def perna_tras(nome, lado):
    qu = [6 * lado, 14, 7]
    jo = [6.5 * lado, 8, 4.5]
    ja = [6.5 * lado, 4, 8]
    p = m.osso(nome, pivo=qu, pai="body")
    junta(p, [qu[0], qu[1] - 0.5, qu[2]], [7, 8, 8.5], [base("azul"), onde(lambda c: c.y < 12, mat="preto")], raio=2.5)          # coxa
    p.segmento(qu, jo, 6, 6.5, [base("preto")], raio=2, sobra=1.5)
    junta(p, jo, [5, 4.5, 5], [base("preto")], raio=1)
    p.segmento(jo, ja, 4.5, 4.5, [base("preto")], raio=1, sobra=1.5)
    p.cubo_arredondado([ja[0] - 3, ja[1] - 1.5, ja[2] - 3], [6, 3, 6], [base("ouro")], raio=1,
                       arestas="verticais")                                                  # tornozeleira
    p.segmento([ja[0], ja[1] + 1, ja[2] - 3], [ja[0], ja[1] + 4, ja[2] - 4], 1.5, 1.5,
               [base("ouro"), afinar("+y", largura_ponta=0.1)], sobra=0.25)
    p.cubo_arredondado([ja[0] - 3, 0, ja[2] - 5], [6, 3, 7], [base("preto")], raio=1, arestas="verticais")
    for k in (-1, 0, 1):
        x = ja[0] + k * 2
        p.cubo([x - 0.75, 0, ja[2] - 7], [1.5, 2, 2.5], [base("ouro"),
               afinar("-z", largura_ponta=0.0, curva=0.9, apoio="y")])


perna_frente("leg_front_left", 1)
perna_frente("leg_front_right", -1)
perna_tras("leg_back_left", 1)
perna_tras("leg_back_right", -1)

# ----------------------------------------------------------------------------- cauda azul
cauda = m.osso("tail", pivo=[0, 15, 11], pai="body")
cauda.segmento([0, 15, 10], [0, 14, 18], 5, 4.5, [base("azul")], raio=1.5, sobra=1.5)
ponta = m.osso("tail_tip", pivo=[0, 14, 18], pai="tail")
ponta.segmento([0, 14, 18], [0, 15, 25], 3, 3, [base("azul")], raio=0.75, sobra=1)
ponta.segmento([0, 15, 25], [0, 16.5, 29], 1.5, 1.5, [base("azul")], sobra=0.5)


# ----------------------------------------------------------------------------- asas vermelhas enormes
def _tri(px, py, a, b_, c):
    def l(p1, p2):
        return (px - p2[0]) * (p1[1] - p2[1]) - (p1[0] - p2[0]) * (py - p2[1])
    d1, d2, d3 = l(a, b_), l(b_, c), l(c, a)
    return ~(((d1 < 0) | (d2 < 0) | (d3 < 0)) & ((d1 > 0) | (d2 > 0) | (d3 > 0)))


def asa(lado):
    zr = 0.0
    w = m.osso(f"wing_{'left' if lado > 0 else 'right'}", pivo=[4 * lado, 23, zr], pai="body",
               rotacao=[-15, -30 * lado, 10 * lado])
    raiz = np.array([4.0 * lado, 23.0])
    pulso = np.array([raiz[0] + lado * 16, raiz[1] + 20])
    pontas = [np.array([raiz[0] + lado * u, raiz[1] + v]) for u, v in ((42, 12), (38, 0), (29, -8), (17, -11))]
    base_baixa = np.array([raiz[0] + lado * 4, raiz[1] - 6])

    def fora(c):
        dentro = _tri(c.x, c.y, raiz, pulso, pontas[0]) | _tri(c.x, c.y, raiz, pulso, base_baixa)
        cad = [pulso] + pontas + [base_baixa]
        for i in range(1, len(cad) - 1):
            a, b_ = cad[i], cad[i + 1]
            recuo = pulso + ((a + b_) / 2 - pulso) * 0.78
            dentro |= _tri(c.x, c.y, pulso, a, recuo) | _tri(c.x, c.y, pulso, recuo, b_)
        return ~dentro

    xs = [raiz[0], pulso[0], base_baixa[0]] + [p[0] for p in pontas]
    ys = [raiz[1], pulso[1], base_baixa[1]] + [p[1] for p in pontas]
    x0, x1, y0, y1 = np.floor(min(xs)), np.ceil(max(xs)), np.floor(min(ys)), np.ceil(max(ys))
    w.plano([x0, y0, zr], [x1 - x0, y1 - y0, 0], [base("asa"), gradiente(1, y0, y1, -0.5, 0.5), recortar(fora)])
    w.cubo_arredondado([raiz[0] - 2.5, raiz[1] - 3, zr - 2.5], [5, 5, 5], [base("preto")], raio=1)   # encaixe
    w.segmento([raiz[0], raiz[1], zr], [pulso[0], pulso[1], zr], 2.5, 2.5, [base("osso_asa")], sobra=0.75)
    w.cubo_arredondado([pulso[0] - 1.5, pulso[1] - 1.5, zr - 1.5], [3, 3, 3], [base("osso_asa")], raio=0.5)
    w.segmento([pulso[0], pulso[1], zr], [pulso[0] + lado * 2, pulso[1] + 4, zr], 1.5, 1.5,
               [base("osso_asa"), afinar("+y", largura_ponta=0.1)])
    for p in pontas:
        w.segmento([pulso[0], pulso[1], zr], [p[0], p[1], zr], 1.5, 1.25, [base("osso_asa")], sobra=0.5)


asa(1)
asa(-1)

# ----------------------------------------------------------------------------- animações
anims = quadrupede(peso=1.4)
d = anims["idle"]["animation_length"]
anims["idle"]["bones"]["tail_tip"] = {"rotation": onda(8, d, eixo=1, fase=60)}
anims["idle"]["bones"]["jaw"] = {"rotation": onda(4, d, deslocamento=12)}
w = anims["walk"]["animation_length"]
anims["walk"]["bones"]["tail_tip"] = {"rotation": onda(12, w, eixo=1, fase=120)}
for nome_an, amp in (("idle", 5), ("walk", 9)):
    dur = anims[nome_an]["animation_length"]
    anims[nome_an]["bones"]["wing_left"] = {"rotation": onda(amp, dur, eixo=1)}
    anims[nome_an]["bones"]["wing_right"] = {"rotation": onda(amp, dur, eixo=1, fase=180)}
a = anims["attack"]["animation_length"]
anims["attack"]["bones"]["jaw"] = {"rotation": chaves({0: [12, 0, 0], a * 0.3: [40, 0, 0], a * 0.7: [40, 0, 0],
                                                       a: [12, 0, 0]}, True)}
for nome, an in anims.items():
    m.animacao(nome, an["animation_length"], an["bones"], an["loop"])

if __name__ == "__main__":
    finalizar(m, refs=("Imperialdramon_DM_Model_SC.png", "Imperialdramon_DM_Model_DSR.png",
                       "Imperialdramon_DM_New_Century.png"), estilo="0006_charizard")
