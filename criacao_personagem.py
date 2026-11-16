import pygame
import sys
import json
import random

# ==========================================
# CONFIGURAÇÕES VISUAIS
# ==========================================
TEMA = {
    'fundo_tela': (15, 15, 15),
    'fundo_painel': (30, 30, 50),
    'borda_painel': (200, 200, 200),
    'texto_normal': (255, 255, 255),
    'texto_destaque': (255, 215, 0),
    'texto_modificado': (100, 255, 100), 
    'texto_hover': (100, 200, 255),
    'texto_desativado': (100, 100, 100),
    'alerta': (255, 100, 100)
}

class Painel:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
    def desenhar(self, surface):
        pygame.draw.rect(surface, TEMA['fundo_painel'], self.rect)
        pygame.draw.rect(surface, TEMA['borda_painel'], self.rect, 2)

def desenhar_texto(surface, texto, x, y, fonte, cor=TEMA['texto_normal']):
    img = fonte.render(texto, True, cor)
    surface.blit(img, (x, y))
    return img.get_rect(topleft=(x, y))

# ==========================================
# SISTEMA DE CRIAÇÃO
# ==========================================
class CriacaoPersonagemGUI:
    def __init__(self, tela):
        self.tela = tela
        self.fonte = pygame.font.SysFont("consolas", 16)
        self.fonte_titulo = pygame.font.SysFont("consolas", 20, bold=True)
        
        self.carregar_dados()
        
        self.estado = 'TELA_RACA'
        self.indice_selecionado = 0
        self.ultima_pos_mouse = (0, 0)
        
        self.dados_personagem = {
            'nome': '',
            'raca': None,
            'classe': None,
            'atributos_base': {}, 
            'atributos_gastos': {}, 
            'skills_base': {},
            'skills_gastos_classe': {},
            'skills_gastos_outras': {}
        }
        
        self.pontos_atributos_iniciais = 0
        self.pontos_atributos_livres = 0
        self.pontos_skills_classe = 8
        self.pontos_skills_outras = 6
        
        self.alerta_popup = False
        
        self.painel_principal = Painel(50, 50, 750, 500)
        self.painel_info = Painel(450, 100, 330, 380)

    def carregar_dados(self):
        try:
            with open('racas.json', 'r', encoding='utf-8') as f:
                self.racas = json.load(f)
            with open('classes.json', 'r', encoding='utf-8') as f:
                self.classes = json.load(f)
            with open('skills.json', 'r', encoding='utf-8') as f:
                self.skills_dict = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar JSON: {e}")
            self.racas = []
            self.classes = []
            self.skills_dict = {}

    def mudar_tela(self, nova_tela):
        self.estado = nova_tela
        self.indice_selecionado = 0
        self.alerta_popup = False

    def rodar(self):
        clock = pygame.time.Clock()
        self.rodando = True
        
        while self.rodando:
            self.tela.fill(TEMA['fundo_tela'])
            
            mouse_pos = pygame.mouse.get_pos()
            mouse_moveu = mouse_pos != self.ultima_pos_mouse
            self.ultima_pos_mouse = mouse_pos
            
            clique = False
            tecla_enter = False
            tecla_esc = False
            mover_cima = False
            mover_baixo = False
            mover_esq = False
            mover_dir = False
            eventos_teclado = []

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    clique = True
                if event.type == pygame.KEYDOWN:
                    eventos_teclado.append(event)
                    if event.key == pygame.K_UP: mover_cima = True
                    elif event.key == pygame.K_DOWN: mover_baixo = True
                    elif event.key == pygame.K_LEFT: mover_esq = True
                    elif event.key == pygame.K_RIGHT: mover_dir = True
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE: tecla_enter = True
                    elif event.key == pygame.K_ESCAPE: tecla_esc = True

            if mover_cima: self.indice_selecionado -= 1
            if mover_baixo: self.indice_selecionado += 1

            max_idx = {
                'TELA_RACA': len(self.racas), 
                'TELA_CLASSE': len(self.classes) + 1, 
                'TELA_ATRIBUTOS': 10, 
                'TELA_SKILLS': len(self.dados_personagem.get('skills_base', {})) + 1, 
                'TELA_RESUMO': 2
            }.get(self.estado, 0)
            
            self.indice_selecionado = max(0, min(self.indice_selecionado, max_idx))

            self.painel_principal.desenhar(self.tela)
            
            if self.estado == 'TELA_RACA':
                self.render_tela_raca(clique, mouse_pos, mouse_moveu, tecla_enter)
            elif self.estado == 'TELA_CLASSE':
                if tecla_esc: self.mudar_tela('TELA_RACA')
                self.render_tela_classe(clique, mouse_pos, mouse_moveu, tecla_enter)
            elif self.estado == 'TELA_ATRIBUTOS':
                if tecla_esc: self.mudar_tela('TELA_CLASSE')
                self.render_tela_atributos(clique, mouse_pos, mouse_moveu, tecla_enter, mover_esq, mover_dir)
            elif self.estado == 'TELA_SKILLS':
                if tecla_esc: self.mudar_tela('TELA_ATRIBUTOS')
                self.render_tela_skills(clique, mouse_pos, mouse_moveu, tecla_enter, mover_esq, mover_dir)
            elif self.estado == 'TELA_RESUMO':
                if tecla_esc: self.mudar_tela('TELA_SKILLS')
                self.render_tela_resumo(clique, mouse_pos, mouse_moveu, tecla_enter, eventos_teclado)

            if self.alerta_popup:
                self.render_popup(clique, mouse_pos, tecla_enter)

            pygame.display.flip()
            clock.tick(30)
            
        return self.dados_personagem

    def render_popup(self, clique, mouse_pos, tecla_enter):
        painel = Painel(200, 250, 400, 100)
        painel.desenhar(self.tela)
        desenhar_texto(self.tela, "Você ainda tem pontos para distribuir!", 220, 270, self.fonte, TEMA['alerta'])
        
        btn_rect = desenhar_texto(self.tela, "> [ FECHAR ]", 350, 310, self.fonte_titulo, TEMA['texto_destaque'])
        if (btn_rect.collidepoint(mouse_pos) and clique) or tecla_enter:
            self.alerta_popup = False

    def render_tela_raca(self, clique, mouse_pos, mouse_moveu, tecla_enter):
        desenhar_texto(self.tela, "1. SELECIONE SUA RAÇA", 70, 70, self.fonte_titulo, TEMA['texto_destaque'])
        self.painel_info.desenhar(self.tela)
        
        py = 120
        for i, raca in enumerate(self.racas):
            esta_selecionado = (self.indice_selecionado == i)
            cor = TEMA['texto_hover'] if esta_selecionado else (TEMA['texto_destaque'] if self.dados_personagem['raca'] == raca else TEMA['texto_normal'])
            prefixo = "> " if esta_selecionado else "  "
            
            rect = desenhar_texto(self.tela, f"{prefixo}{raca['nome']}", 70, py, self.fonte, cor)
            
            if mouse_moveu and rect.collidepoint(mouse_pos):
                self.indice_selecionado = i
            
            if esta_selecionado or self.dados_personagem['raca'] == raca:
                desenhar_texto(self.tela, f"Info: {raca['nome']}", 460, 110, self.fonte_titulo)
                bonus_list = raca['bonus'] if isinstance(raca['bonus'], list) else [raca['bonus']]
                oy = 150
                for b in bonus_list:
                    alvo = b.get('atributo_alvo', b.get('atributo', ''))
                    sinal = "+" if b['calculo'] == 'adicao' else "-"
                    desenhar_texto(self.tela, f"{sinal}{b['valor']} {alvo}", 460, oy, self.fonte)
                    oy += 20

            if (clique and rect.collidepoint(mouse_pos)) or (tecla_enter and esta_selecionado):
                self.dados_personagem['raca'] = raca
            py += 30

        idx_prox = len(self.racas)
        valido = self.dados_personagem['raca'] is not None
        cor_prox = TEMA['texto_hover'] if self.indice_selecionado == idx_prox else (TEMA['texto_destaque'] if valido else TEMA['texto_desativado'])
        
        rect_prox = desenhar_texto(self.tela, f"{'> ' if self.indice_selecionado == idx_prox else '  '}[ PROSSEGUIR ]", 70, 480, self.fonte_titulo, cor_prox)
        if mouse_moveu and rect_prox.collidepoint(mouse_pos): self.indice_selecionado = idx_prox
        
        if valido and ((clique and rect_prox.collidepoint(mouse_pos)) or (tecla_enter and self.indice_selecionado == idx_prox)):
            self.mudar_tela('TELA_CLASSE')

    def render_tela_classe(self, clique, mouse_pos, mouse_moveu, tecla_enter):
        desenhar_texto(self.tela, "2. SELECIONE SUA CLASSE", 70, 70, self.fonte_titulo, TEMA['texto_destaque'])
        self.painel_info.desenhar(self.tela)
        
        py = 120
        for i, classe in enumerate(self.classes):
            esta_selecionado = (self.indice_selecionado == i)
            cor = TEMA['texto_hover'] if esta_selecionado else (TEMA['texto_destaque'] if self.dados_personagem['classe'] == classe else TEMA['texto_normal'])
            prefixo = "> " if esta_selecionado else "  "
            
            rect = desenhar_texto(self.tela, f"{prefixo}{classe['name']}", 70, py, self.fonte, cor)
            if mouse_moveu and rect.collidepoint(mouse_pos): self.indice_selecionado = i
            
            if esta_selecionado or self.dados_personagem['classe'] == classe:
                desenhar_texto(self.tela, f"Info: {classe['name']}", 460, 110, self.fonte_titulo)
                desenhar_texto(self.tela, f"HP/Nível: {classe['max_hp_per_level']}", 460, 140, self.fonte)
                desenhar_texto(self.tela, "Vantagens:", 460, 170, self.fonte_titulo)
                oy = 190
                for adv in classe['advantages']:
                    desenhar_texto(self.tela, f"- {adv[:30]}", 460, oy, self.fonte)
                    oy += 20
                desenhar_texto(self.tela, "Desvantagens:", 460, oy+10, self.fonte_titulo)
                oy += 30
                for dis in classe['disadvantages']:
                    desenhar_texto(self.tela, f"- {dis[:30]}", 460, oy, self.fonte)
                    oy += 20
            
            if (clique and rect.collidepoint(mouse_pos)) or (tecla_enter and esta_selecionado):
                self.dados_personagem['classe'] = classe
            py += 30

        idx_voltar = len(self.classes)
        cor_voltar = TEMA['texto_hover'] if self.indice_selecionado == idx_voltar else TEMA['texto_normal']
        rect_voltar = desenhar_texto(self.tela, f"{'> ' if self.indice_selecionado == idx_voltar else '  '}[ VOLTAR ]", 70, 480, self.fonte_titulo, cor_voltar)
        if mouse_moveu and rect_voltar.collidepoint(mouse_pos): self.indice_selecionado = idx_voltar
        if (clique and rect_voltar.collidepoint(mouse_pos)) or (tecla_enter and self.indice_selecionado == idx_voltar):
            self.mudar_tela('TELA_RACA')

        idx_prox = idx_voltar + 1
        valido = self.dados_personagem['classe'] is not None
        cor_prox = TEMA['texto_hover'] if self.indice_selecionado == idx_prox else (TEMA['texto_destaque'] if valido else TEMA['texto_desativado'])
        rect_prox = desenhar_texto(self.tela, f"{'> ' if self.indice_selecionado == idx_prox else '  '}[ PROSSEGUIR ]", 220, 480, self.fonte_titulo, cor_prox)
        if mouse_moveu and rect_prox.collidepoint(mouse_pos): self.indice_selecionado = idx_prox
        if valido and ((clique and rect_prox.collidepoint(mouse_pos)) or (tecla_enter and self.indice_selecionado == idx_prox)):
            self.gerar_rolagem_atributos()
            self.mudar_tela('TELA_ATRIBUTOS')

    def gerar_rolagem_atributos(self):
        c = self.dados_personagem['classe']
        r = self.dados_personagem['raca']
        self.pontos_atributos_iniciais = random.randint(6, 14)
        self.pontos_atributos_livres = self.pontos_atributos_iniciais
        self.dados_personagem['atributos_base'] = {}
        self.dados_personagem['atributos_gastos'] = {}
        
        for atr, val in c['base_attributes'].items():
            self.dados_personagem['atributos_base'][atr] = val + random.randint(0, 10)
            self.dados_personagem['atributos_gastos'][atr] = 0

        bonus_list = r['bonus'] if isinstance(r['bonus'], list) else [r['bonus']]
        for b in bonus_list:
            if b['tipo'] == 'atributo_primario':
                alvo = b.get('atributo_alvo', b.get('atributo', ''))
                valor = int(b['valor'])
                if alvo == 'qualquer':
                    self.pontos_atributos_livres += valor
                    self.pontos_atributos_iniciais += valor
                elif alvo in self.dados_personagem['atributos_base']:
                    if b['calculo'] == 'adicao': self.dados_personagem['atributos_base'][alvo] += valor
                    else: self.dados_personagem['atributos_base'][alvo] -= valor

    def render_tela_atributos(self, clique, mouse_pos, mouse_moveu, tecla_enter, mover_esq, mover_dir):
        desenhar_texto(self.tela, "3. DISTRIBUIR ATRIBUTOS", 70, 70, self.fonte_titulo, TEMA['texto_destaque'])
        
        cor_pontos = TEMA['texto_hover'] if self.pontos_atributos_livres > 0 else TEMA['texto_modificado']
        desenhar_texto(self.tela, f"Pontos Livres: {self.pontos_atributos_livres}", 450, 70, self.fonte_titulo, cor_pontos)

        py = 120
        for i, atr in enumerate(self.dados_personagem['atributos_base'].keys()):
            esta_selecionado = (self.indice_selecionado == i)
            base = self.dados_personagem['atributos_base'][atr]
            gasto = self.dados_personagem['atributos_gastos'][atr]
            total = base + gasto
            
            cor = TEMA['texto_hover'] if esta_selecionado else (TEMA['texto_modificado'] if gasto > 0 else TEMA['texto_normal'])
            prefixo = "> " if esta_selecionado else "  "
            
            linha_rect = pygame.Rect(70, py, 250, 20)
            if mouse_moveu and linha_rect.collidepoint(mouse_pos): self.indice_selecionado = i
            
            desenhar_texto(self.tela, f"{prefixo}{atr}: {total}", 70, py, self.fonte, cor)
            
            btn_menos = desenhar_texto(self.tela, "[-]", 250, py, self.fonte_titulo, TEMA['alerta'] if gasto > 0 else TEMA['texto_desativado'])
            btn_mais = desenhar_texto(self.tela, "[+]", 300, py, self.fonte_titulo, TEMA['texto_modificado'] if self.pontos_atributos_livres > 0 else TEMA['texto_desativado'])
            
            acao_menos = (clique and btn_menos.collidepoint(mouse_pos)) or (esta_selecionado and mover_esq)
            acao_mais = (clique and btn_mais.collidepoint(mouse_pos)) or (esta_selecionado and mover_dir)
            
            if acao_menos and gasto > 0:
                self.dados_personagem['atributos_gastos'][atr] -= 1
                self.pontos_atributos_livres += 1
            elif acao_mais and self.pontos_atributos_livres > 0:
                self.dados_personagem['atributos_gastos'][atr] += 1
                self.pontos_atributos_livres -= 1
            py += 30

        idx_reroll = 8
        cor_reroll = TEMA['texto_hover'] if self.indice_selecionado == idx_reroll else TEMA['texto_destaque']
        rect_reroll = desenhar_texto(self.tela, f"{'> ' if self.indice_selecionado == idx_reroll else '  '}[ REROLLAR DADOS ]", 450, 120, self.fonte_titulo, cor_reroll)
        if mouse_moveu and rect_reroll.collidepoint(mouse_pos): self.indice_selecionado = idx_reroll
        if (clique and rect_reroll.collidepoint(mouse_pos)) or (tecla_enter and self.indice_selecionado == idx_reroll):
            self.gerar_rolagem_atributos()

        idx_voltar = 9
        cor_voltar = TEMA['texto_hover'] if self.indice_selecionado == idx_voltar else TEMA['texto_normal']
        rect_voltar = desenhar_texto(self.tela, f"{'> ' if self.indice_selecionado == idx_voltar else '  '}[ VOLTAR ]", 70, 480, self.fonte_titulo, cor_voltar)
        if mouse_moveu and rect_voltar.collidepoint(mouse_pos): self.indice_selecionado = idx_voltar
        if (clique and rect_voltar.collidepoint(mouse_pos)) or (tecla_enter and self.indice_selecionado == idx_voltar):
            self.mudar_tela('TELA_CLASSE')

        idx_prox = 10
        cor_prox = TEMA['texto_hover'] if self.indice_selecionado == idx_prox else TEMA['texto_destaque']
        rect_prox = desenhar_texto(self.tela, f"{'> ' if self.indice_selecionado == idx_prox else '  '}[ PROSSEGUIR ]", 220, 480, self.fonte_titulo, cor_prox)
        if mouse_moveu and rect_prox.collidepoint(mouse_pos): self.indice_selecionado = idx_prox
        if (clique and rect_prox.collidepoint(mouse_pos)) or (tecla_enter and self.indice_selecionado == idx_prox):
            if self.pontos_atributos_livres > 0:
                self.alerta_popup = True
            else:
                self.gerar_rolagem_skills()
                self.mudar_tela('TELA_SKILLS')

    def gerar_rolagem_skills(self):
        c = self.dados_personagem['classe']
        r = self.dados_personagem['raca']
        self.pontos_skills_classe = 8
        self.pontos_skills_outras = 6
        
        # Puxa dinamicamente as skills a partir do dicionário carregado do JSON
        todas_skills = list(self.skills_dict.keys())
        
        # O novo classes.json pode não ter todas as chaves (primary, major, minor), então usamos .get()
        skills_da_classe = c['skills'].get('primary', []) + c['skills'].get('major', []) + c['skills'].get('minor', [])
        
        todas_skills.sort(key=lambda x: (0 if x in skills_da_classe else 1, x))
        
        self.dados_personagem['skills_base'] = {}
        self.dados_personagem['skills_gastos_classe'] = {}
        self.dados_personagem['skills_gastos_outras'] = {}
        
        for sk in todas_skills:
            base = 25 if sk in skills_da_classe else 15
            base += random.randint(3, 6)
            self.dados_personagem['skills_base'][sk] = base
            
            if sk in skills_da_classe: self.dados_personagem['skills_gastos_classe'][sk] = 0
            else: self.dados_personagem['skills_gastos_outras'][sk] = 0

        bonus_list = r['bonus'] if isinstance(r['bonus'], list) else [r['bonus']]
        for b in bonus_list:
            if b['tipo'] == 'atributo_secundario':
                alvo = b.get('atributo_alvo', '').upper() # Garantir compatibilidade de caps
                valor = int(b['valor'])
                
                # Procura a skill ignorando case
                alvo_encontrado = None
                for base_sk in self.dados_personagem['skills_base']:
                    if base_sk.lower() == alvo.lower():
                        alvo_encontrado = base_sk
                        break

                if alvo_encontrado:
                    if b['calculo'] == 'adicao': self.dados_personagem['skills_base'][alvo_encontrado] += valor
                    else: self.dados_personagem['skills_base'][alvo_encontrado] -= valor

    def render_tela_skills(self, clique, mouse_pos, mouse_moveu, tecla_enter, mover_esq, mover_dir):
        desenhar_texto(self.tela, "4. DISTRIBUIR SKILLS", 70, 60, self.fonte_titulo, TEMA['texto_destaque'])
        desenhar_texto(self.tela, f"Pts Classe: {self.pontos_skills_classe}", 350, 60, self.fonte, TEMA['texto_hover'] if self.pontos_skills_classe > 0 else TEMA['texto_modificado'])
        desenhar_texto(self.tela, f"Pts Outras: {self.pontos_skills_outras}", 550, 60, self.fonte, TEMA['texto_hover'] if self.pontos_skills_outras > 0 else TEMA['texto_modificado'])
        
        c = self.dados_personagem['classe']
        skills_da_classe = c['skills'].get('primary', []) + c['skills'].get('major', []) + c['skills'].get('minor', [])
        todas = list(self.dados_personagem['skills_base'].keys())
        
        for i, sk in enumerate(todas):
            esta_selecionado = (self.indice_selecionado == i)
            eh_classe = sk in skills_da_classe
            base = self.dados_personagem['skills_base'][sk]
            gasto = self.dados_personagem['skills_gastos_classe'].get(sk, 0) + self.dados_personagem['skills_gastos_outras'].get(sk, 0)
            
            px = 70 if i < 15 else 430
            py = 100 + (i % 15) * 23
            
            cor = TEMA['texto_hover'] if esta_selecionado else (TEMA['texto_modificado'] if gasto > 0 else (TEMA['texto_destaque'] if eh_classe else TEMA['texto_normal']))
            prefixo = "> " if esta_selecionado else ("* " if eh_classe else "  ")
            
            linha_rect = pygame.Rect(px, py, 260, 20)
            if mouse_moveu and linha_rect.collidepoint(mouse_pos): self.indice_selecionado = i
            
            # Mostra até os 18 primeiros caracteres da Skill para não cortar as grandes, antes ficava limitado a 12
            desenhar_texto(self.tela, f"{prefixo}{sk[:18]}: {base+gasto}", px, py, self.fonte, cor)
            
            # Botões afastados: px+230 e px+260 para dar espaço ao nome
            btn_menos = desenhar_texto(self.tela, "[-]", px+230, py, self.fonte, TEMA['alerta'] if gasto > 0 else TEMA['texto_desativado'])
            btn_mais = desenhar_texto(self.tela, "[+]", px+260, py, self.fonte, TEMA['texto_modificado'])
            
            acao_menos = (clique and btn_menos.collidepoint(mouse_pos)) or (esta_selecionado and mover_esq)
            acao_mais = (clique and btn_mais.collidepoint(mouse_pos)) or (esta_selecionado and mover_dir)
            
            if acao_menos and gasto > 0:
                if eh_classe:
                    self.dados_personagem['skills_gastos_classe'][sk] -= 1
                    self.pontos_skills_classe += 1
                else:
                    self.dados_personagem['skills_gastos_outras'][sk] -= 1
                    self.pontos_skills_outras += 1
            elif acao_mais:
                if eh_classe and self.pontos_skills_classe > 0:
                    self.dados_personagem['skills_gastos_classe'][sk] += 1
                    self.pontos_skills_classe -= 1
                elif not eh_classe and self.pontos_skills_outras > 0:
                    self.dados_personagem['skills_gastos_outras'][sk] += 1
                    self.pontos_skills_outras -= 1

        idx_voltar = len(todas)
        cor_voltar = TEMA['texto_hover'] if self.indice_selecionado == idx_voltar else TEMA['texto_normal']
        rect_voltar = desenhar_texto(self.tela, f"{'> ' if self.indice_selecionado == idx_voltar else '  '}[ VOLTAR ]", 70, 500, self.fonte_titulo, cor_voltar)
        if mouse_moveu and rect_voltar.collidepoint(mouse_pos): self.indice_selecionado = idx_voltar
        if (clique and rect_voltar.collidepoint(mouse_pos)) or (tecla_enter and self.indice_selecionado == idx_voltar):
            self.pontos_atributos_livres = 0 
            self.mudar_tela('TELA_ATRIBUTOS')

        idx_prox = idx_voltar + 1
        cor_prox = TEMA['texto_hover'] if self.indice_selecionado == idx_prox else TEMA['texto_destaque']
        rect_prox = desenhar_texto(self.tela, f"{'> ' if self.indice_selecionado == idx_prox else '  '}[ PROSSEGUIR ]", 220, 500, self.fonte_titulo, cor_prox)
        if mouse_moveu and rect_prox.collidepoint(mouse_pos): self.indice_selecionado = idx_prox
        if (clique and rect_prox.collidepoint(mouse_pos)) or (tecla_enter and self.indice_selecionado == idx_prox):
            if self.pontos_skills_classe > 0 or self.pontos_skills_outras > 0:
                self.alerta_popup = True
            else:
                self.mudar_tela('TELA_RESUMO')

    def render_tela_resumo(self, clique, mouse_pos, mouse_moveu, tecla_enter, eventos_teclado):
        desenhar_texto(self.tela, "5. FINALIZAR PERSONAGEM", 70, 70, self.fonte_titulo, TEMA['texto_destaque'])
        
        idx_nome = 0
        desenhar_texto(self.tela, "Nome:", 70, 110, self.fonte_titulo)
        caixa_nome = pygame.Rect(130, 110, 200, 25)
        
        if mouse_moveu and caixa_nome.collidepoint(mouse_pos): self.indice_selecionado = idx_nome
        if clique and caixa_nome.collidepoint(mouse_pos): self.indice_selecionado = idx_nome
            
        cor_caixa = TEMA['texto_hover'] if self.indice_selecionado == idx_nome else TEMA['borda_painel']
        pygame.draw.rect(self.tela, cor_caixa, caixa_nome, 2)
        desenhar_texto(self.tela, self.dados_personagem['nome'] + ("_" if self.indice_selecionado == idx_nome else ""), 135, 115, self.fonte)
        
        if self.indice_selecionado == idx_nome:
            for event in eventos_teclado:
                if event.key == pygame.K_BACKSPACE:
                    self.dados_personagem['nome'] = self.dados_personagem['nome'][:-1]
                elif event.key not in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RETURN, pygame.K_ESCAPE]:
                    if len(self.dados_personagem['nome']) < 15 and event.unicode.isprintable():
                        self.dados_personagem['nome'] += event.unicode

        r = self.dados_personagem['raca']
        c = self.dados_personagem['classe']
        desenhar_texto(self.tela, f"Raça: {r['nome']}   Classe: {c['name']}", 70, 150, self.fonte)
        
        vit = self.dados_personagem['atributos_base'].get('END', 10) + self.dados_personagem['atributos_gastos'].get('END', 0)
        hp = c['max_hp_per_level'] + vit
        desenhar_texto(self.tela, f"HP Inicial Estimado: {hp}", 70, 180, self.fonte)
        
        py = 220
        desenhar_texto(self.tela, "ATRIBUTOS FINAIS:", 70, py, self.fonte_titulo)
        py += 25
        for atr in self.dados_personagem['atributos_base'].keys():
            t = self.dados_personagem['atributos_base'][atr] + self.dados_personagem['atributos_gastos'][atr]
            desenhar_texto(self.tela, f"{atr}: {t}", 70, py, self.fonte)
            py += 20

        idx_voltar = 1
        cor_voltar = TEMA['texto_hover'] if self.indice_selecionado == idx_voltar else TEMA['texto_normal']
        rect_voltar = desenhar_texto(self.tela, f"{'> ' if self.indice_selecionado == idx_voltar else '  '}[ VOLTAR ]", 70, 480, self.fonte_titulo, cor_voltar)
        if mouse_moveu and rect_voltar.collidepoint(mouse_pos): self.indice_selecionado = idx_voltar
        if (clique and rect_voltar.collidepoint(mouse_pos)) or (tecla_enter and self.indice_selecionado == idx_voltar):
            self.mudar_tela('TELA_SKILLS')

        idx_prox = 2
        valido = self.dados_personagem['nome'].strip() != ""
        cor_prox = TEMA['texto_hover'] if self.indice_selecionado == idx_prox else (TEMA['texto_modificado'] if valido else TEMA['texto_desativado'])
        rect_prox = desenhar_texto(self.tela, f"{'> ' if self.indice_selecionado == idx_prox else '  '}[ CONFIRMAR CRIAÇÃO ]", 220, 480, self.fonte_titulo, cor_prox)
        if mouse_moveu and rect_prox.collidepoint(mouse_pos): self.indice_selecionado = idx_prox
        if valido and ((clique and rect_prox.collidepoint(mouse_pos)) or (tecla_enter and self.indice_selecionado == idx_prox)):
            self.rodando = False

# ==========================================
# TESTE STANDALONE
# ==========================================
if __name__ == "__main__":
    pygame.init()
    tela_principal = pygame.display.set_mode((850, 600))
    pygame.display.set_caption("Criação de Personagem - Controles Híbridos")
    
    criador = CriacaoPersonagemGUI(tela_principal)
    dados_finais = criador.rodar()
    
    print("\n--- PERSONAGEM CRIADO ---")
    print(f"Nome: {dados_finais['nome']}")
    if dados_finais['raca']:
        print(f"Raça: {dados_finais['raca']['nome']}")
        print(f"Classe: {dados_finais['classe']['name']}")
    pygame.quit()