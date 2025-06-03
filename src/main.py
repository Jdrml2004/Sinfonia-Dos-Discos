import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
# OpenGL.GLUT já não é necessário
import numpy as np
import math
import random
import sys
from config import *
from game import *
from draw import *
from PIL import Image
import pygame
from text_renderer import TextRenderer
from menus import MenuPrincipal, MenuVitoria, MenuDerrota, MenuDificuldade, MenuConfiguracoes, MenuNiveis, MenuPausa, MenuFimDesafio, MenuCreditos
from nivel import GerenciadorNiveis
from config_manager import ConfigManager
from model_loader import ObjReader, draw_obj_model # Importar o leitor e o desenhador de modelos OBJ

# Inicializa pygame para renderização de texto e áudio
pygame.init()
pygame.mixer.init() # Inicializa o mixer do Pygame

# Criar instância global do renderizador de texto e menus
text_renderer = TextRenderer()

# Criar instância do ConfigManager e carregar configurações
config_manager = ConfigManager()

# Declare menu variables globally
menu_principal = None
menu_vitoria = None
menu_derrota = None
menu_dificuldade = None
menu_configuracoes = None
menu_niveis = None  # Explicitamente declarado como None
menu_pausa = None
menu_fim_desafio = None  # Novo menu para o final do desafio especial
menu_creditos = None  # Novo menu para o menu de créditos

# --- Estados do Jogo ---
ESTADO_MENU = 0
ESTADO_MENU_DIFICULDADE = 1
ESTADO_JOGANDO = 2
ESTADO_VITORIA = 3
ESTADO_DERROTA = 4
ESTADO_CONFIGURACOES = 5
ESTADO_PAUSADO = 6  # Novo estado para o menu de pausa
ESTADO_MENU_NIVEIS = 7
ESTADO_FIM_DESAFIO = 8  # Novo estado para o final do desafio especial
ESTADO_CREDITOS = 9  # Novo estado para o menu de créditos
estado_jogo_atual = ESTADO_MENU
estado_anterior = None  # Variável para rastrear o estado anterior

# --- Configurações do Nível ---
gerenciador_niveis = GerenciadorNiveis()
ALVOS_NECESSARIOS = 10
TEMPO_LIMITE = 30.0  # segundos
tempo_inicio_nivel = 0
tempo_restante = TEMPO_LIMITE

# --- Cores do Jogo ---
COR_FUNDO_JOGO = (0.2, 0.2, 0.3, 1.0)  # Azul mais claro
COR_FUNDO_GRADIENTE = (0.3, 0.3, 0.4, 1.0)  # Cor secundária mais clara para o gradiente
COR_DISCO = (0.1, 0.1, 0.1, 1.0)  # Preto do vinil
COR_DISCO_BRILHO = (0.2, 0.2, 0.2, 1.0)  # Brilho do vinil
COR_LABEL_DISCO = (0.8, 0.1, 0.1, 1.0)  # Vermelho para o label central
COR_FAIXAS_DISCO = (0.15, 0.15, 0.15, 1.0)  # Cinza escuro para as faixas

# --- Opções do Menu ---
TITULO_JOGO = "Sinfonia dos Discos"
opcoes_menu = [
    {'texto': 'Jogar', 'id': 'jogar'},
    {'texto': 'Sair', 'id': 'sair'}
]
item_menu_selecionado_idx = 0

# Cores do menu (convertidas para RGB)
COR_FUNDO_MENU = (0.1, 0.1, 0.3, 1.0)  # Azul escuro
COR_TITULO_RGB = (255, 255, 77)  # Amarelo
COR_BOTAO = (0.2, 0.2, 0.5, 1.0)  # Azul médio
COR_BOTAO_SELECIONADO = (0.4, 0.4, 0.8, 1.0)  # Azul claro
COR_TEXTO_RGB = (255, 255, 255)  # Branco

# Dimensões do menu (serão ajustadas na função desenhar_menu)
largura_botao = 200
altura_botao = 60
espacamento_botoes = 20
botoes_rects = []  # Lista de retângulos para os botões (usado para deteção de clique)

# --- Configurações da Câmara (valores iniciais, podem ser resetados) ---
camera_pos_inicial = np.array([0.0, 0.5, 2.0])  # Reduzindo a altura Y de 1.0 para 0.5
camera_front_inicial = np.array([0.0, 0.0, -1.0])
camera_up_inicial = np.array([0.0, 1.0, 0.0])
yaw_inicial = -90.0
pitch_inicial = 0.0

camera_pos = np.copy(camera_pos_inicial)
camera_front = np.copy(camera_front_inicial)
camera_up = np.copy(camera_up_inicial)
yaw = yaw_inicial
pitch = pitch_inicial

last_x, last_y = 400, 300
first_mouse = True
mouse_sensitivity = 0.1
fov = 60.0 # Aumenta o campo de visão para reduzir o zoom

# --- Dimensões da Sala ---
LARGURA_SALA = 15.0  # Aumentado de 10.0
ALTURA_SALA = 6.0    # Aumentado de 4.0
PROFUNDIDADE_SALA = 30.0  # Aumentado de 20.0

# Adiciona margem de segurança para colisão
MARGEM_COLISAO = 0.5  # Metade da largura do jogador

# --- Configurações de Iluminação ---
LUZ_HABILITADA = True  # Controla se a luz está habilitada
POSICAO_LUZ = [0.0, ALTURA_SALA/2 - 0.2, 0.0, 1.0]  # Posição da luz no teto (centro)
COR_LUZ_AMBIENTE = [0.3, 0.3, 0.3, 1.0]  # Cor da luz ambiente
COR_LUZ_DIFUSA = [0.9, 0.9, 0.9, 1.0]  # Cor da luz difusa
COR_LUZ_ESPECULAR = [1.0, 1.0, 1.0, 1.0]  # Cor da luz especular
SOMBRAS_HABILITADAS = True  # Controla se as sombras estão habilitadas

# Novas variáveis para as luzes dos cantos
LUZES_CANTOS_HABILITADAS = True  # Será substituído pelo valor das configurações
COR_LUZ_CANTO_AMBIENTE = [0.1, 0.1, 0.1, 1.0]  # Cor ambiente mais fraca para as luzes dos cantos
COR_LUZ_CANTO_DIFUSA = [0.4, 0.4, 0.4, 1.0]  # Cor difusa mais fraca para as luzes dos cantos
COR_LUZ_CANTO_ESPECULAR = [0.6, 0.6, 0.6, 1.0]  # Cor especular mais fraca para as luzes dos cantos

# --- Configurações do Alvo ---
NUM_ALVOS = 4
RAIO_ALVO_PADRAO = 0.5
# Multiplicadores de tamanho com base na dificuldade
MULTIPLICADOR_ALVO_NORMAL = 2.0  # Dobro do tamanho para o modo normal
MULTIPLICADOR_ALVO_DIFICIL = 1.25  # Aumento de 25% para o modo difícil
MULTIPLICADOR_ALVO_IMPOSSIVEL = 1.0  # Tamanho original para o modo impossível
INTERVALO_REAPARECIMENTO_ALVO = 0.5
lista_alvos = []
lista_tiros = []  # Lista para armazenar os tiros

# Inicializa o gerador de números aleatórios
random.seed()

# --- Configurações da Mira ---
MIRA_TAMANHO = 7

# --- Texturas ---
textura_fundo = None
textura_chao = None
textura_titulo = None
textura_trompete = None  # Nova textura para o trompete
textura_baixo = None  # Nova textura para o baixo
textura_trombone = None  # Nova textura para o trombone
textura_vibrafone = None  # Nova textura para o vibrafone
textura_extra = None  # Nova textura extra

# --- Variáveis de Estado do Jogo ---
estado_jogo_atual = ESTADO_MENU
item_menu_selecionado_idx = 0
botoes_rects = []
score = 0

# Variáveis de movimento
movement_keys = {
    'forward': False,
    'backward': False,
    'left': False,
    'right': False,
    'jump': False,
    'crouch': False,
    'sprint': False  # Nova tecla para corrida
}
last_frame_time = 0.0
movement_speed = 5.0  # Velocidade base de movimento
sprint_speed = 10.0   # Velocidade durante a corrida

# Variáveis de pulo
is_jumping = False
jump_velocity = 0.0
jump_height = 1.0  # Altura máxima do pulo
gravity = 9.8  # Aceleração da gravidade
initial_jump_velocity = math.sqrt(2 * gravity * jump_height)  # Velocidade inicial para atingir a altura desejada

# Variáveis para o agachamento
is_crouching = False
crouch_height_offset = 0.8 # Quanto a câmera desce ao agachar
crouch_transition_duration = 0.2 # Duração da transição (em segundos)
crouch_transition_timer = 0.0 # Contador de tempo da transição
is_transitioning_crouch = False # Flag para indicar se está em transição
transition_start_height = 0.0 # Altura inicial da transição
transition_target_height = 0.0 # Altura alvo da transição

# Variáveis para os tiros (notas musicais)
shots = []
last_shot_time = 0.0 # Para controlar o intervalo entre tiros
shot_interval = 0.5 # Segundos entre tiros

# Variável para o modelo do vibrafone
obj_vibrafone_geometry = None # Variável global para armazenar a geometria do vibrafone
obj_vibrafone_texture = None
obj_trompete_geometry = None # Variável global para armazenar a geometria do trompete
obj_baixo_geometry = None # Variável global para armazenar a geometria do baixo
obj_trombone_geometry = None # Variável global para armazenar a geometria do trombone
obj_bateria_geometry = None # Variável global para armazenar a geometria da bateria

# Sons
sons_trompete = None
indice_som_trompete = 0
sons_vibrafone = None
indice_som_vibrafone = 0
sons_baixo = None
indice_som_baixo = 0
sons_trombone = None
indice_som_trombone = 0
sons_bateria = None
indice_som_bateria = 0

# Variáveis para controle de volume individual dos instrumentos
VOLUME_TROMPETE = 0.5  # Reduzido para 50%
VOLUME_BATERIA = 3.6   # Aumentado para 360%
VOLUME_VIBRAFONE = 1.0 # Mantido em 100%
VOLUME_BAIXO = 1.0     # Mantido em 100%
VOLUME_TROMBONE = 1.0  # Mantido em 100%

# Variáveis globais para controle de pausa
tempo_pausa_inicio = 0
tempo_total_pausado = 0

def carregar_textura(caminho_imagem):
    """Carrega uma imagem e a converte em textura OpenGL"""
    try:
        print(f"Tentando carregar textura: {caminho_imagem}")
        imagem = Image.open(caminho_imagem)
        print(f"Imagem aberta com sucesso: {caminho_imagem}, modo: {imagem.mode}, tamanho: {imagem.size}")
        imagem = imagem.transpose(Image.FLIP_TOP_BOTTOM)  # Inverte a imagem verticalmente
        dados_imagem = np.array(list(imagem.getdata()), np.uint8)
        
        # Gera um ID de textura
        textura_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, textura_id)
        
        # Configura os parâmetros da textura
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        # Carrega os dados da imagem na textura
        if imagem.mode == 'RGB':
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, imagem.width, imagem.height, 0, GL_RGB, GL_UNSIGNED_BYTE, dados_imagem)
        elif imagem.mode == 'RGBA':
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, imagem.width, imagem.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, dados_imagem)
        else:
            print(f"Aviso: Modo de imagem não suportado: {imagem.mode}, convertendo para RGB")
            imagem = imagem.convert("RGB")
            dados_imagem = np.array(list(imagem.getdata()), np.uint8)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, imagem.width, imagem.height, 0, GL_RGB, GL_UNSIGNED_BYTE, dados_imagem)
        
        print(f"Textura carregada com sucesso, ID: {textura_id}")
        return textura_id
    except Exception as e:
        print(f"Erro ao carregar textura '{caminho_imagem}': {e}")
        import traceback
        traceback.print_exc()
        return None

# --- Funções de Desenho do Jogo (cubo, sala, circulo, alvos, mira - maioritariamente inalteradas) ---
def desenhar_cubo(size=1.0):
    half_size = size / 2.0
    vertices = [
        [-half_size, -half_size, half_size], [half_size, -half_size, half_size],
        [half_size, half_size, half_size], [-half_size, half_size, half_size],
        [-half_size, -half_size, -half_size], [half_size, -half_size, -half_size],
        [half_size, half_size, -half_size], [-half_size, half_size, -half_size]
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]
    glBegin(GL_LINES)
    for edge in edges:
        for vertex_index in edge:
            glVertex3fv(vertices[vertex_index])
    glEnd()

