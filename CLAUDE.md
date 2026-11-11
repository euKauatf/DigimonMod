# Digimon Aurity — instruções para o Claude

Este arquivo vai junto com o projeto no GitHub. Ele faz o Claude do **notebook** começar com o mesmo
contexto do PC. As memórias abaixo foram copiadas da memória do PC em 2026-11-11.

## Quem é o usuário e como falar com ele

- Responda sempre em **português do Brasil**.
- O usuário **não programa**. Claude faz todo o código e todas as ferramentas, e o usuário testa o mod
  no jogo com os amigos.
- Explique os resultados **com imagens** (prévias renderizadas) e em linguagem simples.
- Só faça commit quando ele pedir.
- Use só coisas **gratuitas**.
- Downloads e ferramentas ficam na pasta de ferramentas, nunca espalhados:
  - `D:\FerramentasMinecraft` no PC;
  - `C:\FerramentasMinecraft` no notebook, que só tem C:.

## O projeto

- Mod de Minecraft Java **26.3** com **NeoForge 26.3.0.99** e **GeckoLib 5.5.7**, alvo Java 25.
- Linhas evolutivas iniciais:
  - Agumon (Botamon → WarGreymon)
  - Gabumon (Punimon → MetalGarurumon)
  - Veemon (Chibomon → Imperialdramon, com Digi-Egg próprio)
- Selvagens soltos: Goburimon, Gotsumon e Numemon.
- Os dados ficam em `src/main/resources/data/digimonaurity/digimonaurity/`:
  - `line/`, `form/`, `attack/` e `wild_spawn/`;
  - nomes em `assets/digimonaurity/lang/pt_br.json` e `en_us.json`.
- Atalhos `.bat` na raiz:
  - `compilar.bat` gera o `.jar` em `build\libs\`;
  - `jogar_teste.bat` abre o Minecraft de teste;
  - `empacotar.bat` monta `distribuicao\mods` para os amigos.

## Modelos (skill `modelos-minecraft`)

- Ferramentas de modelo:
  - os scripts dos Digimon ficam em `tools/modelos/<nome>.py` e importam `comum.py`;
  - `comum.py` acha sozinho a pasta de ferramentas (D: ou C:).
- Rodar um modelo:
  - `<base>\venv\Scripts\python.exe tools\modelos\<nome>.py` gera a prévia e a comparação em `tools/modelos/saida_v2/previas`;
  - com `--mod`, grava direto no mod.
- A skill fica em `<base>\skills\modelos-minecraft` e as referências baixadas em `<base>\referencias`.
- No notebook, a skill precisa de uma junction em `%USERPROFILE%\.claude\skills\modelos-minecraft`.
  Veja `COMO_USAR_NO_NOTEBOOK.md`.

### O que o usuário já aprovou ou reprovou (siga sempre)

- **Cores vivas e lisas.** Ele rejeitou a paleta vanilla com granulado: achou "apagado" e com cara de
  "spray manchado". Use rampas da referência oficial com `estilo="limpo"` e ruído baixo.
- **Anatomia fiel à referência oficial.** Ele reprovou modelos grandes feitos de cubos retos (pernas de
  pilar, tronco de caixa). Para champion, ultimate e mega:
  - siga `references/anatomia.md` da skill;
  - meça na folha oficial ("reference art");
  - mostre "referência | modelo" antes de pôr no mod;
  - faça um Digimon por vez e espere o ok dele.
- **Regras de forma que ele pediu:**
  - juntas fechadas, sem buracos;
  - olhos com pupila;
  - corpo nem esquelético nem gordo demais;
  - cabeça de dragão com pescoço, sem empurrar a cabeça para a frente demais;
  - asas presas às costas e abrindo para fora;
  - emblemas da barriga em faces lisas;
  - dentes para fora da boca.
- **Sempre busque referências** com `referencias.py`, nunca desenhe de memória. Compare com
  `comparar.py`, que roda sozinho no fim de cada script.

## Detalhes técnicos que já custaram caro

- **GeckoLib 5.5 e as faces leste/oeste:** a face pintada no lado +X se chama "west" no `.geo.json`. A
  biblioteca já trata isso (`CHAVE_ARQUIVO`), então não "corrija" UVs à mão.
- **Faces sobrepostas piscam no jogo.** O validador avisa; a biblioteca esconde ou infla as faces sozinha.
- **Olhos cortados na quina:** o decalque não pinta a quina. Use `raio` pequeno na cabeça onde vão olhos grandes.
- **Pernas mais compridas sem estragar a pintura:** use `m.deslocar("body", [0, dy, 0])`.
- **Compilar no PC:** o nome de usuário tem acento, por isso os `.bat` usam `.tmp\jtmp` como pasta
  temporária. Use sempre os `.bat`.
