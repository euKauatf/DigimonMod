"""
Gera modelos (.geo.json), animações (.animation.json) e texturas (.png) dos Digimon
no formato do GeckoLib, a partir de descrições em código (caixas coloridas).

Uso:  python tools/gerar_modelos.py

Convenções do formato (Bedrock geometry 1.12.0, usado pelo GeckoLib):
- 16 unidades = 1 bloco. O modelo olha para -Z (norte).
- "origin" de um cubo é o canto mínimo [x, y, z]; "pivot" é o ponto de rotação do osso.
- Cada face de cada cubo recebe um retângulo próprio na textura (UV por face),
  o que permite desenhar olhos, barriga e marcas exatamente onde queremos.
"""
import json
import os
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(RAIZ, "src", "main", "resources", "assets", "digimonaurity")
PASTA_MODELOS = os.path.join(ASSETS, "geckolib", "models", "entity")
PASTA_ANIMACOES = os.path.join(ASSETS, "geckolib", "animations", "entity")
PASTA_TEXTURAS = os.path.join(ASSETS, "textures", "entity")


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def escurecer(cor, f):
    return tuple(max(0, int(c * f)) for c in cor[:3]) + (255,)


# ---------------------------------------------------------------- pintura ---

class Face:
    """Pintor de uma face: cor base, borda escurecida e desenhos opcionais."""

    def __init__(self, cor, borda=0.78, desenho=None):
        self.cor = hex_rgb(cor) if isinstance(cor, str) else cor
        self.borda = borda
        self.desenho = desenho  # função(img, x, y, w, h)

    def pintar(self, img, x, y, w, h):
        for i in range(w):
            for j in range(h):
                img.putpixel((x + i, y + j), self.cor)
        if self.borda and w > 2 and h > 2:
            # Sombra na base da face; laterais só em faces largas (evita listras em pernas finas).
            escura = escurecer(self.cor, self.borda)
            for i in range(w):
                img.putpixel((x + i, y + h - 1), escura)
            if w >= 5:
                lateral = escurecer(self.cor, (1 + self.borda) / 2)
                for j in range(h):
                    img.putpixel((x, y + j), lateral)
                    img.putpixel((x + w - 1, y + j), lateral)
        if self.desenho:
            self.desenho(img, x, y, w, h)


def px(img, x, y, cor):
    img.putpixel((x, y), hex_rgb(cor))


def retangulo(img, x, y, w, h, cor):
    for i in range(w):
        for j in range(h):
            px(img, x + i, y + j, cor)


# ------------------------------------------------------------------ cubos ---

FACES = ("north", "south", "east", "west", "up", "down")


class Cubo:
    def __init__(self, origem, tamanho, cor, faces=None, inflar=0.0):
        self.origem = origem
        self.tamanho = tamanho
        self.base = Face(cor) if isinstance(cor, str) else cor
        self.faces = faces or {}  # nome da face -> Face
        self.inflar = inflar

    def dimensoes_face(self, face):
        w, h, d = self.tamanho
        return {"north": (w, h), "south": (w, h), "east": (d, h), "west": (d, h),
                "up": (w, d), "down": (w, d)}[face]


class Osso:
    def __init__(self, nome, pivo, pai=None, cubos=None, rotacao=None):
        self.nome = nome
        self.pivo = pivo
        self.pai = pai
        self.cubos = cubos or []
        self.rotacao = rotacao


# --------------------------------------------------------------- empacotar ---

def empacotar(ossos, largura=128):
    """Distribui todos os retângulos de face na textura (empacotamento em prateleiras)."""
    pedidos = []
    for osso in ossos:
        for cubo in osso.cubos:
            for face in FACES:
                w, h = cubo.dimensoes_face(face)
                w, h = max(1, int(round(w))), max(1, int(round(h)))
                pedidos.append((cubo, face, w, h))
    pedidos.sort(key=lambda p: -p[3])
    x = y = altura_prateleira = 0
    posicoes = {}
    for cubo, face, w, h in pedidos:
        if x + w > largura:
            x, y = 0, y + altura_prateleira
            altura_prateleira = 0
        posicoes[(id(cubo), face)] = (x, y, w, h)
        x += w
        altura_prateleira = max(altura_prateleira, h)
    altura = y + altura_prateleira
    altura_final = 16
    while altura_final < altura:
        altura_final *= 2
    return posicoes, largura, altura_final


def gerar(nome, ossos, animacoes, largura_textura=128):
    posicoes, tw, th = empacotar(ossos, largura_textura)
    img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))

    ossos_json = []
    for osso in ossos:
        cubos_json = []
        for cubo in osso.cubos:
            uv = {}
            for face in FACES:
                x, y, w, h = posicoes[(id(cubo), face)]
                (cubo.faces.get(face) or cubo.base).pintar(img, x, y, w, h)
                if face == "down":
                    uv[face] = {"uv": [x, y + h], "uv_size": [w, -h]}
                else:
                    uv[face] = {"uv": [x, y], "uv_size": [w, h]}
            c = {"origin": cubo.origem, "size": cubo.tamanho, "uv": uv}
            if cubo.inflar:
                c["inflate"] = cubo.inflar
            cubos_json.append(c)
        o = {"name": osso.nome, "pivot": osso.pivo}
        if osso.pai:
            o["parent"] = osso.pai
        if osso.rotacao:
            o["rotation"] = osso.rotacao
        if cubos_json:
            o["cubes"] = cubos_json
        ossos_json.append(o)

    geo = {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": f"geometry.{nome}",
                "texture_width": tw,
                "texture_height": th,
                "visible_bounds_width": 4,
                "visible_bounds_height": 4,
                "visible_bounds_offset": [0, 1, 0],
            },
            "bones": ossos_json,
        }],
    }

    for pasta in (PASTA_MODELOS, PASTA_ANIMACOES, PASTA_TEXTURAS):
        os.makedirs(pasta, exist_ok=True)
    with open(os.path.join(PASTA_MODELOS, f"{nome}.geo.json"), "w", encoding="utf-8") as f:
        json.dump(geo, f, indent=1)
    with open(os.path.join(PASTA_ANIMACOES, f"{nome}.animation.json"), "w", encoding="utf-8") as f:
        json.dump({"format_version": "1.8.0", "animations": animacoes}, f, indent=1)
    img.save(os.path.join(PASTA_TEXTURAS, f"{nome}.png"))
    print(f"{nome}: textura {tw}x{th}, {len(ossos)} ossos")


# ------------------------------------------------------------- animações ---

def onda(amplitude, periodo, fase=0.0, eixo=0, base=(0, 0, 0)):
    """Expressão Molang de oscilação senoidal num eixo (graus ou unidades)."""
    vals = [str(v) for v in base]
    vals[eixo] = f"{base[eixo]} + math.sin((query.anim_time / {periodo}) * 360 + {fase}) * {amplitude}"
    return vals


# ================================================================ AGUMON ===

LARANJA = "#F4A62A"
LARANJA_ESC = "#D9821A"
CREME = "#FBE3A6"
VERDE = "#3FB54A"
BRANCO = "#F4F4F0"
ROXO = "#7B4FA0"
BOCA = "#5A2A1E"


