# Configurações e constantes globais
import numpy as np

# --- Estados do Jogo ---
ESTADO_MENU = 0
ESTADO_JOGANDO = 1

# --- Opções do Menu ---
TITULO_JOGO = "Sinfonia dos Discos"
opcoes_menu = [
    {'texto': 'Jogar', 'id': 'jogar'},
    {'texto': 'Sair', 'id': 'sair'}
]

# Cores do menu
COR_FUNDO_MENU = (0.1, 0.1, 0.3, 1.0)  # Azul escuro
COR_TITULO = (1.0, 1.0, 0.3, 1.0)  # Amarelo
COR_BOTAO = (0.2, 0.2, 0.5, 1.0)  # Azul médio
COR_BOTAO_SELECIONADO = (0.4, 0.4, 0.8, 1.0)  # Azul claro
COR_TEXTO = (1.0, 1.0, 1.0, 1.0)  # Branco

# Dimensões do menu
largura_botao = 200
altura_botao = 60
espacamento_botoes = 20

# --- Configurações da Câmara ---
camera_pos_inicial = np.array([0.0, 1.0, 2.0])
camera_front_inicial = np.array([0.0, 0.0, -1.0])
camera_up_inicial = np.array([0.0, 1.0, 0.0])
yaw_inicial = -90.0
pitch_inicial = 0.0

# --- Dimensões da Sala ---
LARGURA_SALA = 10.0
ALTURA_SALA = 4.0
PROFUNDIDADE_SALA = 20.0

# --- Configurações do Alvo ---
NUM_ALVOS = 4
RAIO_ALVO_PADRAO = 0.3
INTERVALO_REAPARECIMENTO_ALVO = 0.5

# --- Configurações da Mira ---
MIRA_TAMANHO = 7 