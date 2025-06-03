from OpenGL.GL import *
from OpenGL.GLU import *
import math
from config import *
import numpy as np
import glfw

# Adicionar no início do arquivo, após os imports
contador_disparos = 0

# --- Funções de Desenho ---
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
    glPushMatrix()
    glScalef(largura, altura, profundidade)
    desenhar_cubo(1.0)
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

def desenhar_alvos(lista_alvos):
    global contador_disparos
    glEnable(GL_BLEND)
    for alvo in lista_alvos:
        if alvo['visivel']:
            glPushMatrix()
            glTranslatef(alvo['pos'][0], alvo['pos'][1], alvo['pos'][2])
            desenhar_disco_vinil(raio=alvo['raio'])
            glPopMatrix()
        else:
            tempo_atual = glfw.get_time()
            tempo_atingido = alvo['tempo_atingido']
            if tempo_atual - tempo_atingido < 0.5:
                glPushMatrix()
                glTranslatef(alvo['pos'][0], alvo['pos'][1], alvo['pos'][2])
                # Alterna entre os diferentes tipos de notas baseado no contador de disparos
                tipo_nota = contador_disparos % 5
                if tipo_nota == 0:
                    desenhar_clave_sol(raio=alvo['raio'])
                elif tipo_nota == 1:
                    desenhar_colcheia(raio=alvo['raio'])
                elif tipo_nota == 2:
                    desenhar_par_colcheias(raio=alvo['raio'])
                elif tipo_nota == 3:
                    desenhar_semicolcheia(raio=alvo['raio'])
                else:
                    desenhar_seminima(raio=alvo['raio'])
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
    glMatrixMode(GL_MODELVIEW)

def desenhar_retangulo_2d(x, y, largura, altura, cor):
    glColor4f(cor[0], cor[1], cor[2], cor[3])
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + largura, y)
    glVertex2f(x + largura, y + altura)
    glVertex2f(x, y + altura)
    glEnd()

def desenhar_texto_simples(texto, x, y, escala=1.0, cor=(1.0, 1.0, 1.0, 1.0)):
    # (Função igual à versão já melhorada, copiar do main.py)
    # ...
    pass

def desenhar_texto_2d(texto, x, y, largura_janela, altura_janela, escala=1.0, cor=(1.0,1.0,1.0,1.0)):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, largura_janela, 0, altura_janela)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    desenhar_texto_simples(texto, x, y, escala, cor)
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def desenhar_score(score, largura_janela, altura_janela):
    texto = f"SCORE: {score}"
    x = 20
    y = altura_janela - 40
    desenhar_texto_2d(texto, x, y, largura_janela, altura_janela, escala=2.0, cor=(1.0, 1.0, 1.0, 1.0))