def agumon():
    def olhos(img, x, y, w, h):
        # Dois olhos grandes, verdes, com pupila e brilho.
        for ox in (1, w - 4):
            retangulo(img, x + ox, y + 1, 3, 3, BRANCO)
            retangulo(img, x + ox + 1, y + 1, 2, 3, VERDE)
            px(img, x + ox + 1, y + 2, "#1B1B1B")
            px(img, x + ox + 2, y + 1, BRANCO)

    def focinho(img, x, y, w, h):
        # Narinas no topo da frente do focinho
        px(img, x + 1, y, BOCA)
        px(img, x + w - 2, y, BOCA)

    def boca(img, x, y, w, h):
        # Linha da boca com dentinhos brancos, mandíbula clara embaixo
        retangulo(img, x, y, w, 1, BOCA)
        px(img, x + 1, y, BRANCO)
        px(img, x + w - 2, y, BRANCO)
        retangulo(img, x, y + 1, w, h - 1, CREME)

    def barriga(img, x, y, w, h):
        retangulo(img, x + 1, y, w - 2, h - 1, CREME)

    def marcas_braco(img, x, y, w, h):
        retangulo(img, x, y + 1, w, 1, ROXO)

    def garras(img, x, y, w, h):
        for i in range(0, w, 2):
            px(img, x + i, y + h - 1, BRANCO)

    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 8, 0], "root", [
            # Corpo em forma de pera: quadril largo, peito mais estreito
            Cubo([-4, 6, -3], [8, 5, 6], LARANJA, {"north": Face(LARANJA, borda=0, desenho=barriga)}),
            Cubo([-3.5, 11, -2.5], [7, 4, 5], LARANJA, {"north": Face(LARANJA, desenho=barriga)}),
        ]),
        Osso("head", [0, 15, -1], "body", [
            Cubo([-4.5, 15, -5.5], [9, 7, 8], LARANJA, {"north": Face(LARANJA, desenho=olhos)}),
            Cubo([-3, 16.5, -9], [6, 2, 4], LARANJA, {"north": Face(LARANJA, borda=0, desenho=focinho)}),
            Cubo([-3, 15, -8.5], [6, 1.5, 3.5], CREME, {"north": Face(CREME, borda=0, desenho=boca)}),
        ]),
        Osso("arm_left", [4, 14, -1], "body", [
            Cubo([3.5, 10, -2], [2, 4, 2], LARANJA, {"north": Face(LARANJA, desenho=marcas_braco)}),
            Cubo([3.5, 9, -3], [2, 1, 3], LARANJA, {"north": Face(LARANJA, desenho=garras),
                                                    "down": Face(BRANCO)}),
        ]),
        Osso("arm_right", [-4, 14, -1], "body", [
            Cubo([-5.5, 10, -2], [2, 4, 2], LARANJA, {"north": Face(LARANJA, desenho=marcas_braco)}),
            Cubo([-5.5, 9, -3], [2, 1, 3], LARANJA, {"north": Face(LARANJA, desenho=garras),
                                                     "down": Face(BRANCO)}),
        ]),
        Osso("leg_left", [2.5, 7, 0], "root", [
            Cubo([1, 0, -2.5], [3, 7, 4], LARANJA_ESC),
            Cubo([1, 0, -4.5], [3, 1.5, 2], Face(LARANJA_ESC, borda=0, desenho=garras)),
        ]),
        Osso("leg_right", [-2.5, 7, 0], "root", [
            Cubo([-4, 0, -2.5], [3, 7, 4], LARANJA_ESC),
            Cubo([-4, 0, -4.5], [3, 1.5, 2], Face(LARANJA_ESC, borda=0, desenho=garras)),
        ]),
        Osso("tail", [0, 8, 3], "body", [
            Cubo([-2, 6, 3], [4, 3, 5], LARANJA),
        ]),
        Osso("tail_tip", [0, 7.5, 8], "tail", [
            Cubo([-1.5, 6, 8], [3, 2, 4], LARANJA),
        ]),
    ]

    animacoes = {f"animation.agumon.{n}": a for n, a in _animacoes_bipede().items()}
    gerar("agumon", ossos, animacoes)


# =============================================================== GABUMON ===

AZUL = "#7FB6E6"
AZUL_LISTRA = "#3D5AA8"
BRANCO_PELO = "#EEF3F7"
AMARELO = "#E9C25A"
CHIFRE = "#E8B23A"
VERMELHO = "#C8282E"


def gabumon():
    def listras(img, x, y, w, h):
        # Listras escuras características da pele de Garurumon
        for i in range(1, w - 1, 3):
            retangulo(img, x + i, y, 1, max(1, h // 2), AZUL_LISTRA)

    def capuz_frente(img, x, y, w, h):
        # Olhos vermelhos logo abaixo da borda do capuz, acima do focinho
        retangulo(img, x, y, w, 1, AZUL_LISTRA)
        for ox in (1, w - 4):
            retangulo(img, x + ox, y + 1, 3, 2, BRANCO)
            retangulo(img, x + ox + 1, y + 1, 2, 2, VERMELHO)
            px(img, x + ox + 1, y + 1, "#1B1B1B")

    def focinho(img, x, y, w, h):
        px(img, x + 1, y, "#5A3A1E")
        px(img, x + w - 2, y, "#5A3A1E")
        retangulo(img, x, y + h - 1, w, 1, "#5A3A1E")

    def barriga(img, x, y, w, h):
        retangulo(img, x + 1, y, w - 2, h - 1, BRANCO_PELO)

    def ponta_branca(img, x, y, w, h):
        retangulo(img, x, y + h - 2, w, 2, BRANCO_PELO)

    def garras(img, x, y, w, h):
        for i in range(0, w, 2):
            px(img, x + i, y + h - 1, BRANCO)

    pelo = lambda: Face(AZUL, desenho=listras)

    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 8, 0], "root", [
            Cubo([-4, 6, -3], [8, 5, 6], pelo(), {"north": Face(AZUL, borda=0, desenho=barriga)}),
            Cubo([-3.5, 11, -2.5], [7, 4, 5], pelo(), {"north": Face(AZUL, desenho=barriga)}),
        ]),
        Osso("head", [0, 15, -1], "body", [
            # Capuz de pele com chifre
            Cubo([-4.5, 15, -5.5], [9, 7, 8], pelo(), {"north": Face(AZUL, desenho=capuz_frente)}),
            Cubo([-0.75, 22, -4.5], [1.5, 3, 1.5], CHIFRE),
            # Focinho amarelo saindo do capuz
            Cubo([-2.5, 15.5, -8.5], [5, 3, 3], AMARELO, {"north": Face(AMARELO, borda=0, desenho=focinho)}),
        ]),
        Osso("arm_left", [4, 14, -1], "body", [
            Cubo([3.5, 9, -2], [2, 5, 2], pelo(), {"north": Face(AZUL, desenho=ponta_branca)}),
            Cubo([3.5, 8, -3], [2, 1, 3], AMARELO, {"north": Face(AMARELO, desenho=garras)}),
        ]),
        Osso("arm_right", [-4, 14, -1], "body", [
            Cubo([-5.5, 9, -2], [2, 5, 2], pelo(), {"north": Face(AZUL, desenho=ponta_branca)}),
            Cubo([-5.5, 8, -3], [2, 1, 3], AMARELO, {"north": Face(AMARELO, desenho=garras)}),
        ]),
        Osso("leg_left", [2.5, 7, 0], "root", [
            Cubo([1, 0, -2.5], [3, 7, 4], pelo()),
            Cubo([1, 0, -4.5], [3, 1.5, 2], Face(AMARELO, borda=0, desenho=garras)),
        ]),
        Osso("leg_right", [-2.5, 7, 0], "root", [
            Cubo([-4, 0, -2.5], [3, 7, 4], pelo()),
            Cubo([-4, 0, -4.5], [3, 1.5, 2], Face(AMARELO, borda=0, desenho=garras)),
        ]),
        Osso("tail", [0, 8, 3], "body", [
            Cubo([-2, 6, 3], [4, 3, 5], pelo()),
        ]),
        Osso("tail_tip", [0, 7.5, 8], "tail", [
            Cubo([-1.5, 6, 8], [3, 2, 4], Face(BRANCO_PELO)),
        ]),
    ]

    animacoes = {f"animation.gabumon.{n}": a for n, a in _animacoes_bipede().items()}
    gerar("gabumon", ossos, animacoes)


