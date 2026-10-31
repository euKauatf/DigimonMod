"""
Gera texturas, modelos e blockstates dos blocos do mod (altar, Digi-Eggs, incubadora).

Uso:  python tools/gerar_blocos.py
"""
import json
import os
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(RAIZ, "src", "main", "resources", "assets", "digimonaurity")
NS = "digimonaurity"


def hexc(h, a=255):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def nova(cor):
    return Image.new("RGBA", (16, 16), hexc(cor))


def salvar_textura(nome, img):
    pasta = os.path.join(ASSETS, "textures", "block")
    os.makedirs(pasta, exist_ok=True)
    img.save(os.path.join(pasta, f"{nome}.png"))


def salvar_json(*partes, dados):
    caminho = os.path.join(ASSETS, *partes)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2)


def bloco_simples(nome, modelo):
    """Blockstate + modelo de item apontando para o modelo do bloco."""
    salvar_json("blockstates", f"{nome}.json", dados={"variants": {"": {"model": f"{NS}:block/{nome}"}}})
    salvar_json("models", "block", f"{nome}.json", dados=modelo)
    salvar_json("items", f"{nome}.json", dados={"model": {"type": "minecraft:model", "model": f"{NS}:block/{nome}"}})


# ------------------------------------------------------------------ altar

def altar():
    escuro, ciano, ciano_claro = "#1E2430", "#2FC4D6", "#9AF2FF"
    topo = nova(escuro)
    for i in range(16):  # moldura
        for p in ((i, 0), (i, 15), (0, i), (15, i)):
            topo.putpixel(p, hexc("#2A3242"))
    # Círculo digital com cruz no meio
    for x in range(16):
        for y in range(16):
            d = ((x - 7.5) ** 2 + (y - 7.5) ** 2) ** 0.5
            if 4.5 < d < 5.6:
                topo.putpixel((x, y), hexc(ciano))
    for i in range(5, 11):
        topo.putpixel((i, 7), hexc(ciano_claro))
        topo.putpixel((7, i), hexc(ciano_claro))
    salvar_textura("territory_altar_top", topo)

    lado = nova(escuro)
    for x in range(16):
        lado.putpixel((x, 0), hexc("#2A3242"))
        lado.putpixel((x, 15), hexc("#141820"))
    # Linhas de circuito
    for y in (4, 11):
        for x in range(2, 14):
            lado.putpixel((x, y), hexc(ciano))
    for x in (4, 11):
        for y in range(4, 12):
            lado.putpixel((x, y), hexc(ciano))
    for p in ((4, 4), (11, 4), (4, 11), (11, 11)):
        lado.putpixel(p, hexc(ciano_claro))
    salvar_textura("territory_altar_side", lado)

    bloco_simples("territory_altar", {
        "parent": "minecraft:block/cube_bottom_top",
        "textures": {"top": f"{NS}:block/territory_altar_top", "bottom": f"{NS}:block/territory_altar_side",
                     "side": f"{NS}:block/territory_altar_side"},
    })


# --------------------------------------------------------------- Digi-Eggs

