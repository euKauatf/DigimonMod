"""
ExVeemon (XV-mon): champion da linha do Veemon. Medido nas folhas de modelo oficiais
(XV-mon_reference_art*.jpg) e nos modelos 3D (SC, DSR).

Traços que identificam:
  1. dragão humanoide musculoso, em pé; ombros largos, cintura média, coxas grossas
  2. cabeça de dragão pequena (~0,17 H) com focinho comprido; CHIFRE grande branco/cinza no focinho;
     "V" amarelo largo na testa; risquinhos amarelos; olhos alaranjados; parte de baixo do focinho e
     garganta BRANCAS; presas; orelhas varridas para trás como no Veemon e bochechas serrilhadas
  3. peito BRANCO com o "X" cinza; barriga branca descendo até a virilha
  4. braços compridos e fortes, mãos grandes com garras brancas; espinho no antebraço
  5. pernas fortes, pés grandes com 3 garras brancas
  6. ASAS de morcego brancas/cinza nas costas; cauda azul comprida
Medidas: H = 38 até o topo da cabeça (sem chifre/orelhas).
Regras aprovadas: cabeça de dragão com pescoço (sem ir para frente demais), juntas fechadas, olhos sem
cortar na quina, cores vivas e lisas, asas presas nas costas e abertas para fora.
"""
from comum import *

m = Modelo("exveemon", densidade=2)
m.material("azul", rampa_manual("#0C4A80", "#1462A2", "#1C7EC4", "#2C98DC", "#4EB0EC", "#7EC8F4", base=3),
           estilo="limpo", ruido=0.06)
m.material("branco", rampa_manual("#B4B8C8", "#D2D6E2", "#EAEDF4", "#F8FAFD", "#FFFFFF", base=4),
           estilo="limpo", ruido=0.0, volume=0.25)
m.material("cinza", rampa_manual("#5A5E6A", "#7A7E8A", "#9A9EAA", "#B8BCC6", base=2), estilo="liso", volume=0.1)
m.material("chifre", rampa_manual("#4A4038", "#6E6458", "#A8A4A0", "#D8D6D4", "#F4F4F4", base=3), estilo="liso",
           aresta_clara=0.6)
m.material("garra", rampa_manual("#A8A4B0", "#CCC8D2", "#E8E6EC", "#FAF8FC", "#FFFFFF", base=3), estilo="liso",
           aresta_clara=0.3, volume=0.25)
m.material("amarelo", rampa_manual("#8A6A08", "#B88E10", "#D8AE1C", "#F0CA34", base=2), estilo="liso", volume=0)
m.material("asa", rampa_manual("#8C90A0", "#A8ACBA", "#C4C8D4", "#DCDFE8", "#F0F2F6", base=3), estilo="limpo",
           ruido=0.0, aresta_clara=0, aresta_escura=0, volume=0.25, oclusao=0.3)
m.material("osso_asa", rampa_manual("#B8BCC8", "#D6D9E2", "#EEF0F5", "#FFFFFF", base=2), estilo="liso")
m.material("boca", rampa_manual("#3A0810", "#5E141E", "#8A2430", base=1), estilo="liso", volume=0,
           aresta_clara=0, aresta_escura=0)

CORES_OLHO = {"k": "#1A0806", "o": "#B84A18", "O": "#F08A3A", "P": "#140604", "W": "#FFFFFF"}
OLHO_LADO = """
kkkkk.
kOWPok
kOPPok
.kkkk.
"""
OLHO_FRENTE = """
.k
Wk
Pk
k.
"""

root = m.osso("root")
corpo = m.osso("body", pivo=[0, 19, 0.5], pai="root")

# ----------------------------------------------------------------------------- tronco
X = """
gg..........gg
ggg........ggg
.ggg......ggg.
..ggg....ggg..
...ggg..ggg...
....gg..gg....
...ggg..ggg...
..ggg....ggg..
.ggg......ggg.
ggg........ggg
gg..........gg
"""
peito = onde(e_(lambda c: c.n[2] < -0.5, lambda c: np.abs(c.x) < 4.2 - np.clip(24 - c.y, 0, None) * 0.25,
                lambda c: c.y > 17), mat="branco")
