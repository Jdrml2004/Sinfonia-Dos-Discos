import glfw
import numpy as np
import random
import math
from config import *
from draw import *

# --- Variáveis de Estado do Jogo ---
estado_jogo_atual = ESTADO_MENU
item_menu_selecionado_idx = 0
botoes_rects = []
score = 0

# Câmara
camera_pos = np.copy(camera_pos_inicial)
camera_front = np.copy(camera_front_inicial)
camera_up = np.copy(camera_up_inicial)
yaw = yaw_inicial
pitch = pitch_inicial
last_x, last_y = 400, 300
first_mouse = True
mouse_sensitivity = 0.1
fov = 45.0

# Alvos
global lista_alvos
lista_alvos = []

# --- Funções de Lógica do Jogo ---
def gerar_posicao_alvo_aleatoria(alvos_existentes_info, raio_novo_alvo):
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
    print("Aviso: Não foi possível encontrar posição sem colisão para novo alvo.")
    return np.array([0.0, 0.0, z_pos])

def inicializar_alvos():
    global lista_alvos
    lista_alvos = []
    alvos_para_verificacao = []
    for i in range(NUM_ALVOS):
        novo_raio = RAIO_ALVO_PADRAO
        nova_pos = gerar_posicao_alvo_aleatoria(alvos_para_verificacao, novo_raio)
        alvo = {
            'id': i, 'pos': nova_pos, 'raio': novo_raio,
            'visivel': True, 'tempo_atingido': 0.0
        }
        lista_alvos.append(alvo)
        alvos_para_verificacao.append({'pos': alvo['pos'], 'raio': alvo['raio']})

def reiniciar_jogo():
    global camera_pos, camera_front, camera_up, yaw, pitch, first_mouse, lista_alvos, score
    score = 0
    camera_pos = np.copy(camera_pos_inicial)
    camera_front = np.copy(camera_front_inicial)
    camera_up = np.copy(camera_up_inicial)
    yaw = yaw_inicial
    pitch = pitch_inicial
    first_mouse = True
    inicializar_alvos()

def mouse_callback(window, xpos, ypos):
    global first_mouse, last_x, last_y, yaw, pitch, camera_front, item_menu_selecionado_idx
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
        rato_x = xpos
        _, altura_janela = glfw.get_window_size(window)
        rato_y_opengl = altura_janela - ypos
        for i, botao in enumerate(botoes_rects):
            if (botao['x'] <= rato_x <= botao['x'] + botao['largura'] and 
                botao['y'] <= rato_y_opengl <= botao['y'] + botao['altura']):
                item_menu_selecionado_idx = i
                break

def mouse_button_callback(window, button, action, mods):
    global lista_alvos, estado_jogo_atual, item_menu_selecionado_idx, first_mouse, score
    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        if estado_jogo_atual == ESTADO_MENU:
            rato_x = glfw.get_cursor_pos(window)[0]
            altura_janela = glfw.get_window_size(window)[1]
            rato_y_opengl = altura_janela - glfw.get_cursor_pos(window)[1]
            for i, botao in enumerate(botoes_rects):
                if (botao['x'] <= rato_x <= botao['x'] + botao['largura'] and 
                    botao['y'] <= rato_y_opengl <= botao['y'] + botao['altura']):
                    if botao['id'] == 'jogar':
                        estado_jogo_atual = ESTADO_JOGANDO
                        reiniciar_jogo()
                        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                        first_mouse = True
                    elif botao['id'] == 'sair':
                        glfw.set_window_should_close(window, True)
                    break
        elif estado_jogo_atual == ESTADO_JOGANDO:
            for i, alvo in enumerate(lista_alvos):
                if alvo['visivel']:
                    z_plano_alvo = alvo['pos'][2]
                    if abs(camera_front[2]) < 1e-6: continue
                    t = (z_plano_alvo - camera_pos[2]) / camera_front[2]
                    if t > 0:
                        p_inter_x = camera_pos[0] + t * camera_front[0]
                        p_inter_y = camera_pos[1] + t * camera_front[1]
                        dist_sq = (p_inter_x - alvo['pos'][0])**2 + (p_inter_y - alvo['pos'][1])**2
                        if dist_sq <= alvo['raio']**2:
                            lista_alvos[i]['visivel'] = False
                            lista_alvos[i]['tempo_atingido'] = glfw.get_time()
                            score += 1
                            print(f"Alvo {alvo['id']} atingido!")
                            break

def key_callback(window, key, scancode, action, mods):
    global estado_jogo_atual, item_menu_selecionado_idx, first_mouse
    global camera_pos, camera_front, camera_up
    if action == glfw.PRESS or action == glfw.REPEAT:
        if estado_jogo_atual == ESTADO_MENU:
            if key == glfw.KEY_UP or key == glfw.KEY_W:
                item_menu_selecionado_idx = max(0, item_menu_selecionado_idx - 1)
            elif key == glfw.KEY_DOWN or key == glfw.KEY_S:
                item_menu_selecionado_idx = min(len(opcoes_menu) - 1, item_menu_selecionado_idx + 1)
            elif key == glfw.KEY_ENTER or key == glfw.KEY_SPACE:
                if opcoes_menu[item_menu_selecionado_idx]['id'] == 'jogar':
                    estado_jogo_atual = ESTADO_JOGANDO
                    reiniciar_jogo()
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                    first_mouse = True
                elif opcoes_menu[item_menu_selecionado_idx]['id'] == 'sair':
                    glfw.set_window_should_close(window, True)
            elif key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(window, True)
        elif estado_jogo_atual == ESTADO_JOGANDO:
            velocidade_movimento = 0.1
            camera_right = np.cross(camera_front, camera_up)
            camera_right = camera_right / np.linalg.norm(camera_right)
            if key == glfw.KEY_W: camera_pos += camera_front * velocidade_movimento
            elif key == glfw.KEY_S: camera_pos -= camera_front * velocidade_movimento
            elif key == glfw.KEY_A: camera_pos -= camera_right * velocidade_movimento
            elif key == glfw.KEY_D: camera_pos += camera_right * velocidade_movimento
            elif key == glfw.KEY_SPACE: camera_pos += camera_up * velocidade_movimento
            elif key == glfw.KEY_LEFT_SHIFT: camera_pos -= camera_up * velocidade_movimento
            elif key == glfw.KEY_ESCAPE:
                estado_jogo_atual = ESTADO_MENU
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL) 