"""
Chibomon (Chicomon no Japão): o bebê antes do DemiVeemon. Medido na folha de modelo oficial do Adventure 02
(Chicomon_Adventure_02_reference_art.jpg, 13 vistas) e no modelo 3D oficial (Chicomon_Model_DSR.png).

Traços que identificam:
  1. uma GOTA só, azul-claro, sem braços nem pernas: base larga e chata, domo arredondado em cima
  2. UMA barbatana no alto da cabeça: sobe do centro e se curva para TRÁS, com a ponta saindo como
     um rabinho de girino (de frente parece um calombo no topo; de lado, uma onda para trás)
  3. olhos pretos redondos com borda rosa-magenta e brilho branco, bem afastados, no meio da frente
  4. boquinha em "ω" com a língua rosa, baixinha na frente
Medidas: largura 10, altura do corpo 7, fundura 9; barbatana sobe ~3 e vai ~6 para trás.
"""
from comum import *

m = Modelo("chibomon", densidade=2)
m.material("azul", rampa_manual("#466EA6", "#5E88C0", "#7AA4D8", "#96BEEA", "#B4D6F6", "#D4EAFE", base=3),
           estilo="limpo", ruido=0.05)

CORES_OLHO = {"k": "#100810", "P": "#0C060C", "m": "#C84A80", "W": "#FFFFFF"}
OLHO = """
.kkk.
kmWPk
kPPPk
kPPmk
.kkk.
"""
BOCA = """
b..bb..b
.bb..bb.
...pp...
"""
CORES_BOCA = {"b": "#2E3E66", "p": "#F07CA0"}

root = m.osso("root")
corpo = m.osso("body", pivo=[0, 0, 0], pai="root")
olhos_c = olhos_frente(OLHO, CORES_OLHO, 2.75, 3.5, -4.5, profundidade=0.4)
# gota: base larga com a frente lisa (olhos e boca) e um domo em degraus suaves por cima
corpo.cubo_arredondado([-5.5, 0, -4.5], [11, 5, 9], [base("azul"), gradiente(1, 0, 5, -0.6, 0.2)] + olhos_c
                       + [decalque(BOCA, CORES_BOCA, centro=[0, 1.5, -4.5], profundidade=0.4)],
                       raio=2, arestas="verticais")
for k, (w, h, d) in enumerate(((9.5, 1.5, 8), (8, 1, 6.5), (6, 0.75, 5), (3.5, 0.5, 3))):
    y0 = 5 + sum(t[1] for t in ((9.5, 1.5, 8), (8, 1, 6.5), (6, 0.75, 5), (3.5, 0.5, 3))[:k])
    corpo.cubo_arredondado([-w / 2, y0, -d / 2], [w, h, d], [base("azul"), gradiente(1, 5, 9, 0.2, 0.6)],
                           raio=min(2, w / 3, d / 3), arestas="verticais")

# barbatana do topo: nasce larga no alto do domo e se curva para trás até uma ponta (rabinho de girino)
fin = m.osso("fin", pivo=[0, 7, 0.5], pai="body")
fin.cadeia([[0, 6, 0], [0, 8.5, 2.5], [0, 8.5, 6]], [(3.5, 4.5), (2.5, 3)],
           [base("azul"), gradiente(1, 6, 10, 0, 0.6)], sobra=0.75)
fin.segmento([0, 8.5, 6], [0, 9.25, 8.5], 1.5, 1.5, [base("azul"), gradiente(1, 8.5, 10, 0.3, 0.8)], sobra=0.5)

anims = bolinha()
anims["idle"]["bones"]["fin"] = {"rotation": onda(6, 1.6, eixo=0)}
anims["walk"]["bones"]["fin"] = {"rotation": onda(12, 0.6, eixo=0, fase=90)}
for nome, an in anims.items():
    m.animacao(nome, an["animation_length"], an["bones"], an["loop"])

if __name__ == "__main__":
    finalizar(m, refs=("Chicomon_Model_DSR.png", "Chicomon.jpg", "Chicomon.png"), zoom=None, estilo="0004_charmander")