def desenhar_sala(largura, altura, profundidade):
    nivel_atual = gerenciador_niveis.obter_nivel_atual()
    cor_sala = nivel_atual.cor_sala
    
    # Configura a iluminação
    configurar_iluminacao()
    
    # Desenha as paredes da sala
    glPushMatrix()
    
    # Habilita texturas para as paredes
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, textura_fundo)
    
    # Paredes laterais e teto (com textura)
    glColor4f(*cor_sala)  # Usa a cor do nível atual
    
    # Parede esquerda
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex3f(-largura/2, -altura/2, -profundidade/2)
    glTexCoord2f(0.0, 1.0); glVertex3f(-largura/2, altura/2, -profundidade/2)
    glTexCoord2f(1.0, 1.0); glVertex3f(-largura/2, altura/2, profundidade/2)
    glTexCoord2f(1.0, 0.0); glVertex3f(-largura/2, -altura/2, profundidade/2)
    glEnd()
    
    # Parede direita
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex3f(largura/2, -altura/2, -profundidade/2)
    glTexCoord2f(1.0, 0.0); glVertex3f(largura/2, -altura/2, profundidade/2)
    glTexCoord2f(1.0, 1.0); glVertex3f(largura/2, altura/2, profundidade/2)
    glTexCoord2f(0.0, 1.0); glVertex3f(largura/2, altura/2, -profundidade/2)
    glEnd()

    # Parede traseira (com textura)
    glColor4f(*cor_sala)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex3f(-largura/2, -altura/2, profundidade/2)
    glTexCoord2f(1.0, 0.0); glVertex3f(largura/2, -altura/2, profundidade/2)
    glTexCoord2f(1.0, 1.0); glVertex3f(largura/2, altura/2, profundidade/2)
    glTexCoord2f(0.0, 1.0); glVertex3f(-largura/2, altura/2, profundidade/2)
    glEnd()

    # Teto
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex3f(-largura/2, altura/2, -profundidade/2)
    glTexCoord2f(1.0, 0.0); glVertex3f(largura/2, altura/2, -profundidade/2)
    glTexCoord2f(1.0, 1.0); glVertex3f(largura/2, altura/2, profundidade/2)
    glTexCoord2f(0.0, 1.0); glVertex3f(-largura/2, altura/2, profundidade/2)
    glEnd()

    # Chão (com textura e cor da sala)
    glBindTexture(GL_TEXTURE_2D, textura_chao)
    glColor4f(*cor_sala)  # Aplica a cor da sala à textura do chão
    glBegin(GL_QUADS)
    # Repetir a textura várias vezes para criar um padrão mais denso
    glTexCoord2f(0.0, 0.0); glVertex3f(-largura/2, -altura/2, -profundidade/2)
    glTexCoord2f(0.0, 4.0); glVertex3f(-largura/2, -altura/2, profundidade/2)
    glTexCoord2f(4.0, 4.0); glVertex3f(largura/2, -altura/2, profundidade/2)
    glTexCoord2f(4.0, 0.0); glVertex3f(largura/2, -altura/2, -profundidade/2)
    glEnd()
    
    # Parede frontal (cor sólida, sem textura)
    glDisable(GL_TEXTURE_2D)
    glColor4f(*cor_sala)
    glBegin(GL_QUADS)
    glVertex3f(-largura/2, -altura/2, -profundidade/2)
    glVertex3f(-largura/2, altura/2, -profundidade/2)
    glVertex3f(largura/2, altura/2, -profundidade/2)
    glVertex3f(largura/2, -altura/2, -profundidade/2)
    glEnd()

    # Desenha as esferas de luz nos cantos
    desenhar_esferas_luz()

    glPopMatrix()

def desenhar_circulo(raio, segmentos=32, cor=(1.0, 0.0, 0.0)):
    glColor3f(cor[0], cor[1], cor[2])
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0.0, 0.0, 0.0)
    for i in range(segmentos + 1):
        angulo = 2.0 * math.pi * float(i) / float(segmentos)
        x = raio * math.cos(angulo)
        y = raio * math.sin(angulo)
        glVertex3f(x, y, 0.0)
    glEnd()

def gerar_posicao_alvo_aleatoria(alvos_existentes_info, raio_novo_alvo):
    # Usa o tempo atual como semente adicional para mais aleatoriedade
    random.seed(glfw.get_time())
    max_tentativas = 50
    z_pos = -PROFUNDIDADE_SALA / 2.0 + raio_novo_alvo + 0.01
    for _ in range(max_tentativas):
        x_rand = random.uniform(-LARGURA_SALA / 2.0 + raio_novo_alvo, LARGURA_SALA / 2.0 - raio_novo_alvo)
        y_rand = random.uniform(-ALTURA_SALA / 2.0 + raio_novo_alvo, ALTURA_SALA / 2.0 - raio_novo_alvo)
        nova_pos = np.array([x_rand, y_rand, z_pos])
        colisao = False
        for alvo_info in alvos_existentes_info:
            dist_centros = np.linalg.norm(nova_pos[:2] - alvo_info['pos'][:2])
            soma_raios = raio_novo_alvo + alvo_info['raio']
            if dist_centros < soma_raios + 0.1:
                colisao = True
                break
        if not colisao:
            return nova_pos
    
    # Se não encontrou posição sem colisão, tenta uma última vez com uma posição mais afastada
    print("Aviso: Tentando posição alternativa para novo alvo.")
    x_rand = random.uniform(-LARGURA_SALA / 2.0 + raio_novo_alvo, LARGURA_SALA / 2.0 - raio_novo_alvo)
    y_rand = random.uniform(-ALTURA_SALA / 2.0 + raio_novo_alvo, ALTURA_SALA / 2.0 - raio_novo_alvo)
    return np.array([x_rand, y_rand, z_pos])

def inicializar_alvos():
    global lista_alvos
    lista_alvos = []
    alvos_para_verificacao = []
    
    # Determina o multiplicador com base na dificuldade atual
    multiplicador = MULTIPLICADOR_ALVO_NORMAL  # Valor padrão
    if gerenciador_niveis.dificuldade_atual == gerenciador_niveis.DIFICULDADE_NORMAL:
        multiplicador = MULTIPLICADOR_ALVO_NORMAL
    elif gerenciador_niveis.dificuldade_atual == gerenciador_niveis.DIFICULDADE_DIFICIL:
        multiplicador = MULTIPLICADOR_ALVO_DIFICIL
    elif gerenciador_niveis.dificuldade_atual == gerenciador_niveis.DIFICULDADE_IMPOSSIVEL:
        multiplicador = MULTIPLICADOR_ALVO_IMPOSSIVEL
    
    for i in range(NUM_ALVOS):
        novo_raio = RAIO_ALVO_PADRAO * multiplicador
        nova_pos = gerar_posicao_alvo_aleatoria(alvos_para_verificacao, novo_raio)
        alvo = {
            'id': i, 'pos': nova_pos, 'raio': novo_raio,
            'visivel': True, 'tempo_atingido': 0.0
        }
        lista_alvos.append(alvo)
        alvos_para_verificacao.append({'pos': alvo['pos'], 'raio': alvo['raio']})

def desenhar_disco_vinil(raio, segmentos=64, cor_sala=None):
    """Desenha um disco de vinil com faixas e label central"""
    # Disco base (preto)
    glColor4f(*COR_DISCO)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0.0, 0.0, 0.0)
    for i in range(segmentos + 1):
        angulo = 2.0 * math.pi * float(i) / float(segmentos)
        x = raio * math.cos(angulo)
        y = raio * math.sin(angulo)
        glVertex3f(x, y, 0.0)
    glEnd()
    
    # Faixas do disco (círculos concêntricos)
    num_faixas = 8
    for i in range(num_faixas):
        raio_faixa = raio * (0.3 + (i * 0.08))  # Começa a 30% do raio
        glColor4f(*COR_FAIXAS_DISCO)
        glBegin(GL_LINE_LOOP)
        for j in range(segmentos):
            angulo = 2.0 * math.pi * float(j) / float(segmentos)
            x = raio_faixa * math.cos(angulo)
            y = raio_faixa * math.sin(angulo)
            glVertex3f(x, y, 0.0)
        glEnd()
    
    # Label central (usa a cor da sala atual)
    raio_label = raio * 0.25  # Label ocupa 25% do raio total
    if cor_sala:
        glColor4f(*cor_sala)
    else:
        glColor4f(*COR_LABEL_DISCO)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0.0, 0.0, 0.0)
    for i in range(segmentos + 1):
        angulo = 2.0 * math.pi * float(i) / float(segmentos)
        x = raio_label * math.cos(angulo)
        y = raio_label * math.sin(angulo)
        glVertex3f(x, y, 0.0)
    glEnd()
    
    # Brilho do disco (reflexo sutil)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(COR_DISCO_BRILHO[0], COR_DISCO_BRILHO[1], COR_DISCO_BRILHO[2], 0.2)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0.0, raio * 0.2, 0.0)  # Deslocado para criar efeito de luz
    for i in range(segmentos + 1):
        angulo = 2.0 * math.pi * float(i) / float(segmentos)
        x = raio * 0.8 * math.cos(angulo)  # 80% do raio para o brilho
        y = raio * (0.2 + 0.6 * math.sin(angulo))  # Efeito oval
        glVertex3f(x, y, 0.0)
    glEnd()
    glDisable(GL_BLEND)

def desenhar_alvos(alvos):
    glEnable(GL_BLEND)  # Habilita blending para todos os alvos
    nivel_atual = gerenciador_niveis.obter_nivel_atual()
    for alvo in alvos:
        if alvo['visivel']:
            glPushMatrix()
            glTranslatef(alvo['pos'][0], alvo['pos'][1], alvo['pos'][2])
            desenhar_disco_vinil(raio=alvo['raio'], cor_sala=nivel_atual.cor_sala)
            glPopMatrix()
    glDisable(GL_BLEND)

def desenhar_mira(largura_janela, altura_janela):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, largura_janela, 0, altura_janela)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING) # Desabilita iluminação para a mira
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2.0)
    centro_x, centro_y = largura_janela / 2, altura_janela / 2
    glBegin(GL_LINES)
    glVertex2f(centro_x - MIRA_TAMANHO, centro_y)
    glVertex2f(centro_x + MIRA_TAMANHO, centro_y)
    glVertex2f(centro_x, centro_y - MIRA_TAMANHO)
    glVertex2f(centro_x, centro_y + MIRA_TAMANHO)
    glEnd()
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()

# --- Funções de Desenho do Menu ---
def desenhar_retangulo_2d(x, y, largura, altura, cor):
    glDisable(GL_TEXTURE_2D)
    glColor4f(cor[0], cor[1], cor[2], cor[3])
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + largura, y)
    glVertex2f(x + largura, y + altura)
    glVertex2f(x, y + altura)
    glEnd()

def desenhar_menu(largura_janela, altura_janela):
    global botoes_rects
    
    # Salva estados OpenGL
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    
    # Configura a visualização 2D
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING) # Garante que a iluminação está desligada
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, largura_janela, 0, altura_janela, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Desenha fundo do menu
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    desenhar_retangulo_2d(0, 0, largura_janela, altura_janela, COR_FUNDO_MENU)
    
    # Botões
    botoes_rects = []
    y_botao = altura_janela / 2
    espacamento_botoes = altura_botao + 20
    
    for i, opcao in enumerate(opcoes_menu):
        cor_botao = COR_BOTAO_SELECIONADO if i == item_menu_selecionado_idx else COR_BOTAO
        x_botao = (largura_janela - largura_botao) / 2
        y_atual = y_botao - i * espacamento_botoes
        
        # Desenha botão
        desenhar_retangulo_2d(x_botao, y_atual, largura_botao, altura_botao, cor_botao)
        
        # Guarda rect para deteção de clique
        botoes_rects.append({
            'x': x_botao,
            'y': y_atual,
            'largura': largura_botao,
            'altura': altura_botao,
            'id': opcao['id']
        })
        
        # Desenha texto do botão
        texto = opcao['texto']
        tamanho_texto = 48
        largura_texto = len(texto) * tamanho_texto * 0.4
        x_texto = x_botao + (largura_botao - largura_texto) / 2
        y_texto = y_atual + (altura_botao - tamanho_texto/2) / 2
        text_renderer.draw_text(texto, x_texto, y_texto, tamanho_texto, COR_TEXTO_RGB)
    
    # Título
    texto_titulo = TITULO_JOGO
    tamanho_titulo = 72
    largura_titulo = len(texto_titulo) * tamanho_titulo * 0.5
    x_titulo = (largura_janela - largura_titulo) / 2
    y_titulo = altura_janela - 150
    text_renderer.draw_text(texto_titulo, x_titulo, y_titulo, tamanho_titulo, COR_TITULO_RGB)
    
    # Restaura estados OpenGL
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glPopAttrib()

