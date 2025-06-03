from OpenGL.GL import *
import glfw
from text_renderer import TextRenderer
import math
import random
from PIL import Image # Importar Image para carregar texturas
import numpy as np
import pygame

class Menu:
    def __init__(self, text_renderer, textura_titulo=None):
        self.text_renderer = text_renderer
        self.botoes_rects = []
        self.item_selecionado_idx = -1 # Initialize to -1 (no selection)
        self.largura_botao = 400  # Aumentado significativamente
        self.altura_botao = 80    # Aumentado significativamente
        self.espacamento_botoes = 40  # Aumentado o espaçamento
        
        # Cores atualizadas
        self.COR_FUNDO = (0.05, 0.05, 0.15, 1.0)  # Azul mais escuro
        self.COR_FUNDO_GRADIENTE = (0.1, 0.1, 0.25, 1.0)  # Cor secundária para gradiente
        self.COR_TITULO_RGB = (255, 215, 0)  # Dourado
        self.COR_BOTAO = (0.15, 0.15, 0.35, 1.0)  # Azul mais escuro
        self.COR_BOTAO_SELECIONADO = (0.3, 0.3, 0.8, 1.0)  # Azul mais vibrante
        self.COR_TEXTO_RGB = (255, 255, 255)  # Branco
        self.COR_BORDA = (0.4, 0.4, 0.9, 1.0)  # Cor da borda dos botões
        self.COR_ONDAS = (0.2, 0.2, 0.5, 0.3)  # Cor das ondas
        
        # Variáveis para animação
        self.tempo_animacao = 0
        
        # Texturas das notas musicais - Inicializar vazio e carregar depois
        self.texturas_notas = {}
        self.texturas_carregadas = False # Flag para controlar o carregamento
        
        # Lista de notas musicais para animação
        self.notas_animadas = []
        # Geração inicial pode ser feita aqui ou no primeiro desenhar
        self.textura_titulo = textura_titulo
    
    def carregar_textura(self, caminho_imagem):
        """Carrega uma imagem e a converte em textura OpenGL"""
        try:
            imagem = Image.open(caminho_imagem).convert("RGBA") # Converter para RGBA
            imagem = imagem.transpose(Image.FLIP_TOP_BOTTOM)  # Inverte a imagem verticalmente
            dados_imagem = np.array(list(imagem.getdata()), np.uint8)
            
            # Gera um ID de textura
            textura_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, textura_id)
            
            # Configura os parâmetros da textura
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE) # Lidar com bordas
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE) # Lidar com bordas

            # Carrega os dados da imagem na textura
            if imagem.mode == 'RGB':
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, imagem.width, imagem.height, 0, GL_RGB, GL_UNSIGNED_BYTE, dados_imagem)
            elif imagem.mode == 'RGBA':
                 glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, imagem.width, imagem.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, dados_imagem)
            
            return textura_id, imagem.width, imagem.height
        except Exception as e:
            print(f"Erro ao carregar textura {caminho_imagem}: {e}")
            return None, 0, 0

    def carregar_texturas_notas(self):
        self.texturas_notas['semicolcheia'], _, _ = self.carregar_textura('images/semicolcheia.png')
        self.texturas_notas['colcheia'], _, _ = self.carregar_textura('images/colcheia.png')
        self.texturas_notas['seminima'], _, _ = self.carregar_textura('images/seminima.png')
        self.texturas_notas['par_colcheias'], _, _ = self.carregar_textura('images/par_colcheias.png')
        self.texturas_notas['clave_sol'], _, _ = self.carregar_textura('images/clave_sol.png')

    def gerar_notas_animadas(self, num_notas, largura_janela, altura_janela):
        tipos_notas = ['semicolcheia', 'colcheia', 'seminima', 'par_colcheias', 'clave_sol']
        for _ in range(num_notas):
            tipo = random.choice(tipos_notas)
            self.notas_animadas.append({
                'tipo': tipo,
                'x': random.uniform(0, largura_janela),
                'y': random.uniform(0, altura_janela), # Posição inicial aleatória na tela
                'velocidade': random.uniform(30, 60), # Velocidade um pouco maior
                'tamanho': random.uniform(100, 200)    # Tamanho maior - Aumentado novamente
            })

    def desenhar_onda(self, x_inicio, y, amplitude, frequencia, fase, cor, largura_janela):
        glColor4f(*cor)
        glBegin(GL_LINE_STRIP)
        num_segmentos = int(largura_janela / 5)  # Número de segmentos proporcional à largura da janela
        for i in range(num_segmentos):
            x_pos = x_inicio + (i / num_segmentos) * largura_janela  # Distribui pontos pela largura da janela
            y_pos = y + amplitude * math.sin(frequencia * (x_pos + fase))
            glVertex2f(x_pos, y_pos)
        glEnd()
    
    def desenhar_fundo_animado(self, largura_janela, altura_janela):
        # Carregar texturas se ainda não foram carregadas
        if not self.texturas_carregadas:
            self.carregar_texturas_notas()
            self.gerar_notas_animadas(30, largura_janela, altura_janela) # Gerar mais notas (aumentado de 15 para 30)
            self.texturas_carregadas = True

        # Desenha o gradiente base
        self.desenhar_gradiente(largura_janela, altura_janela)
        
        # Desenha as ondas
        self.tempo_animacao += 0.02
        num_ondas = 8 # Aumenta o número de ondas
        for i in range(num_ondas):
            fase = self.tempo_animacao + i * 1.5 # Ajusta a fase para espaçar as ondas
            # Ajusta a posição vertical para distribuir as 8 ondas
            y_pos = altura_janela * (0.1 + i * (0.8 / (num_ondas - 1)))
            self.desenhar_onda(0, y_pos, 
                             20, 0.01, fase, self.COR_ONDAS, largura_janela)
        
        # Atualiza e desenha as notas musicais com textura
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        for nota in self.notas_animadas:
            # Atualiza a posição (movendo para cima)
            nota['y'] += nota['velocidade'] * 0.016  # 0.016 é aproximadamente 1/60 (60 FPS)
            
            # Reposiciona a nota se sair da tela por cima
            if nota['y'] > altura_janela + nota['tamanho']:
                nota['y'] = -nota['tamanho']
                nota['x'] = random.uniform(0, largura_janela) # Reposiciona horizontalmente também
                nota['velocidade'] = random.uniform(30, 60) # Velocidade aleatória ao reaparecer
                nota['tamanho'] = random.uniform(100, 200) # Tamanho aleatório ao reaparecer
                nota['tipo'] = random.choice(['semicolcheia', 'colcheia', 'seminima', 'par_colcheias', 'clave_sol']) # Tipo aleatório

            # Desenha a nota com textura
            if nota['tipo'] in self.texturas_notas and self.texturas_notas[nota['tipo']] is not None:
                glBindTexture(GL_TEXTURE_2D, self.texturas_notas[nota['tipo']])
                tamanho = nota['tamanho']
                # Posição de desenho ajustada para a textura
                x = nota['x'] - tamanho/2 
                y = nota['y'] - tamanho/2

                glColor4f(1.0, 1.0, 1.0, 1.0) # Usar cor branca para não afetar a cor da textura
                glBegin(GL_QUADS)
                glTexCoord2f(0, 0); glVertex2f(x, y)
                glTexCoord2f(1, 0); glVertex2f(x + tamanho, y)
                glTexCoord2f(1, 1); glVertex2f(x + tamanho, y + tamanho)
                glTexCoord2f(0, 1); glVertex2f(x, y + tamanho)
                glEnd()
        
        glDisable(GL_TEXTURE_2D)
    
    def desenhar_retangulo_2d(self, x, y, largura, altura, cor, borda=False):
        glDisable(GL_TEXTURE_2D)
        
        # Desenha o preenchimento
        glColor4f(cor[0], cor[1], cor[2], cor[3])
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + largura, y)
        glVertex2f(x + largura, y + altura)
        glVertex2f(x, y + altura)
        glEnd()
        
        # Desenha a borda se solicitado
        if borda:
            glColor4f(self.COR_BORDA[0], self.COR_BORDA[1], self.COR_BORDA[2], self.COR_BORDA[3])
            glBegin(GL_LINE_LOOP)
            glVertex2f(x, y)
            glVertex2f(x + largura, y)
            glVertex2f(x + largura, y + altura)
            glVertex2f(x, y + altura)
            glEnd()
    
    def desenhar_gradiente(self, largura_janela, altura_janela):
        glDisable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        # Canto superior esquerdo
        glColor4f(*self.COR_FUNDO)
        glVertex2f(0, 0)
        # Canto superior direito
        glColor4f(*self.COR_FUNDO_GRADIENTE)
        glVertex2f(largura_janela, 0)
        # Canto inferior direito
        glColor4f(*self.COR_FUNDO_GRADIENTE)
        glVertex2f(largura_janela, altura_janela)
        # Canto inferior esquerdo
        glColor4f(*self.COR_FUNDO)
        glVertex2f(0, altura_janela)
        glEnd()
    
    def configurar_viewport_2d(self, largura_janela, altura_janela):
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, largura_janela, 0, altura_janela, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
    
    def restaurar_viewport(self):
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glPopAttrib()
    
    def processar_mouse(self, rato_x, rato_y_opengl, action=None):
        novo_idx = -1                                  # assume "sem hover"
        for i, botao in enumerate(self.botoes_rects):
            if (botao['x'] <= rato_x <= botao['x'] + botao['largura'] and
                botao['y'] <= rato_y_opengl <= botao['y'] + botao['altura']):
                novo_idx = i                          # o rato está sobre este
                if action == glfw.PRESS:
                    return botao['id']                # clique
                break
        self.item_selecionado_idx = novo_idx          # -1 se não estiver sobre nada
        return None

    def _cursor_dentro(self, x, y, rect):
        """Retorna True se (x,y) estiver dentro do rect = {'x','y','largura','altura'}."""
        return rect and rect['x'] <= x <= rect['x'] + rect['largura'] \
            and rect['y'] <= y <= rect['y'] + rect['altura']

