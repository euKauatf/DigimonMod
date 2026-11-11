"""
Paildramon: ultimate da linha do Veemon (fusão de ExVeemon + Stingmon). Medido na folha de modelo oficial
(Paildramon_reference_art_1.jpg, frente/costas/cabeça) e nos modelos 3D (DSR, SC).

Traços que identificam:
  1. capacete VERMELHO (do Stingmon) com chifre curvo em cima e viseira escura; olhos laranja; parte de
     baixo do rosto e queixo brancos
  2. colete VERDE-OLIVA de placas no peito, com o centro branco (esterno) entre as placas
  3. ombreiras escuras com espinhos prateados
  4. braços azuis com MANOPLAS pretas enormes (do cotovelo à mão), espinhos e 4 garras prateadas
  5. cinto/sunga verde; duas pistolas verdes (Desperado Blasters) presas nos quadris
  6. coxas com armadura PRETA grande; canelas azuis compridas; pés grandes com garras brancas
  7. DOIS pares de asas: em cima azuis (do Stingmon, de ponta), embaixo brancas de morcego (do ExVeemon)
  8. cauda azul
Medidas: H = 44 até o topo do capacete (sem chifre).
"""
from comum import *

m = Modelo("paildramon", densidade=2)
m.material("azul", rampa_manual("#0C4A80", "#1462A2", "#1C7EC4", "#2C98DC", "#4EB0EC", "#7EC8F4", base=3),
           estilo="limpo", ruido=0.06)
m.material("branco", rampa_manual("#B4B8C8", "#D2D6E2", "#EAEDF4", "#F8FAFD", "#FFFFFF", base=4),
           estilo="limpo", ruido=0.0, volume=0.25)
m.material("verde", rampa_manual("#2A3216", "#3C4620", "#525E2C", "#6A783A", "#86944C", base=3),
           estilo="limpo", ruido=0.06, aresta_clara=0.5)
m.material("preto", rampa_manual("#0E0E14", "#1A1A22", "#282832", "#3A3A46", "#50505E", base=2),
           estilo="liso", aresta_clara=0.5)
m.material("vermelho", rampa_manual("#5A1A10", "#842818", "#B03C24", "#D25838", "#EC7C58", base=3),
           estilo="liso", aresta_clara=0.6)
m.material("prata", rampa_manual("#4A4E58", "#6C727E", "#949AA6", "#BCC2CC", "#E2E6EC", base=3), estilo="liso",
           aresta_clara=0.6)
m.material("garra", rampa_manual("#A8A4B0", "#CCC8D2", "#E8E6EC", "#FAF8FC", "#FFFFFF", base=3), estilo="liso",
           aresta_clara=0.3, volume=0.25)
m.material("asa", rampa_manual("#8C90A0", "#A8ACBA", "#C4C8D4", "#DCDFE8", "#F0F2F6", base=3), estilo="limpo",
           ruido=0.0, aresta_clara=0, aresta_escura=0, volume=0.25, oclusao=0.3)
m.material("asa_azul", rampa_manual("#0C3E70", "#145692", "#1C70B4", "#2C8ACE", "#4EA6E2", base=3),
           estilo="limpo", ruido=0.0, aresta_clara=0, aresta_escura=0, volume=0.25, oclusao=0.3)
m.material("osso_asa", rampa_manual("#B8BCC8", "#D6D9E2", "#EEF0F5", "#FFFFFF", base=2), estilo="liso")

CORES_OLHO = {"k": "#1A0806", "o": "#B84A18", "O": "#F08A3A", "P": "#140604", "W": "#FFFFFF"}
OLHO = """
kkkk
kOWk
kOPk
.kk.
"""

root = m.osso("root")
DY = 5      # pernas mais compridas: o tronco inteiro sobe DY no arquivo final (pintura não muda)
corpo = m.osso("body", pivo=[0, 22, 0.5], pai="root")
m.deslocar("body", [0, DY, 0])