def desenhar_score_e_tempo(largura_janela, altura_janela):
    # Salva o estado atual das matrizes
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    glDisable(GL_LIGHTING) # Desabilita iluminação para texto 2D
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, largura_janela, 0, altura_janela, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Desenha contagem de alvos à esquerda
    nivel_atual = gerenciador_niveis.obter_nivel_atual()
    
    # Texto para alvos diferente no modo desafio
    if gerenciador_niveis.esta_em_modo_desafio():
        texto_alvos = f"ALVOS: {score}"
    else:
        texto_alvos = f"ALVOS {score} / {nivel_atual.alvos_necessarios}"
    
    text_renderer.draw_text(texto_alvos, 20, altura_janela - 60, 48, COR_TEXTO_RGB)
    
    # Calcula as posições para centralizar melhor
    espaco_total = largura_janela - 40  # 20 pixels de margem em cada lado
    espaco_entre_itens = espaco_total / 3  # Divide o espaço em 3 partes iguais
    
    # Desenha nível atual
    if gerenciador_niveis.esta_em_modo_desafio():
        texto_nivel = "DESAFIO ESPECIAL"
    else:
        texto_nivel = f"NÍVEL {nivel_atual.numero}"
    
    tamanho_texto_nivel = 48
    largura_texto_nivel = len(texto_nivel) * tamanho_texto_nivel * 0.4
    x_texto_nivel = espaco_entre_itens - largura_texto_nivel / 2
    text_renderer.draw_text(texto_nivel, x_texto_nivel, altura_janela - 60, tamanho_texto_nivel, COR_TEXTO_RGB)
    
    # Desenha dificuldade
    dificuldade_texto = {
        "normal": "NORMAL",
        "dificil": "DIFÍCIL",
        "impossivel": "IMPOSSÍVEL"
    }
    texto_dificuldade = f"DIFICULDADE: {dificuldade_texto[gerenciador_niveis.dificuldade_atual]}"
    largura_texto_dificuldade = len(texto_dificuldade) * tamanho_texto_nivel * 0.4
    x_texto_dificuldade = 2 * espaco_entre_itens - largura_texto_dificuldade / 2
    text_renderer.draw_text(texto_dificuldade, x_texto_dificuldade, altura_janela - 60, tamanho_texto_nivel, COR_TEXTO_RGB)
    
    # Desenha tempo à direita
    texto_tempo = f"TEMPO: {int(tempo_restante)}s"
    text_renderer.draw_text(texto_tempo, largura_janela - 250, altura_janela - 60, 48, COR_TEXTO_RGB)
    
    # Restaura o estado das matrizes
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glPopAttrib()

def desenhar_tela_vitoria(largura_janela, altura_janela):
    # Salva estados OpenGL
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    
    # Configura a visualização 2D
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING) # Garante que a iluminação está desligada
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, largura_janela, 0, altura_janela, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Limpa a tela e desenha fundo
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    desenhar_retangulo_2d(0, 0, largura_janela, altura_janela, (0.0, 0.3, 0.0, 1.0))
    
    # Mensagem de parabéns
    mensagem = f"PARABENS POR CONCLUIR O NIVEL {gerenciador_niveis.obter_nivel_atual().numero}"
    tamanho_texto = 64
    largura_texto = len(mensagem) * tamanho_texto * 0.4
    x_texto = (largura_janela - largura_texto) / 2
    y_texto = altura_janela - 200
    text_renderer.draw_text(mensagem, x_texto, y_texto, tamanho_texto, (255, 255, 0))
    
    # Botões
    botoes = [
        {'texto': 'Proximo Nivel', 'id': 'proximo'},
        {'texto': 'Jogar Novamente', 'id': 'replay'},
        {'texto': 'Menu Principal', 'id': 'menu'}
    ]
    
    y_botao = altura_janela / 2
    for i, botao in enumerate(botoes):
        x_botao = (largura_janela - largura_botao) / 2
        y_atual = y_botao - i * (altura_botao + 20)
        
        cor_botao = COR_BOTAO_SELECIONADO if i == item_menu_selecionado_idx else COR_BOTAO
        desenhar_retangulo_2d(x_botao, y_atual, largura_botao, altura_botao, cor_botao)
        
        # Desenha texto do botão
        texto = botao['texto']
        tamanho_texto = 48
        largura_texto = len(texto) * tamanho_texto * 0.4
        x_texto = x_botao + (largura_botao - largura_texto) / 2
        y_texto = y_atual + (altura_botao - tamanho_texto/2) / 2
        text_renderer.draw_text(texto, x_texto, y_texto, tamanho_texto, COR_TEXTO_RGB)
    
    # Restaura estados OpenGL
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glPopAttrib()

def desenhar_tela_derrota(largura_janela, altura_janela):
    # Salva estados OpenGL
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    
    # Configura a visualização 2D
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING) # Garante que a iluminação está desligada
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, largura_janela, 0, altura_janela, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Limpa a tela e desenha fundo
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    desenhar_retangulo_2d(0, 0, largura_janela, altura_janela, (0.3, 0.0, 0.0, 1.0))
    
    # Mensagem
    mensagem = "TENTE NOVAMENTE"
    tamanho_texto = 64
    largura_texto = len(mensagem) * tamanho_texto * 0.4
    x_texto = (largura_janela - largura_texto) / 2
    y_texto = altura_janela - 200
    text_renderer.draw_text(mensagem, x_texto, y_texto, tamanho_texto, COR_TEXTO_RGB)
    
    # Botões
    botoes = [
        {'texto': 'Tentar Novamente', 'id': 'replay'},
        {'texto': 'Menu Principal', 'id': 'menu'}
    ]
    
    y_botao = altura_janela / 2
    for i, botao in enumerate(botoes):
        x_botao = (largura_janela - largura_botao) / 2
        y_atual = y_botao - i * (altura_botao + 20)
        
        cor_botao = COR_BOTAO_SELECIONADO if i == item_menu_selecionado_idx else COR_BOTAO
        desenhar_retangulo_2d(x_botao, y_atual, largura_botao, altura_botao, cor_botao)
        
        # Desenha texto do botão
        texto = botao['texto']
        tamanho_texto = 48
        largura_texto = len(texto) * tamanho_texto * 0.4
        x_texto = x_botao + (largura_botao - largura_texto) / 2
        y_texto = y_atual + (altura_botao - tamanho_texto/2) / 2
        text_renderer.draw_text(texto, x_texto, y_texto, tamanho_texto, COR_TEXTO_RGB)
    
    # Restaura estados OpenGL
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glPopAttrib()

def desenhar_fundo_estetico():
    global textura_fundo
    
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING) # Desabilita iluminação para o fundo
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Verifica se a textura foi carregada com sucesso
    if textura_fundo is not None:
        # Habilita texturas
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, textura_fundo)
        
        # Desenha o quad com a textura
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0); glVertex2f(-1.0, -1.0)
        glTexCoord2f(1.0, 0.0); glVertex2f(1.0, -1.0)
        glTexCoord2f(1.0, 1.0); glVertex2f(1.0, 1.0)
        glTexCoord2f(0.0, 1.0); glVertex2f(-1.0, 1.0)
        glEnd()
        
        # Desabilita texturas
        glDisable(GL_TEXTURE_2D)
    else:
        # Se a textura não foi carregada, desenha o fundo gradiente original
        glBegin(GL_QUADS)
        glColor4f(*COR_FUNDO_JOGO)
        glVertex2f(-1.0, -1.0)
        glVertex2f(1.0, -1.0)
        glColor4f(*COR_FUNDO_GRADIENTE)
        glVertex2f(1.0, 1.0)
        glVertex2f(-1.0, 1.0)
        glEnd()
    
    # Adiciona um efeito de "estrelas" sutis com movimento mais suave
    tempo_atual = glfw.get_time()
    glPointSize(1.5)
    glBegin(GL_POINTS)
    for i in range(50):
        random.seed(i)
        x_base = random.uniform(-1.0, 1.0)
        y_base = random.uniform(-1.0, 1.0)
        
        offset_x = math.sin(tempo_atual * 0.2 + i) * 0.01
        offset_y = math.cos(tempo_atual * 0.2 + i) * 0.01
        
        x = x_base + offset_x
        y = y_base + offset_y
        
        intensidade = 0.3 + 0.2 * math.sin(tempo_atual * 0.3 + i)
        glColor4f(1.0, 1.0, 1.0, intensidade)
        glVertex2f(x, y)
    glEnd()
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)
    
    # Reativa a iluminação se estiver habilitada
    if LUZ_HABILITADA and estado_jogo_atual == ESTADO_JOGANDO:
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        # Ativa as luzes dos cantos se estiverem habilitadas
        if LUZES_CANTOS_HABILITADAS:
            glEnable(GL_LIGHT1)
            glEnable(GL_LIGHT2)
            glEnable(GL_LIGHT3)
            glEnable(GL_LIGHT4)
        
        glEnable(GL_COLOR_MATERIAL)
        
        # Configura as propriedades da luz
        glLightfv(GL_LIGHT0, GL_POSITION, POSICAO_LUZ)
        glLightfv(GL_LIGHT0, GL_AMBIENT, COR_LUZ_AMBIENTE)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, COR_LUZ_DIFUSA)
        glLightfv(GL_LIGHT0, GL_SPECULAR, COR_LUZ_ESPECULAR)
        
        # Configura o modelo de sombreamento
        glShadeModel(GL_SMOOTH)
        
        # Habilitar luz para materiais
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)

def reiniciar_jogo():
    global camera_pos, camera_front, camera_up, yaw, pitch, first_mouse, lista_alvos, score
    global tempo_inicio_nivel, tempo_restante, lista_tiros, is_jumping, jump_velocity, is_crouching
    score = 0
    lista_tiros = []  # Limpa a lista de tiros
    camera_pos = np.copy(camera_pos_inicial)
    camera_front = np.copy(camera_front_inicial)
    camera_up = np.copy(camera_up_inicial)
    yaw = yaw_inicial
    pitch = pitch_inicial
    first_mouse = True
    is_jumping = False
    jump_velocity = 0.0
    is_crouching = False
    nivel_atual = gerenciador_niveis.obter_nivel_atual()
    tempo_inicio_nivel = glfw.get_time()
    tempo_restante = nivel_atual.tempo_limite
    inicializar_alvos()

def mouse_callback(window, xpos, ypos):
    global first_mouse, last_x, last_y, yaw, pitch, camera_front, menu_niveis, menu_principal, menu_dificuldade, menu_vitoria, menu_derrota, menu_configuracoes, menu_pausa, menu_fim_desafio
    
    _, altura_janela = glfw.get_window_size(window)
    rato_y_opengl = altura_janela - ypos  # Converte coordenadas do rato para OpenGL

    if estado_jogo_atual == ESTADO_JOGANDO:
        if first_mouse:
            last_x = xpos
            last_y = ypos
            first_mouse = False
        xoffset = xpos - last_x
        yoffset = last_y - ypos
        last_x = xpos
        last_y = ypos
        xoffset *= mouse_sensitivity
        yoffset *= mouse_sensitivity
        yaw += xoffset
        pitch += yoffset
        if pitch > 89.0: pitch = 89.0
        if pitch < -89.0: pitch = -89.0
        front = np.array([0.0,0.0,0.0])
        front[0] = np.cos(np.radians(yaw)) * np.cos(np.radians(pitch))
        front[1] = np.sin(np.radians(pitch))
        front[2] = np.sin(np.radians(yaw)) * np.cos(np.radians(pitch))
        camera_front = front / np.linalg.norm(front)
    elif estado_jogo_atual == ESTADO_MENU:
        # Verifica hover em botões
        if menu_principal is not None:
            menu_principal.processar_mouse(xpos, rato_y_opengl, action=None) # Pass mouse coordinates
        else:
            print("Erro: menu_principal não foi inicializado!")
    elif estado_jogo_atual == ESTADO_MENU_DIFICULDADE:
        # Verifica hover em botões
        if menu_dificuldade is not None:
            menu_dificuldade.processar_mouse(xpos, rato_y_opengl, action=None) # Pass mouse coordinates
        else:
            print("Erro: menu_dificuldade não foi inicializado!")
    elif estado_jogo_atual == ESTADO_MENU_NIVEIS:
        # Verifica hover em botões
        if menu_niveis is not None:
            menu_niveis.processar_mouse(xpos, rato_y_opengl, action=None) # Pass mouse coordinates
        else:
            print("Erro: menu_niveis não foi inicializado!")
    elif estado_jogo_atual == ESTADO_VITORIA:
        # Verifica hover em botões
        if menu_vitoria is not None:
            menu_vitoria.processar_mouse(xpos, rato_y_opengl, action=None) # Pass mouse coordinates
        else:
            print("Erro: menu_vitoria não foi inicializado!")
    elif estado_jogo_atual == ESTADO_DERROTA:
        # Verifica hover em botões
        if menu_derrota is not None:
            menu_derrota.processar_mouse(xpos, rato_y_opengl, action=None) # Pass mouse coordinates
        else:
            print("Erro: menu_derrota não foi inicializado!")
    elif estado_jogo_atual == ESTADO_CONFIGURACOES:
        # Handle mouse movement for hover and volume slider dragging
        if menu_configuracoes is not None:
            if menu_configuracoes.estado == 'menu':
                # Handle hover for menu options
                menu_configuracoes.processar_mouse(xpos, rato_y_opengl, action=None)
            elif menu_configuracoes.estado == 'ajustar_volume':
                # Somente atualiza o volume se o botão estiver pressionado (volume_ajustando == True)
                if menu_configuracoes.volume_ajustando:
                    menu_configuracoes.mouse_move(xpos, rato_y_opengl)
                else:
                    # Se não estiver ajustando o volume, apenas processa hover
                    menu_configuracoes.processar_mouse(xpos, rato_y_opengl, action=None)
    elif estado_jogo_atual == ESTADO_PAUSADO:
            if menu_pausa is not None:
                menu_pausa.processar_mouse(xpos, rato_y_opengl, action=None)
    elif estado_jogo_atual == ESTADO_FIM_DESAFIO:
        if menu_fim_desafio is not None:
            menu_fim_desafio.processar_mouse(xpos, rato_y_opengl, action=None)

