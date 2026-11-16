import pygame
import sys

TEMA = {
    'fundo_tela': (15, 15, 15),
    'fundo_painel': (30, 30, 50),
    'borda_painel': (200, 200, 200),
    'texto_normal': (255, 255, 255),
    'texto_destaque': (255, 215, 0),
    'texto_hover': (100, 200, 255),
    'barra_hp': (200, 50, 50),
    'barra_mp': (50, 100, 200),
    'log_dano': (255, 100, 100),
    'log_sistema': (150, 255, 150),
    'texto_desativado': (100, 100, 100)
}

class Painel:
    def __init__(self, x, y, w, h): 
        self.rect = pygame.Rect(x, y, w, h)
        
    def desenhar(self, surface):
        pygame.draw.rect(surface, TEMA['fundo_painel'], self.rect)
        pygame.draw.rect(surface, TEMA['borda_painel'], self.rect, 2)

def desenhar_texto(surface, texto, x, y, fonte, cor=TEMA['texto_normal']):
    img_texto = fonte.render(texto, True, cor)
    surface.blit(img_texto, (x, y))
    return img_texto.get_rect(topleft=(x, y))

class JogoGUI:
    def __init__(self, motor_batalha):
        pygame.init()
        self.tela = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Simulador RPG - Controles Híbridos")
        self.fonte = pygame.font.SysFont("consolas", 16)
        self.fonte_titulo = pygame.font.SysFont("consolas", 20, bold=True)
        self.motor = motor_batalha
        
        self.painel_herois = Painel(10, 10, 250, 200)
        self.painel_inimigos = Painel(540, 10, 250, 200)
        self.painel_acoes = Painel(270, 10, 260, 200)
        self.painel_log = Painel(10, 420, 780, 170)
        self.painel_char_info = Painel(200, 100, 400, 300) 
        
        self.estado_ui = 'MENU_PRINCIPAL'
        self.acao_selecionada = None
        
        # Variáveis de Navegação
        self.indice_selecionado = 0
        self.ultima_pos_mouse = (0, 0)

    def mudar_menu(self, novo_estado):
        """Muda o estado da UI e reseta a seleção do teclado para o topo"""
        self.estado_ui = novo_estado
        self.indice_selecionado = 0

    def rodar(self):
        clock = pygame.time.Clock()
        self.motor.iniciar_batalha()

        while True:
            self.tela.fill(TEMA['fundo_tela'])
            
            # --- CAPTURA DE INPUTS ---
            mouse_pos = pygame.mouse.get_pos()
            mouse_moveu = mouse_pos != self.ultima_pos_mouse
            self.ultima_pos_mouse = mouse_pos
            
            clique = False
            tecla_enter = False
            tecla_esc = False
            mover_cima = False
            mover_baixo = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    clique = True
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        mover_cima = True
                    elif event.key == pygame.K_DOWN:
                        mover_baixo = True
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        tecla_enter = True
                    elif event.key == pygame.K_ESCAPE:
                        tecla_esc = True

            # Aplica navegação por setas de forma global
            if mover_cima: self.indice_selecionado -= 1
            if mover_baixo: self.indice_selecionado += 1

            self.motor.atualizar_estado()

            # --- DESENHO BÁSICO ---
            self.painel_herois.desenhar(self.tela)
            self.painel_inimigos.desenhar(self.tela)
            self.painel_acoes.desenhar(self.tela)
            self.painel_log.desenhar(self.tela)

            self.desenhar_grupo(self.motor.jogadores, self.painel_herois.rect.x, self.painel_herois.rect.y, "GRUPO")
            self.desenhar_grupo(self.motor.inimigos, self.painel_inimigos.rect.x, self.painel_inimigos.rect.y, "INIMIGOS")
            self.desenhar_log()

            # --- CONTROLE DA UI DE BATALHA ---
            if self.motor.estado_atual == 'AGUARDANDO_ACAO' and self.motor.combatente_atual in self.motor.jogadores:
                if self.estado_ui == 'INFO_CHAR': 
                    self.desenhar_char_info(clique, mouse_pos, tecla_enter, tecla_esc, mouse_moveu)
                else: 
                    self.gerenciar_menu_batalha(clique, mouse_pos, tecla_enter, tecla_esc, mouse_moveu)
            elif self.motor.estado_atual in ['VITORIA', 'DERROTA', 'FUGA']:
                desenhar_texto(self.tela, f"--- {self.motor.estado_atual} ---", self.painel_acoes.rect.x + 60, self.painel_acoes.rect.y + 90, self.fonte_titulo, TEMA['texto_destaque'])
            else:
                desenhar_texto(self.tela, "Aguarde...", self.painel_acoes.rect.x + 80, self.painel_acoes.rect.y + 90, self.fonte_titulo, TEMA['texto_destaque'])

            pygame.display.flip()
            clock.tick(30)

    # --- FUNÇÕES DE STATUS (Sem alterações estruturais, apenas visuais) ---
    def desenhar_grupo(self, grupo, px, py, titulo):
        desenhar_texto(self.tela, titulo, px + 10, py + 10, self.fonte_titulo, TEMA['texto_destaque'])
        offset_y = 40
        for p in grupo:
            cor_nome = TEMA['texto_normal'] if p.vida_atual > 0 else TEMA['texto_desativado']
            if self.motor.combatente_atual == p and p.vida_atual > 0:
                cor_nome = TEMA['texto_destaque']
                desenhar_texto(self.tela, ">", px + 5, py + offset_y, self.fonte, cor_nome)

            desenhar_texto(self.tela, f"{p.nome} (Nv {p.nivel})", px + 20, py + offset_y, self.fonte, cor_nome)
            desenhar_texto(self.tela, f"HP: {p.vida_atual}/{p.vida_maxima}", px + 20, py + offset_y + 15, self.fonte, TEMA['barra_hp'])
            desenhar_texto(self.tela, f"MP: {p.mana_atual}/{p.mana_maxima}", px + 120, py + offset_y + 15, self.fonte, TEMA['barra_mp'])
            offset_y += 45

    def desenhar_log(self):
        desenhar_texto(self.tela, "LOG DE BATALHA", self.painel_log.rect.x + 10, self.painel_log.rect.y + 10, self.fonte_titulo, TEMA['texto_destaque'])
        mensagens = self.motor.log_batalha[-7:]
        offset_y = 35
        for msg in mensagens:
            cor = TEMA['texto_normal']
            if "dano" in msg.lower() or "morreu" in msg.lower() or "derrota" in msg.lower(): cor = TEMA['log_dano']
            elif "curou" in msg.lower() or "vitória" in msg.lower() or "sucesso" in msg.lower(): cor = TEMA['log_sistema']
            desenhar_texto(self.tela, msg, self.painel_log.rect.x + 10, self.painel_log.rect.y + offset_y, self.fonte, cor)
            offset_y += 18

    # --- NAVEGAÇÃO DE MENUS (Agora com renderizador de listas e teclado suportado) ---
    def renderizar_opcoes(self, opcoes, px, py, clique, mouse_pos, tecla_enter, mouse_moveu):
        """Recebe uma lista de dicionários com regras, e desenha os botões selecionáveis"""
        # Trava o índice no limite da lista
        self.indice_selecionado = max(0, min(self.indice_selecionado, len(opcoes) - 1))
        
        acao_escolhida = None
        
        for i, op in enumerate(opcoes):
            if op.get('espaco_antes'):
                py += 10
                
            # Verifica Hover do Mouse
            rect = pygame.Rect(px, py, 200, 20)
            hover = rect.collidepoint(mouse_pos)
            
            # Se o mouse se mover por cima, sincroniza o índice com ele
            if hover and mouse_moveu:
                self.indice_selecionado = i
                
            esta_selecionado = (self.indice_selecionado == i)
            valido = op.get('valido', True)
            
            # Definição de Cores
            if not valido:
                cor = (150, 150, 150) if esta_selecionado else TEMA['texto_desativado']
            else:
                cor = TEMA['texto_hover'] if esta_selecionado else TEMA['texto_normal']
            
            prefixo = "> " if (esta_selecionado and not op.get('sem_prefixo')) else "  "
            
            desenhar_texto(self.tela, f"{prefixo}{op['texto']}", px, py, self.fonte, cor)
            
            # Trigger da Ação (Se clicou em cima, ou se apertou enter no selecionado)
            if valido and ((hover and clique) or (esta_selecionado and tecla_enter)):
                acao_escolhida = op['id']
                
            py += 25
            
        return acao_escolhida

    def gerenciar_menu_batalha(self, clique, mouse_pos, tecla_enter, tecla_esc, mouse_moveu):
        px, py = self.painel_acoes.rect.x + 15, self.painel_acoes.rect.y + 15
        desenhar_texto(self.tela, "AÇÕES", px, py, self.fonte_titulo, TEMA['texto_destaque'])
        py += 30

        # --- MENU PRINCIPAL ---
        if self.estado_ui == 'MENU_PRINCIPAL':
            opcoes = [
                {'id': 'Atacar', 'texto': 'Atacar'},
                {'id': 'Magia', 'texto': 'Magia'},
                {'id': 'Item', 'texto': 'Item'},
                {'id': 'Info', 'texto': 'Char (Info)'},
                {'id': 'Fugir', 'texto': 'Fugir'}
            ]
            
            escolha = self.renderizar_opcoes(opcoes, px, py, clique, mouse_pos, tecla_enter, mouse_moveu)
            
            if escolha == 'Atacar': self.mudar_menu('ALVOS_ATAQUE')
            elif escolha == 'Magia': self.mudar_menu('MENU_MAGIAS')
            elif escolha == 'Item': self.mudar_menu('MENU_ITENS')
            elif escolha == 'Info': self.mudar_menu('INFO_CHAR')
            elif escolha == 'Fugir': self.motor.executar_acao_jogador('FUGIR')
                
        # --- SELECIONAR ALVO (ATAQUE) ---
        elif self.estado_ui == 'ALVOS_ATAQUE':
            desenhar_texto(self.tela, "Selecione o Alvo:", px, py, self.fonte, TEMA['texto_destaque'])
            py += 25
            
            if tecla_esc: self.mudar_menu('MENU_PRINCIPAL')
                
            opcoes = []
            for inimigo in self.motor.inimigos:
                if inimigo.vida_atual > 0:
                    opcoes.append({'id': inimigo, 'texto': inimigo.nome})
            opcoes.append({'id': 'voltar', 'texto': '[ Voltar ]', 'espaco_antes': True, 'sem_prefixo': True})
            
            escolha = self.renderizar_opcoes(opcoes, px, py, clique, mouse_pos, tecla_enter, mouse_moveu)
            
            if escolha == 'voltar':
                self.mudar_menu('MENU_PRINCIPAL')
            elif escolha:
                self.motor.executar_acao_jogador('ATACAR', alvo=escolha)
                self.mudar_menu('MENU_PRINCIPAL')

        # --- MENU DE MAGIAS ---
        elif self.estado_ui == 'MENU_MAGIAS':
            c = self.motor.combatente_atual
            
            if tecla_esc: self.mudar_menu('MENU_PRINCIPAL')
            
            opcoes = []
            if not c.magias_conhecidas:
                opcoes.append({'id': None, 'texto': 'Nenhuma magia.', 'valido': False, 'sem_prefixo': True})
            else:
                for mag in c.magias_conhecidas:
                    tem_mp = c.mana_atual >= mag['custo_mp']
                    opcoes.append({'id': mag, 'texto': f"{mag['nome']} ({mag['custo_mp']} MP)", 'valido': tem_mp})
                    
            opcoes.append({'id': 'voltar', 'texto': '[ Voltar ]', 'espaco_antes': True, 'sem_prefixo': True})
            
            escolha = self.renderizar_opcoes(opcoes, px, py, clique, mouse_pos, tecla_enter, mouse_moveu)
            
            if escolha == 'voltar':
                self.mudar_menu('MENU_PRINCIPAL')
            elif escolha: # É uma magia
                self.acao_selecionada = escolha
                self.mudar_menu('ALVOS_MAGIA')

        # --- SELECIONAR ALVO (MAGIA) ---
        elif self.estado_ui == 'ALVOS_MAGIA':
            desenhar_texto(self.tela, f"Alvo para {self.acao_selecionada['nome']}:", px, py, self.fonte, TEMA['texto_destaque'])
            py += 25
            
            if tecla_esc: self.mudar_menu('MENU_MAGIAS')
            
            alvos_validos = self.motor.inimigos if self.acao_selecionada['tipo'] == 'dano' else self.motor.jogadores
            opcoes = []
            for alvo in alvos_validos:
                if alvo.vida_atual > 0:
                    opcoes.append({'id': alvo, 'texto': alvo.nome})
            opcoes.append({'id': 'voltar', 'texto': '[ Voltar ]', 'espaco_antes': True, 'sem_prefixo': True})
            
            escolha = self.renderizar_opcoes(opcoes, px, py, clique, mouse_pos, tecla_enter, mouse_moveu)
            
            if escolha == 'voltar':
                self.mudar_menu('MENU_MAGIAS')
            elif escolha:
                self.motor.executar_acao_jogador('MAGIA', alvo=escolha, habilidade=self.acao_selecionada)
                self.mudar_menu('MENU_PRINCIPAL')

        # --- MENU DE ITENS ---
        elif self.estado_ui == 'MENU_ITENS':
            if tecla_esc: self.mudar_menu('MENU_PRINCIPAL')
            
            opcoes = [
                {'id': None, 'texto': 'Inventário Vazio.', 'valido': False, 'sem_prefixo': True},
                {'id': 'voltar', 'texto': '[ Voltar ]', 'espaco_antes': True, 'sem_prefixo': True}
            ]
            
            escolha = self.renderizar_opcoes(opcoes, px, py, clique, mouse_pos, tecla_enter, mouse_moveu)
            if escolha == 'voltar':
                self.mudar_menu('MENU_PRINCIPAL')

    def desenhar_char_info(self, clique, mouse_pos, tecla_enter, tecla_esc, mouse_moveu):
        """Tela de Status detalhada"""
        c = self.motor.combatente_atual
        self.painel_char_info.desenhar(self.tela)
        px, py = self.painel_char_info.rect.x, self.painel_char_info.rect.y
        desenhar_texto(self.tela, f"--- INFO: {c.nome} ---", px + 20, py + 20, self.fonte_titulo, TEMA['texto_destaque'])
        
        infos = [
            f"Nível: {c.nivel}  |  XP Geral: {c.xp_atual}",
            f"HP: {c.vida_atual} / {c.vida_maxima}  |  MP: {c.mana_atual} / {c.mana_maxima}",
            "--- ATRIBUTOS ---",
            f"STR: {c.atributos['STR']}   AGI: {c.atributos['AGI']}",
            f"VIT: {c.atributos['VIT']}   INT: {c.atributos['INT']}",
            f"LCK: {c.atributos['LCK']}   CAR: {c.atributos['CAR']}",
            f"WILL: {c.atributos['WILL']}  PER: {c.atributos['PER']}"
        ]
        
        oy = 60
        for linha in infos:
            desenhar_texto(self.tela, linha, px + 20, py + oy, self.fonte)
            oy += 22
            
        # O botão "Voltar" aqui é a única opção
        if tecla_esc: self.mudar_menu('MENU_PRINCIPAL')
            
        opcoes = [{'id': 'voltar', 'texto': '[ VOLTAR ]', 'sem_prefixo': True}]
        escolha = self.renderizar_opcoes(opcoes, px + 150, py + 260, clique, mouse_pos, tecla_enter, mouse_moveu)
        
        if escolha == 'voltar': 
            self.mudar_menu('MENU_PRINCIPAL')