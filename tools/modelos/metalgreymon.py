"""
MetalGreymon: o MESMO corpo do Greymon (herdado: anatomia, juntas, listras, cores vivas e lisas)
com as peças que a evolução acrescenta, segundo os modelos oficiais (DSR, Encounters, SC, New Century):
  - capacete de METAL prateado no mesmo formato do capacete do Greymon; chifre do nariz de metal;
    chifres laterais cor de osso; UM olho azul de cada lado
  - juba de espinhos vermelhos saindo de trás do capacete
  - braço ESQUERDO dele (+X, à direita de quem olha de frente) mecânico: ombreira, braço e antebraço
    de metal grandes e 3 garras de metal compridas
  - placa de metal no peito com escotilha escura e rebites; cinta de metal na barriga
  - duas asas roxas grandes de morcego (4 pontas, buracos na membrana) saindo de trás dos ombros e
    subindo acima da cabeça
Regras do usuário aplicadas: poucas peças grandes, tudo encostado, um olho por lado, cores vivas e lisas.
"""
from comum import *

g = herdar("greymon.py", NOME="metalgreymon",
           CORES_OLHO={"k": "#0A1424", "r": "#1C5CC0", "R": "#5AA8F0", "W": "#FFFFFF", "P": "#06101E",
                       "s": "#3A4048"})
m = g["m"]
METAL = rampa_manual("#2E3238", "#4A5058", "#6C7480", "#929CA8", "#B8C0CA", "#DCE2E8", "#F6F8FA", base=4)
m.material("capacete", METAL, estilo="liso", aresta_clara=0.8, volume=0.4)          # capacete vira metal
m.material("chifre_nariz", METAL, estilo="liso", aresta_clara=0.8, volume=0.4)
m.material("chifre", rampa_manual("#5A4022", "#7E5C34", "#A07A4A", "#C29C66", "#DCBC88", "#F0D8AC", base=3),
           estilo="liso", aresta_clara=0.5)                                          # chifres cor de osso
m.material("metal", METAL, estilo="liso", aresta_clara=0.8, volume=0.4)
m.material("metal_escuro", rampa_manual("#14161A", "#22262C", "#343A42", "#4A5058", base=2), estilo="liso",
           aresta_clara=0.3)
m.material("cabelo", rampa_manual("#5A0A0A", "#8A1414", "#B82222", "#E03A2A", "#FF6040", base=3), estilo="limpo",
           ruido=0.1)
m.material("asa", rampa_manual("#2A1450", "#3E2070", "#563096", "#6E44B8", "#8A62D2", "#A884E6", base=3),
           estilo="limpo", ruido=0.1, aresta_clara=0, aresta_escura=0, volume=0.25, oclusao=0.3)
m.material("osso_asa", rampa_manual("#2A1450", "#3E2070", "#4E2C88", "#6A44A8", base=2), estilo="liso",
           aresta_clara=0.5)
cab, corpo = m.ossos["head"], m.ossos["body"]

# ----------------------------------------------------------------------------- juba vermelha
# espinhos grossos saindo de trás do capacete para trás e para cima (sem recorte: recorte em peça
# fina girada vira "garfo")
for x, sobe, abre in ((-3, 1, -0.6), (0, 2, 0), (3, 1, 0.6)):
    cab.segmento([x, 41, -6], [x + abre * 4, 42 + sobe, 2], 3, 2.5, [base("cabelo"), gradiente(2, -6, 2, -0.3, 0.6)],
                 sobra=1)                                           # mecha para trás
    cab.segmento([x + abre * 4, 42 + sobe, 2], [x + abre * 6, 41.5 + sobe, 6], 1.5, 1.5,
                 [base("cabelo"), gradiente(2, 2, 6, 0.4, 1)], sobra=0.5)                    # ponta

# ----------------------------------------------------------------------------- peito e barriga de metal
rebites = onde(lambda c: (np.round(c.x * 2) % 6 == 0) & (np.abs(c.y - 29.5) < 0.3), luz=2)
escotilha = onde(e_(faces("north"), caixa([-3.5, 24.5, -12], [3.5, 28.5, -9])), mat="metal_escuro")
corpo.cubo_arredondado([-7, 23.5, -11], [14, 7, 4], [base("metal"), gradiente(1, 23.5, 30.5, -0.6, 0.5),
                       rebites, escotilha], raio=1, arestas="verticais")                     # placa do peito
corpo.cubo([-9, 21.5, -8.5], [18, 2, 13], [base("metal_escuro"), onde(listras(0, 3, 1), luz=1)])  # cinta