class MenuPrincipal(Menu):
    def __init__(self, text_renderer, textura_titulo=None):
        super().__init__(text_renderer, textura_titulo)
        self.titulo = "Sinfonia dos Discos"
        self.botoes = [
            {'texto': 'Sair', 'id': 'sair'},
            {'texto': 'Créditos', 'id': 'creditos'},
            {'texto': 'Configurações', 'id': 'configuracoes'},
            {'texto': 'Jogar', 'id': 'jogar'}
        ]
        self.item_selecionado_idx = -1     # -1  ⇒  nenhum botão realçado
    
    def desenhar(self, largura_janela, altura_janela):
        self.configurar_viewport_2d(largura_janela, altura_janela)
        
        # Desenha fundo animado
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.desenhar_fundo_animado(largura_janela, altura_janela)
        
        # Título
        if self.textura_titulo is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.textura_titulo)
            glColor4f(1.0, 1.0, 1.0, 1.0) # Cor branca para não tingir a textura
            
            # Define a posição e tamanho do quad para a textura do título
            # Ajuste estes valores conforme o tamanho da imagem e onde quer que apareça
            largura_titulo_img = 800 # Exemplo: ajuste a largura desejada
            altura_titulo_img = 300 # Exemplo: ajuste a altura desejada (aumentado)
            x_titulo_img = (largura_janela - largura_titulo_img) / 2
            y_titulo_img = altura_janela - 350 # Exemplo: ajuste a posição vertical (movido para baixo)
            
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0); glVertex2f(x_titulo_img, y_titulo_img)
            glTexCoord2f(1.0, 0.0); glVertex2f(x_titulo_img + largura_titulo_img, y_titulo_img)
            glTexCoord2f(1.0, 1.0); glVertex2f(x_titulo_img + largura_titulo_img, y_titulo_img + altura_titulo_img)
            glTexCoord2f(0.0, 1.0); glVertex2f(x_titulo_img, y_titulo_img + altura_titulo_img)
            glEnd()
            
            glDisable(GL_TEXTURE_2D)
        
        # Botões
        self.botoes_rects = []
        y_botao = altura_janela / 2 - (len(self.botoes) * (self.altura_botao + self.espacamento_botoes)) / 2 # Calculate starting y for the block of buttons

        # Calculate total height of all buttons and spacing
        total_botoes_altura = len(self.botoes) * self.altura_botao + (len(self.botoes) - 1) * self.espacamento_botoes if len(self.botoes) > 0 else 0
        y_botao_start = altura_janela / 2 - total_botoes_altura / 2

        for i, botao in enumerate(self.botoes):
            x_botao = (largura_janela - self.largura_botao) / 2
            # Calculate the y position for the current button
            y_atual = y_botao_start + i * (self.altura_botao + self.espacamento_botoes)

            # Efeito de hover com animação
            cor_botao = self.COR_BOTAO_SELECIONADO if i == self.item_selecionado_idx else self.COR_BOTAO
            self.desenhar_retangulo_2d(x_botao, y_atual, self.largura_botao, self.altura_botao, cor_botao, True)

            self.botoes_rects.append({
                'x': x_botao,
                'y': y_atual,
                'largura': self.largura_botao,
                'altura': self.altura_botao,
                'id': botao['id']
            })
            
            texto = botao['texto']
            tamanho_texto = 48
            # Use text_renderer to get text dimensions
            largura_texto, altura_texto = self.text_renderer.get_text_dimensions(texto, tamanho_texto)

            x_texto = x_botao + (self.largura_botao - largura_texto) / 2
            # Centralizar verticalmente usando a altura exata do texto
            y_texto = y_atual + (self.altura_botao - altura_texto) / 2
            self.text_renderer.draw_text(texto, x_texto, y_texto, tamanho_texto, self.COR_TEXTO_RGB)
        
        self.restaurar_viewport()
    
    def processar_teclado(self, key):
        if key in [glfw.KEY_UP, glfw.KEY_W]:
            self.item_selecionado_idx = max(0, self.item_selecionado_idx - 1)
        elif key in [glfw.KEY_DOWN, glfw.KEY_S]:
            self.item_selecionado_idx = min(len(self.botoes) - 1, self.item_selecionado_idx + 1)
        elif key in [glfw.KEY_ENTER, glfw.KEY_SPACE]:
            # Optional: Prevent action if no button is selected
            if self.item_selecionado_idx >= 0:
                return self.botoes[self.item_selecionado_idx]['id']
        return None

class MenuVitoria(Menu):
    def __init__(self, text_renderer, textura_titulo=None):
        super().__init__(text_renderer, textura_titulo)
        self.COR_FUNDO = (0.0, 0.3, 0.0, 1.0)  # Verde
        self.botoes_padrao = [
            {'texto': 'Proximo Nivel', 'id': 'proximo'},
            {'texto': 'Jogar Novamente', 'id': 'replay'},
            {'texto': 'Alterar Dificuldade', 'id': 'dificuldade'},
            {'texto': 'Menu Principal', 'id': 'menu'}
        ]
        self.botoes_ultimo_nivel = [
            {'texto': 'Jogar Novamente', 'id': 'replay'},
            {'texto': 'Alterar Dificuldade', 'id': 'dificuldade'},
            {'texto': 'Menu Principal', 'id': 'menu'}
        ]
        self.botoes_nivel5 = [
            {'texto': 'Selecionar Nivel', 'id': 'niveis'},
            {'texto': 'Alterar Dificuldade', 'id': 'dificuldade'},
            {'texto': 'Menu Principal', 'id': 'menu'}
        ]
        self.botoes = self.botoes_padrao
    
    def desenhar(self, largura_janela, altura_janela, nivel_atual, eh_ultimo_nivel=False):
        # Define quais botões mostrar com base no nível atual
        if nivel_atual == 5:  # Se for o nível 5
            self.botoes = self.botoes_nivel5
        elif eh_ultimo_nivel:  # Se for o último nível (que não seja o 5)
            self.botoes = self.botoes_ultimo_nivel
        else:  # Níveis normais
            self.botoes = self.botoes_padrao

        self.configurar_viewport_2d(largura_janela, altura_janela)
        
        # Desenha o fundo: gradiente e ondas (sem notas a cair)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # Limpa a tela
        self.desenhar_gradiente(largura_janela, altura_janela) # Desenha o gradiente
        
        # Desenha as ondas (copiado de desenhar_fundo_animado)
        self.tempo_animacao += 0.02
        num_ondas = 8 # Aumenta o número de ondas
        for i in range(num_ondas):
            fase = self.tempo_animacao + i * 1.5 # Ajusta a fase para espaçar as ondas
            # Ajusta a posição vertical para distribuir as 8 ondas
            y_pos = altura_janela * (0.1 + i * (0.8 / (num_ondas - 1)))
            self.desenhar_onda(0, y_pos, 
                             20, 0.01, fase, self.COR_ONDAS, largura_janela)
        
        # Desenha o título com textura
        if self.textura_titulo:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.textura_titulo)
            
            # Dimensões da textura (assumindo que a textura tem um tamanho razoável)
            largura_titulo = 800 # Mesma largura do menu principal
            altura_titulo = 300 # Mesma altura do menu principal
            
            x_titulo = (largura_janela - largura_titulo) / 2
            y_titulo = altura_janela - 350 # Mesma posição Y do menu principal
            
            glColor4f(1.0, 1.0, 1.0, 1.0) # Cor branca para não tingir a textura
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0); glVertex2f(x_titulo, y_titulo)
            glTexCoord2f(1.0, 0.0); glVertex2f(x_titulo + largura_titulo, y_titulo)
            glTexCoord2f(1.0, 1.0); glVertex2f(x_titulo + largura_titulo, y_titulo + altura_titulo)
            glTexCoord2f(0.0, 1.0); glVertex2f(x_titulo, y_titulo + altura_titulo)
            glEnd()
            
            glDisable(GL_TEXTURE_2D)
        else:
            # Fallback: desenhar texto simples se a textura não carregar
            mensagem_titulo = "VITORIA!"
            tamanho_texto_titulo = 72
            largura_texto_titulo = len(mensagem_titulo) * tamanho_texto_titulo * 0.5
            x_texto_titulo = (largura_janela - largura_texto_titulo) / 2
            y_texto_titulo = altura_janela - 150
            self.text_renderer.draw_text(mensagem_titulo, x_texto_titulo, y_texto_titulo, tamanho_texto_titulo, (255, 255, 0))

        # Mensagem do nível concluído (texto adicional)
        mensagem_nivel = f"NIVEL {nivel_atual} CONCLUIDO!"
        if eh_ultimo_nivel:
             mensagem_nivel = "PARABENS PELA VITORIA FINAL!"
        tamanho_texto_nivel = 48
        largura_texto_nivel = len(mensagem_nivel) * tamanho_texto_nivel * 0.4
        x_texto_nivel = (largura_janela - largura_texto_nivel) / 2
        # Posição abaixo do título texturizado
        # A base do título texturizado está em altura_janela - 350
        y_texto_nivel = (altura_janela - 350) - 50 # Subtrai um offset para posicionar abaixo
        self.text_renderer.draw_text(mensagem_nivel, x_texto_nivel, y_texto_nivel, tamanho_texto_nivel, (255, 255, 255)) # Cor branca

        # Desenha botões
        self.botoes_rects = []
        y_botao = altura_janela / 2
        
        for i, botao in enumerate(self.botoes):
            x_botao = (largura_janela - self.largura_botao) / 2
            y_atual = y_botao - i * (self.altura_botao + self.espacamento_botoes)
            
            cor_botao = self.COR_BOTAO_SELECIONADO if i == self.item_selecionado_idx else self.COR_BOTAO
            self.desenhar_retangulo_2d(x_botao, y_atual, self.largura_botao, self.altura_botao, cor_botao, True)
            
            self.botoes_rects.append({
                'x': x_botao,
                'y': y_atual,
                'largura': self.largura_botao,
                'altura': self.altura_botao,
                'id': botao['id']
            })
            
            texto = botao['texto']
            tamanho_texto = 48
            # Obter as dimensões exatas do texto para centralização
            largura_texto, altura_texto = self.text_renderer.get_text_dimensions(texto, tamanho_texto)

            x_texto = x_botao + (self.largura_botao - largura_texto) / 2
            # Centralizar verticalmente usando a altura exata do texto
            y_texto = y_atual + (self.altura_botao - altura_texto) / 2
            self.text_renderer.draw_text(texto, x_texto, y_texto, tamanho_texto, self.COR_TEXTO_RGB)
        
        self.restaurar_viewport()
    
    def processar_mouse(self, rato_x, rato_y_opengl, action=None):
        # Update selected item based on mouse position for hover effect
        self.item_selecionado_idx = -1 # Reset selection
        for i, botao_rect in enumerate(self.botoes_rects):
            if self._cursor_dentro(rato_x, rato_y_opengl, botao_rect):
                self.item_selecionado_idx = i
                # If action is PRESS, also return the button id for click handling
                if action == glfw.PRESS:
                    return self.botoes_rects[i]['id']
        return None # No action to return for hover or click outside buttons

    def processar_teclado(self, key):
        if key in [glfw.KEY_UP, glfw.KEY_W]:
            self.item_selecionado_idx = max(0, self.item_selecionado_idx - 1)
        elif key in [glfw.KEY_DOWN, glfw.KEY_S]:
            self.item_selecionado_idx = min(len(self.botoes) - 1, self.item_selecionado_idx + 1)
        elif key in [glfw.KEY_ENTER, glfw.KEY_SPACE]:
            return self.botoes[self.item_selecionado_idx]['id']
        return None

