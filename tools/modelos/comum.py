"""
Peças e utilidades comuns aos Digimon feitos com a skill modelos-minecraft.

Cada script de Digimon faz `from comum import *` e no fim chama `finalizar(m)`, que:
  - sem argumentos: grava em tools/modelos/saida_v2 e gera prévias + comparação com as referências
  - com --mod: grava direto nas pastas do mod (modelo, animação, textura)
"""
import os
import subprocess
import sys

def _base_ferramentas():
    """Pasta das ferramentas: D:\\FerramentasMinecraft no PC, C:\\FerramentasMinecraft no notebook
    (ou a variável de ambiente FERRAMENTAS_MINECRAFT)."""
    for p in (os.environ.get("FERRAMENTAS_MINECRAFT"), r"D:\FerramentasMinecraft", r"C:\FerramentasMinecraft"):
        if p and os.path.isdir(p):
            return p
    return r"C:\FerramentasMinecraft"


BASE = _base_ferramentas()
SKILL = os.path.join(BASE, "skills", "modelos-minecraft")
PY = os.path.join(BASE, "venv", "Scripts", "python.exe")
REFS = os.path.join(BASE, "referencias")
sys.path.insert(0, os.path.join(SKILL, "scripts"))

from mcmodel import *  # noqa: E402,F401,F403
import numpy as np  # noqa: E402,F401

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
ASSETS = os.path.join(RAIZ, "src", "main", "resources", "assets", "digimonaurity")
SAIDA = os.path.join(AQUI, "saida_v2")


def espelhar_arte(arte):
    """Espelha uma pixel art em texto (para o olho do outro lado)."""
    linhas = arte.strip("\n").split("\n")
    larg = max(len(x) for x in linhas)
    return "\n".join(x.ljust(larg, ".")[::-1] for x in linhas)


def olhos(frente, lado, cores, x_quina, y, z_frente, px=0.5):
    """
    Par de olhos que dobram a quina da cabeça (parte da frente + parte da lateral), pixel-perfeitos.
    `frente`/`lado` são a arte do olho ESQUERDO dele (+X, à direita de quem olha de frente):
    a última coluna de `frente` encosta na quina; a primeira de `lado` também.
    x_quina: |x| da lateral da cabeça; z_frente: z da face da frente.
    """
    lf = frente.strip("\n").split("\n")
    ll = lado.strip("\n").split("\n")
    wf = max(len(x) for x in lf) * px
    wl = max(len(x) for x in ll) * px
    return [
        decalque(frente, cores, centro=[x_quina - wf / 2, y, z_frente], direcao=(0, 0, -1), profundidade=0.3),
        decalque(lado, cores, centro=[x_quina, y, z_frente + wl / 2], direcao=(1, 0, 0), profundidade=0.3),
        decalque(espelhar_arte(frente), cores, centro=[-x_quina + wf / 2, y, z_frente], direcao=(0, 0, -1),
                 profundidade=0.3),
        decalque(espelhar_arte(lado), cores, centro=[-x_quina, y, z_frente + wl / 2], direcao=(-1, 0, 0),
                 profundidade=0.3),
    ]


def olhos_frente(arte, cores, x_centro, y, z_frente, profundidade=0.3, espelhar=True):
    """Par de olhos projetados de frente (bebês, bolinhas). x_centro = centro do olho esquerdo dele (+X)."""
    outro = espelhar_arte(arte) if espelhar else arte
    return [decalque(arte, cores, centro=[x_centro, y, z_frente], direcao=(0, 0, -1), profundidade=profundidade),
            decalque(outro, cores, centro=[-x_centro, y, z_frente], direcao=(0, 0, -1),
                     profundidade=profundidade)]


DENTE = None   # definido em dentes() (precisa do material)


def dentes(osso, mat, x_lado, y_labio, zs_lado, xs_frente=(), z_frente=None, tam=1.0):
    """Presinhas em "L" penduradas no lábio: nas laterais (x = ±x_lado) e na frente."""
    camada = [base(mat), sprite("gg\ng_", {"g": mat})] if tam == 1.0 else [base(mat), afinar("-y")]
    for lado in (1, -1):
        for z in zs_lado:
            osso.plano([x_lado * lado, y_labio - tam, z], [0, tam, tam], camada)
    for x in xs_frente:
        osso.plano([x - tam / 2, y_labio - tam, z_frente], [tam, tam, 0], camada)


def garras(osso, mat, x0, y_topo, z0, n=3, larg=1.0, comp=3.0, prof=1.5, passo=1.0, ponta="-y",
           inclinar=-12, abrir=6):
    """Garras cônicas lado a lado (mão: ponta "-y"; pé: ponta "-z")."""
    for k in range(n):
        x = x0 + k * passo
        if ponta == "-y":
            osso.cubo([x, y_topo - comp, z0], [larg, comp, prof],
                      [base(mat), afinar("-y", largura_ponta=0.3, curva=0.5, apoio="-z")],
                      rotacao=[inclinar, 0, (k - (n - 1) / 2) * abrir], pivo=[x + larg / 2, y_topo, z0 + prof / 2])
        else:
            osso.cubo([x, y_topo, z0 - comp], [larg, prof, comp],
                      [base(mat), afinar("-z", largura_ponta=0.0, curva=0.9, apoio="y")])


