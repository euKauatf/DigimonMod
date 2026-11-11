# Como usar o projeto no notebook

O projeto fica guardado em dois repositórios privados seus no GitHub:

- **DigimonMod**: o mod, os scripts dos modelos e este guia
- **FerramentasMinecraft**: a skill de modelos e as imagens de referência

O que é pesado e dá para baixar de novo (o Python da skill, o Blockbench e os arquivos de compilação)
não vai para o GitHub. O notebook baixa sozinho.

## 1. Instalar os programas no notebook (só uma vez, tudo gratuito)

1. **Git para Windows**: git-scm.com/download/win
2. **Python 3**: python.org/downloads. Na instalação, marque **"Add python.exe to PATH"**.
3. **Java 25 (Temurin JDK)**: adoptium.net
4. **App do Claude** (o mesmo que você usa no PC), entrando com a mesma conta.

## 2. Baixar o projeto

Abra o app do Claude no notebook, abra uma conversa no Code na pasta `C:\` e mande:

> Baixe meus repositórios DigimonMod para C:\DigimonMod e FerramentasMinecraft para
> C:\FerramentasMinecraft do meu GitHub, rode o instalar.bat da skill e crie a junction da skill
> modelos-minecraft em %USERPROFILE%\.claude\skills. Depois leia o CLAUDE.md.

Na primeira vez, o Git abre uma janela para você entrar na sua conta do GitHub. Entre normalmente.

Depois disso, abra as conversas na pasta `C:\DigimonMod`. O Claude lê o `CLAUDE.md` sozinho e já sabe
tudo sobre o projeto e sobre como você gosta das coisas.

## 3. Manter PC e notebook iguais

- Ao terminar no notebook, peça ao Claude: **"envie tudo para o GitHub"**.
- Ao voltar para o PC (ou para o notebook), peça: **"baixe as novidades do GitHub"**.

Assim os dois ficam sempre com a última versão. Evite mexer nos dois ao mesmo tempo sem sincronizar.

## 4. Jogar no notebook

- Para testar rápido, dê dois cliques em `jogar_teste.bat`.
- Para jogar com os amigos, rode `empacotar.bat` e use a pasta `distribuicao\mods`.