class MenuDerrota(Menu):
    def __init__(self, text_renderer, textura_titulo=None):
        super().__init__(text_renderer, textura_titulo)
        self.COR_FUNDO = (0.3, 0.0, 0.0, 1.0)  # Vermelho
        self.botoes = [
            {'texto': 'Tentar Novamente', 'id': 'replay'},
            {'texto': 'Alterar Dificuldade', 'id': 'dificuldade'},
            {'texto': 'Menu Principal', 'id': 'menu'}
        ]
    
    def desenhar(self, largura_janela, altura_janela):
        self.configurar_viewport_2d(largura_janela, altura_janela)
        
        # Desenha o fundo: gradiente e ondas (sem notas a cair)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # Limpa a tela
        self.desenhar_gradiente(largura_janela, altura_janela) # Desenha o gradiente
        
        # Desenha as ondas (copiado de desenhar_fundo_animado)
        self.tempo_animacao += 0.02
        num_ondas = 8 # Aumenta o número de ondas
        for i in range(num_ondas):
            fase = self.tempo_animacao + i * 1.5 # Ajusta a fase para espaçar as ondas
            # Ajusta a posição vertical para distribuir as 8 ondas
            y_pos = altura_janela * (0.1 + i * (0.8 / (num_ondas - 1)))
            self.desenhar_onda(0, y_pos, 
                             20, 0.01, fase, self.COR_ONDAS, largura_janela)
        
        # Desenha o título com textura
        if self.textura_titulo:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.textura_titulo)
            
            # Dimensões da textura (assumindo que a textura tem um tamanho razoável)
            largura_titulo = 800 # Mesma largura do menu principal
            altura_titulo = 300 # Mesma altura do menu principal
            
            x_titulo = (largura_janela - largura_titulo) / 2
            y_titulo = altura_janela - 350 # Mesma posição Y do menu principal
            
            glColor4f(1.0, 1.0, 1.0, 1.0) # Cor branca para não tingir a textura
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0); glVertex2f(x_titulo, y_titulo)
            glTexCoord2f(1.0, 0.0); glVertex2f(x_titulo + largura_titulo, y_titulo)
            glTexCoord2f(1.0, 1.0); glVertex2f(x_titulo + largura_titulo, y_titulo + altura_titulo)
            glTexCoord2f(0.0, 1.0); glVertex2f(x_titulo, y_titulo + altura_titulo)
            glEnd()
            
            glDisable(GL_TEXTURE_2D)
        else:
            # Fallback: desenhar texto simples se a textura não carregar
            mensagem_titulo = "DERROTA!"
            tamanho_texto_titulo = 72
            largura_texto_titulo = len(mensagem_titulo) * tamanho_texto_titulo * 0.5
            x_texto_titulo = (largura_janela - largura_texto_titulo) / 2
            y_texto_titulo = altura_janela - 150
            self.text_renderer.draw_text(mensagem_titulo, x_texto_titulo, y_texto_titulo, tamanho_texto_titulo, self.COR_TEXTO_RGB)

        # Mensagem adicional
        mensagem_adicional = "Você perdeu, esgotou-se o tempo"
        tamanho_texto_adicional = 48
        # Obter as dimensões exatas do texto para centralização
        largura_texto_adicional, altura_texto_adicional = self.text_renderer.get_text_dimensions(mensagem_adicional, tamanho_texto_adicional)

        x_texto_adicional = (largura_janela - largura_texto_adicional) / 2
        # Posição abaixo do título texturizado
        # A base do título texturizado está em altura_janela - 350
        y_texto_adicional = (altura_janela - 350) - 50 # Subtrai um offset para posicionar abaixo
        self.text_renderer.draw_text(mensagem_adicional, x_texto_adicional, y_texto_adicional, tamanho_texto_adicional, self.COR_TEXTO_RGB)

        # Desenha botões
        self.botoes_rects = []
        y_botao = altura_janela / 2
        
        for i, botao in enumerate(self.botoes):
            x_botao = (largura_janela - self.largura_botao) / 2
            y_atual = y_botao - i * (self.altura_botao + self.espacamento_botoes)
            
            cor_botao = self.COR_BOTAO_SELECIONADO if i == self.item_selecionado_idx else self.COR_BOTAO
            self.desenhar_retangulo_2d(x_botao, y_atual, self.largura_botao, self.altura_botao, cor_botao, True)
            
            self.botoes_rects.append({
                'x': x_botao,
                'y': y_atual,
                'largura': self.largura_botao,
                'altura': self.altura_botao,
                'id': botao['id']
            })
            
            texto = botao['texto']
            tamanho_texto = 48
            largura_texto, altura_texto = self.text_renderer.get_text_dimensions(texto, tamanho_texto)
            x_texto = x_botao + (self.largura_botao - largura_texto) / 2
            y_texto = y_atual + (self.altura_botao - altura_texto) / 2
            self.text_renderer.draw_text(texto, x_texto, y_texto, tamanho_texto, self.COR_TEXTO_RGB)
        
        self.restaurar_viewport()
    
    def processar_mouse(self, rato_x, rato_y_opengl, action=None):
        # Update selected item based on mouse position for hover effect
        self.item_selecionado_idx = -1 # Reset selection
        for i, botao_rect in enumerate(self.botoes_rects):
            if self._cursor_dentro(rato_x, rato_y_opengl, botao_rect):
                self.item_selecionado_idx = i
                # If action is PRESS, also return the button id for click handling
                if action == glfw.PRESS:
                    return self.botoes_rects[i]['id']
        return None # No action to return for hover or click outside buttons

    def processar_teclado(self, key):
        if key in [glfw.KEY_UP, glfw.KEY_W]:
            self.item_selecionado_idx = max(0, self.item_selecionado_idx - 1)
        elif key in [glfw.KEY_DOWN, glfw.KEY_S]:
            self.item_selecionado_idx = min(len(self.botoes) - 1, self.item_selecionado_idx + 1)
        elif key in [glfw.KEY_ENTER, glfw.KEY_SPACE]:
            if self.item_selecionado_idx >= 0:
                return self.botoes[self.item_selecionado_idx]['id']
        elif key == glfw.KEY_ESCAPE:
            return 'menu'
        return None