# ----------------------------------------------------------------------------- tronco
esterno = onde(e_(lambda c: c.n[2] < -0.5, lambda c: np.abs(c.x) < 1.25 + np.clip(c.y - 28, 0, None) * 0.15),
               mat="branco")
placas = onde(lambda c: (c.n[2] < -0.5) & (np.abs((c.y - 26) % 2.5) < 0.3), luz=-1.5)
corpo.cubo_arredondado([-4.5, 20, -3], [9, 6, 6], [base("azul"), onde(lambda c: c.n[2] < -0.5, mat="branco")],
                       raio=1.5, arestas="verticais")                                      # cintura
corpo.cubo_arredondado([-7.5, 25.5, -4.5], [15, 9.5, 9], [base("verde"), placas, esterno], raio=2,
                       arestas="verticais")                                                # colete de placas
corpo.cubo_arredondado([-6, 17, -3.5], [12, 4, 7], [base("verde"),
                       onde(lambda c: (c.n[2] < -0.5) & (np.abs(c.x) < 1.5) & (np.abs((c.y - 17.5) % 1.5) < 0.3),
                            mat="preto")], raio=1.5, arestas="verticais")                  # sunga/cinto verde
corpo.cubo([-7, 19.5, -3.75], [14, 1, 7.5], [base("prata")])                               # cinto prateado
# pistolas nos quadris (Desperado Blasters), apontando para a frente
for lado in (1, -1):
    x = 7.5 * lado
    corpo.cubo_arredondado([x - 1.5, 17, -7], [3, 3, 11], [base("verde"),
                           onde(lambda c: np.abs(c.z + 3) < 0.4, mat="preto")], raio=0.75, arestas="z")
    corpo.cubo([x - 1.25, 17.25, -8], [2.5, 2.5, 1], [base("prata"),
               onde(lambda c: (c.n[2] < -0.5) & (np.hypot(c.x - x, c.y - 18.5) < 0.6), mat="preto")])  # cano

# ----------------------------------------------------------------------------- pescoço e cabeça
corpo.segmento([0, 34, -1], [0, 37.5, -2], 5, 5, [base("verde")], raio=1.5, sobra=1.5)    # gola do colete
cab = m.osso("head", pivo=[0, 37, -2], pai="body")
olhos_p = olhos_frente(OLHO, CORES_OLHO, 1.75, 40, -5, profundidade=0.4)
visor = onde(e_(lambda c: c.n[2] < -0.5, lambda c: (c.y > 40.75) & (c.y < 43.5) & (np.abs(c.x) < 2.75)), mat="preto")
cab.cubo_arredondado([-3.5, 37, -5], [7, 7.5, 7], [base("vermelho"), visor,
                     onde(e_(lambda c: c.n[2] < -0.3, abaixo(39)), mat="branco")] + olhos_p,
                     raio=1, arestas="verticais")                                          # capacete
cab.cubo_arredondado([-2.25, 36.25, -7], [4.5, 2.75, 2.5], [base("branco")], raio=0.75, arestas="verticais")  # queixo
cab.cadeia([[0, 44, -2.5], [0, 46, -3], [0, 48, -2.5], [0, 49.5, -1], [0, 50.5, 1]],
           [(2.5, 3.5), (2, 3), (1.5, 2.5), (1, 1.5)],
           [base("vermelho"), gradiente(1, 44, 51, 0, 0.8)], sobra=0.5)                    # chifre curvo
for lado in (1, -1):                                                                     # aletas do capacete
    cab.segmento([3.25 * lado, 39.5, -2], [6 * lado, 41, 0], 2, 1, [base("vermelho"),
                 afinar("+y", largura_ponta=0.15)], sobra=0.5)
    cab.segmento([3.25 * lado, 38, -1], [5.5 * lado, 37.5, 1], 1.5, 1, [base("vermelho"),
                 afinar("+y", largura_ponta=0.15)], sobra=0.5)