def mouse_button_callback(window, button, action, mods):
    global lista_alvos, estado_jogo_atual, first_mouse, score, lista_tiros
    global third_person_camera_pos # Variável global para a posição da câmera de 3a pessoa
    global sons_trompete, indice_som_trompete # Variáveis globais para os sons do trompete
    global sons_vibrafone, indice_som_vibrafone # Variáveis globais para os sons do vibrafone
    global sons_baixo, indice_som_baixo # Variáveis globais para os sons do baixo
    global sons_trombone, indice_som_trombone # Variáveis globais para os sons do trombone
    global sons_bateria, indice_som_bateria # Variáveis globais para os sons da bateria
    global tempo_pausa_inicio, tempo_total_pausado, estado_anterior

    if button == glfw.MOUSE_BUTTON_LEFT:
        if estado_jogo_atual == ESTADO_MENU:
            rato_x = glfw.get_cursor_pos(window)[0]
            altura_janela = glfw.get_window_size(window)[1]
            rato_y_opengl = altura_janela - glfw.get_cursor_pos(window)[1]
            
            if action == glfw.PRESS and menu_principal is not None:
                acao = menu_principal.processar_mouse(rato_x, rato_y_opengl, action)
                if acao == 'jogar':
                    estado_jogo_atual = ESTADO_MENU_DIFICULDADE
                elif acao == 'sair':
                    glfw.set_window_should_close(window, True)
                elif acao == 'configuracoes':
                    estado_anterior = ESTADO_MENU
                    estado_jogo_atual = ESTADO_CONFIGURACOES
                elif acao == 'creditos':
                    estado_anterior = ESTADO_MENU
                    estado_jogo_atual = ESTADO_CREDITOS

        # Adiciona tratamento para o menu de vitória
        elif estado_jogo_atual == ESTADO_VITORIA:
            rato_x = glfw.get_cursor_pos(window)[0]
            altura_janela = glfw.get_window_size(window)[1]
            rato_y_opengl = altura_janela - glfw.get_cursor_pos(window)[1]
            
            if action == glfw.PRESS and menu_vitoria is not None:
                acao = menu_vitoria.processar_mouse(rato_x, rato_y_opengl, action)
                if acao == 'proximo':
                    # Avança para o próximo nível
                    if gerenciador_niveis.proximo_nivel():
                        estado_jogo_atual = ESTADO_JOGANDO
                        reiniciar_jogo()
                        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                        first_mouse = True
                        pygame.mixer.music.stop()
                    else:
                        # Se não houver próximo nível, volta ao menu de níveis
                        estado_jogo_atual = ESTADO_MENU_NIVEIS
                        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
                elif acao == 'replay':
                    # Reinicia o nível atual
                    estado_jogo_atual = ESTADO_JOGANDO
                    reiniciar_jogo()
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                    first_mouse = True
                    pygame.mixer.music.stop()
                elif acao == 'niveis':
                    # Vai para o menu de seleção de níveis
                    estado_jogo_atual = ESTADO_MENU_NIVEIS
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
                elif acao == 'dificuldade':
                    # Vai para o menu de seleção de dificuldade
                    estado_jogo_atual = ESTADO_MENU_DIFICULDADE
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
                elif acao == 'menu':
                    # Volta para o menu principal
                    estado_jogo_atual = ESTADO_MENU
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)

        # Adiciona tratamento para o menu de derrota
        elif estado_jogo_atual == ESTADO_DERROTA:
            rato_x = glfw.get_cursor_pos(window)[0]
            altura_janela = glfw.get_window_size(window)[1]
            rato_y_opengl = altura_janela - glfw.get_cursor_pos(window)[1]
            
            if action == glfw.PRESS and menu_derrota is not None:
                acao = menu_derrota.processar_mouse(rato_x, rato_y_opengl, action)
                if acao == 'replay':
                    # Reinicia o nível atual
                    estado_jogo_atual = ESTADO_JOGANDO
                    reiniciar_jogo()
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                    first_mouse = True
                    pygame.mixer.music.stop()
                elif acao == 'dificuldade':
                    # Vai para o menu de seleção de dificuldade
                    estado_jogo_atual = ESTADO_MENU_DIFICULDADE
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
                elif acao == 'menu':
                    # Volta para o menu principal
                    estado_jogo_atual = ESTADO_MENU
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)

        elif estado_jogo_atual == ESTADO_MENU_DIFICULDADE:
            rato_x = glfw.get_cursor_pos(window)[0]
            altura_janela = glfw.get_window_size(window)[1]
            rato_y_opengl = altura_janela - glfw.get_cursor_pos(window)[1]
            
            if action == glfw.PRESS and menu_dificuldade is not None:
                acao = menu_dificuldade.processar_mouse(rato_x, rato_y_opengl, action)
                if acao in ['normal', 'dificil', 'impossivel']:
                    gerenciador_niveis.definir_dificuldade(acao)
                    estado_jogo_atual = ESTADO_MENU_NIVEIS  # Vai para o menu de níveis
                elif acao == 'voltar':
                    estado_jogo_atual = ESTADO_MENU
                    
        elif estado_jogo_atual == ESTADO_MENU_NIVEIS:
            rato_x = glfw.get_cursor_pos(window)[0]
            altura_janela = glfw.get_window_size(window)[1]
            rato_y_opengl = altura_janela - glfw.get_cursor_pos(window)[1]
            
            if action == glfw.PRESS and menu_niveis is not None:
                acao = menu_niveis.processar_mouse(rato_x, rato_y_opengl, action)
                if acao == 'nivel1':
                    gerenciador_niveis.nivel_atual = 0  # Define o nível como 1
                    estado_jogo_atual = ESTADO_JOGANDO
                    reiniciar_jogo()
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                    first_mouse = True
                    pygame.mixer.music.stop()
                elif acao == 'nivel2':
                    gerenciador_niveis.nivel_atual = 1  # Define o nível como 2
                    estado_jogo_atual = ESTADO_JOGANDO
                    reiniciar_jogo()
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                    first_mouse = True
                    pygame.mixer.music.stop()
                elif acao == 'nivel3':
                    gerenciador_niveis.nivel_atual = 2  # Define o nível como 3
                    estado_jogo_atual = ESTADO_JOGANDO
                    reiniciar_jogo()
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                    first_mouse = True
                    pygame.mixer.music.stop()
                elif acao == 'nivel4':
                    gerenciador_niveis.nivel_atual = 3  # Define o nível como 4
                    estado_jogo_atual = ESTADO_JOGANDO
                    reiniciar_jogo()
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                    first_mouse = True
                    pygame.mixer.music.stop()
                elif acao == 'nivel5':
                    gerenciador_niveis.nivel_atual = 4  # Define o nível como 5
                    estado_jogo_atual = ESTADO_JOGANDO
                    reiniciar_jogo()
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                    first_mouse = True
                    pygame.mixer.music.stop()
                elif acao == 'desafio_especial':
                    # Ativa o modo desafio
                    gerenciador_niveis.ativar_modo_desafio()
                    estado_jogo_atual = ESTADO_JOGANDO
                    reiniciar_jogo()
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                    first_mouse = True
                    pygame.mixer.music.stop()
                elif acao == 'voltar':
                    estado_jogo_atual = ESTADO_MENU_DIFICULDADE

        elif estado_jogo_atual == ESTADO_JOGANDO:
            if action == glfw.PRESS:
                # Cria um novo tiro
                tiro = {
                    'pos': np.copy(third_person_camera_pos), # O tiro sai da posição da câmera em terceira pessoa (mira)
                    'direcao': np.copy(camera_pos) - np.copy(third_person_camera_pos), # A direção é do ponto de vista da câmera para o jogador
                    'tempo_criacao': glfw.get_time(),
                    'raio': 0.2  # Raio aumentado para melhor visibilidade
                }
                # Normaliza a direção do tiro para garantir velocidade consistente
                norma_direcao = np.linalg.norm(tiro['direcao'])
                if norma_direcao > 0:
                    tiro['direcao'] = tiro['direcao'] / norma_direcao
                else:
                    # Se a direção for zero (câmera na mesma posição do jogador?), usar a direção frontal padrão
                    tiro['direcao'] = np.copy(camera_front) # Fallback
                lista_tiros.append(tiro)
                # Incrementa o contador de disparos
                incrementar_contador_disparos()
                
                # Toca o som da nota de trompete se estiver no nível 1
                nivel_atual = gerenciador_niveis.obter_nivel_atual()
                if nivel_atual.numero == 1 and sons_trompete:
                    sons_trompete[indice_som_trompete].set_volume(VOLUME_TROMPETE)
                    sons_trompete[indice_som_trompete].play()
                    indice_som_trompete = (indice_som_trompete + 1) % len(sons_trompete)
                elif nivel_atual.numero == 2 and sons_vibrafone:
                    sons_vibrafone[indice_som_vibrafone].set_volume(VOLUME_VIBRAFONE)
                    sons_vibrafone[indice_som_vibrafone].play()
                    indice_som_vibrafone = (indice_som_vibrafone + 1) % len(sons_vibrafone)
                elif nivel_atual.numero == 3 and sons_trombone:
                    sons_trombone[indice_som_trombone].set_volume(VOLUME_TROMBONE)
                    sons_trombone[indice_som_trombone].play()
                    indice_som_trombone = (indice_som_trombone + 1) % len(sons_trombone)
                elif nivel_atual.numero == 4 and sons_baixo:
                    sons_baixo[indice_som_baixo].set_volume(VOLUME_BAIXO)
                    sons_baixo[indice_som_baixo].play()
                    indice_som_baixo = (indice_som_baixo + 1) % len(sons_baixo)
                elif nivel_atual.numero >= 5 and sons_bateria:
                    sons_bateria[indice_som_bateria].set_volume(VOLUME_BATERIA)
                    sons_bateria[indice_som_bateria].play()
                    indice_som_bateria = (indice_som_bateria + 1) % len(sons_bateria)
        
        elif estado_jogo_atual == ESTADO_FIM_DESAFIO:
            rato_x = glfw.get_cursor_pos(window)[0]
            altura_janela = glfw.get_window_size(window)[1]
            rato_y_opengl = altura_janela - glfw.get_cursor_pos(window)[1]
            
            if action == glfw.PRESS and menu_fim_desafio is not None:
                acao = menu_fim_desafio.processar_mouse(rato_x, rato_y_opengl, action)
                if acao == 'replay':
                    # Reinicia o desafio especial
                    gerenciador_niveis.ativar_modo_desafio()
                    estado_jogo_atual = ESTADO_JOGANDO
                    reiniciar_jogo()
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                    first_mouse = True
                    pygame.mixer.music.stop() # Para a música ao entrar no jogo
                elif acao == 'dificuldade':
                    # Desativa o modo desafio e vai para o menu de dificuldade
                    gerenciador_niveis.desativar_modo_desafio()
                    estado_jogo_atual = ESTADO_MENU_DIFICULDADE
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
                elif acao == 'menu':
                    # Desativa o modo desafio e volta para o menu principal
                    gerenciador_niveis.desativar_modo_desafio()
                    estado_jogo_atual = ESTADO_MENU
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
                elif acao == 'niveis':
                    # Desativa o modo desafio e vai para o menu de níveis
                    gerenciador_niveis.desativar_modo_desafio()
                    estado_jogo_atual = ESTADO_MENU_NIVEIS
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)

        elif estado_jogo_atual == ESTADO_PAUSADO:
            rato_x = glfw.get_cursor_pos(window)[0]
            altura_janela = glfw.get_window_size(window)[1]
            rato_y_opengl = altura_janela - glfw.get_cursor_pos(window)[1]
            
            if action == glfw.PRESS and menu_pausa is not None:
                acao = menu_pausa.processar_mouse(rato_x, rato_y_opengl, action)
                if acao == 'retomar':
                    estado_jogo_atual = ESTADO_JOGANDO
                    tempo_total_pausado += glfw.get_time() - tempo_pausa_inicio
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                    first_mouse = True
                    pygame.mixer.music.stop()  # Para a música ao sair do pause
                elif acao == 'configuracoes':
                    estado_anterior = ESTADO_PAUSADO
                    estado_jogo_atual = ESTADO_CONFIGURACOES
                elif acao == 'menu':
                    estado_jogo_atual = ESTADO_MENU
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)

        elif estado_jogo_atual == ESTADO_CONFIGURACOES:
            rato_x = glfw.get_cursor_pos(window)[0]
            altura_janela = glfw.get_window_size(window)[1]
            rato_y_opengl = altura_janela - glfw.get_cursor_pos(window)[1]
            
            if action == glfw.PRESS and menu_configuracoes is not None:
                acao = menu_configuracoes.processar_mouse(rato_x, rato_y_opengl, action)
                if acao == 'voltar':
                    estado_jogo_atual = estado_anterior if estado_anterior is not None else ESTADO_MENU
                    config_manager.save_config()
            elif estado_jogo_atual == ESTADO_CREDITOS:
                # Volta para o estado anterior ou menu principal
                estado_jogo_atual = estado_anterior if estado_anterior is not None else ESTADO_MENU

        elif estado_jogo_atual == ESTADO_CREDITOS:
            rato_x = glfw.get_cursor_pos(window)[0]
            altura_janela = glfw.get_window_size(window)[1]
            rato_y_opengl = altura_janela - glfw.get_cursor_pos(window)[1]
            
            if action == glfw.PRESS and menu_creditos is not None:
                acao = menu_creditos.processar_mouse(rato_x, rato_y_opengl, action)
                if acao == 'voltar':
                    estado_jogo_atual = estado_anterior if estado_anterior is not None else ESTADO_MENU

    # Não é necessário fazer nada para RELEASE do botão do mouse
    elif action == glfw.RELEASE:
        # Verificar se está no menu de configurações e ajustar volume
        if estado_jogo_atual == ESTADO_CONFIGURACOES and menu_configuracoes is not None:
            if menu_configuracoes.volume_ajustando:
                menu_configuracoes.volume_ajustando = False