def desenhar_menu(largura_janela, altura_janela, botoes_rects, item_menu_selecionado_idx):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, largura_janela, 0, altura_janela)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    desenhar_retangulo_2d(0, 0, largura_janela, altura_janela, COR_FUNDO_MENU)
    escala_titulo = 3.0
    texto_titulo = TITULO_JOGO
    largura_titulo = len(texto_titulo) * 12 * escala_titulo
    x_titulo = (largura_janela - largura_titulo) / 2
    y_titulo = altura_janela - 100
    desenhar_texto_simples(texto_titulo, x_titulo, y_titulo, escala=escala_titulo, cor=COR_TITULO)
    botoes_rects.clear()
    y_botao = altura_janela / 2
    espacamento_botoes_local = altura_botao + 20
    for i, opcao in enumerate(opcoes_menu):
        cor_botao = COR_BOTAO_SELECIONADO if i == item_menu_selecionado_idx else COR_BOTAO
        x_botao = (largura_janela - largura_botao) / 2
        y_atual = y_botao - i * espacamento_botoes_local
        desenhar_retangulo_2d(x_botao, y_atual, largura_botao, altura_botao, cor_botao)
        botoes_rects.append({
            'x': x_botao,
            'y': y_atual,
            'largura': largura_botao,
            'altura': altura_botao,
            'id': opcao['id']
        })
        escala_texto = 2.0
        texto = opcao['texto']
        largura_texto = len(texto) * 12 * escala_texto
        x_texto = x_botao + (largura_botao - largura_texto) / 2
        y_texto = y_atual + (altura_botao - 12 * escala_texto) / 2
        desenhar_texto_simples(texto, x_texto, y_texto, escala=escala_texto, cor=COR_TEXTO)
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def desenhar_clave_sol(raio=0.3):
    """Desenha uma clave de sol bonita e realista usando primitivas OpenGL"""
    tempo_atual = glfw.get_time()
    angulo_rotacao = tempo_atual * 90.0  # Rotação mais lenta e suave
    
    # Cor preta para a clave
    glColor3f(0.0, 0.0, 0.0)  # Preto
    glLineWidth(8.0)  # Linha mais espessa para melhor definição
    
    glPushMatrix()
    glRotatef(angulo_rotacao, 0.0, 0.0, 1.0)  # Rotaciona em torno do eixo Z
    
    # Círculo superior da clave (mais definido e gordo)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(-raio * 0.1, raio * 0.7, 0.0)  # Centro do círculo
    for i in range(65):  # Mais segmentos para suavidade
        angulo = 2.0 * math.pi * float(i) / float(64)
        x = raio * 0.25 * math.cos(angulo) - raio * 0.1  # Deslocado para a esquerda
        y = raio * 0.25 * math.sin(angulo) + raio * 0.7   # Posicionado no topo
        glVertex3f(x, y, 0.0)
    glEnd()
    
    # Linha vertical principal da clave (mais gorda)
    glBegin(GL_QUAD_STRIP)
    for i in range(20):
        t = float(i) / 19.0
        x = raio * 0.15 - raio * 0.05 * math.sin(t * math.pi)
        y = raio * 0.7 - t * raio * 1.5
        # Desenha uma linha com espessura
        glVertex3f(x - raio * 0.03, y, 0.0)
        glVertex3f(x + raio * 0.03, y, 0.0)
    glEnd()
    
    # Espiral principal (característica da clave de sol)
    glBegin(GL_QUAD_STRIP)
    for i in range(40):
        t = float(i) / 39.0
        angulo = math.pi * 3.5 * t  # Mais voltas na espiral
        raio_espiral = raio * 0.4 * (1.0 - t * 0.6)  # Espiral que diminui
        x = raio * 0.1 + raio_espiral * math.cos(angulo)
        y = -raio * 0.1 - t * raio * 0.6 + raio_espiral * 0.3 * math.sin(angulo)
        # Desenha uma linha com espessura
        glVertex3f(x - raio * 0.03, y, 0.0)
        glVertex3f(x + raio * 0.03, y, 0.0)
    glEnd()
    
    # Segunda espiral interna (mais gorda)
    glBegin(GL_QUAD_STRIP)
    for i in range(25):
        t = float(i) / 24.0
        angulo = math.pi * 2.0 * t + math.pi
        raio_espiral = raio * 0.15 * (1.0 - t * 0.5)
        x = raio * 0.1 + raio_espiral * math.cos(angulo)
        y = -raio * 0.2 - t * raio * 0.3 + raio_espiral * 0.2 * math.sin(angulo)
        # Desenha uma linha com espessura
        glVertex3f(x - raio * 0.02, y, 0.0)
        glVertex3f(x + raio * 0.02, y, 0.0)
    glEnd()
    
    # Círculo central decorativo (ponto focal mais gordo)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(raio * 0.1, -raio * 0.1, 0.0)
    for i in range(33):  # Mais segmentos para suavidade
        angulo = 2.0 * math.pi * float(i) / float(32)
        x = raio * 0.1 + raio * 0.1 * math.cos(angulo)  # Raio aumentado
        y = -raio * 0.1 + raio * 0.1 * math.sin(angulo)  # Raio aumentado
        glVertex3f(x, y, 0.0)
    glEnd()
    
    # Curva final elegante (terminação da clave mais gorda)
    glBegin(GL_QUAD_STRIP)
    for i in range(15):
        t = float(i) / 14.0
        angulo = math.pi * 0.8 * t
        x = raio * 0.05 + raio * 0.2 * math.cos(angulo + math.pi)
        y = -raio * 0.5 - raio * 0.15 * math.sin(angulo)
        # Desenha uma linha com espessura
        glVertex3f(x - raio * 0.03, y, 0.0)
        glVertex3f(x + raio * 0.03, y, 0.0)
    glEnd()
    
    # Pontos decorativos para dar brilho (mais grossos)
    glColor3f(0.0, 0.0, 0.0)  # Preto
    glPointSize(8.0)  # Pontos maiores
    glBegin(GL_POINTS)
    glVertex3f(-raio * 0.1, raio * 0.7, 0.0)  # Topo
    glVertex3f(raio * 0.15, -raio * 0.1, 0.0)  # Centro
    glVertex3f(-raio * 0.05, -raio * 0.5, 0.0)  # Parte inferior
    glEnd()
    
    glPopMatrix()
    glLineWidth(1.0)  # Restaura espessura padrão
    glPointSize(1.0)  # Restaura tamanho de ponto padrão

