from OpenGL.GL import *
import pygame

class TextRenderer:
    def __init__(self):
        self.fonts = {}
        self.textures = {}
        
    def get_font(self, size):
        if size not in self.fonts:
            self.fonts[size] = pygame.font.Font(None, size)
        return self.fonts[size]
    
    def render_text(self, text, size, color):
        font = self.get_font(size)
        text_surface = font.render(text, True, color)
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        
        # Criar textura OpenGL
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text_surface.get_width(), text_surface.get_height(),
                    0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
        return texture, text_surface.get_width(), text_surface.get_height()
    
    def get_text_dimensions(self, text, size):
        """Obtém a largura e altura do texto sem renderizá-lo."""
        font = self.get_font(size)
        text_surface = font.render(text, True, (0, 0, 0)) # Cor não importa, só precisamos das dimensões
        return text_surface.get_width(), text_surface.get_height()
    
    def draw_text(self, text, x, y, size, color):
        # Salva estados atuais do OpenGL
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        
        # Configura estados necessários para renderização de texto
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_2D)
        
        texture, width, height = self.render_text(text, size, color)
        glBindTexture(GL_TEXTURE_2D, texture)
        
        # Desenha o texto
        glBegin(GL_QUADS)
        glColor4f(1.0, 1.0, 1.0, 1.0)  # Cor branca com alpha 1
        glTexCoord2f(0, 0); glVertex2f(x, y)
        glTexCoord2f(1, 0); glVertex2f(x + width, y)
        glTexCoord2f(1, 1); glVertex2f(x + width, y + height)
        glTexCoord2f(0, 1); glVertex2f(x, y + height)
        glEnd()
        
        # Limpa a textura
        glDeleteTextures([texture])
        
        # Restaura estados anteriores do OpenGL
        glPopAttrib()
        
        return width, height # Retorna a largura e altura do texto 