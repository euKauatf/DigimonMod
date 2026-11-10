"""
Refaz os sprites do mod (texturas de blocos 16x16, item Chrome Digizoid e retratos dos iniciais 96x96)
no mesmo estilo dos modelos novos: cores vivas e lisas, sombreamento em rampa, sem chuvisco.

    D:\\FerramentasMinecraft\\venv\\Scripts\\python.exe tools/modelos/sprites.py
"""
import os

import numpy as np
from PIL import Image

from comum import *  # noqa: F401,F403  (rampa_manual, Textura2D, render...)
from comum import ASSETS
from mcmodel import Textura2D, base, onde, sprite, render

BLOCO = os.path.join(ASSETS, "textures", "block")
ITEM = os.path.join(ASSETS, "textures", "item")
GUI = os.path.join(ASSETS, "textures", "gui", "starter")


def chanfro(t, img_ctx_luz=1.0):
    """Camada: realce na borda de cima/esquerda e sombra na de baixo/direita (bloco com volume)."""
    def camada(c):
        m = (c.j == 0) | (c.i == 0)
        n = (c.j == c.h - 1) | (c.i == c.w - 1)
        c.luz[m & ~c.fixo] += img_ctx_luz
        c.luz[n & ~c.fixo] -= img_ctx_luz
    return camada


def degrade_vertical(de, ate):
    def camada(c):
        t = c.j / max(1, c.h - 1)
        c.luz[~c.fixo] += (de + (ate - de) * t)[~c.fixo]
    return camada


def salvar(img, pasta, nome):
    os.makedirs(pasta, exist_ok=True)
    img.save(os.path.join(pasta, nome + ".png"))
    return img


# ----------------------------------------------------------------------------- Digi-Eggs
# O modelo do ovo usa 3 faixas da textura: base [5..11]x[8..14], meio [5..10]x[5..8], topo [6..9]x[2..4].
# Pinto a textura inteira como um ovo (claro em cima, sombra embaixo) com o desenho de cada Digimon.
def ovo(nome, cor_casca, cor_desenho, arte):
    t = Textura2D(nome, 16, 16)
    t.material("casca", cor_casca, pontilhado=0)
    t.material("desenho", cor_desenho, pontilhado=0)
    cores = {"d": "desenho", "D": ("desenho", 1)}
    img = t.pintar(base("casca"), sprite(arte, cores), degrade_vertical(1.2, -1.4))
    return salvar(img, BLOCO, nome)


OVO_AGUMON = """
................
................
................
................
................
....D......D....
...dd.d..d.dd...
................
dd...dd..dd...dd
.dd.dddddddd.dd.
..dddd....dddd..
................
.......dd.......
......dddd......
................
................
"""
OVO_GABUMON = """
................
................
................
.......dd.......
................
...dd......dd...
..dDDd....dDDd..
................
d..d..d..d..d..d
dddddddddddddddd
.d..d..d..d..d..
................
...dd......dd...
..dddd....dddd..
................
................
"""