corpo.cubo_arredondado([-5.5, 17, -3.5], [11, 7, 7], [base("azul"), peito], raio=2, arestas="verticais")    # barriga
corpo.cubo_arredondado([-7, 23.5, -4], [14, 8, 8], [base("azul"), peito,
                       decalque(X, {"g": "cinza"}, centro=[0, 25.5, -4], profundidade=3)],
                       raio=2, arestas="verticais")                                                      # peito
corpo.cubo_arredondado([-5, 15, -3], [10, 3.5, 6], [base("azul")], raio=1.5, arestas="verticais")         # quadril

# ----------------------------------------------------------------------------- pescoço e cabeça
corpo.segmento([0, 30, -1], [0, 34.5, -2.5], 6, 5.5, [base("azul"), onde(lambda c: c.n[2] < -0.4, mat="branco")],
               raio=1.5, sobra=1.5)
cab = m.osso("head", pivo=[0, 34, -2], pai="body")
mand = m.osso("jaw", pivo=[0, 35, -3.5], pai="head", rotacao=[4, 0, 0])
V = """
yy..........yy
.yyy......yyy.
...yyy..yyy...
.....yyyy.....
"""
olhos_x = [decalque(OLHO_LADO, CORES_OLHO, centro=[3.5, 37.75, -4.5], direcao=(1, 0, 0), profundidade=0.4),
           decalque(espelhar_arte(OLHO_LADO), CORES_OLHO, centro=[-3.5, 37.75, -4.5], direcao=(-1, 0, 0),
                    profundidade=0.4),
           decalque(OLHO_FRENTE, CORES_OLHO, centro=[2.75, 37.75, -6.5], direcao=(0, 0, -1), profundidade=0.4),
           decalque(espelhar_arte(OLHO_FRENTE), CORES_OLHO, centro=[-2.75, 37.75, -6.5], direcao=(0, 0, -1),
                    profundidade=0.4)]
cab.cubo_arredondado([-3.5, 34.5, -6.5], [7, 6, 7.5], [base("azul"),
                     decalque(V, {"y": "amarelo"}, centro=[0, 39.5, -6.5], profundidade=0.4),
                     onde(e_(lambda c: c.n[1] < 0.5, abaixo(36)), mat="branco")] + olhos_x,
                     raio=1, arestas="verticais")                                          # crânio
cab.segmento([0, 37, -6], [0, 36, -11.5], 5, 3.5, [base("azul"), onde(abaixo(35.6), mat="branco"),
             so_faces("down", base("boca"))], raio=1, sobra=1)                             # focinho
cab.cubo([-2, 34.25, -11], [4, 1.5, 5], [base("boca")])                                     # fundo da boca
for lado in (1, -1):                                                                       # presas
    cab.plano([2.05 * lado, 33.5, -9], [0, 1.5, 1.5], [base("garra"), afinar("-y", largura_ponta=0.0)])
    cab.plano([2.05 * lado, 33.5, -6.5], [0, 2, 1.5], [base("garra"), afinar("-y", largura_ponta=0.0)])
mand.cubo_arredondado([-2.25, 33, -11], [4.5, 1.75, 6.5], [base("branco"), so_faces("up", base("boca"))],
                      raio=0.5, arestas="frente")
# chifre grande no focinho, para cima e um pouco para trás
cab.cadeia([[0, 37, -8.5], [0, 40.5, -8], [0, 44, -6.5], [0, 46.5, -5]], [(2, 2.5), (1.5, 2), (1, 1.5)],
           [base("chifre"), gradiente(0, -1, 1, -0.6, 0.6)], sobra=0.5)
# orelhas varridas para trás (como no Veemon, maiores) e bochechas serrilhadas
for lado in (1, -1):
    pts = [[2.5 * lado, 40, -2], [3.5 * lado, 41.5, 0.5], [4 * lado, 41, 5], [4.5 * lado, 42.5, 8]]
    cab.cadeia(pts, [(2.5, 1.5), (2.5, 1.25), (2, 1)], [base("azul"), gradiente(1, 40, 43, -0.2, 0.6)], sobra=0.75)
    for k, y in enumerate((35.5, 37.75)):
        cab.segmento([3 * lado, y, -2.5 + k * 0.5], [5.5 * lado, y + 0.5, -0.5 + k * 0.75], 2, 1,
                     [base("azul"), afinar("+y", largura_ponta=0.2, curva=1.2)], sobra=0.5)