class MenuDificuldade(Menu):
    def __init__(self, text_renderer, textura_titulo=None):
        super().__init__(text_renderer, textura_titulo)
        self.botoes = [
            {'texto': 'Normal', 'id': 'normal'},
            {'texto': 'Difícil', 'id': 'dificil'},
            {'texto': 'Impossível', 'id': 'impossivel'},
            {'texto': 'Voltar', 'id': 'voltar'}
        ]
        self.estado = 'menu'
        self.tecla_atual = None
    
    def desenhar(self, largura_janela, altura_janela):
        self.configurar_viewport_2d(largura_janela, altura_janela)
        
        # Desenha fundo animado
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.desenhar_fundo_animado(largura_janela, altura_janela)
        
        # Título - Usa a imagem do título se disponível
        if self.textura_titulo is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.textura_titulo)
            glColor4f(1.0, 1.0, 1.0, 1.0) # Cor branca para não tingir a textura
            
            # Define a posição e tamanho do quad para a textura do título
            # Ajuste estes valores conforme o tamanho da imagem e onde quer que apareça
            # Usar os mesmos valores do menu principal, mas ajustar a posição vertical para o menu de dificuldade
            largura_titulo_img = 800 # Exemplo: ajuste a largura desejada
            altura_titulo_img = 300 # Exemplo: ajuste a altura desejada (aumentado)
            x_titulo_img = (largura_janela - largura_titulo_img) / 2
            y_titulo_img = altura_janela - 350 # Ajuste a posição vertical para o menu de dificuldade (mesma altura que o menu principal)
            
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0); glVertex2f(x_titulo_img, y_titulo_img)
            glTexCoord2f(1.0, 0.0); glVertex2f(x_titulo_img + largura_titulo_img, y_titulo_img)
            glTexCoord2f(1.0, 1.0); glVertex2f(x_titulo_img + largura_titulo_img, y_titulo_img + altura_titulo_img)
            glTexCoord2f(0.0, 1.0); glVertex2f(x_titulo_img, y_titulo_img + altura_titulo_img)
            glEnd()
            
            glDisable(GL_TEXTURE_2D)
        else:
            # Fallback para texto se a textura não carregar
            titulo = "SELECIONE A DIFICULDADE"
            tamanho_titulo = 64
            largura_titulo = len(titulo) * tamanho_titulo * 0.4
            x_titulo = (largura_janela - largura_titulo) / 2
            y_titulo = altura_janela - 150
            self.text_renderer.draw_text(titulo, x_titulo, y_titulo, tamanho_titulo, self.COR_TITULO_RGB)
        
        # Botões
        self.botoes_rects = []
        y_botao = altura_janela / 2
        
        for i, botao in enumerate(self.botoes):
            x_botao = (largura_janela - self.largura_botao) / 2
            y_atual = y_botao - i * (self.altura_botao + self.espacamento_botoes)
            
            cor_botao = self.COR_BOTAO_SELECIONADO if i == self.item_selecionado_idx else self.COR_BOTAO
            self.desenhar_retangulo_2d(x_botao, y_atual, self.largura_botao, self.altura_botao, cor_botao, True)
            
            self.botoes_rects.append({
                'x': x_botao,
                'y': y_atual,
                'largura': self.largura_botao,
                'altura': self.altura_botao,
                'id': botao['id']
            })
            
            texto = botao['texto']
            tamanho_texto = 48
            largura_texto, altura_texto = self.text_renderer.get_text_dimensions(texto, tamanho_texto)

            x_texto = x_botao + (self.largura_botao - largura_texto) / 2
            # Centralizar verticalmente usando a altura exata do texto
            y_texto = y_atual + (self.altura_botao - altura_texto) / 2
            self.text_renderer.draw_text(texto, x_texto, y_texto, tamanho_texto, self.COR_TEXTO_RGB)
        
        self.restaurar_viewport()

    def processar_mouse(self, rato_x, rato_y_opengl, action=None):
        # Update selected item based on mouse position for hover effect
        self.item_selecionado_idx = -1 # Reset selection
        for i, botao_rect in enumerate(self.botoes_rects):
            if self._cursor_dentro(rato_x, rato_y_opengl, botao_rect):
                self.item_selecionado_idx = i
                # If action is PRESS, also return the button id for click handling
                if action == glfw.PRESS:
                    return self.botoes_rects[i]['id']
        return None # No action to return for hover or click outside buttons

    def processar_teclado(self, key):
        if key in [glfw.KEY_UP, glfw.KEY_W]:
            self.item_selecionado_idx = max(0, self.item_selecionado_idx - 1)
        elif key in [glfw.KEY_DOWN, glfw.KEY_S]:
            self.item_selecionado_idx = min(len(self.botoes) - 1, self.item_selecionado_idx + 1)
        elif key in [glfw.KEY_ENTER, glfw.KEY_SPACE]:
            return self.botoes[self.item_selecionado_idx]['id']
        elif key == glfw.KEY_ESCAPE:
            return 'voltar'
        return None