def _rodar(*args):
    r = subprocess.run([PY, *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    saida = (r.stdout + r.stderr).strip()
    if saida:
        print(saida)


def finalizar(m, refs=(), estilo=None, vistas="3/4,frente,esquerda", zoom="head", quadros="walk,attack"):
    """Grava e confere. refs: nomes de arquivo dentro de referencias/digimon/<nome>/."""
    if "--mod" in sys.argv:
        m.salvar(modelos=os.path.join(ASSETS, "geckolib", "models", "entity"),
                 animacoes=os.path.join(ASSETS, "geckolib", "animations", "entity"),
                 texturas=os.path.join(ASSETS, "textures", "entity"))
        geo = os.path.join(ASSETS, "geckolib", "models", "entity", f"{m.nome}.geo.json")
        png = os.path.join(ASSETS, "textures", "entity", f"{m.nome}.png")
        anim = os.path.join(ASSETS, "geckolib", "animations", "entity", f"{m.nome}.animation.json")
        _rodar(os.path.join(SKILL, "scripts", "validar.py"), geo, png, anim)
        return
    m.salvar(SAIDA)
    geo = os.path.join(SAIDA, f"{m.nome}.geo.json")
    png = os.path.join(SAIDA, f"{m.nome}.png")
    anim = os.path.join(SAIDA, f"{m.nome}.animation.json")
    _rodar(os.path.join(SKILL, "scripts", "validar.py"), geo, png, anim)
    if "--rapido" in sys.argv:
        return
    args = [os.path.join(SKILL, "scripts", "previa.py"), geo, png, "--anim", anim, "--quadros", quadros]
    if zoom:
        args += ["--zoom", zoom]
    _rodar(*args)
    pasta = os.path.join(REFS, "digimon", m.nome)
    caminhos = [os.path.join(pasta, r) for r in refs if os.path.exists(os.path.join(pasta, r))]
    args = [os.path.join(SKILL, "scripts", "comparar.py"), geo, png, *caminhos, "--vistas", vistas]
    if estilo:
        args += ["--estilo", os.path.join(REFS, "cobblemon", estilo)]
    _rodar(*args)


def cone_empilhado(osso, centro_base, camadas, pintura, rotacao=None, pivo=None, eixo=1):
    """
    Orelha/chifre/espinho grande feito de cubos empilhados que vão afinando (jeito Cobblemon: lê
    melhor que um cubo recortado quando a peça é grande).
    centro_base: [x, y, z] do centro da base; camadas: [(largura, altura, profundidade), ...] de baixo
    para cima. rotacao/pivo: giram a pilha inteira (pivô padrão = centro da base).
    """
    x, y, z = centro_base
    pivo = pivo or [x, y, z]
    grupo = f"cone{id(camadas)}_{x}_{y}_{z}"     # sem listras de quina entre os andares
    cubos = []
    for w, h, d in camadas:
        cubos.append(osso.cubo([x - w / 2, y, z - d / 2], [w, h, d], list(pintura), rotacao=rotacao, pivo=pivo,
                               grupo=grupo))
        y += h
    return cubos


def recortar(condicao):
    """Camada que deixa transparente onde a condição for verdadeira (bordas recortadas de asas, capas)."""
    def camada(ctx):
        mk = np.broadcast_to(np.asarray(condicao(ctx), dtype=bool), (ctx.h, ctx.w))
        ctx.cor[mk] = (0, 0, 0, 0)
        ctx.fixo[mk] = True
    return camada


def herdar(script, **globais):
    """Roda outro script de Digimon sem salvar e devolve as variáveis dele (m, ossos...) para reaproveitar."""
    import runpy
    return runpy.run_path(os.path.join(AQUI, script), init_globals=globais, run_name="herdado")


def listras_eixo(eixo, periodo, largura, ondulacao=0.0, eixo_onda=None, freq_onda=0.35, fase=0.0,
                 fator=None):
    """
    Listras perpendiculares a uma direção qualquer (ex.: o eixo inclinado do tronco ou do pescoço).
    eixo: vetor 3D; eixo_onda: vetor 3D que faz a listra ondular; fator(c) -> 0..1 multiplica a
    largura (afinar listras de tigre em direção à barriga).
    """
    e = np.array(eixo, float)
    e /= np.linalg.norm(e)
    eo = None if eixo_onda is None else np.array(eixo_onda, float) / np.linalg.norm(eixo_onda)

    def cond(c):
        v = c.p @ e + fase
        if ondulacao and eo is not None:
            v = v + ondulacao * np.sin((c.p @ eo) * freq_onda * np.pi)
        larg = np.full(v.shape, float(largura))
        if fator is not None:
            larg = larg * np.clip(fator(c), 0, 1)
        return (v % periodo) < larg
    return cond


def junta(osso, centro, tam, pintura, raio=0, arestas="y"):
    """Peça na articulação (ombro, cotovelo, quadril, joelho, base do pescoço): costura os segmentos."""
    x, y, z = centro
    w, h, d = tam
    if not raio:
        return [osso.cubo([x - w / 2, y - h / 2, z - d / 2], [w, h, d], pintura)]
    return osso.cubo_arredondado([x - w / 2, y - h / 2, z - d / 2], [w, h, d], pintura, raio=raio, arestas=arestas)
