# Sinfonia dos Discos 🎵

Um jogo 3D desenvolvido em Python usando OpenGL, onde o jogador deve acertar discos de vinil em movimento em um ambiente 3D.

## 🎮 Sobre o Jogo

Sinfonia dos Discos é um jogo de tiro em primeira pessoa onde você deve acertar discos de vinil que aparecem em diferentes posições em uma sala 3D. O jogo apresenta diferentes níveis de dificuldade, sistema de pontuação e tempo limite para completar cada fase.

### Características Principais
- Gráficos 3D usando OpenGL
- Sistema de câmera em primeira pessoa
- Múltiplos níveis com diferentes dificuldades
- Sistema de pontuação e tempo
- Menus interativos
- Efeitos visuais e texturas
- Sistema de alvos dinâmicos

## 🛠️ Requisitos

Para executar o jogo, você precisará ter instalado:

- Python 3.x
- PyOpenGL
- GLFW
- NumPy
- Pillow (PIL)
- Pygame

## 📦 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/JoaoGuerreiro16/ProjetoCG.git
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 🚀 Como Jogar

1. Execute o arquivo principal:
```bash
python main.py
```

2. No menu principal, selecione "Jogar"
3. Escolha o nível de dificuldade
4. Use o mouse para mirar e clique para atirar nos discos
5. Complete o objetivo antes que o tempo acabe!

### Controles
- Mouse: Movimenta a mira
- Botão Esquerdo do Mouse: Atira
- ESC: Pausa o jogo
- R: Reinicia o nível atual
- W/A/S/D: Movimenta a câmera (em alguns níveis)

## 🎯 Objetivos do Jogo

- Acerte os discos de vinil que aparecem na sala
- Complete o número necessário de acertos antes do tempo acabar
- Avance pelos níveis aumentando sua pontuação

## 🏗️ Estrutura do Projeto

- `main.py`: Arquivo principal do jogo
- `game.py`: Lógica principal do jogo
- `draw.py`: Funções de renderização
- `menus.py`: Sistema de menus
- `nivel.py`: Gerenciamento de níveis
- `config.py`: Configurações do jogo
- `text_renderer.py`: Sistema de renderização de texto
- `images/`: Diretório com texturas e imagens
- `fonts/`: Diretório com fontes utilizadas 