# ----------------------------------------------------------------------------- braços
def braco(nome, lado):
    om = [7.5 * lado, 29.5, 0]
    co = [9.5 * lado, 22, 0.5]
    pu = [10.5 * lado, 15, -1]
    b = m.osso(nome, pivo=om, pai="body")
    junta(b, om, [5.5, 6, 6], [base("azul")], raio=1.5)                                   # ombro
    b.segmento(om, co, 4.5, 4.5, [base("azul")], raio=1, sobra=1.5)
    junta(b, co, [4, 4, 4], [base("azul")], raio=1)
    b.segmento(co, pu, 5, 5, [base("azul")], raio=1.5, sobra=1.5)                          # antebraço forte
    b.segmento([co[0] + 2 * lado, co[1] - 3, co[2] + 1.5], [co[0] + 3.5 * lado, co[1] - 3.5, co[2] + 3], 1, 1,
               [base("azul"), afinar("+y", largura_ponta=0.1)])                           # espinho do antebraço
    b.cubo_arredondado([pu[0] - 2.5, pu[1] - 4.5, pu[2] - 2.5], [5, 5, 5], [base("azul")], raio=1.5)   # mão
    for k in (-1, 0, 1):
        x = pu[0] + k * 1.6
        b.cubo([x - 0.75, pu[1] - 7, pu[2] - 2.25], [1.5, 2.5, 2], [base("garra"), afinar("-y", largura_ponta=0.1, apoio="-z")])


braco("arm_left", 1)
braco("arm_right", -1)


# ----------------------------------------------------------------------------- pernas
def perna(nome, lado):
    qu = [3.5 * lado, 16, 0]
    jo = [4.5 * lado, 9, -2]
    ca = [4.75 * lado, 3, 1]
    p = m.osso(nome, pivo=qu, pai="root")
    junta(p, [qu[0], qu[1], qu[2]], [6, 6, 6.5], [base("azul")], raio=2)
    p.segmento(qu, jo, 6, 6.5, [base("azul")], raio=2, sobra=1.5)                           # coxa
    junta(p, jo, [5, 4.5, 5], [base("azul")], raio=1.5)
    p.segmento(jo, ca, 4.5, 4.5, [base("azul")], raio=1, sobra=1.5)                         # canela
    p.cubo_arredondado([ca[0] - 3, 0, -6], [6, 3, 9], [base("azul"), gradiente(1, 0, 3, -0.5, 0.3)],
                       raio=1, arestas="verticais")                                        # pé
    for k in (-1, 0, 1):
        x = ca[0] + k * 2
        p.cubo([x - 1, 0, -8.5], [2, 2.5, 3], [base("garra"), afinar("-z", largura_ponta=0.0, apoio="y")])


perna("leg_left", 1)
perna("leg_right", -1)

# ----------------------------------------------------------------------------- cauda comprida
cauda = m.osso("tail", pivo=[0, 16, 3], pai="body")
cauda.segmento([0, 16.5, 1.5], [0, 12, 8], 5, 5, [base("azul")], raio=1.5, sobra=1.5)
ponta = m.osso("tail_tip", pivo=[0, 12, 8], pai="tail")
ponta.segmento([0, 12, 8], [0, 9, 15], 3.5, 3.5, [base("azul")], raio=1, sobra=1)
ponta.segmento([0, 9, 15], [0, 8.5, 20], 2, 2, [base("azul")], sobra=0.5)