# ----------------------------------------------------------------------------- incubadora
def incubadora():
    metal = rampa_manual("#3A3F48", "#555C66", "#737B86", "#949CA6", "#B8BFC8", "#DCE1E6", base=3)
    vidro = rampa_manual("#2C6E88", "#3E90AE", "#5CB2CE", "#86D2E6", "#BCEAF4", base=2)
    lado = Textura2D("incubator_side", 16, 16)
    lado.material("metal", metal, pontilhado=0)
    lado.material("vidro", vidro, pontilhado=0)
    lado.material("ovo", rampa_manual("#B8A880", "#D8CCA8", "#F0E8CC", "#FFFBEA", base=2), pontilhado=0)
    lado.material("luz", rampa_manual("#B87010", "#E8A020", "#FFD040", "#FFF090", base=2), pontilhado=0)
    ARTE = """
................
.r............r.
...VVVVVVVVVV...
..VVVVVVVVVVVV..
..VVVvVVVVVVVV..
..VVvVVVOOVVVV..
..VVVVVOOOOVVV..
..VVVVVOOOOVVV..
..VVVVOOOOOOVV..
..VVVVOOOOOOVV..
..VVVVVOOOOVVV..
..VVVVVVVVVVVV..
...VVVVVVVVVV...
.r....LLLL....r.
................
................
"""
    cores = {"V": "vidro", "v": ("vidro", 2), "O": "ovo", "L": "luz", "r": ("metal", 2)}
    img = lado.pintar(base("metal"), sprite(ARTE, cores), chanfro(lado), degrade_vertical(0.4, -0.6))
    salvar(img, BLOCO, "incubator_side")

    topo = Textura2D("incubator_top", 16, 16)
    topo.material("metal", metal, pontilhado=0)
    topo.material("vidro", vidro, pontilhado=0)
    TOPO = """
................
.r............r.
.....VVVVVV.....
....VVvVVVVV....
...VVvVVVVVVV...
..VVVVVVVVVVVV..
..VVVVVVVVVVVV..
..VVVVVVVVVVVV..
..VVVVVVVVVVVV..
..VVVVVVVVVVVV..
..VVVVVVVVVVVV..
...VVVVVVVVVV...
....VVVVVVVV....
.....VVVVVV.....
.r............r.
................
"""
    img = topo.pintar(base("metal"), sprite(TOPO, {"V": "vidro", "v": ("vidro", 2), "r": ("metal", 2)}),
                      chanfro(topo))
    salvar(img, BLOCO, "incubator_top")

    fundo = Textura2D("incubator_bottom", 16, 16)
    fundo.material("metal", metal, base=2, pontilhado=0)
    GRADE = "\n".join(("." * 16) if j % 3 else "".join("g" if i % 3 else "." for i in range(16)) for j in range(16))
    img = fundo.pintar(base("metal"), sprite(GRADE, {"g": ("metal", -1)}), chanfro(fundo))
    salvar(img, BLOCO, "incubator_bottom")


# ----------------------------------------------------------------------------- altar do território
def altar():
    pedra = rampa_manual("#10141C", "#1A202C", "#252D3C", "#323C4E", "#424E62", base=2)
    ciano = rampa_manual("#0E6C80", "#16A0B8", "#2CD0E6", "#7CF0FF", "#D0FCFF", base=2)
    top = Textura2D("territory_altar_top", 16, 16)
    top.material("pedra", pedra, pontilhado=0)
    top.material("ciano", ciano, pontilhado=0, emissivo=True)
    TOP = """
................
.cc..........cc.
.c....CCCC....c.
.....C....C.....
....C..cc..C....
...C...cc...C...
..C....cc....C..
..C.cccCCccc.C..
..C.cccCCccc.C..
..C....cc....C..
...C...cc...C...
....C..cc..C....
.....C....C.....
.c....CCCC....c.
.cc..........cc.
................
"""
    img = top.pintar(base("pedra"), sprite(TOP, {"c": "ciano", "C": ("ciano", 1)}), chanfro(top))
    salvar(img, BLOCO, "territory_altar_top")
    lado = Textura2D("territory_altar_side", 16, 16)
    lado.material("pedra", pedra, pontilhado=0)
    lado.material("ciano", ciano, pontilhado=0)
    LADO = """
................
................
.cccc......cccc.
....c......c....
....c..CC..c....
....cccCCccc....
.......CC.......
....cccCCccc....
....c..CC..c....
....c......c....
.cccc......cccc.
................
pppppppppppppppp
p..p..p..p..p..p
pppppppppppppppp
................
"""
    img = lado.pintar(base("pedra"), sprite(LADO, {"c": "ciano", "C": ("ciano", 1), "p": ("pedra", 1)}),
                      chanfro(lado), degrade_vertical(0.3, -0.5))
    salvar(img, BLOCO, "territory_altar_side")


