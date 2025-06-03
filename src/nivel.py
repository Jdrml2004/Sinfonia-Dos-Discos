class Nivel:
    def __init__(self, numero, tempo_limite, cor_sala, alvos_necessarios):
        self.numero = numero
        self.tempo_limite = tempo_limite
        self.cor_sala = cor_sala
        self.alvos_necessarios = alvos_necessarios

class GerenciadorNiveis:
    DIFICULDADE_NORMAL = "normal"
    DIFICULDADE_DIFICIL = "dificil"
    DIFICULDADE_IMPOSSIVEL = "impossivel"
    MODO_DESAFIO = "desafio"
    ARQUIVO_HIGHSCORE_BASE = "highscore"  # Base para o nome do arquivo

    def __init__(self):
        # Cores das salas para cada nível (R, G, B, A)
        self.cores_niveis = [
            (0.2, 0.2, 0.3, 1.0),  # Azul original
            (0.2, 0.3, 0.2, 1.0),  # Verde escuro
            (0.3, 0.2, 0.2, 1.0),  # Vermelho escuro
            (0.3, 0.2, 0.3, 1.0),  # Roxo escuro
            (0.4, 0.1, 0.1, 1.0)   # Vermelho intenso
        ]

        # Cor para o modo desafio (dourado)
        self.cor_desafio = (0.8, 0.7, 0.0, 1.0)  # Dourado

        # Configurações para cada dificuldade
        self.configuracoes = {
            self.DIFICULDADE_NORMAL: [
                {"alvos": 10, "tempo": 30},
                {"alvos": 10, "tempo": 25},
                {"alvos": 10, "tempo": 20},
                {"alvos": 10, "tempo": 15},
                {"alvos": 10, "tempo": 10}
            ],
            self.DIFICULDADE_DIFICIL: [
                {"alvos": 15, "tempo": 45},
                {"alvos": 15, "tempo": 30},
                {"alvos": 15, "tempo": 25},
                {"alvos": 15, "tempo": 18},
                {"alvos": 15, "tempo": 14}
            ],
            self.DIFICULDADE_IMPOSSIVEL: [
                {"alvos": 20, "tempo": 40},
                {"alvos": 20, "tempo": 35},
                {"alvos": 20, "tempo": 30},
                {"alvos": 20, "tempo": 20},
                {"alvos": 20, "tempo": 15}
            ]
        }

        self.dificuldade_atual = self.DIFICULDADE_NORMAL
        self.nivel_atual = 0
        self.niveis = self._criar_niveis(self.dificuldade_atual)
        
        # Variáveis para o modo desafio
        self.modo_desafio = False
        
        # Dicionário para armazenar highscores por dificuldade
        self.highscores_desafio = {
            self.DIFICULDADE_NORMAL: 0,
            self.DIFICULDADE_DIFICIL: 0,
            self.DIFICULDADE_IMPOSSIVEL: 0
        }
        
        # Dicionário para armazenar as datas dos highscores
        self.datas_highscores = {
            self.DIFICULDADE_NORMAL: "Sem recorde",
            self.DIFICULDADE_DIFICIL: "Sem recorde",
            self.DIFICULDADE_IMPOSSIVEL: "Sem recorde"
        }
        
        # Carrega todos os highscores
        self._carregar_todos_highscores()
        
        self.nivel_desafio = None

    def _criar_niveis(self, dificuldade):
        config = self.configuracoes[dificuldade]
        return [
            Nivel(i + 1, cfg["tempo"], self.cores_niveis[i], cfg["alvos"])
            for i, cfg in enumerate(config)
        ]

    def definir_dificuldade(self, dificuldade):
        if dificuldade in self.configuracoes:
            self.dificuldade_atual = dificuldade
            self.nivel_atual = 0
            self.niveis = self._criar_niveis(dificuldade)
            self.modo_desafio = False
    
    def obter_nivel_atual(self):
        if self.modo_desafio:
            return self.nivel_desafio
        return self.niveis[self.nivel_atual]
    
    def proximo_nivel(self):
        if self.modo_desafio:
            return False  # No modo desafio não há próximo nível
        
        if self.nivel_atual < len(self.niveis) - 1:
            self.nivel_atual += 1
            return True
        return False
    
    def reiniciar_nivel(self):
        if self.modo_desafio:
            return self.nivel_desafio
        return self.niveis[self.nivel_atual]
    
    def esta_no_ultimo_nivel(self):
        if self.modo_desafio:
            return True  # O modo desafio é considerado como "último nível"
        return self.nivel_atual == len(self.niveis) - 1
    
    def ativar_modo_desafio(self):
        """Ativa o modo desafio com o tempo e configurações especiais"""
        self.modo_desafio = True
        
        # Criando um nível especial para o desafio
        # Usamos o mesmo alvo do nível 2 (vibrafone)
        # Tempo fixo de 60 segundos, sem limite de alvos (0)
        self.nivel_desafio = Nivel(6, 60, self.cor_desafio, 0)  # 0 alvos = sem limite
        
        return self.nivel_desafio
    
    def desativar_modo_desafio(self):
        """Desativa o modo desafio e volta para o modo normal"""
        self.modo_desafio = False
    
    def atualizar_highscore(self, score):
        """Atualiza o highscore do desafio se o score atual for maior para a dificuldade atual"""
        if score > self.highscores_desafio[self.dificuldade_atual]:
            self.highscores_desafio[self.dificuldade_atual] = score
            self._salvar_highscore(self.dificuldade_atual)  # Salva o novo highscore
            return True
        return False
    
    def obter_highscore(self):
        """Retorna o highscore atual do desafio para a dificuldade atual"""
        return self.highscores_desafio[self.dificuldade_atual]
    
    def esta_em_modo_desafio(self):
        """Retorna se está no modo desafio"""
        return self.modo_desafio
    
    def _obter_nome_arquivo_highscore(self, dificuldade):
        """Retorna o nome do arquivo de highscore para a dificuldade especificada"""
        return f"{self.ARQUIVO_HIGHSCORE_BASE}_{dificuldade}.txt"
        
    def _salvar_highscore(self, dificuldade):
        """Salva o highscore atual em um arquivo com a data e hora para a dificuldade especificada"""
        try:
            from datetime import datetime
            
            # Obter a data e hora atual
            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
            self.datas_highscores[dificuldade] = data_atual
            
            nome_arquivo = self._obter_nome_arquivo_highscore(dificuldade)
            with open(nome_arquivo, 'w') as arquivo:
                # Salva o highscore e a data no formato: "pontuação|data"
                arquivo.write(f"{self.highscores_desafio[dificuldade]}|{data_atual}")
            
            print(f"Highscore {self.highscores_desafio[dificuldade]} para dificuldade {dificuldade} salvo com sucesso em {data_atual}!")
        except Exception as e:
            print(f"Erro ao salvar highscore para dificuldade {dificuldade}: {e}")
    
    def _carregar_highscore(self, dificuldade):
        """Carrega o highscore de um arquivo para a dificuldade especificada, retorna 0 se o arquivo não existir"""
        try:
            nome_arquivo = self._obter_nome_arquivo_highscore(dificuldade)
            with open(nome_arquivo, 'r') as arquivo:
                conteudo = arquivo.read().strip()
                
                # Verifica se o conteúdo contém a data (formato com '|')
                if '|' in conteudo:
                    highscore_str, data = conteudo.split('|', 1)
                    highscore = int(highscore_str)
                    self.datas_highscores[dificuldade] = data
                    print(f"Highscore {highscore} de {data} para dificuldade {dificuldade} carregado com sucesso!")
                else:
                    # Compatibilidade com formato antigo (só o número)
                    highscore = int(conteudo)
                    self.datas_highscores[dificuldade] = "Data desconhecida"
                    print(f"Highscore {highscore} para dificuldade {dificuldade} carregado com sucesso!")
                
                return highscore
        except FileNotFoundError:
            print(f"Arquivo de highscore para dificuldade {dificuldade} não encontrado. Iniciando com 0.")
            self.datas_highscores[dificuldade] = "Sem recorde"
            return 0
        except Exception as e:
            print(f"Erro ao carregar highscore para dificuldade {dificuldade}: {e}")
            self.datas_highscores[dificuldade] = "Erro ao carregar"
            return 0
    
    def _carregar_todos_highscores(self):
        """Carrega os highscores para todas as dificuldades"""
        for dificuldade in [self.DIFICULDADE_NORMAL, self.DIFICULDADE_DIFICIL, self.DIFICULDADE_IMPOSSIVEL]:
            self.highscores_desafio[dificuldade] = self._carregar_highscore(dificuldade)
    
    def obter_data_highscore(self):
        """Retorna a data em que o highscore foi obtido para a dificuldade atual"""
        return self.datas_highscores.get(self.dificuldade_atual, "Data desconhecida")
    
    def obter_nome_dificuldade(self):
        """Retorna o nome da dificuldade atual em formato amigável para exibição"""
        nomes = {
            self.DIFICULDADE_NORMAL: "Normal",
            self.DIFICULDADE_DIFICIL: "Difícil",
            self.DIFICULDADE_IMPOSSIVEL: "Impossível"
        }
        return nomes.get(self.dificuldade_atual, "Desconhecida") 