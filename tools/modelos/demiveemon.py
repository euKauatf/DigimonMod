"""
DemiVeemon (Chibimon no Japão) — refeito do zero a partir da folha de modelo oficial do Adventure 02
(Chibimon_Adventure_02_reference_art.jpg, 5 vistas) e do modelo 3D oficial (Chibimon_Model_DSR.png).

Traços que identificam (lista antes de modelar):
  1. cabeça = BOLA grande e redonda (~55% da altura), bem mais larga que o corpo
  2. "capuz" azul cobrindo o topo, as laterais e a nuca; rosto BRANCO na frente com uma ponta azul em
     "V" descendo no meio da testa, entre os olhos
  3. olhos enormes, ovais em pé, vermelho-escuros, com pupila preta e brilho branco em cima
  4. focinho de bochechas fofas em "ω" com a boquinha aberta (rosa) logo abaixo
  5. duas orelhas compridas que sobem do topo e DOBRAM para fora e para trás, ponta caindo
  7. corpo pequeno em pera com barriga branca; bracinhos azuis abertos; pezinhos azuis curtos
  8. caudinha pontuda atrás

Medidas (lidas na vista de frente da folha de modelo, 30 px = 1 unidade; H = 18 até o topo da cabeça):
  cabeça y 7..18, largura 13, fundura 11 | olhos centro y 12, x ±3,5, 3 x 4 unidades
  ponta do "V" azul em y 12,3 | boca y 8,5 | corpo y 2..8, largura 7 | pés y 0..2 | orelhas até x ±10,5
"""
from comum import *

m = Modelo("demiveemon", densidade=2)
m.material("azul", rampa_manual("#0E4E86", "#1766A6", "#1F80C6", "#2E98DE", "#52B2EE", "#82CCF6", base=3),
           estilo="limpo", ruido=0.06)
m.material("branco", rampa_manual("#C6C2D2", "#E0DCE8", "#F2F0F6", "#FCFBFE", "#FFFFFF", base=4),
           estilo="limpo", ruido=0.0, volume=0.25)

CORES_OLHO = {"k": "#20060E", "r": "#7E1428", "R": "#D23A52", "P": "#1A0408", "W": "#FFFFFF", "w": "#F6B4C2"}
OLHO = """
.kkkkk.
kWWrrrk
kWPPrrk
krPPPrk
kRPPPRk
kRRPRRk
kRwRRRk
kRRRRRk
.kkkkk.
"""
BOCA = """
b....bb....b
.bbbb..bbbb.
...pppppp...
....pPPp....
"""
CORES_BOCA = {"b": "#4A1424", "p": "#7A1E34", "P": "#F0809C"}


def capuz(c):
    """Rosto branco: frente da cabeça abaixo da linha do capuz, com o 'V' azul descendo no meio."""
    linha = 14.4 - np.clip(2.4 - np.abs(c.x), 0, None) * 0.9
    largura = 5.4 - np.clip(9.8 - c.y, 0, None) * 1.0                 # o rosto afina para o queixo
    return (c.n[2] < -0.5) & (c.y < linha) & (np.abs(c.x) < largura)   # só a frente; borda azul dos lados


# ----------------------------------------------------------------------------- esqueleto
root = m.osso("root")
corpo = m.osso("body", pivo=[0, 2, 0], pai="root")
cab = m.osso("head", pivo=[0, 8, -0.5], pai="body")

# ----------------------------------------------------------------------------- corpo (pera pequena)
barriga = onde(e_(lambda c: c.n[2] < -0.4, lambda c: np.abs(c.x) < 2.7, lambda c: (c.y > 2.4) & (c.y < 7.9)),
               mat="branco")
corpo.cubo_arredondado([-3.5, 2, -3], [7, 6, 6], [base("azul"), barriga], raio=2, arestas="verticais")
corpo.segmento([0, 7, -0.5], [0, 8.5, -0.5], 5, 4.5, [base("azul"), onde(lambda c: c.n[2] < -0.4, mat="branco")],
               sobra=1)                                                                  # pescoço curto