def verificar_colisoes_tiros():
    """Verifica colisões entre tiros e alvos"""
    global score, lista_tiros, lista_alvos
    
    tiros_para_remover = []
    
    # Índices dos tiros a serem removidos
    indices_tiros_remover = []
    
    for i, tiro in enumerate(lista_tiros):
        for j, alvo in enumerate(lista_alvos):
            if alvo['visivel']:
                # Calcula a distância entre o tiro e o alvo
                distancia = np.linalg.norm(tiro['pos'] - alvo['pos'])
                
                # Verifica se há colisão (soma dos raios)
                if distancia <= (tiro['raio'] + alvo['raio']):
                    # Colisão detectada!
                    lista_alvos[j]['visivel'] = False
                    lista_alvos[j]['tempo_atingido'] = glfw.get_time()
                    score += 1
                    
                    # Marca o índice do tiro para remoção
                    if i not in indices_tiros_remover:
                        indices_tiros_remover.append(i)
                    break
    
    # Remove tiros que colidiram (do fim para o início para evitar problemas de índice)
    for indice in sorted(indices_tiros_remover, reverse=True):
        lista_tiros.pop(indice)

def desenhar_tiros():
    """Desenha todos os tiros ativos como notas musicais"""
    # Salva o estado atual do OpenGL
    glPushAttrib(GL_ALL_ATTRIB_BITS)

    tempo_atual = glfw.get_time()
    indices_tiros_remover = []
    
    for i, tiro in enumerate(lista_tiros):
        # Atualiza a posição do tiro
        tempo_vida = tempo_atual - tiro['tempo_criacao']
        if tempo_vida > 4.0:  # Remove tiros após 4 segundos
            indices_tiros_remover.append(i)
            continue
            
        # Calcula nova posição com velocidade mais lenta
        velocidade_tiro = 1.5  # Velocidade reduzida para melhor controle
        nova_pos = tiro['pos'] + tiro['direcao'] * tempo_vida * velocidade_tiro
        
        # Atualiza a posição do tiro
        tiro['pos'] = nova_pos
        
        # Desenha a nota musical baseada no contador de disparos
        glPushMatrix()
        glTranslatef(nova_pos[0], nova_pos[1], nova_pos[2])
        from draw import contador_disparos
        tipo_nota = contador_disparos % 5
        if tipo_nota == 0:
            desenhar_clave_sol(raio=tiro['raio'] * 1.2)
        elif tipo_nota == 1:
            desenhar_colcheia(raio=tiro['raio'] * 1.2)
        elif tipo_nota == 2:
            desenhar_par_colcheias(raio=tiro['raio'] * 1.2)
        elif tipo_nota == 3:
            desenhar_semicolcheia(raio=tiro['raio'] * 1.2)
        else:
            desenhar_seminima(raio=tiro['raio'] * 1.2)
        glPopMatrix()
        
        # Desenha a sombra da nota musical no chão
        if SOMBRAS_HABILITADAS:
            glPushMatrix()
            glDisable(GL_LIGHTING)
            
            # Define a cor da sombra
            glColor4f(0.0, 0.0, 0.0, 0.4)
            
            # Habilita blending para transparência
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            # Evitar z-fighting
            glEnable(GL_POLYGON_OFFSET_FILL)
            glPolygonOffset(-1.0, -1.0)
            
            # Projeta a sombra no chão
            glTranslatef(nova_pos[0], -ALTURA_SALA/2 + 0.01, nova_pos[2])
            glScalef(1.0, 0.01, 1.0)  # Achata a sombra mais ainda
            
            # Desenha um disco como sombra
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(0, 0, 0)
            for ang in range(0, 360, 20):
                x = tiro['raio'] * 1.5 * math.cos(math.radians(ang))
                z = tiro['raio'] * 1.5 * math.sin(math.radians(ang))
                glVertex3f(x, 0, z)
            glVertex3f(tiro['raio'] * 1.5, 0, 0)  # Fecha o círculo
            glEnd()
            
            glDisable(GL_POLYGON_OFFSET_FILL)
            
        glPopMatrix()
    
    # Remove tiros antigos (do fim para o início)
    for indice in sorted(indices_tiros_remover, reverse=True):
        lista_tiros.pop(indice)
    
    # Verifica colisões após atualizar posições
    verificar_colisoes_tiros()

    # Restaura o estado anterior do OpenGL
    glPopAttrib()

def verificar_colisao_parede(nova_pos):
    """Verifica se a nova posição colide com as paredes da sala"""
    # Limites da sala com margem de segurança
    limite_x_min = -LARGURA_SALA/2 + MARGEM_COLISAO
    limite_x_max = LARGURA_SALA/2 - MARGEM_COLISAO
    limite_z_min = -PROFUNDIDADE_SALA/2 + MARGEM_COLISAO
    limite_z_max = PROFUNDIDADE_SALA/2 - MARGEM_COLISAO
    
    # Verifica colisão com as paredes
    if nova_pos[0] < limite_x_min: nova_pos[0] = limite_x_min
    if nova_pos[0] > limite_x_max: nova_pos[0] = limite_x_max
    if nova_pos[2] < limite_z_min: nova_pos[2] = limite_z_min
    if nova_pos[2] > limite_z_max: nova_pos[2] = limite_z_max
    
    return nova_pos

def ajustar_posicao_camera_terceira_pessoa(pos_jogador, direcao_camera, distancia_camera):
    """Ajusta a posição da câmera em terceira pessoa para evitar atravessar paredes"""
    # Calcula a posição ideal da câmera
    pos_ideal = pos_jogador - direcao_camera * distancia_camera
    
    # Limites da sala com margem de segurança para a câmera
    limite_x_min = -LARGURA_SALA/2 + 1.0  # Margem maior para a câmera
    limite_x_max = LARGURA_SALA/2 - 1.0
    limite_z_min = -PROFUNDIDADE_SALA/2 + 1.0
    limite_z_max = PROFUNDIDADE_SALA/2 - 1.0
    # Limites verticais com margem de segurança
    limite_y_min = -ALTURA_SALA/2 + 1.0  # Evita que a câmera vá muito abaixo
    limite_y_max = ALTURA_SALA/2 - 1.0   # Evita que a câmera vá muito acima
    
    # Ajusta a posição da câmera se necessário
    if pos_ideal[0] < limite_x_min:
        # Calcula nova posição mantendo a direção relativa ao jogador
        pos_ideal[0] = limite_x_min
        # Ajusta Z para manter a proporção da direção
        if abs(direcao_camera[0]) > 0.0001:  # Evita divisão por zero
            pos_ideal[2] = pos_jogador[2] + (pos_ideal[0] - pos_jogador[0]) * (direcao_camera[2] / direcao_camera[0])
    
    if pos_ideal[0] > limite_x_max:
        pos_ideal[0] = limite_x_max
        if abs(direcao_camera[0]) > 0.0001:
            pos_ideal[2] = pos_jogador[2] + (pos_ideal[0] - pos_jogador[0]) * (direcao_camera[2] / direcao_camera[0])
    
    if pos_ideal[2] < limite_z_min:
        pos_ideal[2] = limite_z_min
        if abs(direcao_camera[2]) > 0.0001:
            pos_ideal[0] = pos_jogador[0] + (pos_ideal[2] - pos_jogador[2]) * (direcao_camera[0] / direcao_camera[2])
    
    if pos_ideal[2] > limite_z_max:
        pos_ideal[2] = limite_z_max
        if abs(direcao_camera[2]) > 0.0001:
            pos_ideal[0] = pos_jogador[0] + (pos_ideal[2] - pos_jogador[2]) * (direcao_camera[0] / direcao_camera[2])
    
    # Ajusta a altura da câmera se necessário
    if pos_ideal[1] < limite_y_min:
        pos_ideal[1] = limite_y_min
    if pos_ideal[1] > limite_y_max:
        pos_ideal[1] = limite_y_max
    
    return pos_ideal

def configurar_iluminacao():
    """Configura a iluminação da sala com uma luz no teto e luzes nos cantos"""
    if LUZ_HABILITADA:
        glEnable(GL_LIGHTING)
        
        # Configura a luz central
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, POSICAO_LUZ)
        glLightfv(GL_LIGHT0, GL_AMBIENT, COR_LUZ_AMBIENTE)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, COR_LUZ_DIFUSA)
        glLightfv(GL_LIGHT0, GL_SPECULAR, COR_LUZ_ESPECULAR)
        
        # Configura as luzes dos cantos se estiverem habilitadas
        if LUZES_CANTOS_HABILITADAS:
            # Canto superior frontal esquerdo
            posicao_luz1 = [-LARGURA_SALA/2 + 1.0, ALTURA_SALA/2 - 0.5, -PROFUNDIDADE_SALA/2 + 1.0, 1.0]
            glEnable(GL_LIGHT1)
            glLightfv(GL_LIGHT1, GL_POSITION, posicao_luz1)
            glLightfv(GL_LIGHT1, GL_AMBIENT, COR_LUZ_CANTO_AMBIENTE)
            glLightfv(GL_LIGHT1, GL_DIFFUSE, COR_LUZ_CANTO_DIFUSA)
            glLightfv(GL_LIGHT1, GL_SPECULAR, COR_LUZ_CANTO_ESPECULAR)
            
            # Canto superior frontal direito
            posicao_luz2 = [LARGURA_SALA/2 - 1.0, ALTURA_SALA/2 - 0.5, -PROFUNDIDADE_SALA/2 + 1.0, 1.0]
            glEnable(GL_LIGHT2)
            glLightfv(GL_LIGHT2, GL_POSITION, posicao_luz2)
            glLightfv(GL_LIGHT2, GL_AMBIENT, COR_LUZ_CANTO_AMBIENTE)
            glLightfv(GL_LIGHT2, GL_DIFFUSE, COR_LUZ_CANTO_DIFUSA)
            glLightfv(GL_LIGHT2, GL_SPECULAR, COR_LUZ_CANTO_ESPECULAR)
            
            # Canto superior traseiro esquerdo
            posicao_luz3 = [-LARGURA_SALA/2 + 1.0, ALTURA_SALA/2 - 0.5, PROFUNDIDADE_SALA/2 - 1.0, 1.0]
            glEnable(GL_LIGHT3)
            glLightfv(GL_LIGHT3, GL_POSITION, posicao_luz3)
            glLightfv(GL_LIGHT3, GL_AMBIENT, COR_LUZ_CANTO_AMBIENTE)
            glLightfv(GL_LIGHT3, GL_DIFFUSE, COR_LUZ_CANTO_DIFUSA)
            glLightfv(GL_LIGHT3, GL_SPECULAR, COR_LUZ_CANTO_ESPECULAR)
            
            # Canto superior traseiro direito
            posicao_luz4 = [LARGURA_SALA/2 - 1.0, ALTURA_SALA/2 - 0.5, PROFUNDIDADE_SALA/2 - 1.0, 1.0]
            glEnable(GL_LIGHT4)
            glLightfv(GL_LIGHT4, GL_POSITION, posicao_luz4)
            glLightfv(GL_LIGHT4, GL_AMBIENT, COR_LUZ_CANTO_AMBIENTE)
            glLightfv(GL_LIGHT4, GL_DIFFUSE, COR_LUZ_CANTO_DIFUSA)
            glLightfv(GL_LIGHT4, GL_SPECULAR, COR_LUZ_CANTO_ESPECULAR)
        
        glEnable(GL_COLOR_MATERIAL)
        
        # Configura o modelo de sombreamento
        glShadeModel(GL_SMOOTH)
        
        # Habilitar luz para materiais
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)
    else:
        glDisable(GL_LIGHTING)

