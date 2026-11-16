import pygame
import sys
import json
import os
from personagem import Personagem

# ==========================================
# CONFIGURAÇÕES VISUAIS
# ==========================================
TEMA = {
    'fundo': (18, 18, 28),
    'painel': (32, 32, 48),
    'borda': (140, 140, 160),
    'texto': (255, 255, 255),
    'destaque': (255, 215, 0),
    'modificado': (100, 255, 100), 
    'hover': (100, 200, 255),
    'desativado': (100, 100, 100),
    'btn_fundo': (55, 55, 85)
}

LIMITE_MAXIMO = 100

def desenhar_texto(surface, texto, x, y, fonte, cor=TEMA['texto']):
    img = fonte.render(texto, True, cor)
    surface.blit(img, (x, y))
    return img.get_rect(topleft=(x, y))

def desenhar_botao(surface, texto, rect, mouse_pos, clique, fonte, cor_base=TEMA['btn_fundo']):
    hover = rect.collidepoint(mouse_pos)
    cor = TEMA['hover'] if hover else cor_base
    pygame.draw.rect(surface, cor, rect, border_radius=4)
    pygame.draw.rect(surface, TEMA['borda'], rect, 1, border_radius=4)
    
    txt_img = fonte.render(texto, True, TEMA['texto'])
    txt_rect = txt_img.get_rect(center=rect.center)
    surface.blit(txt_img, txt_rect)
    return hover and clique