# ----------------------------------------------------------------------------- asas de morcego
def asa(lado):
    """Asa de morcego cheia: braço da asa (borda de cima) até o 'pulso', 3 dedos saindo dele e a membrana
    preenchida entre os dedos com recortes rasos na borda de baixo (como na referência)."""
    w = m.osso(f"wing_{'left' if lado > 0 else 'right'}", pivo=[3 * lado, 29, 3.5], pai="body",
               rotacao=[-10, -28 * lado, -8 * lado])
    raiz = np.array([3.0 * lado, 29.0])
    pulso = np.array([raiz[0] + lado * 9, raiz[1] + 12])
    pontas = [np.array([raiz[0] + lado * u, raiz[1] + v]) for u, v in ((19, 9), (19, -1), (13, -8))]
    base_baixa = np.array([raiz[0] + lado * 2, raiz[1] - 8])

    def dentro_tri(px, py, a, b_, c):
        def l(p1, p2):
            return (px - p2[0]) * (p1[1] - p2[1]) - (p1[0] - p2[0]) * (py - p2[1])
        d1, d2, d3 = l(a, b_), l(b_, c), l(c, a)
        return ~(((d1 < 0) | (d2 < 0) | (d3 < 0)) & ((d1 > 0) | (d2 > 0) | (d3 > 0)))

    def fora(c):
        dentro = dentro_tri(c.x, c.y, raiz, pulso, pontas[0])
        cadeia_pts = [pulso] + pontas + [base_baixa]
        for i in range(1, len(cadeia_pts) - 1):
            a, b_ = cadeia_pts[i], cadeia_pts[i + 1]
            recuo = pulso + ((a + b_) / 2 - pulso) * 0.8      # recorte raso entre os dedos
            dentro |= dentro_tri(c.x, c.y, pulso, a, recuo) | dentro_tri(c.x, c.y, pulso, recuo, b_)
        dentro |= dentro_tri(c.x, c.y, raiz, pulso, base_baixa)
        return ~dentro

    x0 = raiz[0] if lado > 0 else raiz[0] - 21
    w.plano([x0, 20, 3.5], [21, 22, 0], [base("asa"), gradiente(1, 20, 42, -0.5, 0.5), recortar(fora)])
    w.cubo_arredondado([raiz[0] - 2, 27, 0.5], [4, 4, 4], [base("azul")], raio=1)          # encaixe nas costas
    w.segmento([raiz[0], raiz[1], 3.5], [pulso[0], pulso[1], 3.5], 2, 2, [base("osso_asa")], sobra=0.75)  # braço da asa
    w.cubo_arredondado([pulso[0] - 1.25, pulso[1] - 1.25, 2.25], [2.5, 2.5, 2.5], [base("osso_asa")], raio=0.5)
    w.segmento([pulso[0], pulso[1], 3.5], [pulso[0] + lado * 2, pulso[1] + 3, 3.5], 1, 1, [base("garra"),
               afinar("+y", largura_ponta=0.1)])                                           # garrinha do pulso
    for p in pontas:                                                                       # dedos da asa
        w.segmento([pulso[0], pulso[1], 3.5], [p[0], p[1], 3.5], 1.25, 1, [base("osso_asa")], sobra=0.5)


asa(1)
asa(-1)

anims = bipede(peso=1.2)
d = anims["idle"]["animation_length"]
w_ = anims["walk"]["animation_length"]
anims["idle"]["bones"]["tail_tip"] = {"rotation": onda(6, d, eixo=1)}
for nome_an, amp in (("idle", 4), ("walk", 8)):
    dur = anims[nome_an]["animation_length"]
    anims[nome_an]["bones"]["wing_left"] = {"rotation": onda(amp, dur, eixo=1)}
    anims[nome_an]["bones"]["wing_right"] = {"rotation": onda(amp, dur, eixo=1, fase=180)}
a = anims["attack"]["animation_length"]
anims["attack"]["bones"]["jaw"] = {"rotation": chaves({0: [4, 0, 0], a * 0.3: [30, 0, 0], a * 0.7: [30, 0, 0],
                                                       a: [4, 0, 0]}, True)}
for nome, an in anims.items():
    m.animacao(nome, an["animation_length"], an["bones"], an["loop"])

if __name__ == "__main__":
    finalizar(m, refs=("XV-mon_Model_SC.png", "XV-mon_Model_DSR.png", "XV-mon_model_new_century.png"),
              estilo="0005_charmeleon")
