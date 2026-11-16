import pygame
import sys
import json
import random

# ==========================================
# CONFIGURAÇÕES VISUAIS
# ==========================================
TEMA = {
    'fundo': (20, 20, 30),
    'painel': (40, 40, 60),
    'borda': (150, 150, 150),
    'texto': (255, 255, 255),
    'destaque': (255, 215, 0),
    'modificado': (100, 255, 100), 
    'hover': (100, 200, 255),
    'desativado': (100, 100, 100),
    'btn_fundo': (60, 60, 90)
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
# GERADOR RÁPIDO
# ==========================================
class GeradorRapido:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption("Gerador Rápido de Personagem")
        self.fonte = pygame.font.SysFont("consolas", 14)
        self.fonte_titulo = pygame.font.SysFont("consolas", 18, bold=True)
        
        self.carregar_dados()
        
        self.nome = ""
        self.raca_idx = 0
        self.classe_idx = 0
        
        self.input_ativo = False
        
        self.resetar_dados_distribuicao()
        self.rolar_tudo()

    def carregar_dados(self):
        try:
            with open('racas.json', 'r', encoding='utf-8') as f: self.racas = json.load(f)
            with open('classes.json', 'r', encoding='utf-8') as f: self.classes = json.load(f)
            with open('skills.json', 'r', encoding='utf-8') as f: self.skills_dict = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar JSON: {e}")
            sys.exit()

    def resetar_dados_distribuicao(self):
        self.atributos_base = { 'STR': 10, 'AGI': 10, 'VIT': 10, 'INT': 10, 'LCK': 10, 'CAR': 10, 'WILL': 10}
        self.atributos_gastos = { k: 0 for k in self.atributos_base }
        self.skills_base = { k: 15 for k in self.skills_dict.keys() }
        self.skills_gastos_c = { k: 0 for k in self.skills_dict.keys() }
        self.skills_gastos_o = { k: 0 for k in self.skills_dict.keys() }
        
        self.pts_atr = 0
        self.pts_sk_c = 8
        self.pts_sk_o = 6

    def rolar_tudo(self):
        r = self.racas[self.raca_idx]
        c = self.classes[self.classe_idx]
        
        self.resetar_dados_distribuicao()
        
        self.pts_atr = random.randint(6, 14)
        for atr, val in c['base_attributes'].items():
            k = 'VIT' if atr == 'END' else atr
            if k in self.atributos_base:
                self.atributos_base[k] = val + random.randint(0, 10)

        bonus_list = r['bonus'] if isinstance(r['bonus'], list) else [r['bonus']]
        for b in bonus_list:
            if b['tipo'] == 'atributo_primario':
                alvo = 'VIT' if b.get('atributo_alvo', '') == 'END' else b.get('atributo_alvo', '')
                val = int(b['valor'])
                if b.get('atributo', '') == 'qualquer': self.pts_atr += val
                elif alvo in self.atributos_base:
                    self.atributos_base[alvo] += val if b['calculo'] == 'adicao' else -val

        sk_c = c['skills'].get('primary', []) + c['skills'].get('major', []) + c['skills'].get('minor', [])
        for sk in self.skills_base.keys():
            base = 25 if sk in sk_c else 15
            self.skills_base[sk] = base + random.randint(3, 6)

        for b in bonus_list:
            if b['tipo'] == 'atributo_secundario':
                alvo = b.get('atributo_alvo', '').upper()
                val = int(b['valor'])
                for sk in self.skills_base:
                    if sk.lower() == alvo.lower():
                        self.skills_base[sk] += val if b['calculo'] == 'adicao' else -val
                        break

    def auto_preencher(self):
        c = self.classes[self.classe_idx]
        cid = c['id']
        
        prioridades_atr = {
            'barbarian': ['STR', 'VIT', 'AGI'],
            'knight': ['STR', 'VIT', 'CAR'],
            'mage': ['INT', 'WILL', 'CAR'],
            'monk': ['AGI', 'STR', 'VIT'],
            'thief': ['AGI', 'CAR', 'LCK']
        }.get(cid, ['STR', 'VIT'])
        
        idx = 0
        while self.pts_atr > 0:
            atr_alvo = prioridades_atr[idx % len(prioridades_atr)]
            self.atributos_gastos[atr_alvo] += 1
            self.pts_atr -= 1
            idx += 1

        sk_c = c['skills'].get('primary', []) + c['skills'].get('major', [])
        if not sk_c: sk_c = c['skills'].get('minor', [])
        idx = 0
        while self.pts_sk_c > 0 and sk_c:
            sk_alvo = sk_c[idx % len(sk_c)]
            if sk_alvo in self.skills_gastos_c:
                self.skills_gastos_c[sk_alvo] += 1
                self.pts_sk_c -= 1
            idx += 1

        outras = [sk for sk in self.skills_base.keys() if sk not in sk_c]
        if outras:
            for _ in range(self.pts_sk_o):
                sk_alvo = random.choice(outras)
                self.skills_gastos_o[sk_alvo] += 1
                self.pts_sk_o -= 1

    def salvar_json(self):
        char_data = {
            "nome": self.nome if self.nome else "Desconhecido",
            "raca": self.racas[self.raca_idx]['nome'],
            "classe": self.classes[self.classe_idx]['name'],
            "atributos_finais": {k: self.atributos_base[k] + self.atributos_gastos[k] for k in self.atributos_base},
            "skills_finais": {k: self.skills_base[k] + self.skills_gastos_c[k] + self.skills_gastos_o[k] for k in self.skills_base}
        }
        
        nome_arquivo = f"char_{char_data['nome'].replace(' ', '_').lower()}.json"
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(char_data, f, indent=4, ensure_ascii=False)
            print(f"Personagem salvo com sucesso em: {nome_arquivo}")
        except Exception as e:
            print(f"Erro ao salvar: {e}")

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
                if event.type == pygame.KEYDOWN and self.input_ativo:
                    if event.key == pygame.K_BACKSPACE:
                        self.nome = self.nome[:-1]
                    elif len(self.nome) < 15 and event.unicode.isprintable():
                        self.nome += event.unicode

            # --- HEADER ---
            desenhar_texto(self.tela, "GERADOR RÁPIDO", 20, 20, self.fonte_titulo, TEMA['destaque'])
            
            rect_nome = pygame.Rect(20, 50, 200, 30)
            pygame.draw.rect(self.tela, TEMA['hover'] if self.input_ativo else TEMA['painel'], rect_nome, border_radius=5)
            pygame.draw.rect(self.tela, TEMA['borda'], rect_nome, 2, border_radius=5)
            if clique: self.input_ativo = rect_nome.collidepoint(mouse_pos)
            desenhar_texto(self.tela, f"Nome: {self.nome}{'_' if self.input_ativo else ''}", 30, 55, self.fonte)

            if desenhar_botao(self.tela, f"Raça: {self.racas[self.raca_idx]['nome']}", pygame.Rect(240, 50, 180, 30), mouse_pos, clique, self.fonte):
                self.raca_idx = (self.raca_idx + 1) % len(self.racas)
                self.rolar_tudo()
                
            if desenhar_botao(self.tela, f"Classe: {self.classes[self.classe_idx]['name']}", pygame.Rect(430, 50, 180, 30), mouse_pos, clique, self.fonte):
                self.classe_idx = (self.classe_idx + 1) % len(self.classes)
                self.rolar_tudo()

            if desenhar_botao(self.tela, "REROLLAR TUDO", pygame.Rect(630, 50, 120, 30), mouse_pos, clique, self.fonte, (100, 50, 50)):
                self.rolar_tudo()
            if desenhar_botao(self.tela, "AUTO-PREENCHER", pygame.Rect(760, 50, 130, 30), mouse_pos, clique, self.fonte, (50, 100, 50)):
                self.auto_preencher()
            if desenhar_botao(self.tela, "SALVAR JSON", pygame.Rect(900, 50, 100, 30), mouse_pos, clique, self.fonte, (100, 100, 50)):
                self.salvar_json()

            # --- CORPO: ATRIBUTOS (Esquerda) ---
            desenhar_texto(self.tela, f"ATRIBUTOS (Livres: {self.pts_atr})", 20, 100, self.fonte_titulo, TEMA['destaque'])
            py = 130
            for atr in self.atributos_base.keys():
                base = self.atributos_base[atr]
                gasto = self.atributos_gastos[atr]
                cor = TEMA['modificado'] if gasto > 0 else TEMA['texto']
                
                desenhar_texto(self.tela, f"{atr}: {base+gasto:02d} (Base {base})", 20, py, self.fonte, cor)
                
                btn_menos = pygame.Rect(200, py, 20, 20)
                btn_mais = pygame.Rect(225, py, 20, 20)
                
                if desenhar_botao(self.tela, "-", btn_menos, mouse_pos, clique, self.fonte) and gasto > 0:
                    self.atributos_gastos[atr] -= 1
                    self.pts_atr += 1
                if desenhar_botao(self.tela, "+", btn_mais, mouse_pos, clique, self.fonte) and self.pts_atr > 0:
                    self.atributos_gastos[atr] += 1
                    self.pts_atr -= 1
                py += 30

            # --- CORPO: STATUS DERIVADOS ---
            py += 20
            desenhar_texto(self.tela, "STATUS DERIVADOS", 20, py, self.fonte_titulo, TEMA['destaque'])
            py += 30
            
            str_atual = self.atributos_base['STR'] + self.atributos_gastos['STR']
            vit_atual = self.atributos_base['VIT'] + self.atributos_gastos['VIT']
            int_atual = self.atributos_base['INT'] + self.atributos_gastos['INT']
            
            # ATUALIZADO AQUI: Divisão inteira (//) para arredondar para baixo (Floor division)
            mod_end = (vit_atual - 50) // 10
            
            dado_hp = self.classes[self.classe_idx].get('max_hp_per_level', 10)
            vida_inicial = max(1, int((dado_hp * 2) + mod_end))

            mult_mana = self.classes[self.classe_idx].get('multiplicador_mana', 1.0)
            mana_inicial = int(int_atual * mult_mana)
        
            peso_maximo = str_atual + vit_atual
            
            # ATUALIZADO AQUI: Formatação alterada para inteiro com sinal (+ ou -)
            desenhar_texto(self.tela, f"Modificador de END: {mod_end:+d}", 20, py, self.fonte)
            py += 25
            desenhar_texto(self.tela, f"Vida Inicial: {vida_inicial}", 20, py, self.fonte)
            py += 25
            desenhar_texto(self.tela, f"Mana Inicial: {mana_inicial}", 20, py, self.fonte)
            py += 25
            desenhar_texto(self.tela, f"Peso Máximo (STR+END): {peso_maximo} kg", 20, py, self.fonte)

            # --- CORPO: SKILLS (Direita - 2 Colunas) ---
            desenhar_texto(self.tela, f"SKILLS (Classe: {self.pts_sk_c} | Outras: {self.pts_sk_o})", 280, 100, self.fonte_titulo, TEMA['destaque'])
            
            c = self.classes[self.classe_idx]
            sk_c = c['skills'].get('primary', []) + c['skills'].get('major', []) + c['skills'].get('minor', [])
            todas = list(self.skills_base.keys())
            todas.sort(key=lambda x: (0 if x in sk_c else 1, x))
            
            for i, sk in enumerate(todas):
                eh_classe = sk in sk_c
                base = self.skills_base[sk]
                gasto = self.skills_gastos_c[sk] + self.skills_gastos_o[sk]
                
                px = 280 if i < 15 else 620
                py = 130 + (i % 15) * 35
                
                cor = TEMA['modificado'] if gasto > 0 else (TEMA['destaque'] if eh_classe else TEMA['texto'])
                marcador = "[C] " if eh_classe else "[O] "
                
                desenhar_texto(self.tela, f"{marcador}{sk[:15]}: {base+gasto:02d}", px, py, self.fonte, cor)
                
                btn_m = pygame.Rect(px + 230, py, 25, 25)
                btn_p = pygame.Rect(px + 260, py, 25, 25)
                
                if desenhar_botao(self.tela, "-", btn_m, mouse_pos, clique, self.fonte) and gasto > 0:
                    if eh_classe:
                        self.skills_gastos_c[sk] -= 1
                        self.pts_sk_c += 1
                    else:
                        self.skills_gastos_o[sk] -= 1
                        self.pts_sk_o += 1
                        
                if desenhar_botao(self.tela, "+", btn_p, mouse_pos, clique, self.fonte):
                    if eh_classe and self.pts_sk_c > 0:
                        self.skills_gastos_c[sk] += 1
                        self.pts_sk_c -= 1
                    elif not eh_classe and self.pts_sk_o > 0:
                        self.skills_gastos_o[sk] += 1
                        self.pts_sk_o -= 1

            pygame.display.flip()
            clock.tick(30)

if __name__ == "__main__":
    app = GeradorRapido()
    app.rodar()