def desenhar_colcheia(raio=0.3):
    """Desenha uma colcheia"""
    tempo_atual = glfw.get_time()
    angulo_rotacao = tempo_atual * 90.0
    
    glColor3f(0.0, 0.0, 0.0)  # Preto
    glLineWidth(8.0)
    
    glPushMatrix()
    glRotatef(angulo_rotacao, 0.0, 0.0, 1.0)
    
    # Cabeça da nota (círculo preenchido)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0.0, 0.0, 0.0)
    for i in range(33):
        angulo = 2.0 * math.pi * float(i) / float(32)
        x = raio * 0.2 * math.cos(angulo)
        y = raio * 0.2 * math.sin(angulo)
        glVertex3f(x, y, 0.0)
    glEnd()
    
    # Haste
    glBegin(GL_QUAD_STRIP)
    for i in range(20):
        t = float(i) / 19.0
        x = raio * 0.2 + t * raio * 0.1
        y = t * raio * 1.2
        glVertex3f(x - raio * 0.03, y, 0.0)
        glVertex3f(x + raio * 0.03, y, 0.0)
    glEnd()
    
    # Bandeira
    glBegin(GL_QUAD_STRIP)
    for i in range(15):
        t = float(i) / 14.0
        angulo = math.pi * 0.5 * t
        x = raio * 0.3 + raio * 0.2 * math.cos(angulo)
        y = raio * 1.2 + raio * 0.2 * math.sin(angulo)
        glVertex3f(x - raio * 0.02, y, 0.0)
        glVertex3f(x + raio * 0.02, y, 0.0)
    glEnd()
    
    glPopMatrix()

def desenhar_par_colcheias(raio=0.3):
    """Desenha duas colcheias ligadas"""
    tempo_atual = glfw.get_time()
    angulo_rotacao = tempo_atual * 90.0
    
    glColor3f(0.0, 0.0, 0.0)
    glLineWidth(8.0)
    
    glPushMatrix()
    glRotatef(angulo_rotacao, 0.0, 0.0, 1.0)
    
    # Primeira colcheia
    glPushMatrix()
    glTranslatef(-raio * 0.3, 0.0, 0.0)
    desenhar_colcheia(raio)
    glPopMatrix()
    
    # Segunda colcheia
    glPushMatrix()
    glTranslatef(raio * 0.3, 0.0, 0.0)
    desenhar_colcheia(raio)
    glPopMatrix()
    
    # Ligação entre as colcheias
    glBegin(GL_QUAD_STRIP)
    for i in range(20):
        t = float(i) / 19.0
        x = -raio * 0.3 + t * raio * 0.6
        y = raio * 1.2
        glVertex3f(x, y - raio * 0.03, 0.0)
        glVertex3f(x, y + raio * 0.03, 0.0)
    glEnd()
    
    glPopMatrix()

def desenhar_semicolcheia(raio=0.3):
    """Desenha uma semicolcheia (duas bandeiras)"""
    tempo_atual = glfw.get_time()
    angulo_rotacao = tempo_atual * 90.0
    
    glColor3f(0.0, 0.0, 0.0)
    glLineWidth(8.0)
    
    glPushMatrix()
    glRotatef(angulo_rotacao, 0.0, 0.0, 1.0)
    
    # Cabeça da nota
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0.0, 0.0, 0.0)
    for i in range(33):
        angulo = 2.0 * math.pi * float(i) / float(32)
        x = raio * 0.2 * math.cos(angulo)
        y = raio * 0.2 * math.sin(angulo)
        glVertex3f(x, y, 0.0)
    glEnd()
    
    # Haste
    glBegin(GL_QUAD_STRIP)
    for i in range(20):
        t = float(i) / 19.0
        x = raio * 0.2 + t * raio * 0.1
        y = t * raio * 1.2
        glVertex3f(x - raio * 0.03, y, 0.0)
        glVertex3f(x + raio * 0.03, y, 0.0)
    glEnd()
    
    # Duas bandeiras
    for bandeira in range(2):
        glBegin(GL_QUAD_STRIP)
        for i in range(15):
            t = float(i) / 14.0
            angulo = math.pi * 0.5 * t
            x = raio * 0.3 + raio * 0.2 * math.cos(angulo)
            y = raio * 1.2 + raio * 0.2 * math.sin(angulo) + bandeira * raio * 0.15
            glVertex3f(x - raio * 0.02, y, 0.0)
            glVertex3f(x + raio * 0.02, y, 0.0)
        glEnd()
    
    glPopMatrix()

def desenhar_seminima(raio=0.3):
    """Desenha uma semínima (nota sem bandeira)"""
    tempo_atual = glfw.get_time()
    angulo_rotacao = tempo_atual * 90.0
    
    glColor3f(0.0, 0.0, 0.0)
    glLineWidth(8.0)
    
    glPushMatrix()
    glRotatef(angulo_rotacao, 0.0, 0.0, 1.0)
    
    # Cabeça da nota (círculo preenchido)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0.0, 0.0, 0.0)
    for i in range(33):
        angulo = 2.0 * math.pi * float(i) / float(32)
        x = raio * 0.2 * math.cos(angulo)
        y = raio * 0.2 * math.sin(angulo)
        glVertex3f(x, y, 0.0)
    glEnd()
    
    # Haste
    glBegin(GL_QUAD_STRIP)
    for i in range(20):
        t = float(i) / 19.0
        x = raio * 0.2 + t * raio * 0.1
        y = t * raio * 1.2
        glVertex3f(x - raio * 0.03, y, 0.0)
        glVertex3f(x + raio * 0.03, y, 0.0)
    glEnd()
    
    glPopMatrix() 

def incrementar_contador_disparos():
    global contador_disparos
    contador_disparos += 1 