def desenhar_sombra(modelo_jogador, posicao, escala, rotacao_y=0):
    """Desenha a sombra de um modelo no chão usando projeção de sombra"""
    if not SOMBRAS_HABILITADAS:
        return
        
    # Salva o estado atual
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    glPushMatrix()
    
    # Desabilita iluminação para a sombra
    glDisable(GL_LIGHTING)
    
    # Define a cor da sombra (preto semi-transparente)
    glColor4f(0.0, 0.0, 0.0, 0.5)
    
    # Habilita blending para transparência
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Offset para evitar z-fighting
    glEnable(GL_POLYGON_OFFSET_FILL)
    glPolygonOffset(-1.0, -1.0)
    
    # Usa a posição Y mínima da sala como plano para sombra (chão)
    y_chao = -ALTURA_SALA/2 + 0.01  # Levemente acima do chão para evitar z-fighting
    
    # Aplica transformações diretamente para projetar no chão
    glTranslatef(posicao[0], y_chao, posicao[2])
    glRotatef(-yaw + 90.0 + rotacao_y, 0.0, 1.0, 0.0)
    
    # Aplica escala para a sombra, achatando-a no plano Y
    glScalef(escala, 0.01, escala)
    
    # Desenha o modelo como sombra
    draw_obj_model(modelo_jogador)
    
    # Restaura o estado anterior
    glDisable(GL_POLYGON_OFFSET_FILL)
    glPopMatrix()
    glPopAttrib()

def key_callback(window, key, scancode, action, mods):
    """Manipula eventos de teclado do jogo"""
    global estado_jogo_atual, estado_anterior, tempo_pausa_inicio, movement_keys
    global is_jumping, jump_velocity, is_crouching
    global is_transitioning_crouch, transition_start_height, transition_target_height, crouch_transition_timer
    global first_mouse, tempo_total_pausado
    
    # Processa eventos de tecla pressionada e repetida
    if action == glfw.PRESS or action == glfw.REPEAT:
        # Tratamento da tecla ESC em diferentes estados
        if key == glfw.KEY_ESCAPE:
            if estado_jogo_atual == ESTADO_MENU:
                # No menu principal, a tecla ESC fecha o jogo
                glfw.set_window_should_close(window, True)
            elif estado_jogo_atual == ESTADO_MENU_DIFICULDADE:
                # Volta para o menu principal
                estado_jogo_atual = ESTADO_MENU
            elif estado_jogo_atual == ESTADO_MENU_NIVEIS:
                # Volta para o menu de dificuldade
                estado_jogo_atual = ESTADO_MENU_DIFICULDADE
            elif estado_jogo_atual == ESTADO_JOGANDO:
                # Pausa o jogo
                estado_jogo_atual = ESTADO_PAUSADO
                tempo_pausa_inicio = glfw.get_time()
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            elif estado_jogo_atual == ESTADO_VITORIA or estado_jogo_atual == ESTADO_DERROTA:
                # Volta para o menu principal
                estado_jogo_atual = ESTADO_MENU
            elif estado_jogo_atual == ESTADO_CONFIGURACOES:
                # Volta para o estado anterior ou menu principal
                estado_jogo_atual = estado_anterior if estado_anterior is not None else ESTADO_MENU
                config_manager.save_config()
            elif estado_jogo_atual == ESTADO_PAUSADO:
                # Retorna para o jogo
                estado_jogo_atual = ESTADO_JOGANDO
                tempo_total_pausado += glfw.get_time() - tempo_pausa_inicio
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                first_mouse = True
            elif estado_jogo_atual == ESTADO_FIM_DESAFIO:
                # Volta para o menu principal
                gerenciador_niveis.desativar_modo_desafio()
                estado_jogo_atual = ESTADO_MENU
        
        # Tratamento para o menu de vitória
        elif estado_jogo_atual == ESTADO_VITORIA:
            # Processa as teclas de navegação no menu de vitória
            acao = menu_vitoria.processar_teclado(key)
            if acao == 'proximo':
                # Avança para o próximo nível
                if gerenciador_niveis.proximo_nivel():
                    estado_jogo_atual = ESTADO_JOGANDO
                    reiniciar_jogo()
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                    first_mouse = True
                    pygame.mixer.music.stop()
                else:
                    # Se não houver próximo nível, volta ao menu de níveis
                    estado_jogo_atual = ESTADO_MENU_NIVEIS
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            elif acao == 'replay':
                # Reinicia o nível atual
                estado_jogo_atual = ESTADO_JOGANDO
                reiniciar_jogo()
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                first_mouse = True
                pygame.mixer.music.stop()
            elif acao == 'niveis':
                # Vai para o menu de seleção de níveis
                estado_jogo_atual = ESTADO_MENU_NIVEIS
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            elif acao == 'dificuldade':
                # Vai para o menu de seleção de dificuldade
                estado_jogo_atual = ESTADO_MENU_DIFICULDADE
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            elif acao == 'menu':
                # Volta para o menu principal
                estado_jogo_atual = ESTADO_MENU
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
        
        # Tratamento para o menu de derrota
        elif estado_jogo_atual == ESTADO_DERROTA:
            # Processa as teclas de navegação no menu de derrota
            acao = menu_derrota.processar_teclado(key)
            if acao == 'replay':
                # Reinicia o nível atual
                estado_jogo_atual = ESTADO_JOGANDO
                reiniciar_jogo()
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                first_mouse = True
                pygame.mixer.music.stop()
            elif acao == 'dificuldade':
                # Vai para o menu de seleção de dificuldade
                estado_jogo_atual = ESTADO_MENU_DIFICULDADE
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            elif acao == 'menu':
                # Volta para o menu principal
                estado_jogo_atual = ESTADO_MENU
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
                
            elif estado_jogo_atual == ESTADO_CREDITOS:
                # Volta para o estado anterior ou menu principal
                estado_jogo_atual = estado_anterior if estado_anterior is not None else ESTADO_MENU
        
        # Tratamento para o menu de fim desafio
        elif estado_jogo_atual == ESTADO_FIM_DESAFIO:
            # Processa as teclas de navegação no menu de fim de desafio
            acao = menu_fim_desafio.processar_teclado(key)
            if acao == 'replay':
                # Reinicia o desafio especial
                gerenciador_niveis.ativar_modo_desafio()
                estado_jogo_atual = ESTADO_JOGANDO
                reiniciar_jogo()
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                first_mouse = True
                pygame.mixer.music.stop() # Para a música ao entrar no jogo
            elif acao == 'niveis':
                # Desativa o modo desafio e vai para o menu de níveis
                gerenciador_niveis.desativar_modo_desafio()
                estado_jogo_atual = ESTADO_MENU_NIVEIS
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            elif acao == 'dificuldade':
                # Desativa o modo desafio e vai para o menu de dificuldade
                gerenciador_niveis.desativar_modo_desafio()
                estado_jogo_atual = ESTADO_MENU_DIFICULDADE
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            elif acao == 'menu':
                # Desativa o modo desafio e volta para o menu principal
                gerenciador_niveis.desativar_modo_desafio()
                estado_jogo_atual = ESTADO_MENU
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)

        # Teclas de movimento (para o estado JOGANDO)
        if estado_jogo_atual == ESTADO_JOGANDO:
            # Movimento para frente/trás/esquerda/direita
            if key == glfw.KEY_W:
                movement_keys['forward'] = True
            elif key == glfw.KEY_S:
                movement_keys['backward'] = True
            elif key == glfw.KEY_A:
                movement_keys['left'] = True
            elif key == glfw.KEY_D:
                movement_keys['right'] = True
                
            # Pulo (Space)
            elif key == glfw.KEY_SPACE and not is_jumping:
                is_jumping = True
                jump_velocity = initial_jump_velocity
                
            # Agachamento (Ctrl)
            elif key == glfw.KEY_LEFT_CONTROL:
                if not is_crouching:
                    is_crouching = True
                    is_transitioning_crouch = True
                    transition_start_height = camera_pos[1]
                    transition_target_height = camera_pos_inicial[1] - crouch_height_offset
                    crouch_transition_timer = 0.0
                    
            # Corrida (Shift)
            elif key == glfw.KEY_LEFT_SHIFT:
                movement_keys['sprint'] = True
                
    # Processa eventos de tecla liberada
    elif action == glfw.RELEASE:
        if estado_jogo_atual == ESTADO_JOGANDO:
            # Movimento para frente/trás/esquerda/direita
            if key == glfw.KEY_W:
                movement_keys['forward'] = False
            elif key == glfw.KEY_S:
                movement_keys['backward'] = False
            elif key == glfw.KEY_A:
                movement_keys['left'] = False
            elif key == glfw.KEY_D:
                movement_keys['right'] = False
                
            # Agachamento (Ctrl)
            elif key == glfw.KEY_LEFT_CONTROL:
                if is_crouching:
                    is_crouching = False
                    is_transitioning_crouch = True
                    transition_start_height = camera_pos[1]
                    transition_target_height = camera_pos_inicial[1]
                    crouch_transition_timer = 0.0
                    
            # Corrida (Shift)
            elif key == glfw.KEY_LEFT_SHIFT:
                movement_keys['sprint'] = False

