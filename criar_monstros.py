import pygame
import sys
import json
import os
import random

# ==========================================
# CONFIGURAÇÕES VISUAIS
# ==========================================
TEMA = {
    'fundo': (25, 20, 25),       
    'painel': (45, 35, 45),
    'borda': (160, 120, 120),
    'texto': (255, 255, 255),
    'destaque': (255, 180, 50),
    'modificado': (100, 255, 100), 
    'hover': (255, 150, 100),
    'desativado': (100, 100, 100),
    'btn_fundo': (70, 50, 70),
    'checkbox_on': (50, 150, 50)
}

def desenhar_texto(surface, texto, x, y, fonte, cor=TEMA['texto']):
    img = fonte.render(texto, True, cor)
    surface.blit(img, (x, y))
    return img.get_rect(topleft=(x, y))

def desenhar_botao(surface, texto, rect, mouse_pos, clique, fonte, cor_base=TEMA['btn_fundo']):
    hover = rect.collidepoint(mouse_pos)
    cor = TEMA['hover'] if hover else cor_base
    pygame.draw.rect(surface, cor, rect, border_radius=5)
    pygame.draw.rect(surface, TEMA['borda'], rect, 2, border_radius=5)
    
    txt_img = fonte.render(texto, True, TEMA['texto'])
    txt_rect = txt_img.get_rect(center=rect.center)
    surface.blit(txt_img, txt_rect)
    return hover and clique