# ----------------------------------------------------------------------------- cabeça (bola)
olhos_c = olhos_frente(OLHO, CORES_OLHO, 2.5, 11.75, -5.5, profundidade=0.4)
cab.cubo_arredondado([-5, 7, -4.5], [10, 1.5, 9], [base("azul"), onde(capuz, mat="branco")], raio=2.5,
                     arestas="verticais")                                                # queixo
cab.cubo_arredondado([-6.5, 8.5, -5.5], [13, 6.5, 11], [base("azul"), onde(capuz, mat="branco")] + olhos_c,
                     raio=2, arestas="verticais")                                         # bola
cab.cubo_arredondado([-5.5, 15, -4.5], [11, 2, 9], [base("azul")], raio=2.5, arestas="verticais")    # topo
cab.cubo_arredondado([-3.5, 17, -3], [7, 1, 6], [base("azul")], raio=1.5, arestas="verticais")        # cume
# focinho de bochechas fofas com a boquinha aberta
cab.cubo_arredondado([-3, 8, -6], [6, 2, 1], [base("branco"),
                     decalque(BOCA, CORES_BOCA, centro=[0, 9, -6], profundidade=0.4)], raio=0.5, arestas="verticais")
# orelhas: sobem do topo, dobram para fora e para trás, ponta caindo
for lado in (1, -1):
    pts = [[2.75 * lado, 16.5, 0], [3.5 * lado, 20, 0.5], [7.5 * lado, 21, 3], [11 * lado, 19.5, 5]]
    cab.cadeia(pts, [(3.5, 3), (3, 2.5), (2, 1.5)], [base("azul"), gradiente(1, 16, 23, -0.3, 0.6)], sobra=0.75)

# ----------------------------------------------------------------------------- bracinhos (abertos, para baixo)
for lado in (1, -1):
    b = m.osso("arm_left" if lado > 0 else "arm_right", pivo=[3 * lado, 6.5, -0.5], pai="body")
    b.segmento([3 * lado, 6.5, -0.5], [6 * lado, 4.5, -1], 2, 2, [base("azul")], sobra=0.75)
    b.cubo_arredondado([6 * lado - 1.25, 3.5, -2.25], [2.5, 2, 2.5], [base("azul")], raio=0.5)    # mãozinha

# ----------------------------------------------------------------------------- pezinhos
for lado in (1, -1):
    p = m.osso("leg_left" if lado > 0 else "leg_right", pivo=[2 * lado, 3, 0], pai="root")
    p.segmento([2 * lado, 3.5, 0], [2.25 * lado, 1.5, -0.5], 2.5, 2.5, [base("azul")], sobra=0.75)
    p.cubo_arredondado([2.5 * lado - 2, 0, -4], [4, 2, 5.5], [base("azul")], raio=1, arestas="verticais")

# ----------------------------------------------------------------------------- caudinha
cauda = m.osso("tail", pivo=[0, 4, 2.5], pai="body")
# cauda maior: sai das costas, desce e a ponta sobe em barbatana
cauda.segmento([0, 4.5, 1.5], [0, 2.5, 6.5], 3, 2.5, [base("azul")], raio=0.75, sobra=1)
cauda.segmento([0, 2.5, 6.5], [0, 4.5, 10.5], 2.5, 2, [base("azul"), gradiente(1, 2.5, 5, -0.2, 0.4)], sobra=0.75)
cauda.segmento([0, 4.5, 10.5], [0, 7, 12], 2, 1.5, [base("azul"), gradiente(1, 4.5, 7, 0.2, 0.8)], sobra=0.5)
cauda.segmento([0, 7, 12], [0, 8.5, 12.75], 1, 1, [base("azul")], sobra=0.25)          # ponta (sem recorte)

anims = bipede(peso=0.7)
d = anims["idle"]["animation_length"]
anims["idle"]["bones"]["tail"] = {"rotation": onda(10, d, eixo=1)}
for nome, an in anims.items():
    m.animacao(nome, an["animation_length"], an["bones"], an["loop"])

if __name__ == "__main__":
    finalizar(m, refs=("Chibimon_Model_DSR.png", "Chibimon.png", "Chibimon_survive.png"), zoom="head",
              estilo="0004_charmander")