def main():
    global menu_principal, menu_vitoria, menu_derrota, menu_dificuldade, menu_configuracoes, menu_niveis, menu_pausa, menu_fim_desafio, menu_creditos
    global gerenciador_niveis
    global textura_fundo, textura_chao, tempo_restante, estado_jogo_atual, lista_tiros
    global is_jumping, jump_velocity, last_frame_time
    global textura_titulo
    global textura_trompete
    global textura_baixo
    global textura_trombone
    global textura_vibrafone
    global textura_extra
    global camera_pos, camera_front, camera_up, yaw, pitch, first_mouse
    global is_transitioning_crouch, crouch_transition_timer, transition_start_height, transition_target_height
    global obj_vibrafone_geometry
    global obj_vibrafone_texture
    global obj_trompete_geometry
    global obj_baixo_geometry
    global obj_trombone_geometry
    global obj_bateria_geometry
    global third_person_camera_pos
    global tempo_pausa_inicio, tempo_total_pausado
    global LUZES_CANTOS_HABILITADAS

    # Inicializa o GLFW primeiro
    if not glfw.init():
        print("Erro ao inicializar GLFW")
        return
    
    # Inicializa o tempo do último frame
    last_frame_time = glfw.get_time()
    
    # Inicializa as variáveis da câmera
    camera_pos = np.copy(camera_pos_inicial)
    camera_front = np.copy(camera_front_inicial)
    camera_up = np.copy(camera_up_inicial)
    yaw = yaw_inicial
    pitch = pitch_inicial
    first_mouse = True
    
    # Carregar configuração das luzes dos cantos
    LUZES_CANTOS_HABILITADAS = config_manager.get_enable_corner_lights()
    
    # Carregar o modelo do vibrafone
    obj_vibrafone_geometry = ObjReader("vibrafone.obj") # Carregar o arquivo OBJ
    if obj_vibrafone_geometry.vertex_count() == 0:
        print("Erro ao carregar o modelo vibrafone.obj")
        # Decida se quer sair ou continuar sem o modelo
        # glfw.terminate()
        # return

    # Carregar o modelo do trompete
    obj_trompete_geometry = ObjReader("trompete.obj") # Carregar o arquivo OBJ
    if obj_trompete_geometry.vertex_count() == 0:
        print("Erro ao carregar o modelo trompete.obj")
        # Decida se quer sair ou continuar sem o modelo
        # glfw.terminate()
        # return
        
    # Carregar o modelo do baixo
    obj_baixo_geometry = ObjReader("baixo.obj") # Carregar o arquivo OBJ
    if obj_baixo_geometry.vertex_count() == 0:
        print("Erro ao carregar o modelo baixo.obj")
        # Decida se quer sair ou continuar sem o modelo
        # glfw.terminate()
        # return
    
    # Carregar o modelo do trombone
    obj_trombone_geometry = ObjReader("trombone.obj") # Carregar o arquivo OBJ
    if obj_trombone_geometry.vertex_count() == 0:
        print("Erro ao carregar o modelo trombone.obj")
        # Decida se quer sair ou continuar sem o modelo
        # glfw.terminate()
        # return
    
    # Carregar o modelo da bateria
    obj_bateria_geometry = ObjReader("Bateria.obj") # Carregar o arquivo OBJ
    if obj_bateria_geometry.vertex_count() == 0:
        print("Erro ao carregar o modelo Bateria.obj")
        # Decida se quer sair ou continuar sem o modelo
        # glfw.terminate()
        # return
    
    # Carregar música de fundo (não inicia a reprodução aqui)
    musica_carregada = False
    try:
        pygame.mixer.music.load('audio/musica_menu.mp3') # Caminho para o arquivo de música
        pygame.mixer.music.set_volume(config_manager.get_volume()) # Aplica o volume das configurações
        musica_carregada = True
    except pygame.error as e:
        print(f"Erro ao carregar música: {e}")

    # Carregar sons das notas de trompete
    global sons_trompete, indice_som_trompete
    sons_trompete = []
    indice_som_trompete = 0
    notas = ['do', 're', 'mi', 'fa', 'sol', 'la', 'si', 'do2']
    for nota in notas:
        try:
            som = pygame.mixer.Sound(f'notas_trompete/{nota}.mp3')
            sons_trompete.append(som)
        except pygame.error as e:
            print(f"Erro ao carregar som {nota}.mp3: {e}")

    # Carregar sons das notas de vibrafone
    global sons_vibrafone, indice_som_vibrafone
    sons_vibrafone = []
    indice_som_vibrafone = 0
    notas_vibrafone = ['do', 're', 'mi', 'fa', 'sol', 'la', 'si', 'do2'] # Assumindo os mesmos nomes de nota
    for nota in notas_vibrafone:
        try:
            som = pygame.mixer.Sound(f'notas_vibrafone/{nota}.mp3')
            sons_vibrafone.append(som)
        except pygame.error as e:
            print(f"Erro ao carregar som do vibrafone {nota}.mp3: {e}")
            
    # Carregar sons das notas de baixo
    global sons_baixo, indice_som_baixo
    sons_baixo = []
    indice_som_baixo = 0
    notas_baixo = ['do', 're', 'mi', 'fa', 'sol', 'la', 'si', 'do2'] # Assumindo os mesmos nomes de nota
    for nota in notas_baixo:
        try:
            som = pygame.mixer.Sound(f'notas_baixo/{nota}.mp3')
            sons_baixo.append(som)
        except pygame.error as e:
            print(f"Erro ao carregar som do baixo {nota}.mp3: {e}")
    
    # Carregar sons das notas de trombone
    global sons_trombone, indice_som_trombone
    sons_trombone = []
    indice_som_trombone = 0
    notas_trombone = ['do', 're', 'mi', 'fa', 'sol', 'la', 'si', 'do2'] # Assumindo os mesmos nomes de nota
    for nota in notas_trombone:
        try:
            som = pygame.mixer.Sound(f'notas_trombone/{nota}.mp3')
            sons_trombone.append(som)
        except pygame.error as e:
            print(f"Erro ao carregar som do trombone {nota}.mp3: {e}")
            
    # Carregar sons das notas de bateria
    global sons_bateria, indice_som_bateria
    sons_bateria = []
    indice_som_bateria = 0
    notas_bateria = ['do', 'mi', 'fa', 'la', 'do2'] # Assumindo os mesmos nomes de nota
    for nota in notas_bateria:
        try:
            som = pygame.mixer.Sound(f'notas_bateria/{nota}.mp3')
            sons_bateria.append(som)
        except pygame.error as e:
            print(f"Erro ao carregar som da bateria {nota}.mp3: {e}")
    
    # Obtém o monitor primário
    monitor = glfw.get_primary_monitor()
    modo_video = glfw.get_video_mode(monitor)
    
    # Usa as dimensões do monitor para criar a janela em tela cheia
    largura_janela = modo_video.size.width
    altura_janela = modo_video.size.height
    
    # Cria a janela em tela cheia
    window = glfw.create_window(largura_janela, altura_janela, TITULO_JOGO, monitor, None)
    if not window:
        print("Erro ao criar janela GLFW")
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    
    # Carrega as texturas
    textura_fundo = carregar_textura("images/background.jpg")
    textura_chao = carregar_textura("images/floor.jpg")
    textura_titulo = carregar_textura("images/titulo.png")
    textura_trompete = carregar_textura("images/texture.jpg")  # Carrega a textura do trompete
    textura_baixo = carregar_textura("baixo.jpg")  # Carrega a textura do baixo
    textura_trombone = carregar_textura("trombone.png")  # Carrega a textura do trombone
    textura_vibrafone = carregar_textura("vibrafone.png")  # Carrega a textura do vibrafone
    textura_extra = carregar_textura("images/textura_extra.jpg")  # Carrega a textura extra
    
    # Verifica se a textura do baixo foi carregada corretamente
    if textura_baixo:
        print("Textura do baixo carregada com sucesso! ID:", textura_baixo)
    else:
        print("ERRO: Falha ao carregar a textura do baixo!")
    
    # Verifica se a textura do trombone foi carregada corretamente
    if textura_trombone:
        print("Textura do trombone carregada com sucesso! ID:", textura_trombone)
    else:
        print("ERRO: Falha ao carregar a textura do trombone!")
    
        # Verifica se a textura do vibrafone foi carregada corretamente
    if textura_vibrafone:
        print("Textura do vibrafone carregada com sucesso! ID:", textura_vibrafone)
    else:
        print("ERRO: Falha ao carregar a textura do vibrafone!")
    
    # Passar o config_manager e texturas para os menus que precisam deles
    menu_principal = MenuPrincipal(text_renderer, textura_titulo)
    menu_vitoria = MenuVitoria(text_renderer, textura_titulo)
    menu_derrota = MenuDerrota(text_renderer, textura_titulo)
    menu_dificuldade = MenuDificuldade(text_renderer, textura_titulo)
    menu_configuracoes = MenuConfiguracoes(text_renderer, config_manager, textura_titulo)
    menu_niveis = MenuNiveis(text_renderer, textura_titulo)  # Inicializa o menu de níveis
    print(f"Debug: menu_niveis inicializado: {menu_niveis is not None}")

    # Inicializa o menu de pausa
    menu_pausa = MenuPausa(text_renderer, textura_titulo)
    
    # Inicializa o menu de fim do desafio
    menu_fim_desafio = MenuFimDesafio(text_renderer, textura_titulo)
    
    # Inicializa o menu de créditos
    menu_creditos = MenuCreditos(text_renderer, textura_titulo)

    glfw.set_key_callback(window, key_callback)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    
    if estado_jogo_atual == ESTADO_MENU:
        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
    else:
        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        reiniciar_jogo()
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Habilita cálculo de normais para iluminação
    glEnable(GL_NORMALIZE)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    while not glfw.window_should_close(window):
        # Calcula o delta time
        current_time = glfw.get_time()
        delta_time = current_time - last_frame_time
        last_frame_time = current_time
        
        # Verifica se estamos em um estado de menu e desabilita iluminação
        if estado_jogo_atual in [ESTADO_MENU, ESTADO_MENU_DIFICULDADE, ESTADO_MENU_NIVEIS, 
                                ESTADO_VITORIA, ESTADO_DERROTA, ESTADO_CONFIGURACOES, ESTADO_CREDITOS]:
            glDisable(GL_LIGHTING)
        
        glfw.poll_events()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Atualiza o movimento
        if estado_jogo_atual == ESTADO_JOGANDO:
            camera_right = np.cross(camera_front, camera_up)
            camera_right = camera_right / np.linalg.norm(camera_right)
            
            # Cria um vetor de direção para frente que é sempre horizontal
            forward_direction = np.array([camera_front[0], 0, camera_front[2]])
            if np.linalg.norm(forward_direction) > 0:
                forward_direction = forward_direction / np.linalg.norm(forward_direction)
            
            # Calcula a nova posição baseada no movimento horizontal
            nova_pos = np.copy(camera_pos)
            
            # Determina a velocidade atual baseada no estado de corrida
            velocidade_atual = sprint_speed if movement_keys['sprint'] else movement_speed
            
            # Aplica o movimento baseado nas teclas pressionadas, mantendo no plano horizontal
            if movement_keys['forward']: 
                nova_pos[0] += forward_direction[0] * velocidade_atual * delta_time
                nova_pos[2] += forward_direction[2] * velocidade_atual * delta_time
            if movement_keys['backward']: 
                nova_pos[0] -= forward_direction[0] * velocidade_atual * delta_time
                nova_pos[2] -= forward_direction[2] * velocidade_atual * delta_time
            if movement_keys['left']: 
                nova_pos[0] -= camera_right[0] * velocidade_atual * delta_time
                nova_pos[2] -= camera_right[2] * velocidade_atual * delta_time
            if movement_keys['right']: 
                nova_pos[0] += camera_right[0] * velocidade_atual * delta_time
                nova_pos[2] += camera_right[2] * velocidade_atual * delta_time
            
            # Verifica colisão com as paredes
            nova_pos = verificar_colisao_parede(nova_pos)
            
            # --- Lógica de Transição de Agachamento Suave ---
            if is_transitioning_crouch:
                crouch_transition_timer += delta_time
                progress = min(crouch_transition_timer / crouch_transition_duration, 1.0)
                
                # Interpolação suave (usando easing in-out com uma função cúbica)
                # progress_eased = progress * progress * (3 - 2 * progress)
                # Interpolação linear simples para começar
                progress_eased = progress
                
                current_crouch_height = transition_start_height + (transition_target_height - transition_start_height) * progress_eased
                nova_pos[1] = current_crouch_height # Aplica a altura interpolada à nova posição
                
                if progress >= 1.0:
                    is_transitioning_crouch = False
                    crouch_transition_timer = 0.0
                    # Garante que a altura final é exatamente a alvo
                    nova_pos[1] = transition_target_height
            else:
                # Se não estiver em transição, a altura é a posição atual da câmera (para o pulo, por exemplo)
                nova_pos[1] = camera_pos[1]
            
            # Atualiza a posição da câmera com a nova_pos (incluindo a altura interpolada ou a altura do pulo)
            camera_pos = nova_pos
            
            # Atualiza a posição do pulo (apenas a velocidade vertical é afetada pela gravidade aqui)
            if is_jumping:
                jump_velocity -= gravity * delta_time
                camera_pos[1] += jump_velocity * delta_time # Aplica a velocidade do pulo na altura da câmera
                
                # Verifica se chegou ao chão
                if camera_pos[1] <= camera_pos_inicial[1]:
                    camera_pos[1] = camera_pos_inicial[1]
                    is_jumping = False
                    jump_velocity = 0.0
                    # Garante que se o jogador aterrissar enquanto agachado, a altura seja a de agachado
                    if is_crouching:
                         camera_pos[1] = camera_pos_inicial[1] - crouch_height_offset
        
        if estado_jogo_atual == ESTADO_MENU:
            # Desabilita iluminação para o menu
            glDisable(GL_LIGHTING)
            menu_principal.desenhar(largura_janela, altura_janela)
        elif estado_jogo_atual == ESTADO_MENU_DIFICULDADE:
            # Desabilita iluminação para o menu
            glDisable(GL_LIGHTING)
            menu_dificuldade.desenhar(largura_janela, altura_janela)
        elif estado_jogo_atual == ESTADO_MENU_NIVEIS:
            # Desabilita iluminação para o menu
            glDisable(GL_LIGHTING)
            menu_niveis.desenhar(largura_janela, altura_janela)
        elif estado_jogo_atual == ESTADO_JOGANDO:
            # Habilita iluminação para o jogo
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            desenhar_fundo_estetico()
            # Atualiza o tempo restante
            nivel_atual = gerenciador_niveis.obter_nivel_atual()
            tempo_atual = glfw.get_time()
            tempo_restante = nivel_atual.tempo_limite - (tempo_atual - tempo_inicio_nivel - tempo_total_pausado)
            
            # Verifica condições de vitória/derrota
            if gerenciador_niveis.esta_em_modo_desafio():
                # No modo desafio, só termina quando o tempo acaba
                if tempo_restante <= 0:
                    # Atualiza o highscore se necessário
                    gerenciador_niveis.atualizar_highscore(score)
                    estado_jogo_atual = ESTADO_FIM_DESAFIO
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            else:
                # Modo normal
                if score >= nivel_atual.alvos_necessarios:
                    estado_jogo_atual = ESTADO_VITORIA
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
                elif tempo_restante <= 0:
                    estado_jogo_atual = ESTADO_DERROTA
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            
        nova_largura, nova_altura = glfw.get_window_size(window)
        if nova_largura != largura_janela or nova_altura != altura_janela:
            largura_janela, altura_janela = nova_largura, nova_altura
            glViewport(0, 0, largura_janela, altura_janela)
        
        if estado_jogo_atual == ESTADO_MENU:
            # Desabilita iluminação para o menu
            glDisable(GL_LIGHTING)
            menu_principal.desenhar(largura_janela, altura_janela)
        elif estado_jogo_atual == ESTADO_MENU_DIFICULDADE:
            # Desabilita iluminação para o menu
            glDisable(GL_LIGHTING)
            menu_dificuldade.desenhar(largura_janela, altura_janela)
        elif estado_jogo_atual == ESTADO_MENU_NIVEIS:
            # Desabilita iluminação para o menu
            glDisable(GL_LIGHTING)
            menu_niveis.desenhar(largura_janela, altura_janela)
        elif estado_jogo_atual == ESTADO_JOGANDO:
            # --- Configuração da Câmera em Terceira Pessoa ---
            # Distância da câmera atrás e acima do jogador
            nivel_atual = gerenciador_niveis.obter_nivel_atual()

            # Define a distância da câmera e o offset de altura com base no nível
            if nivel_atual.numero == 1:
                camera_distance_behind = 4.0
                camera_height_offset = 0.5
            elif nivel_atual.numero == 2:
                camera_distance_behind = 6.0 # Mais atrás para o vibrafone
                camera_height_offset = 0.5 # Mais baixo para o vibrafone
            elif nivel_atual.numero == 3:
                camera_distance_behind = 5.5 # Aumenta a distância para o trombone
                camera_height_offset = 0.25 # Ajusta a altura para melhor visualização
            elif nivel_atual.numero == 4:
                camera_distance_behind = 3.0 # Distância reduzida para o baixo
                camera_height_offset = 0.5 # Altura ajustada para o baixo
            elif nivel_atual.numero >= 5:
                camera_distance_behind = 7.5 # Aumentado de 5.0 para 6.5 para afastar mais a câmera
                camera_height_offset = 1.0 # Aumentado de 0.5 para 1.0 para elevar a câmera

            # Offset de altura da câmera, depende do modelo do jogador (nível)
            camera_height_offset = 1.0 # Offset padrão para o trompete (Nível 1)
            if nivel_atual.numero == 2:
                camera_height_offset = -2.5 # Offset para o vibrafone (Nível 2)
            elif nivel_atual.numero == 3:
                camera_height_offset = 0.5 # Offset ajustado para o trombone (Nível 3)
            elif nivel_atual.numero == 4:
                camera_height_offset = -1.0 # Offset ajustado para o baixo (Nível 4)
            elif nivel_atual.numero >= 5:
                camera_height_offset = -0.25 # Restaurado para o valor original

            # Calcula o vetor para trás baseado na direção da câmera (player)
            behind_vector = -camera_front * camera_distance_behind
            # Calcula o vetor para cima (usando o vetor 'up' global)
            above_vector = camera_up_inicial * camera_height_offset

            # Calcula a posição ideal da câmera
            pos_ideal = camera_pos + behind_vector + above_vector
            
            # Ajusta a posição da câmera para evitar atravessar paredes
            third_person_camera_pos = ajustar_posicao_camera_terceira_pessoa(
                camera_pos,
                camera_front,
                camera_distance_behind
            )
            # Mantém a altura da câmera
            third_person_camera_pos[1] = pos_ideal[1]

            # Configura a matriz de visualização (view matrix) com a posição da câmera em terceira pessoa
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(fov, (largura_janela / altura_janela), 0.1, 50.0)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            # A câmera deve olhar para a posição do jogador (onde o modelo será desenhado)
            gluLookAt(third_person_camera_pos[0], third_person_camera_pos[1], third_person_camera_pos[2],
                      camera_pos[0], camera_pos[1], camera_pos[2],
                      camera_up[0], camera_up[1], camera_up[2])

            # --- Desenho dos elementos do jogo --- #
            # Nota: Desenha a sala, alvos e tiros ANTES do player para evitar clipping
            desenhar_sala(largura=LARGURA_SALA, altura=ALTURA_SALA, profundidade=PROFUNDIDADE_SALA)

            # Lógica de reaparecimento dos alvos
            alvos_visiveis_info = [{'pos': a['pos'], 'raio': a['raio']} for a in lista_alvos if a['visivel']]
            for i in range(len(lista_alvos)):
                if not lista_alvos[i]['visivel'] and \
                   (glfw.get_time() - lista_alvos[i]['tempo_atingido'] > INTERVALO_REAPARECIMENTO_ALVO):
                    outros_alvos_info = []
                    for j, outro_alvo in enumerate(lista_alvos):
                        if i == j: continue
                        if outro_alvo['visivel']:
                             outros_alvos_info.append({'pos': outro_alvo['pos'], 'raio': outro_alvo['raio']})
                    nova_pos = gerar_posicao_alvo_aleatoria(outros_alvos_info, lista_alvos[i]['raio'])
                    lista_alvos[i]['pos'] = nova_pos
                    lista_alvos[i]['visivel'] = True
            desenhar_alvos(lista_alvos)
            desenhar_tiros()  # Desenha os tiros
            
            # --- Desenhar o Jogador --- #
            nivel_atual = gerenciador_niveis.obter_nivel_atual()
            
            # Seleciona o modelo com base no nível
            modelo_jogador = None
            escala_jogador = 1.0
            offset_jogador = np.array([0.0, 0.0, 0.0])
            textura_jogador = None
            rotacao_y_adicional = 0.0 # Rotação Y adicional em graus
            
            if nivel_atual.numero == 1 and obj_trompete_geometry and obj_trompete_geometry.vertex_count() > 0:
                modelo_jogador = obj_trompete_geometry
                escala_jogador = 2.0 / 9.0
                offset_jogador = np.array([-0.6, -0.3, -1.0])
                textura_jogador = textura_trompete
            elif nivel_atual.numero == 2 and obj_vibrafone_geometry and obj_vibrafone_geometry.vertex_count() > 0:
                modelo_jogador = obj_vibrafone_geometry
                escala_jogador = 1.0 / 9.0 # Manter a escala atual por enquanto
                # Ajusta o offset Y para que a base do vibrafone fique no chão
                # camera_pos[1] é a altura atual (geralmente camera_pos_inicial[1] ou agachado)
                # A base do chão está em -ALTURA_SALA / 2.0
                # O offset necessário é a diferença entre a altura da câmera e a altura do chão, menos um pequeno valor para ajustar
                offset_jogador = np.array([0.0, -ALTURA_SALA / 2.0 - camera_pos_inicial[1] + 0.5, -0.4]) # Offset ajustado: mais para cima
                textura_jogador = textura_extra # Usar a textura extra em vez da textura do trompete
            elif nivel_atual.numero == 3 and obj_trombone_geometry and obj_trombone_geometry.vertex_count() > 0:
                modelo_jogador = obj_trombone_geometry
                escala_jogador = 0.4 / 9.0 # Escala menor para o trombone
                offset_jogador = np.array([0.5, -0.6, 1.5])
                textura_jogador = textura_trombone
                rotacao_y_adicional = 200.0 # Rotaciona o trombone 180 graus
            elif nivel_atual.numero == 4 and obj_baixo_geometry and obj_baixo_geometry.vertex_count() > 0:
                modelo_jogador = obj_baixo_geometry
                escala_jogador = 0.025 / 9.0 # Ajuste fino da escala
                # Reposiciona o baixo para sua posição original antes das modificações
                offset_jogador = np.array([0.0, -ALTURA_SALA / 2.0 - camera_pos_inicial[1] + 1.2, 0.0])
                textura_jogador = textura_baixo # Aplica a textura do baixo
                rotacao_y_adicional = 0.0  # Sem rotação adicional
            elif nivel_atual.numero >= 5 and obj_bateria_geometry and obj_bateria_geometry.vertex_count() > 0:
                modelo_jogador = obj_bateria_geometry
                escala_jogador = 5 / 9.0 # Escala para a bateria
                offset_jogador = np.array([0.5, -ALTURA_SALA / 2.0 - camera_pos_inicial[1] + 0.3, -0.2])  # Aumentado Y de 0.1 para 0.3 para elevar a bateria
                textura_jogador = textura_trompete # Aplica a textura do trompete à bateria
                rotacao_y_adicional = 180.0 # Rotaciona a bateria 180 graus

            if modelo_jogador:
                glPushMatrix()
                # Habilita texturas se houver
                if textura_jogador:
                    glEnable(GL_TEXTURE_2D)
                    glBindTexture(GL_TEXTURE_2D, textura_jogador)
                    
                    # Configurações adicionais para textura
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
                    
                    # Se for o baixo, imprimir informações adicionais
                    if nivel_atual.numero == 4:
                        print(f"Aplicando textura ao baixo. ID da textura: {textura_jogador}")
                    # Se for a bateria, imprimir informações adicionais
                    elif nivel_atual.numero >= 5:
                        print(f"Aplicando textura à bateria. ID da textura: {textura_jogador}")
                    # Se for o vibrafone, imprimir informações adicionais
                    elif nivel_atual.numero == 2:
                        print(f"Aplicando textura ao vibrafone. ID da textura: {textura_jogador}")
                else:
                    glDisable(GL_TEXTURE_2D) # Desabilita textura se não houver

                # Transladar para a posição do jogador (camera_pos)
                glTranslatef(camera_pos[0], camera_pos[1], camera_pos[2])

                # Rotacionar o modelo para olhar na direção da câmera (player)
                glRotatef(-yaw + 90.0, 0.0, 1.0, 0.0)  # Rotação base para alinhar com a direção
                
                # Aplica rotação Y adicional se necessário (por exemplo, para a bateria)
                if rotacao_y_adicional != 0.0:
                    glRotatef(rotacao_y_adicional, 0.0, 1.0, 0.0)
                
                # Aplica o offset específico do modelo
                glTranslatef(offset_jogador[0], offset_jogador[1], offset_jogador[2])

                # Aplica a escala do modelo
                glScalef(escala_jogador, escala_jogador, escala_jogador)

                draw_obj_model(modelo_jogador)
                
                glPopMatrix()
                
                # Desenha a sombra do instrumento no chão
                if SOMBRAS_HABILITADAS:
                    desenhar_sombra(modelo_jogador, camera_pos, escala_jogador, rotacao_y_adicional)
            
            desenhar_mira(largura_janela, altura_janela)
            desenhar_score_e_tempo(largura_janela, altura_janela)
        elif estado_jogo_atual == ESTADO_VITORIA:
            # Desabilita iluminação para a tela de vitória
            glDisable(GL_LIGHTING)
            menu_vitoria.desenhar(
                largura_janela, 
                altura_janela, 
                gerenciador_niveis.obter_nivel_atual().numero,
                gerenciador_niveis.esta_no_ultimo_nivel()
            )
        elif estado_jogo_atual == ESTADO_DERROTA:
            # Desabilita iluminação para a tela de derrota
            glDisable(GL_LIGHTING)
            menu_derrota.desenhar(largura_janela, altura_janela)
        elif estado_jogo_atual == ESTADO_CONFIGURACOES:
            # Desabilita iluminação para a tela de configurações
            glDisable(GL_LIGHTING)
            menu_configuracoes.desenhar(largura_janela, altura_janela)
        elif estado_jogo_atual == ESTADO_CREDITOS:
            # Desabilita iluminação para a tela de créditos
            glDisable(GL_LIGHTING)
            menu_creditos.desenhar(largura_janela, altura_janela)
        elif estado_jogo_atual == ESTADO_PAUSADO:
            menu_pausa.desenhar(largura_janela, altura_janela)
        elif estado_jogo_atual == ESTADO_FIM_DESAFIO:
            # Desabilita iluminação para a tela de fim de desafio
            glDisable(GL_LIGHTING)
            menu_fim_desafio.desenhar(largura_janela, altura_janela, score, gerenciador_niveis.obter_highscore(), 
                                     gerenciador_niveis.obter_data_highscore(),
                                     gerenciador_niveis.obter_nome_dificuldade())
        
        nova_largura, nova_altura = glfw.get_window_size(window)
        if nova_largura != largura_janela or nova_altura != altura_janela:
            largura_janela, altura_janela = nova_largura, nova_altura
            glViewport(0, 0, largura_janela, altura_janela)
        
        # Iniciar música do menu se estiver em um estado de menu e não estiver tocando
        if estado_jogo_atual in [ESTADO_MENU, ESTADO_VITORIA, ESTADO_DERROTA, ESTADO_MENU_DIFICULDADE, ESTADO_CONFIGURACOES, ESTADO_PAUSADO, ESTADO_CREDITOS] and musica_carregada and not pygame.mixer.music.get_busy():
             pygame.mixer.music.play(-1) # Inicia a reprodução em loop

        glfw.swap_buffers(window)
    glfw.terminate()