# ----------------------------------------------------------------------------- braço mecânico (+X)
b = m.ossos["arm_left"]
b.cubos.clear()
om, co, pu = [7, 29, -6], [11.5, 23.5, -6.5], [12.5, 21.5, -13]
anel = onde(listras(1, 3, 0.75), mat="metal_escuro")
b.cubo_arredondado([4.5, 25, -10.5], [10, 9, 9], [base("metal"), gradiente(1, 25, 34, -0.5, 0.6)],
                   raio=2, arestas="todas")                                                 # ombreira
b.segmento(om, co, 6, 6, [base("metal"), anel], raio=1, sobra=1.5)                          # braço
b.cubo_arredondado([co[0] - 3.5, co[1] - 3.5, co[2] - 3.5], [7, 7, 7], [base("metal_escuro"),
                   onde(acima(co[1]), mat="metal")], raio=1.5)                              # cotovelo
b.segmento(co, pu, 8, 8, [base("metal"), onde(listras(2, 2.5, 0.5, fase=0.25), luz=-1.5)], raio=1.5,
           sobra=1.5)                                                                       # antebraço
for k, (dx, dy) in enumerate(((-2.5, 2), (2.5, 2), (0, -2.5))):                            # 3 garras longas
    raiz = [pu[0] + dx, pu[1] + dy, pu[2] - 2]
    b.segmento(raiz, [raiz[0] + dx * 0.4, raiz[1] + dy * 0.3 - 1, raiz[2] - 8], 2, 2,
               [base("metal"), gradiente(2, raiz[2] - 8, raiz[2], 1, -0.5)], sobra=0.5)


# ----------------------------------------------------------------------------- asas de morcego
def asa(lado):
    # pivô e raiz NAS COSTAS (z = 3.5, encostado no peito); Y negativo do lado +X abre a asa para fora e
    # para trás (Y positivo, como estava, virava a asa para a frente/para dentro)
    w = m.osso(f"wing_{'left' if lado > 0 else 'right'}", pivo=[4 * lado, 30, 3.5], pai="body",
               rotacao=[-10, -28 * lado, -8 * lado])
    raiz = np.array([4.0 * lado, 30.0])                              # (x, y) no plano z = 3.5
    pontas = [np.array([raiz[0] + lado * u, raiz[1] + v]) for u, v in ((4, 24), (11, 22), (17, 16), (21, 8))]

    def dentro_tri(px, py, a, b_, c):
        def lado_(p1, p2):
            return (px - p2[0]) * (p1[1] - p2[1]) - (p1[0] - p2[0]) * (py - p2[1])
        d1, d2, d3 = lado_(a, b_), lado_(b_, c), lado_(c, a)
        neg = (d1 < 0) | (d2 < 0) | (d3 < 0)
        pos = (d1 > 0) | (d2 > 0) | (d3 > 0)
        return ~(neg & pos)

    def membrana(c):
        px, py = c.x, c.y
        dentro = np.zeros(px.shape, bool)
        for i in range(len(pontas) - 1):
            a, b_ = pontas[i], pontas[i + 1]
            meio = (a + b_) / 2
            recuo = raiz + (meio - raiz) * 0.86                      # borda recortada em "ondas" entre as pontas
            dentro |= dentro_tri(px, py, raiz, a, recuo) | dentro_tri(px, py, raiz, recuo, b_)
        buracos = (fbm(c.p, 1.4, 2, semente=11) > 0.55) & (np.hypot(px - raiz[0], py - raiz[1]) > 9)
        return ~dentro | buracos

    x0 = raiz[0] if lado > 0 else raiz[0] - 22
    w.plano([x0, 29, 3.5], [22, 25, 0], [base("asa"), gradiente(1, 29, 54, -0.6, 0.6), recortar(membrana)])
    w.cubo_arredondado([raiz[0] - 3, 26.5, 0.5], [6, 7, 5], [base("metal"), gradiente(1, 26.5, 33.5, -0.5, 0.5)],
                       raio=1)                                                             # encaixe preso nas costas
    for p in pontas:                                                 # dedos da asa (de raiz até a ponta)
        w.segmento([raiz[0], raiz[1], 3.5], [p[0], p[1], 3.5], 1, 1, [base("osso_asa")], sobra=0.5)


asa(1)
asa(-1)

an = m.animacoes
for nome_an, amp in (("idle", 4), ("walk", 8)):
    dur = an[nome_an]["animation_length"]
    an[nome_an]["bones"]["wing_left"] = {"rotation": onda(amp, dur, eixo=1)}
    an[nome_an]["bones"]["wing_right"] = {"rotation": onda(amp, dur, eixo=1, fase=180)}

if __name__ == "__main__":
    finalizar(m, refs=("Metal_Greymon_Model_DSR.png", "Metalgreymon_newcentury_model.png", "Metal_Greymon_Model_SC.png"),
              estilo="0005_charmeleon")
