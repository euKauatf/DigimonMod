"""
Agumon refeito com a skill modelos-minecraft (teste de comparação; não substitui o do mod).

    D:\\FerramentasMinecraft\\venv\\Scripts\\python.exe tools/modelos/agumon_skill.py
"""
import os
import sys

sys.path.insert(0, r"D:\FerramentasMinecraft\skills\modelos-minecraft\scripts")
from mcmodel import *  # noqa: E402,F403

m = Modelo("agumon", densidade=2)

m.material("pele", rampa("#F5A833", n=7, base=4, saturar_sombras=1.3), ruido=0.06, pontilhado=0.25)
m.material("garra", rampa("#C9D3DE", n=5, base=3, desvio=0.6), ruido=0, aresta_clara=0.8, volume=0.3)
m.material("boca", rampa("#6A2222", n=3, base=1), ruido=0, volume=0, aresta_clara=0, oclusao=0.4)

OLHO = """
kkkkk.
kgggkk
kggPGk
kGGPGk
.kkkk.
"""
CORES_OLHO = {"k": "#1A1612", "g": "#2E9E46", "G": "#6FD25E", "P": "#0D0B0A"}
DENTE = "#F4F1E8"

# ------------------------------------------------------------------ corpo
root = m.osso("root")
corpo = m.osso("body", pivo=[0, 8, 0], pai="root")
corpo.cubo([-4, 6, -3], [8, 6, 6], [base("pele")])                 # quadril/barriga (mais largo)
corpo.cubo([-3.5, 11, -2.5], [7, 4, 5], [base("pele")])            # peito

# ------------------------------------------------------------------ cabeça
cab = m.osso("head", pivo=[0, 14.5, -1], pai="body")
cab.cubo([-4.5, 15, -5], [9, 7, 8], [
    base("pele"),
    onde(e_(faces("north"), abaixo(17.5), entre(0, -3.5, 3.5)), mat="boca"),   # fundo da boca, só atrás do focinho
], faces={"north": [par_de_sprites(OLHO, CORES_OLHO, (0.25, 0.18), (0.75, 0.18), brilho=[(1, 1)])]})
# focinho superior: nariz na ponta de cima, fileira de dentes na borda de baixo
cab.cubo([-3.5, 17.5, -9.5], [7, 2, 4.5], [
    base("pele"),
    so_faces(("north", "east", "west"), onde(local(1, 0, 0.25), mat="boca")),            # linha da boca
    so_faces(("north",), onde(e_(local(1, 0, 0.25), listras(0, 1.5, 0.5, fase=0.5)), cor=DENTE)),
    so_faces(("east", "west"), onde(e_(local(1, 0, 0.25), listras(2, 1.5, 0.5)), cor=DENTE)),
], faces={"up": [pixels([(4, 7), (9, 7)], ("boca", 0))], "down": [base("boca")]})
# mandíbula, um pouco mais estreita, com dentinhos em cima
cab.cubo([-3, 15, -9], [6, 2, 4], [
    base("pele"),
    so_faces(("north", "east", "west"), onde(local(1, 0.75, 1.01), mat="boca")),
    so_faces(("north",), onde(e_(local(1, 0.75, 1.01), listras(0, 1.5, 0.5, fase=1.25)), cor=DENTE)),
    so_faces(("east", "west"), onde(e_(local(1, 0.75, 1.01), listras(2, 1.5, 0.5, fase=0.75)), cor=DENTE)),
], faces={"up": [base("boca")]})


# ------------------------------------------------------------------ braços (curtos, garras para a frente)
def braco(nome, x0, lado):
    b = m.osso(nome, pivo=[x0 + lado * 0.5, 14, -1], pai="body", rotacao=[-20, 0, lado * -8])
    xb = x0 if lado > 0 else x0 - 2
    b.cubo([xb, 10, -2], [2, 5, 2], [base("pele")])
    b.cubo([xb - 0.25, 9, -2.75], [2.5, 1.5, 2.5], [base("pele")])
    for k in range(3):
        b.cubo([xb - 0.25 + k * 1.0, 7.5, -2.75], [0.5, 1.5, 0.5], [base("garra"), gradiente(1, 7.5, 9, 1.5, -0.5)])


braco("arm_left", 3.5, 1)
braco("arm_right", -3.5, -1)


# ------------------------------------------------------------------ pernas (grossas, pés com 3 garras)
def perna(nome, x0):
    p = m.osso(nome, pivo=[x0 + 1.5, 7, 0], pai="root")
    p.cubo([x0, 1, -2], [3, 7, 4], [base("pele")])
    p.cubo([x0 - 0.25, 0, -4], [3.5, 1.5, 5.5], [base("pele")])
    for k in range(3):
        p.cubo([x0 - 0.25 + k * 1.5, 0, -5], [0.5, 1, 1], [base("garra"), gradiente(2, -5, -4, 1.5, 0)])


perna("leg_left", 1)
perna("leg_right", -4)

# ------------------------------------------------------------------ cauda (grossa, afinando, quase no chão)
cauda = m.osso("tail", pivo=[0, 8, 2.5], pai="body", rotacao=[-12, 0, 0])
cauda.cubo([-2.5, 5.5, 2.5], [5, 4, 5], [base("pele")])
ponta = m.osso("tail_tip", pivo=[0, 7.5, 7], pai="tail", rotacao=[-10, 0, 0])
ponta.cubo([-1.5, 5.5, 7], [3, 3, 4], [base("pele")])
fim = m.osso("tail_end", pivo=[0, 7, 10.5], pai="tail_tip", rotacao=[-8, 0, 0])
fim.cubo([-1, 5.5, 10.5], [2, 2, 3], [base("pele")])

# ------------------------------------------------------------------ animações (mesmos nomes do mod)
anims = bipede(peso=0.9)
anims["idle"]["bones"]["tail_tip"] = {"rotation": onda(6, 2.16, eixo=1, fase=60)}
anims["walk"]["bones"]["tail_tip"] = {"rotation": onda(10, 0.81, eixo=1, fase=150)}
anims["walk"]["bones"]["tail_end"] = {"rotation": onda(8, 0.81, eixo=1, fase=210)}
for nome, a in anims.items():
    m.animacao(nome, a["animation_length"], a["bones"], a["loop"])

if __name__ == "__main__":
    m.salvar(os.path.join(os.path.dirname(os.path.abspath(__file__)), "saida"))