def desenhar_esferas_luz():
    """Desenha esferas de luz nos cantos da sala para visualizar a origem das luzes"""
    if not LUZES_CANTOS_HABILITADAS:
        return
        
    # Salva o estado atual de iluminação
    glPushAttrib(GL_LIGHTING_BIT | GL_ENABLE_BIT)
    
    # Configura material emissivo para as esferas de luz
    material_emissivo = [1.0, 1.0, 0.8, 1.0]  # Cor amarelada para as luzes
    glMaterialfv(GL_FRONT, GL_EMISSION, material_emissivo)
    glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 100.0)
    
    # Tamanho da esfera de luz
    raio_luz = 0.1
    slices = 16
    stacks = 16
    
    # Posições das luzes
    posicoes_luz = [
        [-LARGURA_SALA/2 + 1.0, ALTURA_SALA/2 - 0.5, -PROFUNDIDADE_SALA/2 + 1.0],  # Frontal esquerdo
        [LARGURA_SALA/2 - 1.0, ALTURA_SALA/2 - 0.5, -PROFUNDIDADE_SALA/2 + 1.0],   # Frontal direito
        [-LARGURA_SALA/2 + 1.0, ALTURA_SALA/2 - 0.5, PROFUNDIDADE_SALA/2 - 1.0],   # Traseiro esquerdo
        [LARGURA_SALA/2 - 1.0, ALTURA_SALA/2 - 0.5, PROFUNDIDADE_SALA/2 - 1.0]     # Traseiro direito
    ]
    
    # Desenha as esferas de luz
    for pos in posicoes_luz:
        glPushMatrix()
        glTranslatef(pos[0], pos[1], pos[2])
        
        # Desenha uma esfera para representar a luz
        quadric = gluNewQuadric()
        gluQuadricDrawStyle(quadric, GLU_FILL)
        gluSphere(quadric, raio_luz, slices, stacks)
        gluDeleteQuadric(quadric)
        
        glPopMatrix()
    
    # Restaura o estado original de iluminação
    glPopAttrib()

if __name__ == "__main__":
    main() 