def _animacoes_bipede(peso=1.0):
    """Animações de bípede. peso > 1 deixa tudo mais lento e com passos mais curtos (Digimon grandes)."""
    p = peso
    return {
        "idle": {
            "loop": True,
            "animation_length": 2.0 * p,
            "bones": {
                "body": {"position": onda(0.25 * p, 2.0 * p, eixo=1)},
                "head": {"rotation": onda(2, 2.0 * p, fase=60)},
                "tail": {"rotation": onda(6, 2.0 * p, eixo=1)},
                "tail_tip": {"rotation": onda(8, 2.0 * p, fase=45, eixo=1)},
                "arm_left": {"rotation": onda(3, 2.0 * p)},
                "arm_right": {"rotation": onda(3, 2.0 * p, fase=180)},
            },
        },
        "walk": {
            "loop": True,
            "animation_length": 0.8 * p,
            "bones": {
                "leg_left": {"rotation": onda(30 / p, 0.8 * p)},
                "leg_right": {"rotation": onda(30 / p, 0.8 * p, fase=180)},
                "arm_left": {"rotation": onda(20 / p, 0.8 * p, fase=180)},
                "arm_right": {"rotation": onda(20 / p, 0.8 * p)},
                "body": {"position": onda(0.5 * p, 0.4 * p, eixo=1),
                         "rotation": onda(3, 0.8 * p, eixo=2)},
                "head": {"rotation": onda(3, 0.4 * p)},
                "tail": {"rotation": onda(10, 0.8 * p, eixo=1)},
                "tail_tip": {"rotation": onda(12, 0.8 * p, fase=60, eixo=1)},
            },
        },
        # Golpe rápido: inclina o corpo, projeta a cabeça e os braços para a frente e volta.
        "attack": {
            "loop": False,
            "animation_length": 0.4,
            "bones": {
                "body": {"rotation": {"0.0": [0, 0, 0], "0.12": [12, 0, 0], "0.4": [0, 0, 0]}},
                "head": {"rotation": {"0.0": [0, 0, 0], "0.1": [-15, 0, 0], "0.2": [10, 0, 0], "0.4": [0, 0, 0]}},
                "arm_left": {"rotation": {"0.0": [0, 0, 0], "0.12": [-60, 0, -10], "0.4": [0, 0, 0]}},
                "arm_right": {"rotation": {"0.0": [0, 0, 0], "0.12": [-60, 0, 10], "0.4": [0, 0, 0]}},
                "tail": {"rotation": {"0.0": [0, 0, 0], "0.12": [-10, 0, 0], "0.4": [0, 0, 0]}},
            },
        },
    }


# ======================================================== FRESH / IN-TRAINING ===

def _animacoes_bolinha():
    """Bolinhas (Fresh/In-Training): respiram esticando e andam pulando."""
    return {
        "idle": {
            "loop": True,
            "animation_length": 1.6,
            "bones": {
                "body": {"scale": [
                    "1 + math.sin(query.anim_time / 1.6 * 360) * 0.04",
                    "1 - math.sin(query.anim_time / 1.6 * 360) * 0.05",
                    "1 + math.sin(query.anim_time / 1.6 * 360) * 0.04"]},
            },
        },
        "walk": {
            "loop": True,
            "animation_length": 0.5,
            "bones": {
                "body": {
                    "position": ["0", "math.abs(math.sin(query.anim_time / 0.5 * 180)) * 2.5", "0"],
                    "scale": ["1", "1 + math.abs(math.sin(query.anim_time / 0.5 * 180)) * 0.08", "1"],
                },
            },
        },
        "attack": {
            "loop": False,
            "animation_length": 0.3,
            "bones": {
                "body": {"scale": {"0.0": [1, 1, 1], "0.1": [1.15, 0.85, 1.15], "0.3": [1, 1, 1]}},
            },
        },
    }


def botamon():
    PRETO = "#2A2A2E"
    PELO = "#3A3A40"
    AMARELO_OLHO = "#F5D83A"

    def rosto(img, x, y, w, h):
        for ox in (1, w - 3):
            retangulo(img, x + ox, y + 2, 2, 2, AMARELO_OLHO)
            px(img, x + ox + (1 if ox == 1 else 0), y + 3, "#1B1B1B")

    def pelinho(img, x, y, w, h):
        # Pontinhos claros dão textura de pelo
        for i in range(0, w, 2):
            for j in range((i // 2) % 2, h, 2):
                px(img, x + i, y + j, PELO)

    pele = lambda: Face(PRETO, desenho=pelinho)
    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 0, 0], "root", [
            Cubo([-4, 0, -4], [8, 7, 8], pele(), {"north": Face(PRETO, desenho=rosto)}),
            Cubo([-3, 7, -3], [6, 1, 6], pele()),
        ]),
    ]
    gerar("botamon", ossos, {f"animation.botamon.{n}": a for n, a in _animacoes_bolinha().items()})


def koromon():
    ROSA = "#F2A0B6"
    ROSA_ESC = "#D9819A"
    VERMELHO_OLHO = "#D22B2B"

    def rosto(img, x, y, w, h):
        for ox in (1, w - 3):
            retangulo(img, x + ox, y + 2, 2, 2, BRANCO)
            px(img, x + ox + (1 if ox == 1 else 0), y + 3, VERMELHO_OLHO)
        retangulo(img, x + 3, y + h - 3, w - 6, 1, "#7A2E3A")

    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 0, 0], "root", [
            Cubo([-4.5, 0, -4], [9, 7, 8], ROSA, {"north": Face(ROSA, desenho=rosto)}),
        ]),
        # Orelhas compridas que caem para trás
        Osso("ear_left", [2.5, 7, 1], "body", [
            Cubo([1.5, 6.5, 1], [2, 1, 8], ROSA_ESC),
        ], rotacao=[-35, 0, 0]),
        Osso("ear_right", [-2.5, 7, 1], "body", [
            Cubo([-3.5, 6.5, 1], [2, 1, 8], ROSA_ESC),
        ], rotacao=[-35, 0, 0]),
    ]
    animacoes = _animacoes_bolinha()
    animacoes["idle"]["bones"]["ear_left"] = {"rotation": onda(6, 1.6, base=(-35, 0, 0))}
    animacoes["idle"]["bones"]["ear_right"] = {"rotation": onda(6, 1.6, fase=90, base=(-35, 0, 0))}
    animacoes["walk"]["bones"]["ear_left"] = {"rotation": onda(15, 0.5, base=(-35, 0, 0))}
    animacoes["walk"]["bones"]["ear_right"] = {"rotation": onda(15, 0.5, fase=180, base=(-35, 0, 0))}
    gerar("koromon", ossos, {f"animation.koromon.{n}": a for n, a in animacoes.items()})


# =============================================================== GREYMON ===