def ovo(nome, base, listra, mancha):
    img = nova(base)
    # Zigue-zague horizontal no meio e manchas
    for x in range(16):
        y = 7 + (1 if (x // 2) % 2 else -1)
        img.putpixel((x, y), hexc(listra))
        img.putpixel((x, y + 1), hexc(listra))
    for p in ((3, 2), (11, 3), (6, 12), (12, 12), (2, 11)):
        img.putpixel(p, hexc(mancha))
        img.putpixel((p[0] + 1, p[1]), hexc(mancha))
    for x in range(16):
        img.putpixel((x, 15), hexc(listra))
    salvar_textura(nome, img)

    faces = lambda uv: {f: {"uv": uv, "texture": "#egg"} for f in ("north", "south", "east", "west", "up", "down")}
    bloco_simples(nome, {
        "parent": "minecraft:block/block",
        "textures": {"particle": f"{NS}:block/{nome}", "egg": f"{NS}:block/{nome}"},
        "elements": [
            {"from": [5, 0, 5], "to": [11, 6, 11], "faces": faces([5, 8, 11, 14])},
            {"from": [5.5, 6, 5.5], "to": [10.5, 8, 10.5], "faces": faces([5, 5, 10, 8])},
            {"from": [6.5, 8, 6.5], "to": [9.5, 9, 9.5], "faces": faces([6, 2, 9, 4])},
        ],
    })


# --------------------------------------------------------------- incubadora

def incubadora():
    metal, metal_esc, vidro, luz = "#B8BEC6", "#8A9099", "#9FD8E8", "#F7E27A"
    lado = nova(metal)
    for x in range(16):
        lado.putpixel((x, 0), hexc(metal_esc))
        lado.putpixel((x, 15), hexc(metal_esc))
    # Janela de vidro com um ovo dentro
    for x in range(3, 13):
        for y in range(3, 12):
            lado.putpixel((x, y), hexc(vidro))
    for x in range(6, 10):
        for y in range(5, 11):
            if not ((y == 5 and x in (6, 9))):
                lado.putpixel((x, y), hexc("#F3EEDC"))
    for x in range(3, 13):
        lado.putpixel((x, 12), hexc(metal_esc))
    lado.putpixel((7, 13), hexc(luz))
    lado.putpixel((8, 13), hexc(luz))
    salvar_textura("incubator_side", lado)

    topo = nova(metal)
    for x in range(2, 14):
        for y in range(2, 14):
            topo.putpixel((x, y), hexc(vidro))
    for x in range(6, 10):
        for y in range(6, 10):
            topo.putpixel((x, y), hexc("#F3EEDC"))
    salvar_textura("incubator_top", topo)
    salvar_textura("incubator_bottom", nova(metal_esc))

    bloco_simples("incubator", {
        "parent": "minecraft:block/cube_bottom_top",
        "textures": {"top": f"{NS}:block/incubator_top", "bottom": f"{NS}:block/incubator_bottom",
                     "side": f"{NS}:block/incubator_side"},
    })


# ------------------------------------------------------------------ itens

def cromo_digizoide():
    """Fragmento metálico prateado com brilho azul (item simples, sem bloco)."""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    forma = [
        "......##........",
        ".....#aa#.......",
        "....#abba#......",
        "...#abbbba#.....",
        "..#abbccbba#....",
        "..#abbcdcbba#...",
        "...#abcddcba#...",
        "...#abbcdcba#...",
        "....#abbcba#....",
        "....#abbbba#....",
        ".....#abba#.....",
        ".....#abba#.....",
        "......#aa#......",
        ".......##.......",
        "................",
        "................",
    ]
    cores = {"#": "#4A5260", "a": "#E8EEF4", "b": "#B8C0C8", "c": "#8AB8E8", "d": "#D8F0FF"}
    for y, linha in enumerate(forma):
        for x, ch in enumerate(linha):
            if ch in cores:
                img.putpixel((x, y), hexc(cores[ch]))
    pasta = os.path.join(ASSETS, "textures", "item")
    os.makedirs(pasta, exist_ok=True)
    img.save(os.path.join(pasta, "chrome_digizoid.png"))
    salvar_json("models", "item", "chrome_digizoid.json",
                dados={"parent": "minecraft:item/generated", "textures": {"layer0": f"{NS}:item/chrome_digizoid"}})
    salvar_json("items", "chrome_digizoid.json",
                dados={"model": {"type": "minecraft:model", "model": f"{NS}:item/chrome_digizoid"}})


# ---------------------------------------------------------------- pedestal

def pedestal():
    ouro, ouro_esc, laranja, azul = "#E8B530", "#B8862A", "#F08A24", "#7FB6E6"
    topo = nova(ouro)
    for i in range(16):
        for p in ((i, 0), (i, 15), (0, i), (15, i)):
            topo.putpixel(p, hexc(ouro_esc))
    # Dois brasões lado a lado: sol (Coragem) e estrela (Amizade)
    for p in ((4, 7), (3, 7), (5, 7), (4, 6), (4, 8), (3, 6), (5, 8), (5, 6), (3, 8)):
        topo.putpixel(p, hexc(laranja))
    for p in ((11, 6), (11, 7), (11, 8), (10, 7), (12, 7), (11, 5), (11, 9), (9, 7), (13, 7)):
        topo.putpixel(p, hexc(azul))
    salvar_textura("crest_pedestal_top", topo)
    lado = nova(ouro)
    for x in range(16):
        lado.putpixel((x, 0), hexc(ouro_esc))
        lado.putpixel((x, 15), hexc(ouro_esc))
        lado.putpixel((x, 7), hexc(ouro_esc))
    for x in range(2, 14, 3):
        lado.putpixel((x, 4), hexc(laranja))
        lado.putpixel((x + 1, 11), hexc(azul))
    salvar_textura("crest_pedestal_side", lado)
    bloco_simples("crest_pedestal", {
        "parent": "minecraft:block/cube_bottom_top",
        "textures": {"top": f"{NS}:block/crest_pedestal_top", "bottom": f"{NS}:block/crest_pedestal_side",
                     "side": f"{NS}:block/crest_pedestal_side"},
    })


if __name__ == "__main__":
    pedestal()
    cromo_digizoide()
    altar()
    ovo("agumon_digiegg", "#FBF3DC", "#F08A24", "#E05A1A")
    ovo("gabumon_digiegg", "#F2F6FA", "#3D5AA8", "#7FB6E6")
    incubadora()
    print("blocos gerados")