# ----------------------------------------------------------------------------- braços com manoplas pretas
def braco(nome, lado):
    om = [8.5 * lado, 32.5, 0]
    co = [11 * lado, 26.5, 0]
    pu = [13 * lado, 20, -2.5]
    b = m.osso(nome, pivo=om, pai="body")
    b.cubo_arredondado([om[0] - 3, om[1] - 3, -3.5], [6, 6.5, 7], [base("preto")], raio=1.5)          # ombreira
    for k, (dy, dz) in enumerate(((2.5, -1.5), (2.5, 1.5), (0, 0))):
        b.segmento([om[0] + 2.5 * lado, om[1] + dy - 1, dz], [om[0] + 5 * lado, om[1] + dy, dz], 1.5, 1.5,
                   [base("prata"), afinar("+y", largura_ponta=0.1)], sobra=0.25)       # espinhos
    b.segmento(om, co, 3.5, 3.5, [base("azul")], raio=1, sobra=1)                             # braço azul
    junta(b, co, [4.5, 4.5, 4.5], [base("preto")], raio=1)
    b.segmento(co, pu, 6, 6, [base("preto"), gradiente(1, pu[1], co[1], -0.3, 0.4)], raio=1.5, sobra=2)  # manopla
    for dz in (-2, 1.5):
        b.segmento([co[0] + 3 * lado, co[1] - 3, dz], [co[0] + 5 * lado, co[1] - 3.5, dz], 1.25, 1.25,
                   [base("prata"), afinar("+y", largura_ponta=0.1)], sobra=0.25)       # espinhos da manopla
    for k in (-1.5, -0.5, 0.5, 1.5):                                                       # 4 garras compridas
        x = pu[0] + k * 1.5
        b.segmento([x, pu[1] - 2, pu[2] - 1], [x + k * 0.8, pu[1] - 9, pu[2] - 4], 1.5, 1.5,
                   [base("prata"), afinar("+y", largura_ponta=0.35)], sobra=0.5)
        b.cubo([x - 0.75, pu[1] - 3, pu[2] - 2], [1.5, 1.5, 2], [base("vermelho")])        # junta vermelha


braco("arm_left", 1)
braco("arm_right", -1)


# ----------------------------------------------------------------------------- pernas
def perna(nome, lado):
    qu = [3.75 * lado, 18 + DY, 0]
    jo = [4.5 * lado, 14, -2.5]
    to = [4.75 * lado, 3, 1.5]
    p = m.osso(nome, pivo=qu, pai="root")
    p.segmento(qu, jo, 5.5, 6, [base("preto"), gradiente(1, jo[1], qu[1], -0.3, 0.4)], raio=2, sobra=2)  # coxa preta
    p.segmento(jo, to, 4, 4, [base("azul")], raio=1, sobra=1.5)                              # canela azul
    p.cubo_arredondado([to[0] - 3.5, 0, -7], [7, 3, 10], [base("azul"), gradiente(1, 0, 3, -0.5, 0.3)],
                       raio=1, arestas="verticais")                                        # pé grande
    for k in (-1, 0, 1):
        x = to[0] + k * 2.25
        p.cubo([x - 1, 0, -9.5], [2, 2.5, 3], [base("garra"), afinar("-z", largura_ponta=0.0, apoio="y")])


perna("leg_left", 1)
perna("leg_right", -1)

# ----------------------------------------------------------------------------- cauda
cauda = m.osso("tail", pivo=[0, 18, 3], pai="body")
cauda.segmento([0, 18.5, 2], [0, 14, 8], 4.5, 4.5, [base("azul")], raio=1.5, sobra=1.5)
ponta = m.osso("tail_tip", pivo=[0, 14, 8], pai="tail")
ponta.segmento([0, 14, 8], [0, 11, 15], 3, 3, [base("azul")], raio=0.75, sobra=1)
ponta.segmento([0, 11, 15], [0, 10.5, 19], 1.5, 1.5, [base("azul")], sobra=0.5)