def greymon():
    LAR = "#F08A24"
    LAR_ESC = "#D4701A"
    BARRIGA = "#F6C77A"
    CAPACETE = "#8A5A2B"
    CAPACETE_ESC = "#6E4520"
    LISTRA = "#3E6FC4"
    CHIFRE_COR = "#F3EBD3"

    def listras(img, x, y, w, h):
        for i in range(1, w - 1, 4):
            retangulo(img, x + i, y, 2, h, LISTRA)

    def barriga(img, x, y, w, h):
        retangulo(img, x + 2, y, w - 4, h - 1, BARRIGA)

    def olhos(img, x, y, w, h):
        # Olhos verdes, sérios, logo abaixo do capacete e acima do focinho
        for ox in (1, w - 4):
            retangulo(img, x + ox, y + 2, 3, 2, BRANCO)
            retangulo(img, x + ox + (1 if ox == 1 else 0), y + 2, 2, 2, VERDE)
            px(img, x + ox + 1, y + 2, "#1B1B1B")

    def narinas(img, x, y, w, h):
        px(img, x + 1, y + 1, BOCA)
        px(img, x + w - 2, y + 1, BOCA)
        retangulo(img, x, y + h - 1, w, 1, BOCA)

    def dentes(img, x, y, w, h):
        retangulo(img, x, y, w, h, BARRIGA)
        for i in range(0, w, 2):
            px(img, x + i, y, BRANCO)

    def capacete_frente(img, x, y, w, h):
        retangulo(img, x, y + h - 1, w, 1, CAPACETE_ESC)

    def garras(img, x, y, w, h):
        for i in range(0, w, 2):
            px(img, x + i, y + h - 1, BRANCO)

    pele_listrada = lambda: Face(LAR, desenho=listras)
    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 15, 0], "root", [
            Cubo([-7, 13, -5], [14, 8, 12], LAR, {"north": Face(LAR, borda=0, desenho=barriga),
                                                 "up": pele_listrada(), "south": pele_listrada()}),
            Cubo([-6, 21, -6], [12, 7, 10], LAR, {"north": Face(LAR, desenho=barriga),
                                                 "up": pele_listrada(), "south": pele_listrada()}),
        ]),
        Osso("head", [0, 28, -4], "body", [
            Cubo([-3.5, 27, -9], [7, 5, 6], LAR),
            Cubo([-5.5, 30, -14], [11, 8, 11], LAR, {"north": Face(LAR, desenho=olhos)}),
            Cubo([-4, 31, -21], [8, 3, 7], LAR, {"north": Face(LAR, borda=0, desenho=narinas)}),
            Cubo([-4, 28.5, -20], [8, 2.5, 8], BARRIGA, {"north": Face(BARRIGA, borda=0, desenho=dentes)}),
            # Capacete de crânio marrom com três chifres
            Cubo([-6, 37.5, -14.5], [12, 3, 11], CAPACETE, {"north": Face(CAPACETE, desenho=capacete_frente)}),
            Cubo([-6.5, 38, -10], [2, 2, 7], CHIFRE_COR),
            Cubo([4.5, 38, -10], [2, 2, 7], CHIFRE_COR),
            Cubo([-1, 34, -20], [2, 3, 2], CHIFRE_COR),
        ]),
        Osso("arm_left", [7, 25, -3], "body", [
            Cubo([6.5, 18, -5], [4, 8, 4], pele_listrada()),
            Cubo([6.5, 16.5, -7], [4, 2, 4], Face(LAR, desenho=garras)),
        ]),
        Osso("arm_right", [-7, 25, -3], "body", [
            Cubo([-10.5, 18, -5], [4, 8, 4], pele_listrada()),
            Cubo([-10.5, 16.5, -7], [4, 2, 4], Face(LAR, desenho=garras)),
        ]),
        Osso("leg_left", [4.5, 15, 1], "root", [
            Cubo([2, 7, -3], [6, 8, 7], LAR_ESC),
            Cubo([2.5, 0, -2], [5, 7, 5], LAR_ESC),
            Cubo([2, 0, -5.5], [6, 2, 4], Face(LAR_ESC, borda=0, desenho=garras)),
        ]),
        Osso("leg_right", [-4.5, 15, 1], "root", [
            Cubo([-8, 7, -3], [6, 8, 7], LAR_ESC),
            Cubo([-7.5, 0, -2], [5, 7, 5], LAR_ESC),
            Cubo([-8, 0, -5.5], [6, 2, 4], Face(LAR_ESC, borda=0, desenho=garras)),
        ]),
        Osso("tail", [0, 18, 6], "body", [
            Cubo([-4, 13, 6], [8, 7, 9], pele_listrada(), {"up": pele_listrada()}),
        ]),
        Osso("tail_tip", [0, 15.5, 15], "tail", [
            Cubo([-2.5, 13, 15], [5, 5, 9], pele_listrada()),
        ]),
    ]
    animacoes = _animacoes_bipede(peso=1.6)
    gerar("greymon", ossos, {f"animation.greymon.{n}": a for n, a in animacoes.items()})


# ===================================================== LINHA GABUMON (bebês) ===

def punimon():
    VERM = "#E2434E"
    VERM_ESC = "#B8303B"
    PONTA = "#F7C64A"

    def rosto(img, x, y, w, h):
        for ox in (1, w - 3):
            retangulo(img, x + ox, y + 2, 2, 2, BRANCO)
            px(img, x + ox + (1 if ox == 1 else 0), y + 3, "#1B1B1B")
        retangulo(img, x + 3, y + h - 2, w - 6, 1, "#6E1A22")

    def ponta(img, x, y, w, h):
        retangulo(img, x, y, w, 1, PONTA)

    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 0, 0], "root", [
            Cubo([-4, 0, -4], [8, 6, 8], VERM, {"north": Face(VERM, desenho=rosto)}),
        ]),
        # Três antenas em cima da cabeça
        Osso("feelers", [0, 6, 0], "body", [
            Cubo([-0.5, 6, -0.5], [1, 3, 1], Face(VERM_ESC, borda=0, desenho=ponta)),
            Cubo([-3, 6, 0], [1, 2, 1], Face(VERM_ESC, borda=0, desenho=ponta)),
            Cubo([2, 6, 0], [1, 2, 1], Face(VERM_ESC, borda=0, desenho=ponta)),
        ]),
    ]
    animacoes = _animacoes_bolinha()
    animacoes["idle"]["bones"]["feelers"] = {"rotation": onda(8, 1.6, eixo=2)}
    animacoes["walk"]["bones"]["feelers"] = {"rotation": onda(15, 0.5, eixo=2)}
    gerar("punimon", ossos, {f"animation.punimon.{n}": a for n, a in animacoes.items()})


def tsunomon():
    BEGE = "#C9A273"
    BEGE_ESC = "#A9824F"
    CHIFRE_T = "#F1E6CF"

    def rosto(img, x, y, w, h):
        for ox in (1, w - 3):
            retangulo(img, x + ox, y + 2, 2, 2, BRANCO)
            px(img, x + ox + (1 if ox == 1 else 0), y + 3, VERMELHO)
        retangulo(img, x + 3, y + h - 2, w - 6, 1, "#5A3A1E")

    def manchas(img, x, y, w, h):
        for i in range(1, w - 1, 3):
            px(img, x + i, y + 1, BEGE_ESC)

    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 0, 0], "root", [
            Cubo([-4.5, 0, -4], [9, 7, 8], Face(BEGE, desenho=manchas), {"north": Face(BEGE, desenho=rosto)}),
            Cubo([-0.75, 7, -2], [1.5, 3, 1.5], CHIFRE_T),
        ]),
        Osso("ear_left", [3.5, 6, 0], "body", [
            Cubo([3.5, 5, -1], [2, 3, 2], BEGE_ESC),
        ], rotacao=[0, 0, -20]),
        Osso("ear_right", [-3.5, 6, 0], "body", [
            Cubo([-5.5, 5, -1], [2, 3, 2], BEGE_ESC),
        ], rotacao=[0, 0, 20]),
    ]
    animacoes = _animacoes_bolinha()
    animacoes["idle"]["bones"]["ear_left"] = {"rotation": onda(5, 1.6, eixo=2, base=(0, 0, -20))}
    animacoes["idle"]["bones"]["ear_right"] = {"rotation": onda(5, 1.6, eixo=2, fase=180, base=(0, 0, 20))}
    gerar("tsunomon", ossos, {f"animation.tsunomon.{n}": a for n, a in animacoes.items()})


# ============================================================= GARURUMON ===

def _animacoes_quadrupede():
    """Quadrúpedes: pernas em pares diagonais, cauda abanando, cabeça avançando no ataque."""
    return {
        "idle": {
            "loop": True,
            "animation_length": 2.0,
            "bones": {
                "body": {"position": onda(0.3, 2.0, eixo=1)},
                "head": {"rotation": onda(3, 2.0, fase=60)},
                "tail": {"rotation": onda(12, 1.0, eixo=1, base=(35, 0, 0))},
            },
        },
        "walk": {
            "loop": True,
            "animation_length": 0.6,
            "bones": {
                "leg_front_left": {"rotation": onda(28, 0.6)},
                "leg_back_right": {"rotation": onda(28, 0.6)},
                "leg_front_right": {"rotation": onda(28, 0.6, fase=180)},
                "leg_back_left": {"rotation": onda(28, 0.6, fase=180)},
                "body": {"position": onda(0.6, 0.3, eixo=1)},
                "head": {"rotation": onda(4, 0.3)},
                "tail": {"rotation": onda(15, 0.6, eixo=1, base=(25, 0, 0))},
            },
        },
        "attack": {
            "loop": False,
            "animation_length": 0.4,
            "bones": {
                "head": {"rotation": {"0.0": [0, 0, 0], "0.1": [-20, 0, 0], "0.22": [15, 0, 0], "0.4": [0, 0, 0]}},
                "body": {"position": {"0.0": [0, 0, 0], "0.15": [0, 0, -2], "0.4": [0, 0, 0]}},
            },
        },
    }