class MenuConfiguracoes(Menu):
    def __init__(self, text_renderer, config_manager, textura_titulo=None):
        super().__init__(text_renderer, textura_titulo)
        self.config_manager = config_manager
        self.opcoes = [
            {'texto': 'Alterar Teclas', 'id': 'alterar_teclas'},
            {'texto': 'Alterar Volume', 'id': 'ajustar_volume'},
            {'texto': 'Voltar', 'id': 'voltar'}
        ]
        self.estado = 'menu'
        self.tecla_atual = None
        self.volume_atual = self.config_manager.get_volume()
        self.volume_ajustando = False
        self.volume_rect = None
        self.item_selecionado_idx = -1
        
        # Mapeamento de ações para nomes amigáveis
        self.nomes_acoes = {
            'move_forward': 'Mover para Frente',
            'move_backward': 'Mover para Trás',
            'move_left': 'Mover para Esquerda',
            'move_right': 'Mover para Direita',
            'jump': 'Pular'
        }
        
        # Mapeamento de códigos GLFW para nomes de teclas
        self.nomes_teclas = {
            87: 'W', 83: 'S', 65: 'A', 68: 'D', 32: 'ESPAÇO',
            265: 'SETA_CIMA', 264: 'SETA_BAIXO', 263: 'SETA_ESQUERDA', 262: 'SETA_DIREITA',
            340: 'SHIFT_ESQ', 341: 'CTRL_ESQ', 342: 'ALT_ESQ',
            344: 'SHIFT_DIR', 345: 'CTRL_DIR', 346: 'ALT_DIR' # Adicionar teclas modificadoras direitas
        }

        # Adicionar o alfabeto completo
        for i in range(65, 91): # Códigos ASCII para A-Z
            self.nomes_teclas[i] = chr(i)

    def _get_nome_tecla(self, codigo):
        return self.nomes_teclas.get(codigo, f'Tecla {codigo}')

    def _atualizar_volume(self, rato_x):
        """Converte a posição X do rato em [0-1] e actualiza tudo."""
        x_slider = self.volume_rect['x']
        largura_slider = self.volume_rect['largura']
        rel = max(0.0, min(1.0, (rato_x - x_slider) / largura_slider))
        self.volume_atual = rel
        self.config_manager.set_volume(rel)
        pygame.mixer.music.set_volume(rel)

    def desenhar(self, largura_janela, altura_janela):
        self.configurar_viewport_2d(largura_janela, altura_janela)
        self.desenhar_fundo_animado(largura_janela, altura_janela)
        
        # Título
        if self.textura_titulo is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.textura_titulo)
            glColor4f(1.0, 1.0, 1.0, 1.0)
            
            largura_titulo_img = 800
            altura_titulo_img = 300
            x_titulo_img = (largura_janela - largura_titulo_img) / 2
            y_titulo_img = altura_janela - 350
            
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0); glVertex2f(x_titulo_img, y_titulo_img)
            glTexCoord2f(1.0, 0.0); glVertex2f(x_titulo_img + largura_titulo_img, y_titulo_img)
            glTexCoord2f(1.0, 1.0); glVertex2f(x_titulo_img + largura_titulo_img, y_titulo_img + altura_titulo_img)
            glTexCoord2f(0.0, 1.0); glVertex2f(x_titulo_img, y_titulo_img + altura_titulo_img)
            glEnd()
            
            glDisable(GL_TEXTURE_2D)
        
        if self.estado == 'menu':
            # Desenha as opções do menu
            y_botao = altura_janela / 2
            self.botoes_rects = []
            
            for i, opcao in enumerate(self.opcoes):
                cor_botao = self.COR_BOTAO_SELECIONADO if i == self.item_selecionado_idx else self.COR_BOTAO
                x_botao = (largura_janela - self.largura_botao) / 2
                y_atual = y_botao - i * (self.altura_botao + self.espacamento_botoes)
                
                self.desenhar_retangulo_2d(x_botao, y_atual, self.largura_botao, self.altura_botao, cor_botao, True)
                
                self.botoes_rects.append({
                    'x': x_botao,
                    'y': y_atual,
                    'largura': self.largura_botao,
                    'altura': self.altura_botao,
                    'id': opcao['id']
                })
                
                texto = opcao['texto']
                tamanho_texto = 48
                largura_texto, altura_texto = self.text_renderer.get_text_dimensions(texto, tamanho_texto)

                x_texto = x_botao + (self.largura_botao - largura_texto) / 2
                # Centralizar verticalmente usando a altura exata do texto
                y_texto = y_atual + (self.altura_botao - altura_texto) / 2
                self.text_renderer.draw_text(texto, x_texto, y_texto, tamanho_texto, self.COR_TEXTO_RGB)
        
        elif self.estado == 'ajustar_volume':
            # Desenha o slider de volume
            slider_largura = 400
            slider_altura = 40
            x_slider = (largura_janela - slider_largura) / 2
            y_slider = altura_janela / 2
            
            # Desenha o fundo do slider
            self.desenhar_retangulo_2d(x_slider, y_slider, slider_largura, slider_altura, self.COR_BOTAO, True)
            
            # Desenha o indicador de volume
            indicador_largura = 20
            indicador_pos = x_slider + (slider_largura - indicador_largura) * self.volume_atual
            self.desenhar_retangulo_2d(indicador_pos, y_slider - 10, indicador_largura, slider_altura + 20, self.COR_BOTAO_SELECIONADO, True)
            
            # Guarda o retângulo do slider para deteção de clique
            self.volume_rect = {
                'x': x_slider,
                'y': y_slider - 10,
                'largura': slider_largura,
                'altura': slider_altura + 20
            }
            
            # Desenha o texto do volume
            texto_volume = f"Volume: {int(self.volume_atual * 100)}%"
            tamanho_texto = 48
            largura_texto, altura_texto_volume = self.text_renderer.get_text_dimensions(texto_volume, tamanho_texto)
            x_texto = (largura_janela - largura_texto) / 2
            y_texto = y_slider + slider_altura + 50
            self.text_renderer.draw_text(texto_volume, x_texto, y_texto, tamanho_texto, self.COR_TEXTO_RGB)
            
            # Desenha instruções de ajuste
            texto_ajuste = "Clique e arraste para ajustar o volume."
            tamanho_ajuste = 32
            largura_ajuste, altura_ajuste_texto = self.text_renderer.get_text_dimensions(texto_ajuste, tamanho_ajuste)
            x_ajuste = (largura_janela - largura_ajuste) / 2
            y_ajuste = y_slider - 80
            self.text_renderer.draw_text(texto_ajuste, x_ajuste, y_ajuste, tamanho_ajuste, self.COR_TEXTO_RGB)
            
            # Botão Voltar
            self.botoes_rects = [] # Limpa a lista de botões para este estado
            y_voltar = y_ajuste - self.altura_botao - self.espacamento_botoes
            x_voltar = (largura_janela - self.largura_botao) / 2
            
            # O botão de voltar não tem hover no estado de ajuste de volume com mouse, então sempre cor normal
            cor_botao_voltar = self.COR_BOTAO
            self.desenhar_retangulo_2d(x_voltar, y_voltar, self.largura_botao, self.altura_botao, cor_botao_voltar, True)
            
            # Adiciona o botão voltar à lista de rects para interação do mouse
            self.botoes_rects.append({
                'x': x_voltar,
                'y': y_voltar,
                'largura': self.largura_botao,
                'altura': self.altura_botao,
                'id': 'voltar'
            })
            
            texto_voltar = "Voltar"
            tamanho_texto_voltar = 48
            largura_texto_voltar, altura_texto_voltar = self.text_renderer.get_text_dimensions(texto_voltar, tamanho_texto_voltar)
            x_texto_voltar = x_voltar + (self.largura_botao - largura_texto_voltar) / 2
            y_texto_voltar = y_voltar + (self.altura_botao - altura_texto_voltar) / 2
            self.text_renderer.draw_text(texto_voltar, x_texto_voltar, y_texto_voltar, tamanho_texto_voltar, self.COR_TEXTO_RGB)
        
        elif self.estado == 'alterar_teclas':
            # Desenha a lista de teclas
            y_inicio = altura_janela / 2 + 100
            espacamento = 60
            
            # Título da seção
            texto_titulo = "CONFIGURAÇÃO DE TECLAS"
            tamanho_titulo = 48
            largura_titulo, altura_titulo_texto = self.text_renderer.get_text_dimensions(texto_titulo, tamanho_titulo)
            x_titulo = (largura_janela - largura_titulo) / 2
            y_titulo = y_inicio + 100
            self.text_renderer.draw_text(texto_titulo, x_titulo, y_titulo, tamanho_titulo, self.COR_TITULO_RGB)
            
            # Instruções
            texto_instrucoes = "Clique em uma ação para alterar sua tecla."
            tamanho_instrucoes = 32
            largura_instrucoes, altura_instrucoes_texto = self.text_renderer.get_text_dimensions(texto_instrucoes, tamanho_instrucoes)
            x_instrucoes = (largura_janela - largura_instrucoes) / 2
            y_instrucoes = y_titulo - 50
            self.text_renderer.draw_text(texto_instrucoes, x_instrucoes, y_instrucoes, tamanho_instrucoes, self.COR_TEXTO_RGB)
            
            # Lista de teclas
            self.botoes_rects = []
            for i, (acao, nome) in enumerate(self.nomes_acoes.items()):
                y_atual = y_inicio - i * espacamento
                
                # Desenha o nome da ação
                texto_acao = nome
                tamanho_texto = 36
                x_acao = largura_janela / 2 - 200
                self.text_renderer.draw_text(texto_acao, x_acao, y_atual, tamanho_texto, self.COR_TEXTO_RGB)
                
                # Desenha o botão com a tecla atual
                tecla_atual = self.config_manager.get_key_binding(acao)
                nome_tecla = self._get_nome_tecla(tecla_atual)
                
                largura_botao_tecla = 180 # Aumenta a largura do botão da tecla
                altura_botao_tecla = 50 # Aumenta a altura do botão da tecla
                x_botao = largura_janela / 2 + 50
                
                # Destaca o botão se estiver selecionado
                cor_botao = self.COR_BOTAO_SELECIONADO if self.tecla_atual == acao else self.COR_BOTAO # Cor do botão
                self.desenhar_retangulo_2d(x_botao, y_atual - (altura_botao_tecla - 40) / 2, largura_botao_tecla, altura_botao_tecla, cor_botao, True)
                
                self.botoes_rects.append({
                    'x': x_botao,
                    'y': y_atual - (altura_botao_tecla - 40) / 2, # Ajusta a posição Y para centralizar verticalmente com o texto da ação original
                    'largura': largura_botao_tecla,
                    'altura': altura_botao_tecla,
                    'id': acao
                })
                
                # Desenha o nome da tecla ou o texto de espera
                tamanho_texto_tecla = 36 # Tamanho do texto da tecla ou "Pressione uma tecla..."
                
                if self.tecla_atual == acao:
                    texto_espera = "Pressione uma tecla..."
                    largura_texto_espera, altura_texto_espera = self.text_renderer.get_text_dimensions(texto_espera, tamanho_texto_tecla)
                    # Posiciona o texto de espera à direita do botão
                    x_texto_espera = x_botao + largura_botao_tecla + 20 # 20 pixels de espaço
                    y_texto_espera = y_atual + (40 - altura_texto_espera) / 2 # Centraliza verticalmente com a linha de texto da ação original
                    self.text_renderer.draw_text(texto_espera, x_texto_espera, y_texto_espera, tamanho_texto_tecla, self.COR_TITULO_RGB)
                else:
                    largura_texto_tecla, altura_texto_tecla = self.text_renderer.get_text_dimensions(nome_tecla, tamanho_texto_tecla)
                    # Centraliza o nome da tecla dentro do botão
                    x_texto_tecla = x_botao + (largura_botao_tecla - largura_texto_tecla) / 2
                    y_texto_tecla = y_atual - (altura_botao_tecla - 40) / 2 + (altura_botao_tecla - altura_texto_tecla) / 2 # Centraliza verticalmente no novo tamanho do botão
                    self.text_renderer.draw_text(nome_tecla, x_texto_tecla, y_texto_tecla, tamanho_texto_tecla, self.COR_TEXTO_RGB)
            
            # Botão Voltar
            y_voltar = y_inicio - (len(self.nomes_acoes) + 1) * espacamento
            x_voltar = (largura_janela - self.largura_botao) / 2
            
            cor_botao = self.COR_BOTAO_SELECIONADO if self.item_selecionado_idx == -1 else self.COR_BOTAO
            self.desenhar_retangulo_2d(x_voltar, y_voltar, self.largura_botao, self.altura_botao, cor_botao, True)
            
            self.botoes_rects.append({
                'x': x_voltar,
                'y': y_voltar,
                'largura': self.largura_botao,
                'altura': self.altura_botao,
                'id': 'voltar'
            })
            
            texto_voltar = "Voltar"
            tamanho_texto = 48
            largura_texto, altura_texto = self.text_renderer.get_text_dimensions(texto_voltar, tamanho_texto)
            x_texto = x_voltar + (self.largura_botao - largura_texto) / 2
            y_texto = y_voltar + (self.altura_botao - altura_texto) / 2
            self.text_renderer.draw_text(texto_voltar, x_texto, y_texto, tamanho_texto, self.COR_TEXTO_RGB)
        
        self.restaurar_viewport()

    def processar_mouse(self, rato_x, rato_y_opengl, action):
        if self.estado == 'menu':
            novo_idx = -1
            for i, botao in enumerate(self.botoes_rects):
                if self._cursor_dentro(rato_x, rato_y_opengl, botao):
                    novo_idx = i
                    if action == glfw.PRESS:
                        if botao['id'] == 'ajustar_volume':
                            self.estado = 'ajustar_volume'
                        elif botao['id'] == 'alterar_teclas':
                            self.estado = 'alterar_teclas'
                        return botao['id']
            self.item_selecionado_idx = novo_idx
            return None

        elif self.estado == 'ajustar_volume':
            if action == glfw.PRESS:
                # Começa a arrastar se clicas em cima do slider
                if self._cursor_dentro(rato_x, rato_y_opengl, self.volume_rect):
                    self.volume_ajustando = True
                    self._atualizar_volume(rato_x)
                # Verifica clique no botão voltar
                for botao in self.botoes_rects:
                    if botao['id'] == 'voltar' and self._cursor_dentro(rato_x, rato_y_opengl, botao):
                        self.estado = 'menu'
                        self.volume_ajustando = False
                        return 'voltar'
            elif action == glfw.RELEASE:
                # Ao soltar o botão, desativa o arrasto
                self.volume_ajustando = False
            # Retorna None mesmo quando estiver ajustando para não mudar de estado
            return None

        elif self.estado == 'alterar_teclas':
            if action == glfw.PRESS:
                for botao in self.botoes_rects:
                    if self._cursor_dentro(rato_x, rato_y_opengl, botao):
                        if botao['id'] == 'voltar':
                            self.estado = 'menu'
                            self.tecla_atual = None
                            return 'voltar'
                        self.tecla_atual = botao['id']
                        return None
            return None

        return None

    def mouse_move(self, rato_x, rato_y_opengl):
        # Somente atualiza o volume se o botão estiver pressionado (volume_ajustando == True)
        if self.estado == 'ajustar_volume' and self.volume_ajustando:
            self._atualizar_volume(rato_x)
        elif self.estado == 'ajustar_volume':
            # Atualiza o hover do botão voltar no ajuste de volume
            for botao in self.botoes_rects:
                if botao['id'] == 'voltar' and self._cursor_dentro(rato_x, rato_y_opengl, botao):
                    # No estado de ajuste de volume, não há seleção de item por hover para o botão voltar via mouse
                    pass # Manter a cor normal

        elif self.estado == 'alterar_teclas':
            # Atualiza o hover do botão voltar
            for botao in self.botoes_rects:
                if botao['id'] == 'voltar' and self._cursor_dentro(rato_x, rato_y_opengl, botao):
                    self.item_selecionado_idx = -1
                    return
            self.item_selecionado_idx = -2

    def processar_teclado(self, key):
        if self.estado == 'menu':
            if key in [glfw.KEY_UP, glfw.KEY_W]:
                self.item_selecionado_idx = max(0, self.item_selecionado_idx - 1)
            elif key in [glfw.KEY_DOWN, glfw.KEY_S]:
                self.item_selecionado_idx = min(len(self.opcoes) - 1, self.item_selecionado_idx + 1)
            elif key in [glfw.KEY_ENTER, glfw.KEY_SPACE]:
                if self.item_selecionado_idx >= 0:
                    selected_id = self.opcoes[self.item_selecionado_idx]['id']
                    if selected_id == 'ajustar_volume':
                        self.estado = 'ajustar_volume'
                    elif selected_id == 'alterar_teclas':
                        self.estado = 'alterar_teclas'
                    return selected_id
            elif key == glfw.KEY_ESCAPE:
                return 'voltar'
        
        elif self.estado == 'ajustar_volume' and key == glfw.KEY_ESCAPE:
            self.estado = 'menu'
            self.volume_ajustando = False
            return 'voltar'
        
        elif self.estado == 'alterar_teclas':
            if self.tecla_atual is not None:
                # Verifica se a tecla já está em uso por outra ação
                key_bindings = self.config_manager.config['key_bindings']
                tecla_ja_em_uso = False
                for acao, key_code in key_bindings.items():
                    if key_code == key and acao != self.tecla_atual:
                        tecla_ja_em_uso = True
                        break

                if tecla_ja_em_uso:
                    print(f"Tecla {self._get_nome_tecla(key)} já está atribuída à ação {self.nomes_acoes.get(acao, acao)}.")
                    # Opcional: adicionar feedback visual no futuro
                else:
                    # Atualiza a tecla selecionada apenas se não estiver em uso
                    self.config_manager.set_key_binding(self.tecla_atual, key)

                self.tecla_atual = None # Sai do modo de alteração para esta tecla
                return None
            elif key == glfw.KEY_ESCAPE:
                self.estado = 'menu'
                self.tecla_atual = None
                return 'voltar'

        return None 