# ----------------------------------------------------------------------------- asas
def _tri(px, py, a, b_, c):
    def l(p1, p2):
        return (px - p2[0]) * (p1[1] - p2[1]) - (p1[0] - p2[0]) * (py - p2[1])
    d1, d2, d3 = l(a, b_), l(b_, c), l(c, a)
    return ~(((d1 < 0) | (d2 < 0) | (d3 < 0)) & ((d1 > 0) | (d2 > 0) | (d3 > 0)))


def asa(nome, lado, raiz, pulso, pontas, base_baixa, mat_membrana, mat_osso, rot):
    w = m.osso(nome, pivo=[raiz[0], raiz[1], 3.5], pai="body", rotacao=rot)

    def fora(c):
        dentro = _tri(c.x, c.y, raiz, pulso, pontas[0]) | _tri(c.x, c.y, raiz, pulso, base_baixa)
        cadeia_pts = [pulso] + pontas + [base_baixa]
        for i in range(1, len(cadeia_pts) - 1):
            a, b_ = cadeia_pts[i], cadeia_pts[i + 1]
            recuo = pulso + ((a + b_) / 2 - pulso) * 0.8
            dentro |= _tri(c.x, c.y, pulso, a, recuo) | _tri(c.x, c.y, pulso, recuo, b_)
        return ~dentro

    xs = [raiz[0], pulso[0], base_baixa[0]] + [p[0] for p in pontas]
    ys = [raiz[1], pulso[1], base_baixa[1]] + [p[1] for p in pontas]
    x0, x1, y0, y1 = np.floor(min(xs)), np.ceil(max(xs)), np.floor(min(ys)), np.ceil(max(ys))
    w.plano([x0, y0, 3.5], [x1 - x0, y1 - y0, 0], [base(mat_membrana), gradiente(1, y0, y1, -0.5, 0.5),
                                                    recortar(fora)])
    w.cubo_arredondado([raiz[0] - 2, raiz[1] - 2, 0.5], [4, 4, 4], [base("verde")], raio=1)   # encaixe
    w.segmento([raiz[0], raiz[1], 3.5], [pulso[0], pulso[1], 3.5], 2, 2, [base(mat_osso)], sobra=0.75)
    for p in pontas:
        w.segmento([pulso[0], pulso[1], 3.5], [p[0], p[1], 3.5], 1.25, 1, [base(mat_osso)], sobra=0.5)


for lado in (1, -1):
    s = "left" if lado > 0 else "right"
    r = np.array([3.0 * lado, 27.0])
    asa(f"wing_{s}", lado, r, r + [lado * 8, 7], [r + [lado * 17, 4], r + [lado * 17, -6], r + [lado * 11, -12]],
        r + [lado * 2, -9], "asa", "osso_asa", [-10, -28 * lado, -8 * lado])                 # brancas (ExVeemon)
    r2 = np.array([2.5 * lado, 34.0])
    asa(f"wing2_{s}", lado, r2, r2 + [lado * 5, 9], [r2 + [lado * 15, 6], r2 + [lado * 13, -1]],
        r2 + [lado * 4, -2], "asa_azul", "asa_azul", [-15, -20 * lado, -15 * lado])         # azuis (Stingmon)

anims = bipede(peso=1.3)
for nome_an, amp in (("idle", 4), ("walk", 8)):
    dur = anims[nome_an]["animation_length"]
    for s, f in (("left", 0), ("right", 180)):
        anims[nome_an]["bones"][f"wing_{s}"] = {"rotation": onda(amp, dur, eixo=1, fase=f)}
        anims[nome_an]["bones"][f"wing2_{s}"] = {"rotation": onda(amp, dur, eixo=1, fase=f + 60)}
anims["idle"]["bones"]["tail_tip"] = {"rotation": onda(6, anims["idle"]["animation_length"], eixo=1)}
for nome, an in anims.items():
    m.animacao(nome, an["animation_length"], an["bones"], an["loop"])

if __name__ == "__main__":
    finalizar(m, refs=("Paildramon_Model_SC.png", "Paildramon_Model_DSR.png", "Paildramon_newcentury_model.png"),
              estilo="0005_charmeleon")
