"""
Kit de pintura "HD" para as texturas dos Digimon (densidade 2: dois pixels por unidade do modelo).

Cada face é pintada por uma Pintura: cor base com degradê (claro em cima, escuro embaixo),
um ruído leve que dá textura de pelo/pele, contorno de sombra e, por cima, camadas de detalhe
(listras, tufos de pelo, olhos, garras...).

As camadas recebem (img, x, y, w, h): o retângulo da face na textura, em pixels.
"""
import random

ESCURO = "#1B1B1B"
BRANCO = "#F6F6F2"


def rgb(cor):
    if isinstance(cor, tuple):
        return cor[:3] + (255,)
    cor = cor.lstrip("#")
    return tuple(int(cor[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def tom(cor, f):
    """f > 0 clareia (em direção ao branco), f < 0 escurece (em direção ao preto)."""
    r, g, b, _ = rgb(cor)
    if f >= 0:
        return (int(r + (255 - r) * f), int(g + (255 - g) * f), int(b + (255 - b) * f), 255)
    return (int(r * (1 + f)), int(g * (1 + f)), int(b * (1 + f)), 255)


def ponto(img, x, y, cor):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), rgb(cor))


def ret(img, x, y, w, h, cor):
    for i in range(w):
        for j in range(h):
            ponto(img, x + i, y + j, cor)


class Pintura:
    """Uma face: degradê + ruído + sombras de borda + camadas de detalhe."""

    def __init__(self, cor, *camadas, gradiente=0.16, ruido=5, borda=True):
        self.cor = rgb(cor)
        self.camadas = camadas
        self.gradiente = gradiente
        self.ruido = ruido
        self.borda = borda

    def pintar(self, img, x, y, w, h):
        rnd = random.Random(x * 7919 + y * 104729 + w * 31 + h)
        for j in range(h):
            t = j / (h - 1) if h > 1 else 0.5
            f = self.gradiente * (0.5 - t) * 2
            for i in range(w):
                c = tom(self.cor, f)
                n = rnd.randint(-self.ruido, self.ruido)
                ponto(img, x + i, y + j, tuple(max(0, min(255, v + n)) for v in c[:3]) + (255,))
        if self.borda and w > 2 and h > 2:
            for i in range(w):
                ponto(img, x + i, y + h - 1, tom(img.getpixel((x + i, y + h - 1)), -0.22))
                ponto(img, x + i, y, tom(img.getpixel((x + i, y)), 0.08))
            if w >= 6:
                for j in range(h):
                    ponto(img, x, y + j, tom(img.getpixel((x, y + j)), -0.08))
                    ponto(img, x + w - 1, y + j, tom(img.getpixel((x + w - 1, y + j)), -0.12))
        for camada in self.camadas:
            camada(img, x, y, w, h)


# ------------------------------------------------------------------ camadas

def listras(cor, quantidade=3, comprimento=0.6, largura=2, de_baixo=False):
    """Listras verticais que afinam (como as do pelo do Gabumon)."""
    def camada(img, x, y, w, h):
        passo = w / (quantidade + 1)
        tam = max(2, int(h * comprimento))
        for k in range(quantidade):
            cx = int(x + passo * (k + 1))
            for r in range(tam):
                larg = max(1, round(largura * (1 - r / tam) + 0.4))
                yy = y + h - 1 - r if de_baixo else y + r
                ret(img, cx - larg // 2, yy, larg, 1, cor)
    return camada


def chevrons(cor, quantidade=2, espessura=2, abertura=0.5):
    """Faixas em "V" apontando para baixo (costas e topo da cabeça)."""
    def camada(img, x, y, w, h):
        for k in range(quantidade):
            base = y + int(h * (k + 1) / (quantidade + 1))
            for i in range(w):
                dy = int(abs(i - (w - 1) / 2) * abertura)
                for e in range(espessura):
                    if y <= base - dy + e < y + h:
                        ponto(img, x + i, base - dy + e, cor)
    return camada


def regiao_pelo(cor, x0, y0, x1, y1, tufo_cima=True, tufo_lados=False):
    """
    Região de pelo claro (frações da face) com borda em zigue-zague,
    como a barriga e as bochechas da arte de referência.
    """
    def camada(img, x, y, w, h):
        ax, ay = x + int(w * x0), y + int(h * y0)
        bx, by = x + int(w * x1), y + int(h * y1)
        padrao = [0, 1, 2, 1]
        base = rgb(cor)
        for i in range(ax, bx):
            topo = ay + (padrao[(i - ax) % 4] if tufo_cima else 0)
            for j in range(topo, by):
                t = (j - ay) / max(1, by - ay)
                ponto(img, i, j, tom(base, 0.08 - 0.16 * t))
        if tufo_lados:
            for j in range(ay, by):
                d = padrao[(j - ay) % 4]
                for k in range(d):
                    ponto(img, ax - 1 - k, j, tom(base, 0.02))
                    ponto(img, bx + k, j, tom(base, 0.02))
    return camada


def placas(cor_linha, x0, x1, y0, y1, quantidade=3):
    """Linhas horizontais que dividem a barriga em placas."""
    def camada(img, x, y, w, h):
        ax, bx = x + int(w * x0), x + int(w * x1)
        for k in range(1, quantidade):
            yy = y + int(h * (y0 + (y1 - y0) * k / quantidade))
            for i in range(ax + 1, bx - 1):
                ponto(img, i, yy, cor_linha)
    return camada


def olho(rx, ry, iris, raiva=False, espelhado=False, largura=5, altura=5):
    """
    Olho grande: contorno fino, branco, íris voltada para o centro do rosto, pupila e brilho.
    (rx, ry) é o canto superior esquerdo, relativo à face.
    espelhado=True para o olho do lado direito da face (íris fica do lado esquerdo dele).
    raiva desenha uma sobrancelha diagonal descendo em direção ao centro do rosto.
    """
    def camada(img, x, y, w, h):
        ox, oy = x + rx, y + ry
        # contorno: escuro em cima e nos lados, mais suave embaixo
        ret(img, ox, oy, largura, 1, ESCURO)
        ret(img, ox, oy, 1, altura, ESCURO)
        ret(img, ox + largura - 1, oy, 1, altura, ESCURO)
        ret(img, ox + 1, oy + altura - 1, largura - 2, 1, tom(ESCURO, 0.25))
        # branco
        ret(img, ox + 1, oy + 1, largura - 2, altura - 2, BRANCO)
        # íris de 2 colunas encostada no lado de dentro (perto do nariz)
        ix = ox + 1 if espelhado else ox + largura - 3
        ret(img, ix, oy + 1, 2, altura - 2, iris)
        ret(img, ix, oy + altura - 2, 2, 1, tom(iris, -0.35))
        # pupila e brilho
        ret(img, ix + (0 if espelhado else 1), oy + 2, 1, max(1, altura - 3), ESCURO)
        ponto(img, ix + (1 if espelhado else 0), oy + 1, BRANCO)
        if raiva:
            # linha contínua: alta do lado de fora, baixa perto do nariz
            for i in range(largura + 1):
                fx = ox - 1 + i
                t = i / largura
                dy = round((t if not espelhado else 1 - t) * 2)
                ponto(img, fx, oy - 2 + dy, ESCURO)
                ponto(img, fx, oy - 1 + dy, ESCURO)
    return camada


def garras(cor, ponta=BRANCO, quantidade=3, altura=3):
    """Garras na parte de baixo da face (pés e mãos)."""
    def camada(img, x, y, w, h):
        larg = max(1, w // (quantidade * 2))
        espaco = (w - larg * quantidade) / (quantidade + 1)
        alt = min(altura, h)
        for k in range(quantidade):
            gx = int(x + espaco * (k + 1) + larg * k)
            for j in range(alt):
                yy = y + h - alt + j
                c = ponta if j == alt - 1 else (tom(cor, 0.25) if j == 0 else cor)
                ret(img, gx, yy, larg, 1, c)
    return camada


def faixa(cor, y0, espessura=2):
    """Faixa horizontal (pulseiras, bandas), y0 em fração da altura."""
    def camada(img, x, y, w, h):
        yy = y + int(h * y0)
        for e in range(espessura):
            for i in range(w):
                ponto(img, x + i, yy + e, tom(cor, 0.1 if e == 0 else -0.1))
    return camada


def manchas(cor, posicoes):
    """Pintinhas em posições relativas (fração da face) — pele do Agumon."""
    def camada(img, x, y, w, h):
        for fx, fy in posicoes:
            px, py = x + int(w * fx), y + int(h * fy)
            ret(img, px, py, 2, 2, cor)
            ponto(img, px + 2, py + 1, cor)
    return camada


def detalhes(lista):
    """Pixels avulsos: lista de (rx, ry, cor) relativos à face."""
    def camada(img, x, y, w, h):
        for rx, ry, cor in lista:
            ponto(img, x + rx, y + ry, cor)
    return camada


def faixas_curvas(cor, quantidade=3, espessura=2, curva=2, inicio=0.15, fim=0.95):
    """Faixas horizontais que descem no meio (listras da pele do Gabumon)."""
    def camada(img, x, y, w, h):
        for k in range(quantidade):
            base = y + int(h * (inicio + (fim - inicio) * k / max(1, quantidade - 1 if quantidade > 1 else 1)))
            meio = (w - 1) / 2
            for i in range(w):
                d = 1 - abs(i - meio) / max(1, meio)
                dy = round(d * curva)
                for e in range(espessura):
                    yy = base + dy + e
                    if y <= yy < y + h:
                        ponto(img, x + i, yy, cor)
    return camada


def elipse(cor, cx, cy, rx, ry, borda=None):
    """Elipse cheia (com borda opcional), em frações da face."""
    def camada(img, x, y, w, h):
        ox, oy = x + w * cx, y + h * cy
        ax, ay = w * rx, h * ry
        for i in range(w):
            for j in range(h):
                dx = (x + i + 0.5 - ox) / ax
                dy = (y + j + 0.5 - oy) / ay
                d = dx * dx + dy * dy
                if d <= 1:
                    ponto(img, x + i, y + j, borda if borda and d > 0.6 else cor)
    return camada


def emblema_gabumon(azul, rosa):
    """O emblema da barriga do Gabumon: oval azul-claro com anel e traços rosa."""
    def camada(img, x, y, w, h):
        # oval azul-claro com contorno rosa
        elipse(azul, 0.5, 0.52, 0.38, 0.44, borda=rosa)(img, x, y, w, h)
        elipse(azul, 0.5, 0.52, 0.32, 0.36)(img, x, y, w, h)
        # anel rosa em cima
        elipse(rosa, 0.5, 0.36, 0.13, 0.15)(img, x, y, w, h)
        elipse(azul, 0.5, 0.36, 0.06, 0.07)(img, x, y, w, h)
        # arco rosa embaixo, como um sorriso
        cx = x + (w - 1) / 2
        base = y + int(h * 0.66)
        meio = int(w * 0.18)
        for i in range(-meio, meio + 1):
            sobe = 1 if abs(i) >= meio - 1 else 0
            ponto(img, int(cx + i + 0.5), base - sobe, rosa)
    return camada


def sorriso(cor_linha, dentes, largura, curva=1):
    """Boca sorrindo: linha que sobe nas pontas, com dentinhos brancos logo abaixo."""
    def camada(img, x, y, w, h):
        meio = (largura - 1) / 2
        for i in range(largura):
            sobe = curva if abs(i - meio) > meio * 0.7 else 0
            ponto(img, x + i, y + 1 - sobe, cor_linha)
        for dx in dentes:
            ponto(img, x + dx, y + 2, BRANCO)
    return camada


def olho_redondo(rx, ry, d, iris, esclera=None, pupila=2, contorno=ESCURO, cilios=False, espelhado=False):
    """
    Olho redondo (bebês): círculo com contorno, íris (ou esclera + íris), pupila e brilho.
    esclera=None faz um olho todo colorido (como o do Botamon); com esclera, a íris fica no meio.
    """
    def camada(img, x, y, w, h):
        ox, oy = x + rx, y + ry
        c = (d - 1) / 2
        for i in range(d):
            for j in range(d):
                dist = ((i - c) ** 2 + (j - c) ** 2) ** 0.5
                if dist > c + 0.5:
                    continue
                if dist > c - 0.4:
                    cor = contorno
                elif esclera is not None and dist > c * 0.55:
                    cor = esclera
                else:
                    t = (j - (c - c * 0.8)) / max(1, c * 1.6)
                    cor = tom(iris, 0.18 - 0.36 * max(0, min(1, t)))
                ponto(img, ox + i, oy + j, cor)
        # pupila e brilho
        p0 = int(c - pupila / 2 + 0.5)
        ret(img, ox + p0, oy + p0, pupila, pupila, ESCURO)
        ponto(img, ox + int(c) - 1 + (1 if espelhado else 0), oy + int(c) - 1, BRANCO)
        ponto(img, ox + int(c) + (1 if not espelhado else 0), oy + int(c) + 1, tom(BRANCO, -0.3))
        if cilios:
            lado = -1 if not espelhado else d
            ponto(img, ox + lado, oy, contorno)
            ponto(img, ox + lado + (-1 if not espelhado else 1), oy - 1, contorno)
    return camada


def boca_aberta(rx, ry, largura, altura, interior="#5A1E2A", lingua="#E8708A", presas=True):
    """Boca aberta sorrindo: interior escuro, língua embaixo e presinhas em cima."""
    def camada(img, x, y, w, h):
        ox, oy = x + rx, y + ry
        for i in range(largura):
            borda = i in (0, largura - 1)
            for j in range(altura):
                if borda and j == altura - 1:
                    continue
                cor = lingua if j >= altura - max(1, altura // 3) and not borda else interior
                ponto(img, ox + i, oy + j, cor)
        if presas and largura >= 4:
            ponto(img, ox + 1, oy, BRANCO)
            ponto(img, ox + largura - 2, oy, BRANCO)
    return camada


def listras_laterais(cor, quantidade=3, comprimento=0.45, espessura=2):
    """Listras horizontais que entram pelos dois lados e afinam (tigre: Greymon)."""
    def camada(img, x, y, w, h):
        tam = max(2, int(w * comprimento))
        for k in range(quantidade):
            yy = y + int(h * (k + 0.7) / (quantidade + 0.4))
            for r in range(tam):
                esp = max(1, round(espessura * (1 - r / tam) + 0.4))
                for e in range(esp):
                    ponto(img, x + r, yy + e, cor)
                    ponto(img, x + w - 1 - r, yy + e + (k % 2), cor)
    return camada


def brilho(cx, cy, rx, ry, intensidade=0.45):
    """Mancha clara de reflexo (geleias brilhantes como o Punimon)."""
    def camada(img, x, y, w, h):
        ox, oy, ax, ay = x + w * cx, y + h * cy, max(1, w * rx), max(1, h * ry)
        for i in range(w):
            for j in range(h):
                d = ((x + i + 0.5 - ox) / ax) ** 2 + ((y + j + 0.5 - oy) / ay) ** 2
                if d <= 1:
                    ponto(img, x + i, y + j, tom(img.getpixel((x + i, y + j)), intensidade * (1 - d)))
    return camada


def costura(cor, y0, x0=0.0, x1=1.0):
    """Linha tracejada de costura (jeans, couro)."""
    def camada(img, x, y, w, h):
        yy = y + int(h * y0)
        for i in range(int(w * x0), int(w * x1), 2):
            ponto(img, x + i, yy, cor)
    return camada


def caveira(rx, ry, osso="#F2EED8", sombra="#2A2A30"):
    """Caveira com ossos cruzados (estampa da calça do WereGarurumon), 7x7 pixels."""
    padrao = [
        "o.....o",
        ".o###o.",
        "..#s#s.",
        "..#####",
        "...#s#.",
        ".o.###o",
        "o.....o",
    ]
    def camada(img, x, y, w, h):
        for j, linha in enumerate(padrao):
            for i, ch in enumerate(linha):
                if ch in "o#":
                    ponto(img, x + rx + i, y + ry + j, osso)
                elif ch == "s":
                    ponto(img, x + rx + i, y + ry + j, sombra)
    return camada


def painel(cor, margem=1):
    """Contorno de placa de metal (linhas de junção)."""
    def camada(img, x, y, w, h):
        for i in range(margem, w - margem):
            ponto(img, x + i, y + margem, cor)
            ponto(img, x + i, y + h - 1 - margem, cor)
        for j in range(margem, h - margem):
            ponto(img, x + margem, y + j, cor)
            ponto(img, x + w - 1 - margem, y + j, cor)
    return camada


def segmentos(cor, quantidade=3):
    """Linhas horizontais escuras (chifres segmentados)."""
    def camada(img, x, y, w, h):
        for k in range(1, quantidade + 1):
            yy = y + int(h * k / (quantidade + 1))
            for i in range(w):
                ponto(img, x + i, yy, cor)
        for j in range(h):
            ponto(img, x, y + j, tom(img.getpixel((x, y + j)), 0.25))
    return camada