def garurumon():
    def listras(img, x, y, w, h):
        for i in range(1, w - 1, 3):
            retangulo(img, x + i, y, 1, max(1, h * 2 // 3), AZUL_LISTRA)

    def barriga(img, x, y, w, h):
        retangulo(img, x + 1, y + 1, w - 2, h - 2, BRANCO_PELO)

    def olhos(img, x, y, w, h):
        for ox in (0, w - 2):
            retangulo(img, x + ox, y + 2, 2, 2, BRANCO)
            px(img, x + ox + (1 if ox == 0 else 0), y + 3, VERMELHO)
        retangulo(img, x, y, w, 1, AZUL_LISTRA)

    def focinho(img, x, y, w, h):
        retangulo(img, x + 1, y, w - 2, 1, "#1B1B1B")
        retangulo(img, x, y + h - 1, w, 1, "#3A2A2A")

    def garras(img, x, y, w, h):
        for i in range(0, w, 2):
            px(img, x + i, y + h - 1, BRANCO)

    pelo = lambda: Face(AZUL, desenho=listras)
    perna = lambda o, s: Cubo(o, s, pelo(), {"north": Face(AZUL, desenho=listras)})

    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 14, 0], "root", [
            Cubo([-5.5, 9, -10], [11, 10, 20], pelo(), {"down": Face(BRANCO_PELO, borda=0)}),
            # Juba branca no peito
            Cubo([-6, 8, -12], [12, 11, 4], Face(BRANCO_PELO), {"up": pelo()}),
        ]),
        Osso("head", [0, 17, -12], "body", [
            Cubo([-4.5, 14, -20], [9, 9, 8], pelo(), {"north": Face(AZUL, desenho=olhos)}),
            Cubo([-3, 14, -25], [6, 4, 5], Face(BRANCO_PELO), {"north": Face(BRANCO_PELO, borda=0, desenho=focinho)}),
            Cubo([-4, 23, -15], [2, 3, 2], AZUL),
            Cubo([2, 23, -15], [2, 3, 2], AZUL),
            Cubo([-0.5, 23, -20], [1, 3, 1], CHIFRE),
        ]),
        Osso("leg_front_left", [3, 10, -7], "root", [
            perna([1.5, 1.5, -8.5], [3.5, 9, 3.5]),
            Cubo([1.5, 0, -9.5], [3.5, 1.5, 4.5], Face(BRANCO_PELO, borda=0, desenho=garras)),
        ]),
        Osso("leg_front_right", [-3, 10, -7], "root", [
            perna([-5, 1.5, -8.5], [3.5, 9, 3.5]),
            Cubo([-5, 0, -9.5], [3.5, 1.5, 4.5], Face(BRANCO_PELO, borda=0, desenho=garras)),
        ]),
        Osso("leg_back_left", [3, 10, 7], "root", [
            perna([1, 1.5, 5], [4.5, 9, 4.5]),
            Cubo([1, 0, 4], [4.5, 1.5, 4.5], Face(BRANCO_PELO, borda=0, desenho=garras)),
        ]),
        Osso("leg_back_right", [-3, 10, 7], "root", [
            perna([-5.5, 1.5, 5], [4.5, 9, 4.5]),
            Cubo([-5.5, 0, 4], [4.5, 1.5, 4.5], Face(BRANCO_PELO, borda=0, desenho=garras)),
        ]),
        Osso("tail", [0, 17, 10], "body", [
            Cubo([-1.5, 15.5, 10], [3, 3, 8], pelo()),
            Cubo([-1.5, 15.5, 18], [3, 3, 3], Face(BRANCO_PELO)),
        ], rotacao=[35, 0, 0]),
    ]
    gerar("garurumon", ossos, {f"animation.garurumon.{n}": a for n, a in _animacoes_quadrupede().items()})


# ======================================================= INIMIGOS SELVAGENS ===

def numemon():
    VERDE_N = "#7DBB3A"
    VERDE_N_ESC = "#5E9428"
    LINGUA = "#E8708A"

    def boca(img, x, y, w, h):
        retangulo(img, x + 1, y + h - 4, w - 2, 2, "#3A1A1A")
        retangulo(img, x + w // 2 - 1, y + h - 3, 2, 2, LINGUA)

    def olho(img, x, y, w, h):
        retangulo(img, x, y, w, h, BRANCO)
        px(img, x + w // 2, y + h // 2, "#1B1B1B")

    ossos = [
        Osso("root", [0, 0, 0]),
        # Corpo de lesma: base larga e achatada, "pescoço" levantado na frente
        Osso("body", [0, 0, 0], "root", [
            Cubo([-4.5, 0, -2], [9, 5, 11], VERDE_N_ESC),
            Cubo([-4, 0, -5], [8, 10, 5], VERDE_N, {"north": Face(VERDE_N, desenho=boca)}),
        ]),
        # Olhos em antenas
        Osso("eyes", [0, 10, -3], "body", [
            Cubo([-3, 10, -3.5], [1, 3, 1], VERDE_N),
            Cubo([2, 10, -3.5], [1, 3, 1], VERDE_N),
            Cubo([-3.5, 13, -4], [2, 2, 2], Face(BRANCO, borda=0, desenho=olho)),
            Cubo([1.5, 13, -4], [2, 2, 2], Face(BRANCO, borda=0, desenho=olho)),
        ]),
        Osso("arm_left", [4, 6, -3], "body", [Cubo([4, 3, -4], [1.5, 3, 1.5], VERDE_N)]),
        Osso("arm_right", [-4, 6, -3], "body", [Cubo([-5.5, 3, -4], [1.5, 3, 1.5], VERDE_N)]),
    ]
    animacoes = {
        "idle": {"loop": True, "animation_length": 2.0, "bones": {
            "body": {"scale": ["1", "1 + math.sin(query.anim_time / 2 * 360) * 0.04", "1"]},
            "eyes": {"rotation": onda(8, 2.0, eixo=2)},
        }},
        "walk": {"loop": True, "animation_length": 0.8, "bones": {
            "body": {"scale": ["1", "1 - math.sin(query.anim_time / 0.8 * 360) * 0.06",
                               "1 + math.sin(query.anim_time / 0.8 * 360) * 0.08"]},
            "eyes": {"rotation": onda(10, 0.8)},
            "arm_left": {"rotation": onda(30, 0.8)},
            "arm_right": {"rotation": onda(30, 0.8, fase=180)},
        }},
        "attack": {"loop": False, "animation_length": 0.4, "bones": {
            "body": {"rotation": {"0.0": [0, 0, 0], "0.15": [-15, 0, 0], "0.4": [0, 0, 0]}},
            "arm_right": {"rotation": {"0.0": [0, 0, 0], "0.15": [-120, 0, 0], "0.4": [0, 0, 0]}},
        }},
    }
    gerar("numemon", ossos, {f"animation.numemon.{n}": a for n, a in animacoes.items()})


def goburimon():
    VERDE_G = "#6FA84A"
    VERDE_G_ESC = "#52833A"
    TANGA = "#8A5A2B"
    CLAVA = "#7A5530"

    def rosto(img, x, y, w, h):
        for ox in (1, w - 3):
            retangulo(img, x + ox, y + 2, 2, 2, "#F5D83A")
            px(img, x + ox + (1 if ox == 1 else 0), y + 3, "#1B1B1B")
        retangulo(img, x + 2, y + h - 2, w - 4, 1, "#2A1A10")
        px(img, x + 2, y + h - 3, BRANCO)
        px(img, x + w - 3, y + h - 3, BRANCO)

    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 8, 0], "root", [
            Cubo([-3.5, 7, -2], [7, 7, 4], VERDE_G, {"down": Face(TANGA)}),
            Cubo([-3.6, 6, -2.1], [7.2, 2, 4.2], TANGA),
        ]),
        Osso("head", [0, 14, 0], "body", [
            Cubo([-4, 14, -3.5], [8, 7, 7], VERDE_G, {"north": Face(VERDE_G, desenho=rosto)}),
            # Orelhas pontudas e chifrinho
            Cubo([4, 17, -1], [3, 2, 1], VERDE_G_ESC),
            Cubo([-7, 17, -1], [3, 2, 1], VERDE_G_ESC),
            Cubo([-0.5, 21, -1.5], [1, 2, 1], "#E8DCC0"),
        ]),
        Osso("arm_left", [4, 13, 0], "body", [Cubo([3.5, 7, -1], [2, 6, 2], VERDE_G)]),
        Osso("arm_right", [-4, 13, 0], "body", [
            Cubo([-5.5, 7, -1], [2, 6, 2], VERDE_G),
            Cubo([-5.5, 6, -8], [2, 2, 8], CLAVA),
        ]),
        Osso("leg_left", [1.75, 7, 0], "root", [Cubo([0.5, 0, -1.5], [2.5, 7, 3], VERDE_G_ESC)]),
        Osso("leg_right", [-1.75, 7, 0], "root", [Cubo([-3, 0, -1.5], [2.5, 7, 3], VERDE_G_ESC)]),
    ]
    gerar("goburimon", ossos, {f"animation.goburimon.{n}": a for n, a in _animacoes_bipede().items()})