class MenuNiveis(Menu):
    def __init__(self, text_renderer, textura_titulo=None):
        super().__init__(text_renderer, textura_titulo)
        self.botoes = [
            {'texto': 'Nível 1', 'id': 'nivel1'},
            {'texto': 'Nível 2', 'id': 'nivel2'},
            {'texto': 'Nível 3', 'id': 'nivel3'},
            {'texto': 'Nível 4', 'id': 'nivel4'},
            {'texto': 'Nível 5', 'id': 'nivel5'},
            {'texto': 'Desafio Especial', 'id': 'desafio_especial'},
            {'texto': 'Voltar', 'id': 'voltar'}
        ]
        self.item_selecionado_idx = -1

    def desenhar(self, largura_janela, altura_janela):
        self.configurar_viewport_2d(largura_janela, altura_janela)
        
        # Desenha fundo animado
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.desenhar_fundo_animado(largura_janela, altura_janela)
        
        # Título
        if self.textura_titulo is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.textura_titulo)
            glColor4f(1.0, 1.0, 1.0, 1.0)
            
            largura_titulo_img = 800
            altura_titulo_img = 300
            x_titulo_img = (largura_janela - largura_titulo_img) / 2
            y_titulo_img = altura_janela - 350
            
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0); glVertex2f(x_titulo_img, y_titulo_img)
            glTexCoord2f(1.0, 0.0); glVertex2f(x_titulo_img + largura_titulo_img, y_titulo_img)
            glTexCoord2f(1.0, 1.0); glVertex2f(x_titulo_img + largura_titulo_img, y_titulo_img + altura_titulo_img)
            glTexCoord2f(0.0, 1.0); glVertex2f(x_titulo_img, y_titulo_img + altura_titulo_img)
            glEnd()
            
            glDisable(GL_TEXTURE_2D)
        
        # Botões
        self.botoes_rects = []
        
        # Calcula altura total dos botões para centralização
        total_botoes_altura = len(self.botoes) * self.altura_botao + (len(self.botoes) - 1) * self.espacamento_botoes
        
        # Ajusta a posição inicial dos botões para mais abaixo
        # Usa uma posição mais baixa em relação ao título
        y_botao_start = (altura_janela - 350) - 100  # 100 pixels abaixo do título
        
        for i, botao in enumerate(self.botoes):
            x_botao = (largura_janela - self.largura_botao) / 2
            y_atual = y_botao_start - i * (self.altura_botao + self.espacamento_botoes)
            
            cor_botao = self.COR_BOTAO_SELECIONADO if i == self.item_selecionado_idx else self.COR_BOTAO
            self.desenhar_retangulo_2d(x_botao, y_atual, self.largura_botao, self.altura_botao, cor_botao, True)
            
            self.botoes_rects.append({
                'x': x_botao,
                'y': y_atual,
                'largura': self.largura_botao,
                'altura': self.altura_botao,
                'id': botao['id']
            })
            
            texto = botao['texto']
            tamanho_texto = 48
            largura_texto, altura_texto = self.text_renderer.get_text_dimensions(texto, tamanho_texto)

            x_texto = x_botao + (self.largura_botao - largura_texto) / 2
            y_texto = y_atual + (self.altura_botao - altura_texto) / 2
            self.text_renderer.draw_text(texto, x_texto, y_texto, tamanho_texto, self.COR_TEXTO_RGB)
        
        self.restaurar_viewport()

    def processar_teclado(self, key):
        if key in [glfw.KEY_UP, glfw.KEY_W]:
            self.item_selecionado_idx = max(0, self.item_selecionado_idx - 1)
        elif key in [glfw.KEY_DOWN, glfw.KEY_S]:
            self.item_selecionado_idx = min(len(self.botoes) - 1, self.item_selecionado_idx + 1)
        elif key in [glfw.KEY_ENTER, glfw.KEY_SPACE]:
            if self.item_selecionado_idx >= 0:
                return self.botoes[self.item_selecionado_idx]['id']
        elif key == glfw.KEY_ESCAPE:
            return 'voltar'
        return None 