# ----------------------------------------------------------------------------- pedestal do brasão
def pedestal():
    ouro = rampa_manual("#7A5208", "#A8780C", "#D4A010", "#F0C41C", "#FFDC40", "#FFF080", base=3)
    top = Textura2D("crest_pedestal_top", 16, 16)
    top.material("ouro", ouro, pontilhado=0)
    top.material("laranja", rampa_manual("#B04010", "#E06018", "#FF8A2A", "#FFB860", base=2), pontilhado=0)
    top.material("azul", rampa_manual("#1C4A9A", "#2C6CD0", "#4C94F0", "#8AC0FF", base=2), pontilhado=0)
    TOP = """
................
.eeeeeeeeeeeeee.
.e............e.
.e.L..L..A...e..
.e..LLL..A...e..
.e.LLLLL.AAA.e..
.e..LLL..A...e..
.e.L..L..A...e..
.e............e.
.e..AAAAAAAA..e.
.e..A......A..e.
.e..AAAAAAAA..e.
.e............e.
.eeeeeeeeeeeeee.
................
................
"""
    img = top.pintar(base("ouro"), sprite(TOP, {"e": ("ouro", -1), "L": "laranja", "A": "azul"}), chanfro(top))
    salvar(img, BLOCO, "crest_pedestal_top")
    lado = Textura2D("crest_pedestal_side", 16, 16)
    lado.material("ouro", ouro, pontilhado=0)
    LADO = """
eeeeeeeeeeeeeeee
................
................
eeeeeeeeeeeeeeee
.e............e.
.e..e......e..e.
.e..e......e..e.
.e..e......e..e.
.e..e......e..e.
.e..e......e..e.
.e............e.
eeeeeeeeeeeeeeee
................
................
eeeeeeeeeeeeeeee
................
"""
    img = lado.pintar(base("ouro"), sprite(LADO, {"e": ("ouro", -1)}), chanfro(lado), degrade_vertical(0.6, -0.6))
    salvar(img, BLOCO, "crest_pedestal_side")


# ----------------------------------------------------------------------------- Chrome Digizoid (item)
def cromo():
    t = Textura2D("chrome_digizoid", 16, 16)
    t.material("metal", rampa_manual("#3A4250", "#5A6474", "#808A9A", "#A8B2C0", "#D0D8E2", "#F4F8FC", base=3),
               pontilhado=0)
    t.material("azul", rampa_manual("#1E4C9C", "#3070D0", "#58A0F0", "#9ACCFF", "#DDF0FF", base=2), pontilhado=0)
    ARTE = """
................
......mmmm......
....mmMMMMmm....
...mMMbbbMMMm...
..mMMbbBBbbMMm..
..mMbbBWWBbbMm..
.mMMbBWWBBbbMMm.
.mMbbBWBBbbbMMm.
.mMbbBBBbbbMMm..
..mMbbbbbbMMMm..
..mMMbbbbMMMm...
...mMMMMMMMm....
....mmMMMmm.....
......mmm.......
................
................
"""
    cores = {"m": "metal", "M": ("metal", 1), "b": "azul", "B": ("azul", 1), "W": ("azul", 2)}
    img = t.pintar(sprite(ARTE, cores), contorno="#1E2430", luz_de_cima=True)
    return salvar(img, ITEM, "chrome_digizoid")


# ----------------------------------------------------------------------------- retratos dos iniciais
def retrato(nome):
    geo = os.path.join(ASSETS, "geckolib", "models", "entity", f"{nome}.geo.json")
    png = os.path.join(ASSETS, "textures", "entity", f"{nome}.png")
    im = render.renderizar(geo, png, "3/4", fundo=(0, 0, 0, 0), altura_alvo=600)
    a = np.array(im)
    ys, xs = np.nonzero(a[..., 3])
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    lado = 88
    k = lado / max(im.size)
    im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    # limpa a meia-transparência (cutout do jogo) e dá contorno escuro de 1 pixel
    a = np.array(im)
    a[..., 3] = np.where(a[..., 3] > 110, 255, 0)
    tela = np.zeros((96, 96, 4), np.uint8)
    x0, y0 = (96 - a.shape[1]) // 2, 96 - 4 - a.shape[0]
    tela[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a
    cheio = tela[..., 3] > 0
    viz = np.zeros_like(cheio)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        viz |= np.roll(np.roll(cheio, dy, 0), dx, 1)
    borda = viz & ~cheio
    tela[borda] = (20, 16, 24, 255)
    return salvar(Image.fromarray(tela, "RGBA"), GUI, nome)


if __name__ == "__main__":
    ovo("agumon_digiegg", rampa_manual("#C8B89A", "#E2D6BE", "#F6EEDC", "#FFFAF0", "#FFFFFF", base=3),
        rampa_manual("#B04A10", "#D86A1A", "#F28A2A", "#FFAE50", base=2), OVO_AGUMON)
    ovo("gabumon_digiegg", rampa_manual("#B8C0D4", "#D4DAEA", "#ECF0FA", "#F8FAFF", "#FFFFFF", base=3),
        rampa_manual("#162A6E", "#24409A", "#3A5CC0", "#6080DA", base=2), OVO_GABUMON)
    incubadora()
    altar()
    pedestal()
    cromo()
    retrato("agumon")
    retrato("gabumon")
    print("sprites refeitos")