# ==========================================
# SIMULADOR DE EVOLUÇÃO E NÍVEL
# ==========================================
class SimuladorEvolucao:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((1220, 768))
        pygame.display.set_caption("Simulador de Evolução de Personagem (Level & Skills)")
        self.fonte = pygame.font.SysFont("consolas", 13)
        self.fonte_titulo = pygame.font.SysFont("consolas", 16, bold=True)
        
        self.carregar_bancos()
        self.listar_arquivos_personagens()
        
        self.arquivo_idx = 0
        self.gastos_sessao = {}
        self.skills_gastas_sessao = {}
        self.carregar_personagem_atual()

    def carregar_bancos(self):
        try:
            with open('classes.json', 'r', encoding='utf-8') as f:
                self.classes_db = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar classes.json: {e}")
            sys.exit()

    def listar_arquivos_personagens(self):
        self.arquivos_char = [f for f in os.listdir('.') if f.startswith('char_') and f.endswith('.json')]
        if not self.arquivos_char:
            char_padrao = {
                "nome": "Conan Teste",
                "raca": "Humano",
                "classe": "Barbarian",
                "atributos_finais": {"STR": 75, "AGI": 55, "VIT": 65, "INT": 40, "LCK": 55, "CAR": 10, "WILL": 45},
                "skills_finais": {"ARMA-CONTUSAO": 35, "ARMA-CORTE": 35, "RESISTENCIA FISICA": 35, "NATUREZA": 30, "DESTRUICAO": 20}
            }
            with open('char_conan_teste.json', 'w', encoding='utf-8') as f:
                json.dump(char_padrao, f, indent=4, ensure_ascii=False)
            self.arquivos_char = ['char_conan_teste.json']

    def obter_skills_classe_atual(self):
        classe_info = next((c for c in self.classes_db if c['id'] == self.char.classe_id), None)
        if not classe_info:
            return []
        sk = classe_info.get('skills', {})
        return sk.get('primary', []) + sk.get('major', []) + sk.get('minor', [])

    def carregar_personagem_atual(self):
        nome_arq = self.arquivos_char[self.arquivo_idx]
        with open(nome_arq, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        self.char = Personagem.carregar_de_json(dados, self.classes_db)
        self.gastos_sessao = {k: 0 for k in self.char.atributos}
        self.skills_gastas_sessao = {k: 0 for k in self.char.skills}
        self.skills_da_classe = self.obter_skills_classe_atual()

    def auto_distribuir_atributos(self):
        # Define estritamente os 3 atributos principais da classe
        prioridades = {
            'barbarian': ['STR', 'VIT', 'AGI'],
            'knight': ['STR', 'VIT', 'CAR'],
            'mage': ['INT', 'WILL', 'CAR'],
            'monk': ['AGI', 'STR', 'VIT'],
            'thief': ['AGI', 'CAR', 'LCK']
        }.get(self.char.classe_id, ['STR', 'VIT'])
        
        while self.char.pontos_atributo_livres > 0:
            distribuiu_algum = False
            
            # 1. Tenta distribuir ciclando APENAS entre os 3 atributos prioritários
            for atr in prioridades:
                if self.char.pontos_atributo_livres <= 0:
                    break
                if atr in self.char.atributos and self.char.atributos[atr] < LIMITE_MAXIMO:
                    self.char.atributos[atr] += 1
                    self.gastos_sessao[atr] += 1
                    self.char.pontos_atributo_livres -= 1
                    distribuiu_algum = True
            
            # 2. Se os 3 prioritários já estiverem em 100, permite usar nos demais atributos restantes
            if not distribuiu_algum:
                outros = [k for k in self.char.atributos.keys() if k not in prioridades]
                for atr in outros:
                    if self.char.pontos_atributo_livres <= 0:
                        break
                    if self.char.atributos[atr] < LIMITE_MAXIMO:
                        self.char.atributos[atr] += 1
                        self.gastos_sessao[atr] += 1
                        self.char.pontos_atributo_livres -= 1
                        distribuiu_algum = True
            
            # Se absolutamente tudo estiver em 100, para o loop para evitar travamento
            if not distribuiu_algum:
                self.char.historico_evolucao.append("Todos os atributos atingiram o limite de 100!")
                break
            
        self.char.atualizar_status_derivados()

    def upar_skills_da_classe(self, quantidade=5):
        alguma_subiu = False
        for sk in self.skills_da_classe:
            if sk in self.char.skills:
                nivel_atual = self.char.skills[sk]['nivel']
                ganho_real = min(quantidade, LIMITE_MAXIMO - nivel_atual)
                if ganho_real > 0:
                    self.char.skills[sk]['nivel'] += ganho_real
                    self.skills_gastas_sessao[sk] = self.skills_gastas_sessao.get(sk, 0) + ganho_real
                    alguma_subiu = True
                    
        if alguma_subiu:
            self.char.historico_evolucao.append(f"Skills da classe ({self.char.classe_nome}) subiram até +{quantidade} níveis (Máx 100)!")
        else:
            self.char.historico_evolucao.append("Todas as skills da classe já estão no nível máximo (100)!")

    def simular_treino_xp_skills(self, xp_ganha=250):
        subiram = []
        for sk in self.skills_da_classe:
            if sk in self.char.skills:
                nivel_antes = self.char.skills[sk]['nivel']
                self.char.ganhar_xp_skill(sk, xp_ganha)
                ganho = self.char.skills[sk]['nivel'] - nivel_antes
                if ganho > 0:
                    self.skills_gastas_sessao[sk] = self.skills_gastas_sessao.get(sk, 0) + ganho
                    subiram.append(f"{sk} (+{ganho})")
        
        if subiram:
            self.char.historico_evolucao.append(f"Treino (+{xp_ganha} XP): {', '.join(subiram)}")
        else:
            self.char.historico_evolucao.append(f"Treino (+{xp_ganha} XP): Nenhuma skill subiu (ou já atingiram 100).")

    def salvar_evolucao_json(self):
        nome_arq = self.arquivos_char[self.arquivo_idx]
        dados_salvar = {
            "nome": self.char.nome,
            "nivel": self.char.nivel,
            "raca": self.char.raca_nome,
            "classe": self.char.classe_nome,
            "vida_maxima": self.char.vida_maxima,
            "mana_maxima": self.char.mana_maxima,
            "atributos_finais": self.char.atributos,
            "skills_finais": {k: v['nivel'] for k, v in self.char.skills.items()}
        }
        with open(nome_arq, 'w', encoding='utf-8') as f:
            json.dump(dados_salvar, f, indent=4, ensure_ascii=False)
        self.char.historico_evolucao.append(f"Salvo com sucesso em {nome_arq}!")

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
                    if event.key == pygame.K_SPACE:
                        self.char.subir_um_nivel_direto()
                    elif event.key == pygame.K_a:
                        self.auto_distribuir_atributos()
                    elif event.key == pygame.K_s:
                        self.upar_skills_da_classe(5)

            # ==========================================
            # BARRA SUPERIOR: CONTROLES E ARQUIVO
            # ==========================================
            pygame.draw.rect(self.tela, TEMA['painel'], (15, 15, 1190, 75), border_radius=6)
            pygame.draw.rect(self.tela, TEMA['borda'], (15, 15, 1190, 75), 2, border_radius=6)
            
            desenhar_texto(self.tela, f"ARQUIVO: {self.arquivos_char[self.arquivo_idx]}", 30, 25, self.fonte_titulo, TEMA['destaque'])
            desenhar_texto(self.tela, f"{self.char.nome} | Raça: {self.char.raca_nome} | Classe: {self.char.classe_nome} (Prog: {self.char.tipo_progressao})", 30, 52, self.fonte)

            if desenhar_botao(self.tela, "TROCAR JSON", pygame.Rect(520, 30, 120, 40), mouse_pos, clique, self.fonte):
                self.listar_arquivos_personagens()
                self.arquivo_idx = (self.arquivo_idx + 1) % len(self.arquivos_char)
                self.carregar_personagem_atual()

            if desenhar_botao(self.tela, "RESETAR NV 1", pygame.Rect(650, 30, 120, 40), mouse_pos, clique, self.fonte, (100, 50, 50)):
                self.carregar_personagem_atual()

            if desenhar_botao(self.tela, "+1 NÍVEL (Espaço)", pygame.Rect(780, 30, 160, 40), mouse_pos, clique, self.fonte, (40, 110, 60)):
                self.char.subir_um_nivel_direto()

            if desenhar_botao(self.tela, "+5 NÍVEIS", pygame.Rect(950, 30, 110, 40), mouse_pos, clique, self.fonte, (40, 90, 120)):
                for _ in range(5): self.char.subir_um_nivel_direto()

            if desenhar_botao(self.tela, "SALVAR JSON", pygame.Rect(1070, 30, 115, 40), mouse_pos, clique, self.fonte, (110, 100, 40)):
                self.salvar_evolucao_json()

            # ==========================================
            # COLUNA 1: ATRIBUTOS E DISTRIBUIÇÃO
            # ==========================================
            pygame.draw.rect(self.tela, TEMA['painel'], (15, 105, 310, 440), border_radius=6)
            pygame.draw.rect(self.tela, TEMA['borda'], (15, 105, 310, 440), 2, border_radius=6)
            
            cor_pts = TEMA['modificado'] if self.char.pontos_atributo_livres > 0 else TEMA['destaque']
            desenhar_texto(self.tela, f"ATRIBUTOS (Pontos: {self.char.pontos_atributo_livres})", 30, 120, self.fonte_titulo, cor_pts)
            
            py = 160
            for atr, val in self.char.atributos.items():
                gasto = self.gastos_sessao.get(atr, 0)
                cor = TEMA['modificado'] if gasto > 0 else TEMA['texto']
                desenhar_texto(self.tela, f"{atr:4s}: {val:03d} (+{gasto})", 30, py, self.fonte, cor)
                
                btn_menos = pygame.Rect(210, py - 3, 28, 24)
                btn_mais = pygame.Rect(245, py - 3, 28, 24)
                
                cor_m = TEMA['btn_fundo'] if gasto > 0 else TEMA['desativado']
                cor_p = TEMA['btn_fundo'] if (self.char.pontos_atributo_livres > 0 and val < LIMITE_MAXIMO) else TEMA['desativado']
                
                if desenhar_botao(self.tela, "-", btn_menos, mouse_pos, clique, self.fonte, cor_m) and gasto > 0:
                    self.char.atributos[atr] -= 1
                    self.gastos_sessao[atr] -= 1
                    self.char.pontos_atributo_livres += 1
                    self.char.atualizar_status_derivados()
                    
                if desenhar_botao(self.tela, "+", btn_mais, mouse_pos, clique, self.fonte, cor_p) and self.char.pontos_atributo_livres > 0 and val < LIMITE_MAXIMO:
                    self.char.atributos[atr] += 1
                    self.gastos_sessao[atr] += 1
                    self.char.pontos_atributo_livres -= 1
                    self.char.atualizar_status_derivados()
                py += 36

            if desenhar_botao(self.tela, "AUTO-DISTRIBUIR CLASSE (Tecla A)", pygame.Rect(30, 485, 280, 40), mouse_pos, clique, self.fonte, (50, 100, 50)):
                self.auto_distribuir_atributos()

            # ==========================================
            # COLUNA 2: ESTATÍSTICAS CALCULADAS (Personagem)
            # ==========================================
            pygame.draw.rect(self.tela, TEMA['painel'], (340, 105, 355, 440), border_radius=6)
            pygame.draw.rect(self.tela, TEMA['borda'], (340, 105, 355, 440), 2, border_radius=6)
            
            desenhar_texto(self.tela, "ESTATÍSTICAS CALCULADAS", 355, 120, self.fonte_titulo, TEMA['destaque'])
            
            mod_end = self.char.calcular_modificador_end()
            chance_sorte = min(100.0, self.char.atributos['LCK'] * 0.95)
            
            skill_foco = self.skills_da_classe[0] if self.skills_da_classe else 'ARMA-CORTE'
            
            stats_calculados = [
                f"Nível Atual       : {self.char.nivel}",
                f"XP Próximo Nível  : {self.char.calcular_xp_para_proximo_nivel()}",
                f"XP Acumulada Total: {self.char.xp_acumulada_total}",
                "----------------------------------",
                f"Vida Máxima (HP)  : {self.char.vida_maxima} (Dado: d{self.char.dado_hp})",
                f"Mana Máxima (MP)  : {self.char.mana_maxima} (Mult: x{self.char.multiplicador_mana})",
                f"Modificador END   : {mod_end:+d}",
                f"Peso Máximo       : {self.char.peso_maximo} kg",
                f"Crítico de Sorte  : {chance_sorte:.1f}%",
                "----------------------------------",
                f"Esquiva           : {self.char.calcular_esquiva():.1f}%",
                f"Defesa Física     : {self.char.calcular_defesa_fisica()}",
                f"Resistência Mágica: {self.char.calcular_resistencia_magica():.1f}%",
                f"Atq Físico ({skill_foco[:6]}): {self.char.calcular_ataque_fisico(10, skill_foco):.1f}",
                f"Atq Mágico (DESTR): {self.char.calcular_ataque_magico(15, 'DESTRUICAO'):.1f}"
            ]
            
            sy = 155
            for linha in stats_calculados:
                cor_stat = TEMA['destaque'] if "Vida" in linha or "Mana" in linha or "Nível" in linha else TEMA['texto']
                desenhar_texto(self.tela, linha, 355, sy, self.fonte, cor_stat)
                sy += 24

            # ==========================================
            # COLUNA 3: SKILLS E EVOLUÇÃO DE PERÍCIAS
            # ==========================================
            pygame.draw.rect(self.tela, TEMA['painel'], (710, 105, 495, 440), border_radius=6)
            pygame.draw.rect(self.tela, TEMA['borda'], (710, 105, 495, 440), 2, border_radius=6)
            
            desenhar_texto(self.tela, "EVOLUÇÃO DE SKILLS (* = Classe)", 725, 120, self.fonte_titulo, TEMA['destaque'])
            
            todas_skills = list(self.char.skills.keys())
            todas_skills.sort(key=lambda x: (0 if x in self.skills_da_classe else 1, x))
            
            for i, sk in enumerate(todas_skills):
                dados_sk = self.char.skills[sk]
                eh_classe = sk in self.skills_da_classe
                gasto_sk = self.skills_gastas_sessao.get(sk, 0)
                
                px = 725 if i < 11 else 965
                py_sk = 155 + (i % 11) * 28
                
                cor = TEMA['modificado'] if gasto_sk > 0 else (TEMA['destaque'] if eh_classe else TEMA['texto'])
                prefixo = "*" if eh_classe else " "
                
                desenhar_texto(self.tela, f"{prefixo}{sk[:12]:12s}: {dados_sk['nivel']:03d}", px, py_sk, self.fonte, cor)
                
                btn_m = pygame.Rect(px + 150, py_sk - 3, 24, 22)
                btn_p = pygame.Rect(px + 178, py_sk - 3, 24, 22)
                
                cor_sk_m = TEMA['btn_fundo'] if dados_sk['nivel'] > 1 else TEMA['desativado']
                cor_sk_p = TEMA['btn_fundo'] if dados_sk['nivel'] < LIMITE_MAXIMO else TEMA['desativado']
                
                if desenhar_botao(self.tela, "-", btn_m, mouse_pos, clique, self.fonte, cor_sk_m) and dados_sk['nivel'] > 1:
                    dados_sk['nivel'] -= 1
                    self.skills_gastas_sessao[sk] = max(0, gasto_sk - 1)
                    
                if desenhar_botao(self.tela, "+", btn_p, mouse_pos, clique, self.fonte, cor_sk_p) and dados_sk['nivel'] < LIMITE_MAXIMO:
                    dados_sk['nivel'] += 1
                    self.skills_gastas_sessao[sk] = gasto_sk + 1

            # Botões de Evolução Rápida de Skills
            if desenhar_botao(self.tela, "+5 NÍVEIS SKILLS CLASSE (Tecla S)", pygame.Rect(725, 485, 245, 40), mouse_pos, clique, self.fonte, (50, 100, 50)):
                self.upar_skills_da_classe(5)

            if desenhar_botao(self.tela, "TREINAR +250 XP SKILLS", pygame.Rect(980, 485, 210, 40), mouse_pos, clique, self.fonte, (70, 70, 120)):
                self.simular_treino_xp_skills(250)

            # ==========================================
            # RODAPÉ: LOG DE EVOLUÇÃO E SORTE
            # ==========================================
            pygame.draw.rect(self.tela, TEMA['painel'], (15, 560, 1190, 190), border_radius=6)
            pygame.draw.rect(self.tela, TEMA['borda'], (15, 560, 1190, 190), 2, border_radius=6)
            
            desenhar_texto(self.tela, "HISTÓRICO DE SUBIDA DE NÍVEL (ROLAGENS, SORTE E SKILLS)", 30, 575, self.fonte_titulo, TEMA['destaque'])
            
            ly = 605
            for msg in self.char.historico_evolucao[-6:]:
                cor_log = TEMA['modificado'] if ("Sorte" in msg or "Skills" in msg or "Treino" in msg) else TEMA['texto']
                desenhar_texto(self.tela, f"> {msg}", 30, ly, self.fonte, cor_log)
                ly += 22

            pygame.display.flip()
            clock.tick(30)

if __name__ == "__main__":
    simulador = SimuladorEvolucao()
    simulador.rodar()