class MenuPausa(Menu):
    def __init__(self, text_renderer, textura_titulo=None):
        super().__init__(text_renderer, textura_titulo)
        self.COR_FUNDO = (0.0, 0.0, 0.0, 1.0)  # Preto
        self.botoes = [
            {'texto': 'Retomar', 'id': 'retomar'},
            {'texto': 'Configurações', 'id': 'configuracoes'},
            {'texto': 'Menu Principal', 'id': 'menu'}
        ]
    
    def desenhar(self, largura_janela, altura_janela):
        self.configurar_viewport_2d(largura_janela, altura_janela)
        
        # Desenha o fundo: gradiente e ondas (sem notas a cair)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # Limpa a tela
        self.desenhar_gradiente(largura_janela, altura_janela) # Desenha o gradiente
        
        # Desenha as ondas (copiado de desenhar_fundo_animado)
        self.tempo_animacao += 0.02
        num_ondas = 8 # Aumenta o número de ondas
        for i in range(num_ondas):
            fase = self.tempo_animacao + i * 1.5 # Ajusta a fase para espaçar as ondas
            # Ajusta a posição vertical para distribuir as 8 ondas
            y_pos = altura_janela * (0.1 + i * (0.8 / (num_ondas - 1)))
            self.desenhar_onda(0, y_pos, 
                             20, 0.01, fase, self.COR_ONDAS, largura_janela)
        
        # Desenha o título com textura
        if self.textura_titulo:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.textura_titulo)
            
            # Dimensões da textura (assumindo que a textura tem um tamanho razoável)
            largura_titulo = 800 # Mesma largura do menu principal
            altura_titulo = 300 # Mesma altura do menu principal
            
            x_titulo = (largura_janela - largura_titulo) / 2
            y_titulo = altura_janela - 350 # Mesma posição Y do menu principal
            
            glColor4f(1.0, 1.0, 1.0, 1.0) # Cor branca para não tingir a textura
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0); glVertex2f(x_titulo, y_titulo)
            glTexCoord2f(1.0, 0.0); glVertex2f(x_titulo + largura_titulo, y_titulo)
            glTexCoord2f(1.0, 1.0); glVertex2f(x_titulo + largura_titulo, y_titulo + altura_titulo)
            glTexCoord2f(0.0, 1.0); glVertex2f(x_titulo, y_titulo + altura_titulo)
            glEnd()
            
            glDisable(GL_TEXTURE_2D)
        else:
            # Fallback: desenhar texto simples se a textura não carregar
            mensagem_titulo = "PAUSA"
            tamanho_texto_titulo = 72
            largura_texto_titulo = len(mensagem_titulo) * tamanho_texto_titulo * 0.5
            x_texto_titulo = (largura_janela - largura_texto_titulo) / 2
            y_texto_titulo = altura_janela - 150
            self.text_renderer.draw_text(mensagem_titulo, x_texto_titulo, y_texto_titulo, tamanho_texto_titulo, (255, 255, 255))

        # Desenha botões
        self.botoes_rects = []
        y_botao = altura_janela / 2
        
        for i, botao in enumerate(self.botoes):
            x_botao = (largura_janela - self.largura_botao) / 2
            y_atual = y_botao - i * (self.altura_botao + self.espacamento_botoes)
            
            cor_botao = self.COR_BOTAO_SELECIONADO if i == self.item_selecionado_idx else self.COR_BOTAO
            self.desenhar_retangulo_2d(x_botao, y_atual, self.largura_botao, self.altura_botao, cor_botao, True)
            
            self.botoes_rects.append({
                'x': x_botao,
                'y': y_atual,
                'largura': self.largura_botao,
                'altura': self.altura_botao,
                'id': botao['id']
            })
            
            texto = botao['texto']
            tamanho_texto = 48
            # Obter as dimensões exatas do texto para centralização
            largura_texto, altura_texto = self.text_renderer.get_text_dimensions(texto, tamanho_texto)

            x_texto = x_botao + (self.largura_botao - largura_texto) / 2
            # Centralizar verticalmente usando a altura exata do texto
            y_texto = y_atual + (self.altura_botao - altura_texto) / 2
            self.text_renderer.draw_text(texto, x_texto, y_texto, tamanho_texto, self.COR_TEXTO_RGB)
        
        self.restaurar_viewport()
    
    def processar_mouse(self, rato_x, rato_y_opengl, action=None):
        # Update selected item based on mouse position for hover effect
        self.item_selecionado_idx = -1 # Reset selection
        for i, botao_rect in enumerate(self.botoes_rects):
            if self._cursor_dentro(rato_x, rato_y_opengl, botao_rect):
                self.item_selecionado_idx = i
                # If action is PRESS, also return the button id for click handling
                if action == glfw.PRESS:
                    return self.botoes_rects[i]['id']
        return None # No action to return for hover or click outside buttons

    def processar_teclado(self, key):
        if key in [glfw.KEY_UP, glfw.KEY_W]:
            self.item_selecionado_idx = max(0, self.item_selecionado_idx - 1)
        elif key in [glfw.KEY_DOWN, glfw.KEY_S]:
            self.item_selecionado_idx = min(len(self.botoes) - 1, self.item_selecionado_idx + 1)
        elif key in [glfw.KEY_ENTER, glfw.KEY_SPACE]:
            if self.item_selecionado_idx >= 0:
                return self.botoes[self.item_selecionado_idx]['id']
        return None 