def gotsumon():
    PEDRA = "#9A9A96"
    PEDRA_ESC = "#77776F"
    MUSGO = "#6E8F4A"

    def rosto(img, x, y, w, h):
        for ox in (1, w - 3):
            retangulo(img, x + ox, y + 2, 2, 2, "#1B1B1B")
            px(img, x + ox, y + 2, BRANCO)
        retangulo(img, x + 3, y + h - 2, w - 6, 1, "#3A3A36")

    def rachaduras(img, x, y, w, h):
        for i in range(1, w - 1, 3):
            px(img, x + i, y + (i % h), PEDRA_ESC)

    pedra = lambda: Face(PEDRA, desenho=rachaduras)
    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 7, 0], "root", [
            Cubo([-4.5, 6, -3], [9, 8, 6], pedra()),
        ]),
        Osso("head", [0, 14, 0], "body", [
            Cubo([-4, 14, -3.5], [8, 6, 7], pedra(), {"north": Face(PEDRA, desenho=rosto), "up": Face(MUSGO)}),
        ]),
        Osso("arm_left", [5, 13, 0], "body", [Cubo([4.5, 6, -2], [3.5, 7, 4], pedra())]),
        Osso("arm_right", [-5, 13, 0], "body", [Cubo([-8, 6, -2], [3.5, 7, 4], pedra())]),
        Osso("leg_left", [2, 6, 0], "root", [Cubo([0.5, 0, -2], [3.5, 6, 4], PEDRA_ESC)]),
        Osso("leg_right", [-2, 6, 0], "root", [Cubo([-4, 0, -2], [3.5, 6, 4], PEDRA_ESC)]),
    ]
    gerar("gotsumon", ossos, {f"animation.gotsumon.{n}": a for n, a in _animacoes_bipede(peso=1.3).items()})


# ============================================================ ULTIMATES ===

METAL = "#B8C0C8"
METAL_ESC = "#7C848C"


def metalgreymon():
    LAR = "#F08A24"
    LAR_ESC = "#D4701A"
    BARRIGA = "#F6C77A"
    LISTRA = "#3E6FC4"
    MEMBRANA = "#6A4C9C"
    CHIFRE_COR = "#F3EBD3"

    def listras(img, x, y, w, h):
        for i in range(1, w - 1, 4):
            retangulo(img, x + i, y, 2, h, LISTRA)

    def placa(img, x, y, w, h):
        # Placa de peito com rebites
        for i in (1, w - 2):
            for j in (1, h - 2):
                px(img, x + i, y + j, METAL_ESC)
        retangulo(img, x + w // 2, y + 1, 1, h - 2, METAL_ESC)

    def olhos(img, x, y, w, h):
        for ox in (1, w - 4):
            retangulo(img, x + ox, y + 2, 3, 2, BRANCO)
            retangulo(img, x + ox + (1 if ox == 1 else 0), y + 2, 2, 2, VERDE)
            px(img, x + ox + 1, y + 2, "#1B1B1B")

    def narinas(img, x, y, w, h):
        px(img, x + 1, y, BOCA)
        px(img, x + w - 2, y, BOCA)

    def dentes(img, x, y, w, h):
        for i in range(0, w, 2):
            px(img, x + i, y, BRANCO)

    def garras(img, x, y, w, h):
        for i in range(0, w, 2):
            px(img, x + i, y + h - 1, BRANCO)

    pele = lambda: Face(LAR, desenho=listras)
    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 16, 0], "root", [
            Cubo([-8, 14, -5.5], [16, 9, 13], pele(), {"north": Face(BARRIGA)}),
            Cubo([-7, 23, -6.5], [14, 8, 11], pele()),
            Cubo([-6.5, 22, -7.5], [13, 9, 1.5], Face(METAL, desenho=placa)),
        ]),
        Osso("head", [0, 31, -4], "body", [
            Cubo([-4, 30, -9], [8, 5, 6], LAR),
            Cubo([-6, 33, -15], [12, 8, 12], LAR, {"north": Face(LAR, desenho=olhos)}),
            Cubo([-4.5, 34, -22], [9, 3, 7], LAR, {"north": Face(LAR, borda=0, desenho=narinas)}),
            Cubo([-4.5, 31, -21], [9, 3, 9], Face(METAL), {"north": Face(METAL, borda=0, desenho=dentes)}),
            Cubo([-6.5, 40, -15.5], [13, 3, 12], Face(METAL, desenho=placa)),
            Cubo([-7, 41, -11], [2, 2, 8], CHIFRE_COR),
            Cubo([5, 41, -11], [2, 2, 8], CHIFRE_COR),
            Cubo([-1, 37, -22], [2, 3, 2], CHIFRE_COR),
        ]),
        # Braço esquerdo de metal com garras (o "Trident Arm")
        Osso("arm_left", [8, 28, -3], "body", [
            Cubo([7.5, 20, -5], [5, 9, 5], Face(METAL, desenho=placa)),
            Cubo([7, 17, -7], [6, 3, 6], METAL_ESC),
            Cubo([7.5, 13, -7], [1, 4, 1], METAL),
            Cubo([9.5, 13, -7], [1, 4, 1], METAL),
            Cubo([11.5, 13, -7], [1, 4, 1], METAL),
        ]),
        Osso("arm_right", [-8, 28, -3], "body", [
            Cubo([-12, 20, -5], [4, 9, 4], pele()),
            Cubo([-12, 18.5, -7], [4, 2, 4], Face(LAR, desenho=garras)),
        ]),
        Osso("wing_left", [3, 29, 5], "body", [
            Cubo([3, 31, 5], [1, 1, 13], METAL),
            Cubo([3.2, 21, 5.5], [0.6, 10, 12], MEMBRANA),
        ], rotacao=[0, -25, -10]),
        Osso("wing_right", [-3, 29, 5], "body", [
            Cubo([-4, 31, 5], [1, 1, 13], METAL),
            Cubo([-3.8, 21, 5.5], [0.6, 10, 12], MEMBRANA),
        ], rotacao=[0, 25, 10]),
        Osso("leg_left", [5, 16, 1], "root", [
            Cubo([2, 8, -3.5], [7, 8, 8], LAR_ESC),
            Cubo([2.5, 0, -2.5], [6, 8, 6], LAR_ESC),
            Cubo([2, 0, -6], [7, 2, 4], Face(LAR_ESC, borda=0, desenho=garras)),
        ]),
        Osso("leg_right", [-5, 16, 1], "root", [
            Cubo([-9, 8, -3.5], [7, 8, 8], LAR_ESC),
            Cubo([-8.5, 0, -2.5], [6, 8, 6], LAR_ESC),
            Cubo([-9, 0, -6], [7, 2, 4], Face(LAR_ESC, borda=0, desenho=garras)),
        ]),
        Osso("tail", [0, 20, 7], "body", [Cubo([-4.5, 15, 7], [9, 8, 10], pele())]),
        Osso("tail_tip", [0, 17.5, 17], "tail", [Cubo([-3, 15, 17], [6, 5, 10], pele())]),
    ]
    animacoes = _animacoes_bipede(peso=1.8)
    for nome, fase in (("wing_left", 0), ("wing_right", 180)):
        base = (0, -25, -10) if nome == "wing_left" else (0, 25, 10)
        animacoes["idle"]["bones"][nome] = {"rotation": onda(4, 3.6, fase=fase, eixo=2, base=base)}
        animacoes["walk"]["bones"][nome] = {"rotation": onda(8, 1.44, fase=fase, eixo=2, base=base)}
    gerar("metalgreymon", ossos, {f"animation.metalgreymon.{n}": a for n, a in animacoes.items()})