# ==========================================
# BUILDER DE MONSTROS
# ==========================================
class CriadorMonstros:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((1220, 768))
        pygame.display.set_caption("Builder de Templates de Monstros - Avançado")
        self.fonte = pygame.font.SysFont("consolas", 13)
        self.fonte_titulo = pygame.font.SysFont("consolas", 16, bold=True)
        
        # Variáveis de Estado
        self.id_template = "novo_monstro"
        self.nome_monstro = "Novo Monstro"
        
        self.vida_manual = "100"
        self.mana_manual = "50"
        
        self.atributos = { 'STR': "50", 'INT': "50", 'WILL': "50", 'AGI': "50", 'END': "50", 'CAR': "50", 'LCK': "50" }
        self.skills_primarias = ["ARMA-CONTUSAO", "ARMA-CORTE"]
        
        # Inputs para Preenchimento em Lote (Batch Fill)
        self.batch_val_pri = "50"
        self.batch_min_pri = "30"
        self.batch_max_pri = "70"
        
        self.batch_val_sk = "30"
        self.batch_min_sk = "20"
        self.batch_max_sk = "60"
        
        self.carregar_skills_db()
        self.skills_niveis = {sk: "30" for sk in self.skills_dict.keys()}
        
        self.listar_arquivos_monstros()
        
        self.arquivo_idx = 0
        
        # Controle de Foco e Sobrescrita ao Clicar
        self.input_foco = None
        self.input_is_new_focus = False

        if self.arquivos_monstros:
            self.carregar_monstro_arquivo(self.arquivos_monstros[0])

    def carregar_skills_db(self):
        try:
            with open('skills.json', 'r', encoding='utf-8') as f:
                self.skills_dict = json.load(f)
        except Exception as e:
            print(f"Aviso: skills.json não encontrado ({e}). Usando padrão.")
            self.skills_dict = {
                "ARMA-CONTUSAO": "STR", "ARMA-CORTE": "STR", "ARCO": "AGI", "DESARMADO": "STR",
                "RESISTENCIA FISICA": "VIT", "PERCEPCAO": "WILL", "MANIPULACAO": "CAR", 
                "MANHA DA RUA": "CAR", "NATUREZA": "INT", "RASTREIO": "WILL", "REFLEXOS": "AGI"
            }

    def listar_arquivos_monstros(self):
        self.arquivos_monstros = [f for f in os.listdir('.') if f.startswith('monstro_') and f.endswith('.json')]
        if not self.arquivos_monstros:
            self.salvar_template_atual("monstro_goblin_batedor.json")
            self.arquivos_monstros = ['monstro_goblin_batedor.json']

    def carregar_monstro_arquivo(self, nome_arq):
        try:
            with open(nome_arq, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            self.id_template = dados.get("id", "monstro")
            self.nome_monstro = dados.get("nome", "Monstro")
            
            self.vida_manual = str(dados.get("vida_inicial", 100))
            self.mana_manual = str(dados.get("mana_inicial", 50))
            
            base_attr = dados.get("base_attributes", {})
            for atr in self.atributos:
                self.atributos[atr] = str(base_attr.get(atr, 50))
                
            sk_data = dados.get("skills", {})
            self.skills_primarias = sk_data.get("primary", [])
            
            sk_niveis_json = dados.get("skills_niveis", {})
            for sk in self.skills_niveis:
                self.skills_niveis[sk] = str(sk_niveis_json.get(sk, 30))
                
        except Exception as e:
            print(f"Erro ao carregar {nome_arq}: {e}")

    def salvar_template_atual(self, nome_custom=None):
        attr_convertido = {k: max(0, min(100, int(v) if v.isdigit() else 0)) for k, v in self.atributos.items()}
        skills_convertidas = {k: max(0, min(100, int(v) if v.isdigit() else 0)) for k, v in self.skills_niveis.items()}
        
        dados = {
            "id": self.id_template,
            "nome": self.nome_monstro,
            "vida_inicial": int(self.vida_manual) if self.vida_manual.isdigit() else 100,
            "mana_inicial": int(self.mana_manual) if self.mana_manual.isdigit() else 50,
            "base_attributes": attr_convertido,
            "skills": {
                "primary": self.skills_primarias
            },
            "skills_niveis": skills_convertidas
        }
        
        nome_arq = nome_custom if nome_custom else f"monstro_{self.id_template.replace(' ', '_').lower()}.json"
        try:
            with open(nome_arq, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            print(f"Template de monstro salvo com sucesso em: {nome_arq}")
            self.listar_arquivos_monstros()
        except Exception as e:
            print(f"Erro ao salvar monstro: {e}")

    def get_target_string_and_setter(self):
        if not self.input_foco: return None, None
        tipo, chave = self.input_foco
        if tipo == 'nome': return self.nome_monstro, lambda v: setattr(self, 'nome_monstro', v)
        elif tipo == 'vida': return self.vida_manual, lambda v: setattr(self, 'vida_manual', v)
        elif tipo == 'mana': return self.mana_manual, lambda v: setattr(self, 'mana_manual', v)
        elif tipo == 'atributo': return self.atributos[chave], lambda v: self.atributos.__setitem__(chave, v)
        elif tipo == 'skill': return self.skills_niveis[chave], lambda v: self.skills_niveis.__setitem__(chave, v)
        elif tipo == 'b_v_pri': return self.batch_val_pri, lambda v: setattr(self, 'batch_val_pri', v)
        elif tipo == 'b_min_pri': return self.batch_min_pri, lambda v: setattr(self, 'batch_min_pri', v)
        elif tipo == 'b_max_pri': return self.batch_max_pri, lambda v: setattr(self, 'batch_max_pri', v)
        elif tipo == 'b_v_sk': return self.batch_val_sk, lambda v: setattr(self, 'batch_val_sk', v)
        elif tipo == 'b_min_sk': return self.batch_min_sk, lambda v: setattr(self, 'batch_min_sk', v)
        elif tipo == 'b_max_sk': return self.batch_max_sk, lambda v: setattr(self, 'batch_max_sk', v)
        return None, None

    def tratar_input_teclado(self, event):
        val, setter = self.get_target_string_and_setter()
        if val is None or setter is None: return
        tipo, chave = self.input_foco

        if event.key == pygame.K_BACKSPACE:
            if self.input_is_new_focus:
                setter("")
                self.input_is_new_focus = False
            else:
                setter(val[:-1])
        elif event.unicode and event.unicode.isprintable():
            if self.input_is_new_focus:
                new_val = event.unicode
                self.input_is_new_focus = False
            else:
                new_val = val + event.unicode
            
            # Validações por tipo de campo
            if tipo in ['atributo', 'skill', 'b_v_pri', 'b_min_pri', 'b_max_pri', 'b_v_sk', 'b_min_sk', 'b_max_sk']:
                if new_val.isdigit() and len(new_val) <= 3 and int(new_val) <= 100:
                    setter(new_val)
            elif tipo in ['vida', 'mana']:
                if new_val.isdigit() and len(new_val) <= 5:
                    setter(new_val)
            elif tipo == 'nome':
                if len(new_val) < 25:
                    setter(new_val)
                    self.id_template = new_val.lower().replace(" ", "_")

    # Ações de Preenchimento em Lote
    def preencher_pri_fixo(self):
        v = self.batch_val_pri if self.batch_val_pri.isdigit() else "50"
        for atr in self.atributos: self.atributos[atr] = v

    def preencher_pri_range(self):
        try:
            mn = int(self.batch_min_pri) if self.batch_min_pri.isdigit() else 0
            mx = int(self.batch_max_pri) if self.batch_max_pri.isdigit() else 100
            if mn > mx: mn, mx = mx, mn
            for atr in self.atributos:
                self.atributos[atr] = str(random.randint(max(0, mn), min(100, mx)))
        except: pass

    def preencher_sk_fixo(self):
        v = self.batch_val_sk if self.batch_val_sk.isdigit() else "30"
        for sk in self.skills_niveis: self.skills_niveis[sk] = v

    def preencher_sk_range(self):
        try:
            mn = int(self.batch_min_sk) if self.batch_min_sk.isdigit() else 0
            mx = int(self.batch_max_sk) if self.batch_max_sk.isdigit() else 100
            if mn > mx: mn, mx = mx, mn
            for sk in self.skills_niveis:
                self.skills_niveis[sk] = str(random.randint(max(0, mn), min(100, mx)))
        except: pass

    def rodar(self):
        clock = pygame.time.Clock()
        while True:
            self.tela.fill(TEMA['fundo'])
            mouse_pos = pygame.mouse.get_pos()
            clique = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    clique = True
                if event.type == pygame.KEYDOWN:
                    self.tratar_input_teclado(event)

            # ==========================================
            # HEADER: GERENCIAMENTO DE ARQUIVOS E NOME
            # ==========================================
            pygame.draw.rect(self.tela, TEMA['painel'], (15, 15, 1190, 75), border_radius=6)
            pygame.draw.rect(self.tela, TEMA['borda'], (15, 15, 1190, 75), 2, border_radius=6)
            
            desenhar_texto(self.tela, "BUILDER DE MONSTROS (INPUT DIRETO & BATCH)", 30, 25, self.fonte_titulo, TEMA['destaque'])
            
            rect_nome = pygame.Rect(30, 50, 220, 28)
            foco_nome = (self.input_foco == ('nome', None))
            pygame.draw.rect(self.tela, TEMA['hover'] if foco_nome else TEMA['fundo'], rect_nome, border_radius=4)
            pygame.draw.rect(self.tela, TEMA['borda'], rect_nome, 1, border_radius=4)
            if clique and rect_nome.collidepoint(mouse_pos):
                self.input_foco = ('nome', None)
                self.input_is_new_focus = True
            desenhar_texto(self.tela, f"Nome: {self.nome_monstro}{'_' if foco_nome else ''}", 35, 55, self.fonte, TEMA['texto'])

            if desenhar_botao(self.tela, "TROCAR JSON", pygame.Rect(270, 38, 120, 38), mouse_pos, clique, self.fonte):
                self.listar_arquivos_monstros()
                if self.arquivos_monstros:
                    self.arquivo_idx = (self.arquivo_idx + 1) % len(self.arquivos_monstros)
                    self.carregar_monstro_arquivo(self.arquivos_monstros[self.arquivo_idx])

            if desenhar_botao(self.tela, "NOVO TEMPLATE", pygame.Rect(405, 38, 130, 38), mouse_pos, clique, self.fonte, (60, 100, 60)):
                self.nome_monstro = "Novo Monstro"
                self.id_template = "novo_monstro"
                self.vida_manual = "100"
                self.mana_manual = "50"
                self.atributos = { 'STR': "50", 'INT': "50", 'WILL': "50", 'AGI': "50", 'END': "50", 'CAR': "50", 'LCK': "50" }
                self.skills_primarias = ["ARMA-CONTUSAO"]

            if desenhar_botao(self.tela, "SALVAR JSON", pygame.Rect(1070, 38, 120, 38), mouse_pos, clique, self.fonte, (110, 90, 40)):
                self.salvar_template_atual()

            # ==========================================
            # COLUNA 1: ATRIBUTOS PRIMÁRIOS (0-100)
            # ==========================================
            pygame.draw.rect(self.tela, TEMA['painel'], (15, 105, 350, 635), border_radius=6)
            pygame.draw.rect(self.tela, TEMA['borda'], (15, 105, 350, 635), 2, border_radius=6)
            
            desenhar_texto(self.tela, "ATRIBUTOS PRIMÁRIOS (0 - 100)", 30, 120, self.fonte_titulo, TEMA['destaque'])
            
            py = 160
            for atr, val in self.atributos.items():
                desenhar_texto(self.tela, f"{atr:4s}:", 30, py, self.fonte)
                
                rect_input_atr = pygame.Rect(95, py - 3, 55, 24)
                foco_este = (self.input_foco == ('atributo', atr))
                
                pygame.draw.rect(self.tela, TEMA['hover'] if foco_este else TEMA['fundo'], rect_input_atr, border_radius=3)
                pygame.draw.rect(self.tela, TEMA['borda'], rect_input_atr, 1, border_radius=3)
                
                if clique and rect_input_atr.collidepoint(mouse_pos):
                    self.input_foco = ('atributo', atr)
                    self.input_is_new_focus = True
                    
                desenhar_texto(self.tela, f"{val}{'_' if foco_este else ''}", 102, py, self.fonte, TEMA['texto'])
                py += 36

            # ==========================================
            # COLUNA 2: STATUS MANUAIS & BATCH FILL
            # ==========================================
            pygame.draw.rect(self.tela, TEMA['painel'], (380, 105, 380, 635), border_radius=6)
            pygame.draw.rect(self.tela, TEMA['borda'], (380, 105, 380, 635), 2, border_radius=6)
            
            desenhar_texto(self.tela, "STATUS DE COMBATE & PREENCHIMENTO", 395, 120, self.fonte_titulo, TEMA['destaque'])
            
            # Vida Manual
            py_vm = 160
            desenhar_texto(self.tela, "Vida Inicial:", 395, py_vm, self.fonte)
            rect_vida = pygame.Rect(520, py_vm - 3, 75, 26)
            foco_vida = (self.input_foco == ('vida', None))
            pygame.draw.rect(self.tela, TEMA['hover'] if foco_vida else TEMA['fundo'], rect_vida, border_radius=3)
            pygame.draw.rect(self.tela, TEMA['borda'], rect_vida, 1, border_radius=3)
            if clique and rect_vida.collidepoint(mouse_pos):
                self.input_foco = ('vida', None)
                self.input_is_new_focus = True
            desenhar_texto(self.tela, f"{self.vida_manual}{'_' if foco_vida else ''}", 527, py_vm, self.fonte, TEMA['texto'])

            # Mana Manual
            py_mm = 205
            desenhar_texto(self.tela, "Mana Inicial:", 395, py_mm, self.fonte)
            rect_mana = pygame.Rect(520, py_mm - 3, 75, 26)
            foco_mana = (self.input_foco == ('mana', None))
            pygame.draw.rect(self.tela, TEMA['hover'] if foco_mana else TEMA['fundo'], rect_mana, border_radius=3)
            pygame.draw.rect(self.tela, TEMA['borda'], rect_mana, 1, border_radius=3)
            if clique and rect_mana.collidepoint(mouse_pos):
                self.input_foco = ('mana', None)
                self.input_is_new_focus = True
            desenhar_texto(self.tela, f"{self.mana_manual}{'_' if foco_mana else ''}", 527, py_mm, self.fonte, TEMA['texto'])

            # Resumo Peso
            str_val = int(self.atributos['STR']) if self.atributos['STR'].isdigit() else 0
            end_val = int(self.atributos['END']) if self.atributos['END'].isdigit() else 0
            peso_max = str_val + end_val
            desenhar_texto(self.tela, f"Peso Máximo (STR+END): {peso_max} kg", 395, 255, self.fonte)

            # --- PAINEL DE BATCH FILL (PREENCHIMENTO RÁPIDO) ---
            by = 310
            desenhar_texto(self.tela, "FERRAMENTAS DE PREENCHIMENTO RÁPIDO", 395, by, self.fonte_titulo, TEMA['destaque'])
            
            # 1. Primários Fixo
            by += 35
            desenhar_texto(self.tela, "Prim. Fixo:", 395, by, self.fonte)
            r_bp_f = pygame.Rect(485, by - 3, 45, 24)
            f_bp_f = (self.input_foco == ('b_v_pri', None))
            pygame.draw.rect(self.tela, TEMA['hover'] if f_bp_f else TEMA['fundo'], r_bp_f, border_radius=3)
            pygame.draw.rect(self.tela, TEMA['borda'], r_bp_f, 1, border_radius=3)
            if clique and r_bp_f.collidepoint(mouse_pos):
                self.input_foco = ('b_v_pri', None); self.input_is_new_focus = True
            desenhar_texto(self.tela, f"{self.batch_val_pri}{'_' if f_bp_f else ''}", 492, by, self.fonte, TEMA['texto'])
            
            if desenhar_botao(self.tela, "Preencher", pygame.Rect(545, by - 4, 85, 26), mouse_pos, clique, self.fonte, (50, 90, 50)):
                self.preencher_pri_fixo()

            # 2. Primários Range
            by += 40
            desenhar_texto(self.tela, "Prim. Range:", 395, by, self.fonte)
            r_bp_mn = pygame.Rect(485, by - 3, 40, 24)
            f_bp_mn = (self.input_foco == ('b_min_pri', None))
            pygame.draw.rect(self.tela, TEMA['hover'] if f_bp_mn else TEMA['fundo'], r_bp_mn, border_radius=3)
            pygame.draw.rect(self.tela, TEMA['borda'], r_bp_mn, 1, border_radius=3)
            if clique and r_bp_mn.collidepoint(mouse_pos):
                self.input_foco = ('b_min_pri', None); self.input_is_new_focus = True
            desenhar_texto(self.tela, f"{self.batch_min_pri}{'_' if f_bp_mn else ''}", 490, by, self.fonte, TEMA['texto'])

            r_bp_mx = pygame.Rect(535, by - 3, 40, 24)
            f_bp_mx = (self.input_foco == ('b_max_pri', None))
            pygame.draw.rect(self.tela, TEMA['hover'] if f_bp_mx else TEMA['fundo'], r_bp_mx, border_radius=3)
            pygame.draw.rect(self.tela, TEMA['borda'], r_bp_mx, 1, border_radius=3)
            if clique and r_bp_mx.collidepoint(mouse_pos):
                self.input_foco = ('b_max_pri', None); self.input_is_new_focus = True
            desenhar_texto(self.tela, f"{self.batch_max_pri}{'_' if f_bp_mx else ''}", 540, by, self.fonte, TEMA['texto'])

            if desenhar_botao(self.tela, "Sortear", pygame.Rect(585, by - 4, 80, 26), mouse_pos, clique, self.fonte, (50, 70, 110)):
                self.preencher_pri_range()

            # 3. Derivados/Skills Fixo
            by += 50
            desenhar_texto(self.tela, "Skill Fixo:", 395, by, self.fonte)
            r_bs_f = pygame.Rect(485, by - 3, 45, 24)
            f_bs_f = (self.input_foco == ('b_v_sk', None))
            pygame.draw.rect(self.tela, TEMA['hover'] if f_bs_f else TEMA['fundo'], r_bs_f, border_radius=3)
            pygame.draw.rect(self.tela, TEMA['borda'], r_bs_f, 1, border_radius=3)
            if clique and r_bs_f.collidepoint(mouse_pos):
                self.input_foco = ('b_v_sk', None); self.input_is_new_focus = True
            desenhar_texto(self.tela, f"{self.batch_val_sk}{'_' if f_bs_f else ''}", 492, by, self.fonte, TEMA['texto'])
            
            if desenhar_botao(self.tela, "Preencher", pygame.Rect(545, by - 4, 85, 26), mouse_pos, clique, self.fonte, (50, 90, 50)):
                self.preencher_sk_fixo()

            # 4. Derivados/Skills Range
            by += 40
            desenhar_texto(self.tela, "Skill Range:", 395, by, self.fonte)
            r_bs_mn = pygame.Rect(485, by - 3, 40, 24)
            f_bs_mn = (self.input_foco == ('b_min_sk', None))
            pygame.draw.rect(self.tela, TEMA['hover'] if f_bs_mn else TEMA['fundo'], r_bs_mn, border_radius=3)
            pygame.draw.rect(self.tela, TEMA['borda'], r_bs_mn, 1, border_radius=3)
            if clique and r_bs_mn.collidepoint(mouse_pos):
                self.input_foco = ('b_min_sk', None); self.input_is_new_focus = True
            desenhar_texto(self.tela, f"{self.batch_min_sk}{'_' if f_bs_mn else ''}", 490, by, self.fonte, TEMA['texto'])

            r_bs_mx = pygame.Rect(535, by - 3, 40, 24)
            f_bs_mx = (self.input_foco == ('b_max_sk', None))
            pygame.draw.rect(self.tela, TEMA['hover'] if f_bs_mx else TEMA['fundo'], r_bs_mx, border_radius=3)
            pygame.draw.rect(self.tela, TEMA['borda'], r_bs_mx, 1, border_radius=3)
            if clique and r_bs_mx.collidepoint(mouse_pos):
                self.input_foco = ('b_max_sk', None); self.input_is_new_focus = True
            desenhar_texto(self.tela, f"{self.batch_max_sk}{'_' if f_bs_mx else ''}", 540, by, self.fonte, TEMA['texto'])

            if desenhar_botao(self.tela, "Sortear", pygame.Rect(585, by - 4, 80, 26), mouse_pos, clique, self.fonte, (50, 70, 110)):
                self.preencher_sk_range()

            # ==========================================
            # COLUNA 3: SKILLS DO MONSTRO (INPUTS 0-100)
            # ==========================================
            pygame.draw.rect(self.tela, TEMA['painel'], (775, 105, 430, 635), border_radius=6)
            pygame.draw.rect(self.tela, TEMA['borda'], (775, 105, 430, 635), 2, border_radius=6)
            
            desenhar_texto(self.tela, "SKILLS DO MONSTRO (Até 5 Primárias)", 790, 120, self.fonte_titulo, TEMA['destaque'])
            
            todas_skills = list(self.skills_dict.keys())
            
            sk_y = 160
            for sk in todas_skills[:16]:
                eh_primaria = sk in self.skills_primarias
                val_sk = self.skills_niveis.get(sk, "30")
                
                box_rect = pygame.Rect(790, sk_y, 18, 18)
                pygame.draw.rect(self.tela, TEMA['checkbox_on'] if eh_primaria else TEMA['fundo'], box_rect)
                pygame.draw.rect(self.tela, TEMA['borda'], box_rect, 1)
                
                cor_sk = TEMA['destaque'] if eh_primaria else TEMA['texto']
                desenhar_texto(self.tela, f"{sk[:16]:16s}", 815, sk_y - 2, self.fonte, cor_sk)
                
                rect_input_sk = pygame.Rect(1070, sk_y - 3, 50, 22)
                foco_sk = (self.input_foco == ('skill', sk))
                
                pygame.draw.rect(self.tela, TEMA['hover'] if foco_sk else TEMA['fundo'], rect_input_sk, border_radius=3)
                pygame.draw.rect(self.tela, TEMA['borda'], rect_input_sk, 1, border_radius=3)
                
                if clique and rect_input_sk.collidepoint(mouse_pos):
                    self.input_foco = ('skill', sk)
                    self.input_is_new_focus = True
                if clique and box_rect.collidepoint(mouse_pos):
                    if eh_primaria:
                        self.skills_primarias.remove(sk)
                    else:
                        if len(self.skills_primarias) < 5:
                            self.skills_primarias.append(sk)
                            
                desenhar_texto(self.tela, f"{val_sk}{'_' if foco_sk else ''}", 1077, sk_y - 2, self.fonte, TEMA['texto'])
                
                sk_y += 34

            pygame.display.flip()
            clock.tick(30)

if __name__ == "__main__":
    app = CriadorMonstros()
    app.rodar()