class MenuFimDesafio(Menu):
    def __init__(self, text_renderer, textura_titulo=None):
        super().__init__(text_renderer, textura_titulo)
        self.botoes = [
            {'texto': 'Tentar Novamente', 'id': 'replay'},
            {'texto': 'Selecionar Nivel', 'id': 'niveis'},
            {'texto': 'Dificuldade', 'id': 'dificuldade'},
            {'texto': 'Menu Principal', 'id': 'menu'}
        ]
        self.item_selecionado_idx = -1
        
    def desenhar(self, largura_janela, altura_janela, score, highscore, data_highscore="", nome_dificuldade="Normal"):
        self.configurar_viewport_2d(largura_janela, altura_janela)
        
        # Desenha fundo animado
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.desenhar_fundo_animado(largura_janela, altura_janela)
        
        # Mensagem de tempo esgotado
        mensagem = "ACABOU O TEMPO"
        tamanho_texto = 64
        largura_texto, altura_texto = self.text_renderer.get_text_dimensions(mensagem, tamanho_texto)
        x_texto = (largura_janela - largura_texto) / 2
        y_texto = altura_janela - 200
        self.text_renderer.draw_text(mensagem, x_texto, y_texto, tamanho_texto, (255, 215, 0))  # Dourado
        
        # Mostra a dificuldade atual
        mensagem_dificuldade = f"Dificuldade: {nome_dificuldade}"
        tamanho_texto_dificuldade = 40
        largura_texto_dificuldade, altura_texto_dificuldade = self.text_renderer.get_text_dimensions(mensagem_dificuldade, tamanho_texto_dificuldade)
        x_texto_dificuldade = (largura_janela - largura_texto_dificuldade) / 2
        y_texto_dificuldade = y_texto - 70  # 70 pixels abaixo da mensagem principal
        self.text_renderer.draw_text(mensagem_dificuldade, x_texto_dificuldade, y_texto_dificuldade, tamanho_texto_dificuldade, (255, 255, 255))  # Branco
        
        # Mostra o score
        mensagem_score = f"Score: {score}"
        tamanho_texto_score = 48
        largura_texto_score, altura_texto_score = self.text_renderer.get_text_dimensions(mensagem_score, tamanho_texto_score)
        x_texto_score = (largura_janela - largura_texto_score) / 2
        y_texto_score = y_texto_dificuldade - 70  # 70 pixels abaixo da dificuldade
        self.text_renderer.draw_text(mensagem_score, x_texto_score, y_texto_score, tamanho_texto_score, (255, 255, 255))  # Branco
        
        # Mostra o highscore
        mensagem_highscore = f"Highscore: {highscore}"
        largura_texto_highscore, altura_texto_highscore = self.text_renderer.get_text_dimensions(mensagem_highscore, tamanho_texto_score)
        x_texto_highscore = (largura_janela - largura_texto_highscore) / 2
        y_texto_highscore = y_texto_score - 70  # 70 pixels abaixo do score
        
        # Usa cor dourada para o highscore se o score atual for igual ao highscore
        cor_highscore = (255, 215, 0) if score >= highscore else (255, 255, 255)
        self.text_renderer.draw_text(mensagem_highscore, x_texto_highscore, y_texto_highscore, tamanho_texto_score, cor_highscore)
        
        # Mostra a data do highscore, se disponível
        if data_highscore:
            tamanho_texto_data = 28  # Texto menor para a data
            mensagem_data = f"Recorde obtido em: {data_highscore}"
            largura_texto_data, altura_texto_data = self.text_renderer.get_text_dimensions(mensagem_data, tamanho_texto_data)
            x_texto_data = (largura_janela - largura_texto_data) / 2
            y_texto_data = y_texto_highscore - 40  # 40 pixels abaixo do highscore
            self.text_renderer.draw_text(mensagem_data, x_texto_data, y_texto_data, tamanho_texto_data, cor_highscore)
            
            # Ajusta a posição dos botões para dar espaço à nova informação
            y_botao = y_texto_data - 110  # 110 pixels abaixo da data
        else:
            # Sem a data, mantém o layout original
            y_botao = y_texto_highscore - 150
        
        # Botões
        self.botoes_rects = []
        
        for i, botao in enumerate(self.botoes):
            x_botao = (largura_janela - self.largura_botao) / 2
            y_atual = y_botao - i * (self.altura_botao + self.espacamento_botoes)
            
            cor_botao = self.COR_BOTAO_SELECIONADO if i == self.item_selecionado_idx else self.COR_BOTAO
            self.desenhar_retangulo_2d(x_botao, y_atual, self.largura_botao, self.altura_botao, cor_botao, True)
            
            self.botoes_rects.append({
                'x': x_botao,
                'y': y_atual,
                'largura': self.largura_botao,
                'altura': self.altura_botao,
                'id': botao['id']
            })
            
            texto = botao['texto']
            tamanho_texto = 48
            largura_texto, altura_texto = self.text_renderer.get_text_dimensions(texto, tamanho_texto)
            x_texto = x_botao + (self.largura_botao - largura_texto) / 2
            y_texto = y_atual + (self.altura_botao - altura_texto) / 2
            self.text_renderer.draw_text(texto, x_texto, y_texto, tamanho_texto, self.COR_TEXTO_RGB)
        
        self.restaurar_viewport()
    
    def processar_mouse(self, rato_x, rato_y_opengl, action=None):
        # Update selected item based on mouse position for hover effect
        self.item_selecionado_idx = -1 # Reset selection
        for i, botao_rect in enumerate(self.botoes_rects):
            if self._cursor_dentro(rato_x, rato_y_opengl, botao_rect):
                self.item_selecionado_idx = i
                # If action is PRESS, also return the button id for click handling
                if action == glfw.PRESS:
                    return self.botoes_rects[i]['id']
        return None # No action to return for hover or click outside buttons

    def processar_teclado(self, key):
        if key in [glfw.KEY_UP, glfw.KEY_W]:
            self.item_selecionado_idx = max(0, self.item_selecionado_idx - 1)
        elif key in [glfw.KEY_DOWN, glfw.KEY_S]:
            self.item_selecionado_idx = min(len(self.botoes) - 1, self.item_selecionado_idx + 1)
        elif key in [glfw.KEY_ENTER, glfw.KEY_SPACE]:
            if self.item_selecionado_idx >= 0:
                return self.botoes[self.item_selecionado_idx]['id']
        elif key == glfw.KEY_ESCAPE:
            return 'menu'
        return None

class MenuCreditos(Menu):
    def __init__(self, text_renderer, textura_titulo=None):
        super().__init__(text_renderer, textura_titulo)
        self.titulo = "Créditos"
        self.botoes = [
            {'texto': 'Voltar', 'id': 'voltar'}
        ]
        self.item_selecionado_idx = -1
        
        # Informações dos créditos
        self.creditos_texto = [
            "SINFONIA DOS DISCOS",
            "",
            "Desenvolvido por:",
            "João Ventura (79882)",
            "João Guerreiro (81430)",
            "José Lima (79738)",
            "David Piedade (79797)",
            "Leandro Domingos (79889)",
            "",
            "Docente:",
            "Sérgio Jesus",
            "",
            "Universidade:",
            "Universidade do Algarve",
            "",
            "Disciplina:",
            "Computação Gráfica",
            "",
            "Ano Letivo:",
            "2024/2025",
            "",
            "Obrigado por jogar!"
        ]
    
    def desenhar(self, largura_janela, altura_janela):
        self.configurar_viewport_2d(largura_janela, altura_janela)
        
        # Desenha fundo animado
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.desenhar_fundo_animado(largura_janela, altura_janela)
        
        # Título
        if self.textura_titulo is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.textura_titulo)
            glColor4f(1.0, 1.0, 1.0, 1.0)
            
            largura_titulo_img = 600
            altura_titulo_img = 200
            x_titulo_img = (largura_janela - largura_titulo_img) / 2
            y_titulo_img = altura_janela - 250
            
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0); glVertex2f(x_titulo_img, y_titulo_img)
            glTexCoord2f(1.0, 0.0); glVertex2f(x_titulo_img + largura_titulo_img, y_titulo_img)
            glTexCoord2f(1.0, 1.0); glVertex2f(x_titulo_img + largura_titulo_img, y_titulo_img + altura_titulo_img)
            glTexCoord2f(0.0, 1.0); glVertex2f(x_titulo_img, y_titulo_img + altura_titulo_img)
            glEnd()
            
            glDisable(GL_TEXTURE_2D)
        
        # Desenha o texto dos créditos
        inicio_y = altura_janela - 280  # Subido ainda mais para garantir visibilidade
        espacamento_linha = 26  # Reduzido para compactar mais o texto
        
        for i, linha in enumerate(self.creditos_texto):
            if linha == "":  # Linha vazia para espaçamento
                continue
                
            # Determina o tamanho da fonte baseado no tipo de texto
            if linha == "SINFONIA DOS DISCOS":
                tamanho_fonte = 48
                cor = self.COR_TITULO_RGB
            elif linha in ["Desenvolvido por:", "Docente:", "Universidade:", "Disciplina:", "Ano Letivo:"]:
                tamanho_fonte = 32
                cor = (255, 215, 0)  # Dourado para títulos de seção
            else:
                tamanho_fonte = 24
                cor = self.COR_TEXTO_RGB
            
            largura_texto, altura_texto = self.text_renderer.get_text_dimensions(linha, tamanho_fonte)
            x_texto = (largura_janela - largura_texto) / 2
            y_texto = inicio_y - i * espacamento_linha
            
            self.text_renderer.draw_text(linha, x_texto, y_texto, tamanho_fonte, cor)
        
        # Botão de voltar
        self.botoes_rects = []
        y_botao = 150  # Posição fixa perto da parte inferior
        
        for i, botao in enumerate(self.botoes):
            x_botao = (largura_janela - self.largura_botao) / 2
            
            # Efeito de hover
            cor_botao = self.COR_BOTAO_SELECIONADO if i == self.item_selecionado_idx else self.COR_BOTAO
            self.desenhar_retangulo_2d(x_botao, y_botao, self.largura_botao, self.altura_botao, cor_botao, True)
            
            self.botoes_rects.append({
                'x': x_botao,
                'y': y_botao,
                'largura': self.largura_botao,
                'altura': self.altura_botao,
                'id': botao['id']
            })
            
            texto = botao['texto']
            tamanho_texto = 48
            largura_texto, altura_texto = self.text_renderer.get_text_dimensions(texto, tamanho_texto)
            x_texto = x_botao + (self.largura_botao - largura_texto) / 2
            y_texto = y_botao + (self.altura_botao - altura_texto) / 2
            self.text_renderer.draw_text(texto, x_texto, y_texto, tamanho_texto, self.COR_TEXTO_RGB)
        
        self.restaurar_viewport()
    
    def processar_mouse(self, rato_x, rato_y_opengl, action=None):
        # Atualiza item selecionado baseado na posição do mouse
        self.item_selecionado_idx = -1
        for i, botao_rect in enumerate(self.botoes_rects):
            if self._cursor_dentro(rato_x, rato_y_opengl, botao_rect):
                self.item_selecionado_idx = i
                if action == glfw.PRESS:
                    return botao_rect['id']
        return None
    
    def processar_teclado(self, key):
        if key in [glfw.KEY_UP, glfw.KEY_W]:
            self.item_selecionado_idx = max(0, self.item_selecionado_idx - 1)
        elif key in [glfw.KEY_DOWN, glfw.KEY_S]:
            self.item_selecionado_idx = min(len(self.botoes) - 1, self.item_selecionado_idx + 1)
        elif key in [glfw.KEY_ENTER, glfw.KEY_SPACE]:
            if self.item_selecionado_idx >= 0:
                return self.botoes[self.item_selecionado_idx]['id']
        elif key == glfw.KEY_ESCAPE:
            return 'voltar'
        return None