def weregarurumon():
    JEANS = "#2E3E66"
    JEANS_ESC = "#22304F"
    PULSEIRA = "#B0242B"

    def listras(img, x, y, w, h):
        for i in range(1, w - 1, 3):
            retangulo(img, x + i, y, 1, max(1, h // 2), AZUL_LISTRA)

    def peito(img, x, y, w, h):
        retangulo(img, x + 2, y + 1, w - 4, h - 3, BRANCO_PELO)

    def rasgos(img, x, y, w, h):
        px(img, x + 1, y + 2, AZUL)
        px(img, x + w - 2, y + h - 3, AZUL)

    def olhos(img, x, y, w, h):
        retangulo(img, x, y + 1, w, 1, AZUL_LISTRA)
        for ox in (0, w - 2):
            retangulo(img, x + ox, y + 2, 2, 2, BRANCO)
            px(img, x + ox + (1 if ox == 0 else 0), y + 3, VERMELHO)

    def focinho(img, x, y, w, h):
        retangulo(img, x + 1, y, w - 2, 1, "#1B1B1B")
        retangulo(img, x, y + h - 1, w, 1, "#3A2A2A")

    def pinos(img, x, y, w, h):
        for i in range(0, w, 2):
            px(img, x + i, y, "#E0E0E0")

    def garras(img, x, y, w, h):
        for i in range(0, w, 2):
            px(img, x + i, y + h - 1, BRANCO)

    pelo = lambda: Face(AZUL, desenho=listras)
    jeans = lambda: Face(JEANS, desenho=rasgos)
    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 14, 0], "root", [
            Cubo([-4.5, 13, -2.5], [9, 3, 5], jeans()),
            Cubo([-5, 16, -3], [10, 10, 6], pelo(), {"north": Face(AZUL, desenho=peito)}),
        ]),
        Osso("head", [0, 26, -1], "body", [
            Cubo([-3.5, 26, -4.5], [7, 7, 7], pelo(), {"north": Face(AZUL, desenho=olhos)}),
            Cubo([-2, 26, -8.5], [4, 3, 4], Face(BRANCO_PELO), {"north": Face(BRANCO_PELO, borda=0, desenho=focinho)}),
            Cubo([-3, 33, -2], [2, 3, 1.5], AZUL),
            Cubo([1, 33, -2], [2, 3, 1.5], AZUL),
        ]),
        Osso("arm_left", [5.5, 25, 0], "body", [
            Cubo([5, 18, -1.5], [3, 8, 3], pelo()),
            Cubo([4.8, 16, -1.7], [3.4, 2, 3.4], Face(PULSEIRA, borda=0, desenho=pinos)),
            Cubo([5, 14, -1.5], [3, 2, 3], Face(BRANCO_PELO, borda=0, desenho=garras)),
        ]),
        Osso("arm_right", [-5.5, 25, 0], "body", [
            Cubo([-8, 18, -1.5], [3, 8, 3], pelo()),
            Cubo([-8.2, 16, -1.7], [3.4, 2, 3.4], Face(PULSEIRA, borda=0, desenho=pinos)),
            Cubo([-8, 14, -1.5], [3, 2, 3], Face(BRANCO_PELO, borda=0, desenho=garras)),
        ]),
        Osso("leg_left", [2.5, 14, 0], "root", [
            Cubo([0.5, 7, -2], [4, 7, 4], jeans()),
            Cubo([1, 1.5, -1.5], [3, 5.5, 3], Face(JEANS_ESC)),
            Cubo([0.5, 0, -3.5], [4, 1.5, 5], Face(BRANCO_PELO, borda=0, desenho=garras)),
        ]),
        Osso("leg_right", [-2.5, 14, 0], "root", [
            Cubo([-4.5, 7, -2], [4, 7, 4], jeans()),
            Cubo([-4, 1.5, -1.5], [3, 5.5, 3], Face(JEANS_ESC)),
            Cubo([-4.5, 0, -3.5], [4, 1.5, 5], Face(BRANCO_PELO, borda=0, desenho=garras)),
        ]),
        Osso("tail", [0, 15, 2.5], "body", [Cubo([-1, 13, 2.5], [2, 2, 6], pelo())]),
        Osso("tail_tip", [0, 14, 8.5], "tail", [Cubo([-1, 13, 8.5], [2, 2, 3], Face(BRANCO_PELO))]),
    ]
    gerar("weregarurumon", ossos, {f"animation.weregarurumon.{n}": a for n, a in _animacoes_bipede(peso=1.1).items()})


# ================================================================= MEGAS ===

def wargreymon():
    OURO = "#E8B530"
    OURO_ESC = "#B8862A"
    LAR = "#F08A24"
    CABELO = "#C8282E"
    GARRA = "#D8DEE4"

    def peitoral(img, x, y, w, h):
        # Brasão da Coragem estilizado no peito: sol laranja
        cx, cy = x + w // 2, y + h // 2
        retangulo(img, cx - 1, cy - 1, 2, 2, LAR)
        for d in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            px(img, cx + d[0] - (1 if d[0] > 0 else 0), cy + d[1] - (1 if d[1] > 0 else 0), LAR)
        retangulo(img, x, y + h - 1, w, 1, OURO_ESC)

    def escudo(img, x, y, w, h):
        # Escudo Brave Shield: borda escura e emblema no centro
        retangulo(img, x, y, w, 1, OURO_ESC)
        retangulo(img, x, y + h - 1, w, 1, OURO_ESC)
        cx, cy = x + w // 2, y + h // 2
        retangulo(img, cx - 2, cy - 2, 4, 4, LAR)
        retangulo(img, cx - 1, cy - 1, 2, 2, CABELO)

    def rosto(img, x, y, w, h):
        # Elmo dourado com fenda mostrando os olhos verdes e o rosto laranja
        retangulo(img, x + 1, y + 2, w - 2, 3, LAR)
        for ox in (1, w - 3):
            px(img, x + ox, y + 3, BRANCO)
            px(img, x + ox + (1 if ox == 1 else 0), y + 3, VERDE)
        retangulo(img, x + 2, y + h - 2, w - 4, 1, LAR)

    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 14, 0], "root", [
            Cubo([-4, 13, -2.5], [8, 3, 5], LAR),
            Cubo([-5, 16, -3], [10, 9, 6], OURO, {"north": Face(OURO, desenho=peitoral)}),
            Cubo([5, 22, -3.5], [3, 4, 7], OURO_ESC),
            Cubo([-8, 22, -3.5], [3, 4, 7], OURO_ESC),
        ]),
        Osso("shield", [0, 20, 3], "body", [
            Cubo([-6, 14, 3], [12, 12, 2], OURO, {"south": Face(OURO, borda=0, desenho=escudo)}),
        ]),
        Osso("head", [0, 25, -0.5], "body", [
            Cubo([-3.5, 25, -4], [7, 7, 7], OURO, {"north": Face(OURO, borda=0, desenho=rosto)}),
            Cubo([-0.5, 29.5, -5.5], [1, 2, 2], GARRA),
            Cubo([-3.5, 32, -2], [1.5, 3, 1.5], GARRA),
            Cubo([2, 32, -2], [1.5, 3, 1.5], GARRA),
            Cubo([-3, 26, 3], [6, 6, 2], CABELO),
        ]),
        Osso("arm_left", [6.5, 23, 0], "body", [
            Cubo([5, 17, -1.5], [3, 6, 3], LAR),
            Cubo([4.5, 12, -2], [4, 5, 4], OURO),
            Cubo([4.8, 9, -2.5], [1, 3, 1], GARRA),
            Cubo([6.3, 9, -2.5], [1, 3, 1], GARRA),
            Cubo([7.8, 9, -2.5], [1, 3, 1], GARRA),
        ]),
        Osso("arm_right", [-6.5, 23, 0], "body", [
            Cubo([-8, 17, -1.5], [3, 6, 3], LAR),
            Cubo([-8.5, 12, -2], [4, 5, 4], OURO),
            Cubo([-8.8, 9, -2.5], [1, 3, 1], GARRA),
            Cubo([-7.3, 9, -2.5], [1, 3, 1], GARRA),
            Cubo([-5.8, 9, -2.5], [1, 3, 1], GARRA),
        ]),
        Osso("leg_left", [2.5, 14, 0], "root", [
            Cubo([0.5, 7, -2], [4, 7, 4], OURO),
            Cubo([0.8, 1.5, -1.8], [3.4, 5.5, 3.6], OURO_ESC),
            Cubo([0.5, 0, -3.8], [4, 1.5, 5], OURO),
        ]),
        Osso("leg_right", [-2.5, 14, 0], "root", [
            Cubo([-4.5, 7, -2], [4, 7, 4], OURO),
            Cubo([-4.2, 1.5, -1.8], [3.4, 5.5, 3.6], OURO_ESC),
            Cubo([-4.5, 0, -3.8], [4, 1.5, 5], OURO),
        ]),
        Osso("tail", [0, 14, 2.5], "body", [Cubo([-1, 12, 2.5], [2, 2, 5], LAR)]),
        Osso("tail_tip", [0, 13, 7.5], "tail", [Cubo([-0.75, 12.25, 7.5], [1.5, 1.5, 2], LAR)]),
    ]
    gerar("wargreymon", ossos, {f"animation.wargreymon.{n}": a for n, a in _animacoes_bipede(peso=1.0).items()})


def metalgarurumon():
    PRATA_AZUL = "#9FB7D6"
    METAL_AZ = "#5A6E8C"
    GELO = "#9FE8FF"

    def placas(img, x, y, w, h):
        for i in range(1, w - 1, 4):
            retangulo(img, x + i, y, 1, h, METAL_AZ)
        px(img, x + 1, y + 1, GELO)

    def olhos(img, x, y, w, h):
        retangulo(img, x, y, w, 1, METAL_AZ)
        for ox in (0, w - 2):
            retangulo(img, x + ox, y + 2, 2, 2, GELO)
            px(img, x + ox + (1 if ox == 0 else 0), y + 3, VERMELHO)

    def focinho(img, x, y, w, h):
        retangulo(img, x + 1, y, w - 2, 1, "#1B1B1B")
        retangulo(img, x, y + h - 1, w, 1, METAL_AZ)

    def garras(img, x, y, w, h):
        for i in range(0, w, 2):
            px(img, x + i, y + h - 1, GELO)

    metal = lambda: Face(PRATA_AZUL, desenho=placas)
    perna = lambda o, s: Cubo(o, s, metal())
    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 15, 0], "root", [
            Cubo([-6, 10, -11], [12, 10, 22], metal(), {"down": Face(METAL_AZ, borda=0)}),
            Cubo([-6.5, 9, -13], [13, 11, 4], Face(BRANCO_PELO), {"up": metal()}),
            # Lançadores de mísseis nas costas
            Cubo([-5, 20, -6], [3, 2, 9], METAL_AZ),
            Cubo([2, 20, -6], [3, 2, 9], METAL_AZ),
        ]),
        Osso("wing_left", [6, 19, -2], "body", [Cubo([6, 18, -4], [9, 1, 5], Face(GELO, borda=0))],
             rotacao=[0, 0, 15]),
        Osso("wing_right", [-6, 19, -2], "body", [Cubo([-15, 18, -4], [9, 1, 5], Face(GELO, borda=0))],
             rotacao=[0, 0, -15]),
        Osso("head", [0, 18, -13], "body", [
            Cubo([-5, 15, -21], [10, 9, 8], metal(), {"north": Face(PRATA_AZUL, desenho=olhos)}),
            Cubo([-3, 15, -27], [6, 4, 6], Face(PRATA_AZUL), {"north": Face(PRATA_AZUL, borda=0, desenho=focinho)}),
            Cubo([-4.5, 24, -16], [2, 4, 2], METAL_AZ),
            Cubo([2.5, 24, -16], [2, 4, 2], METAL_AZ),
            Cubo([-0.5, 24, -21], [1, 4, 1], GELO),
        ]),
        Osso("leg_front_left", [3.5, 11, -8], "root", [
            perna([1.5, 1.5, -9.5], [4, 10, 4]),
            Cubo([1.5, 0, -10.5], [4, 1.5, 5], Face(METAL_AZ, borda=0, desenho=garras)),
        ]),
        Osso("leg_front_right", [-3.5, 11, -8], "root", [
            perna([-5.5, 1.5, -9.5], [4, 10, 4]),
            Cubo([-5.5, 0, -10.5], [4, 1.5, 5], Face(METAL_AZ, borda=0, desenho=garras)),
        ]),
        Osso("leg_back_left", [3.5, 11, 8], "root", [
            perna([1, 1.5, 5.5], [5, 10, 5]),
            Cubo([1, 0, 4.5], [5, 1.5, 5], Face(METAL_AZ, borda=0, desenho=garras)),
        ]),
        Osso("leg_back_right", [-3.5, 11, 8], "root", [
            perna([-6, 1.5, 5.5], [5, 10, 5]),
            Cubo([-6, 0, 4.5], [5, 1.5, 5], Face(METAL_AZ, borda=0, desenho=garras)),
        ]),
        Osso("tail", [0, 18, 11], "body", [
            Cubo([-1.5, 16.5, 11], [3, 3, 9], metal()),
            Cubo([-1.5, 16.5, 20], [3, 3, 3], Face(GELO)),
        ], rotacao=[30, 0, 0]),
    ]
    animacoes = _animacoes_quadrupede()
    animacoes["idle"]["bones"]["wing_left"] = {"rotation": onda(6, 2.0, eixo=2, base=(0, 0, 15))}
    animacoes["idle"]["bones"]["wing_right"] = {"rotation": onda(6, 2.0, eixo=2, fase=180, base=(0, 0, -15))}
    gerar("metalgarurumon", ossos, {f"animation.metalgarurumon.{n}": a for n, a in animacoes.items()})


if __name__ == "__main__":
    wargreymon()
    metalgarurumon()
    agumon()
    gabumon()
    botamon()
    koromon()
    greymon()
    punimon()
    tsunomon()
    garurumon()
    numemon()
    goburimon()
    gotsumon()
    metalgreymon()
    weregarurumon()
