import pygame
import sys
import json
import os

# ==========================================
# CONFIGURAÇÕES VISUAIS
# ==========================================
TEMA = {
    'fundo': (20, 22, 30),
    'painel': (32, 35, 48),
    'borda': (120, 130, 150),
    'texto': (255, 255, 255),
    'destaque': (255, 215, 0),
    'modificado': (100, 255, 100), 
    'hover': (80, 110, 160),
    'ativo': (60, 90, 140),
    'desativado': (80, 80, 90),
    'btn_fundo': (50, 60, 90),
    'checkbox_on': (50, 160, 50)
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
# GERENCIADOR DE EQUIPAMENTOS
# ==========================================
class GerenciadorEquipamentos:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((1280, 768))
        pygame.display.set_caption("Gerenciador de Equipamentos - Elder SIM")
        self.fonte = pygame.font.SysFont("consolas", 13)
        self.fonte_titulo = pygame.font.SysFont("consolas", 16, bold=True)
        
        self.categoria_atual = "armas" 
        self.item_selecionado_idx = 0
        
        self.carregar_bases()
        self.carregar_equipamentos_json()
        
        self.input_foco = None
        self.input_is_new_focus = False
        
        self.atualizar_formulario_com_item_atual()

    def carregar_bases(self):
        try:
            with open('elementos.json', 'r', encoding='utf-8') as f:
                self.elementos_db = json.load(f)
        except:
            self.elementos_db = [{"id": "fogo", "nome": "Fogo"}]

        try:
            with open('materiais.json', 'r', encoding='utf-8') as f:
                self.materiais_db = json.load(f)
        except:
            self.materiais_db = [{"id": "ferro", "nome": "Ferro", "preco_multiplicador": 1.0}]

    def carregar_equipamentos_json(self):
        self.arquivo_nome = "equipamentos.json"
        if os.path.exists(self.arquivo_nome):
            try:
                with open(self.arquivo_nome, 'r', encoding='utf-8') as f:
                    self.dados = json.load(f)
            except:
                self.dados = {"armas": [], "armaduras": [], "equipaveis": []}
        else:
            self.dados = {"armas": [], "armaduras": [], "equipaveis": []}
            self.salvar_arquivo_json()

    def salvar_arquivo_json(self):
        self.sincronizar_item_atual()
        try:
            with open(self.arquivo_nome, 'w', encoding='utf-8') as f:
                json.dump(self.dados, f, indent=4, ensure_ascii=False)
            print("Equipamentos salvos com sucesso em equipamentos.json!")
        except Exception as e:
            print(f"Erro ao salvar: {e}")

    def criar_item_vazio(self):
        return {
            "nome": "Novo Item",
            "dano_base": "10",
            "atributo_derivado": "STR",
            "material": self.materiais_db[0]['id'],
            "peso": "2.0",
            "modificador_atributo": {"STR": "0", "AGI": "0", "VIT": "0", "INT": "0", "LCK": "0", "CAR": "0", "WILL": "0"},
            "bonus_critico": "5",
            "preco": "50",
            "dano_elemental": [],
            "reservado": False
        }

    def atualizar_formulario_com_item_atual(self):
        lista = self.dados[self.categoria_atual]
        if not lista:
            lista.append(self.criar_item_vazio())
            self.item_selecionado_idx = 0
        
        if self.item_selecionado_idx >= len(lista):
            self.item_selecionado_idx = len(lista) - 1

        item = lista[self.item_selecionado_idx]
        self.form_nome = str(item.get("nome", ""))
        self.form_dano = str(item.get("dano_base", "0"))
        self.form_atr_derivado = str(item.get("atributo_derivado", "STR"))
        self.form_material = str(item.get("material", self.materiais_db[0]['id']))
        self.form_peso = str(item.get("peso", "1.0"))
        
        mods = item.get("modificador_atributo", {})
        self.form_mods = {k: str(mods.get(k, "0")) for k in ["STR", "AGI", "VIT", "INT", "LCK", "CAR", "WILL"]}
        
        self.form_critico = str(item.get("bonus_critico", "0"))
        self.form_preco = str(item.get("preco", "10"))
        self.form_elementos = list(item.get("dano_elemental", []))
        self.form_reservado = bool(item.get("reservado", False))

    def sincronizar_item_atual(self):
        lista = self.dados[self.categoria_atual]
        if not lista: return
        
        item = {
            "nome": self.form_nome,
            "dano_base": int(self.form_dano) if self.form_dano.isdigit() or (self.form_dano.startswith('-') and self.form_dano[1:].isdigit()) else 0,
            "atributo_derivado": self.form_atr_derivado,
            "material": self.form_material,
            "peso": float(self.form_peso) if self.form_peso.replace('.', '', 1).isdigit() else 1.0,
            "modificador_atributo": {k: int(v) if v.isdigit() or (v.startswith('-') and v[1:].isdigit()) else 0 for k, v in self.form_mods.items()},
            "bonus_critico": int(self.form_critico) if self.form_critico.isdigit() else 0,
            "preco": int(self.form_preco) if self.form_preco.isdigit() else 0,
            "dano_elemental": self.form_elementos,
            "reservado": self.form_reservado
        }
        lista[self.item_selecionado_idx] = item

    def adicionar_novo_item(self):
        self.sincronizar_item_atual()
        self.dados[self.categoria_atual].append(self.criar_item_vazio())
        self.item_selecionado_idx = len(self.dados[self.categoria_atual]) - 1
        self.atualizar_formulario_com_item_atual()

    def deletar_item_atual(self):
        lista = self.dados[self.categoria_atual]
        if len(lista) > 1:
            lista.pop(self.item_selecionado_idx)
            self.item_selecionado_idx = max(0, self.item_selecionado_idx - 1)
            self.atualizar_formulario_com_item_atual()

    def get_target_string_and_setter(self):
        if not self.input_foco: return None, None
        tipo, chave = self.input_foco
        if tipo == 'nome': return self.form_nome, lambda v: setattr(self, 'form_nome', v)
        elif tipo == 'dano': return self.form_dano, lambda v: setattr(self, 'form_dano', v)
        elif tipo == 'atr_derivado': return self.form_atr_derivado, lambda v: setattr(self, 'form_atr_derivado', v)
        elif tipo == 'peso': return self.form_peso, lambda v: setattr(self, 'form_peso', v)
        elif tipo == 'critico': return self.form_critico, lambda v: setattr(self, 'form_critico', v)
        elif tipo == 'preco': return self.form_preco, lambda v: setattr(self, 'form_preco', v)
        elif tipo == 'mod': return self.form_mods[chave], lambda v: self.form_mods.__setitem__(chave, v)
        return None, None

    def tratar_input_teclado(self, event):
        val, setter = self.get_target_string_and_setter()
        if val is None or setter is None: return
        tipo, _ = self.input_foco

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
            
            if tipo in ['dano', 'critico', 'preco']:
                if new_val.isdigit() or new_val == '-' or (new_val.startswith('-') and new_val[1:].isdigit()):
                    if len(new_val) <= 6: setter(new_val)
            elif tipo == 'peso':
                if new_val.replace('.', '', 1).isdigit() or new_val == '.':
                    if len(new_val) <= 6: setter(new_val)
            elif tipo == 'mod':
                if new_val.isdigit() or new_val == '-' or (new_val.startswith('-') and new_val[1:].isdigit()):
                    if len(new_val) <= 4: setter(new_val)
            elif tipo in ['nome', 'atr_derivado']:
                if len(new_val) < 30: setter(new_val)

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
            # ABAS DE CATEGORIA
            # ==========================================
            categorias = [("armas", "Armas"), ("armaduras", "Armaduras"), ("equipaveis", "Equipáveis")]
            bx = 20
            for cat_key, cat_nome in categorias:
                rect_aba = pygame.Rect(bx, 15, 140, 35)
                ativo = (self.categoria_atual == cat_key)
                cor_fundo = TEMA['ativo'] if ativo else TEMA['painel']
                if desenhar_botao(self.tela, cat_nome, rect_aba, mouse_pos, clique, self.fonte, cor_fundo):
                    self.sincronizar_item_atual()
                    self.categoria_atual = cat_key
                    self.item_selecionado_idx = 0
                    self.atualizar_formulario_com_item_atual()
                bx += 150

            # Botão Salvar Global
            if desenhar_botao(self.tela, "SALVAR JSON", pygame.Rect(1100, 15, 160, 35), mouse_pos, clique, self.fonte, (40, 130, 60)):
                self.salvar_arquivo_json()

            # ==========================================
            # PAINEL ESQUERDO: LISTA DE ITENS
            # ==========================================
            pygame.draw.rect(self.tela, TEMA['painel'], (20, 65, 300, 680), border_radius=6)
            pygame.draw.rect(self.tela, TEMA['borda'], (20, 65, 300, 680), 2, border_radius=6)
            
            desenhar_texto(self.tela, "Lista de Itens", 35, 75, self.fonte_titulo, TEMA['destaque'])

            if desenhar_botao(self.tela, "+ Criar Novo Item", pygame.Rect(35, 105, 270, 30), mouse_pos, clique, self.fonte, (50, 100, 50)):
                self.adicionar_novo_item()

            lista_itens = self.dados[self.categoria_atual]
            ly = 150
            for i, itm in enumerate(lista_itens):
                rect_item = pygame.Rect(35, ly, 270, 32)
                selec = (i == self.item_selecionado_idx)
                cor_item = TEMA['hover'] if selec else TEMA['fundo']
                
                if desenhar_botao(self.tela, f"{i+1}. {itm.get('nome', 'Sem Nome')}", rect_item, mouse_pos, clique, self.fonte, cor_item):
                    self.sincronizar_item_atual()
                    self.item_selecionado_idx = i
                    self.atualizar_formulario_com_item_atual()
                ly += 38

            if len(lista_itens) > 1 and desenhar_botao(self.tela, "Deletar Item Atual", pygame.Rect(35, 695, 270, 30), mouse_pos, clique, self.fonte, (120, 40, 40)):
                self.deletar_item_atual()

            # ==========================================
            # PAINEL DIREITO: FORMULÁRIO DE EDIÇÃO (LARGURA AMPLIADA E SEGURA)
            # ==========================================
            pygame.draw.rect(self.tela, TEMA['painel'], (340, 65, 920, 680), border_radius=6)
            pygame.draw.rect(self.tela, TEMA['borda'], (340, 65, 920, 680), 2, border_radius=6)
            
            desenhar_texto(self.tela, "Propriedades do Equipamento", 360, 75, self.fonte_titulo, TEMA['destaque'])

            fx = 360
            fy = 115

            # Nome do Objeto
            desenhar_texto(self.tela, "Nome do Objeto:", fx, fy, self.fonte)
            r_nome = pygame.Rect(fx, fy + 20, 340, 26)
            f_nome = (self.input_foco == ('nome', None))
            pygame.draw.rect(self.tela, TEMA['hover'] if f_nome else TEMA['fundo'], r_nome, border_radius=3)
            pygame.draw.rect(self.tela, TEMA['borda'], r_nome, 1, border_radius=3)
            if clique and r_nome.collidepoint(mouse_pos):
                self.input_foco = ('nome', None); self.input_is_new_focus = True
            desenhar_texto(self.tela, f"{self.form_nome}{'_' if f_nome else ''}", fx + 5, fy + 22, self.fonte)

            # Dano Base & Atr. Derivado
            fy_d = fy + 58
            desenhar_texto(self.tela, "Dano Base:", fx, fy_d, self.fonte)
            r_dano = pygame.Rect(fx, fy_d + 20, 150, 26)
            f_dano = (self.input_foco == ('dano', None))
            pygame.draw.rect(self.tela, TEMA['hover'] if f_dano else TEMA['fundo'], r_dano, border_radius=3)
            pygame.draw.rect(self.tela, TEMA['borda'], r_dano, 1, border_radius=3)
            if clique and r_dano.collidepoint(mouse_pos):
                self.input_foco = ('dano', None); self.input_is_new_focus = True
            desenhar_texto(self.tela, f"{self.form_dano}{'_' if f_dano else ''}", fx + 5, fy_d + 22, self.fonte)

            desenhar_texto(self.tela, "Atr. Derivado Relativo:", fx + 175, fy_d, self.fonte)
            r_atr = pygame.Rect(fx + 175, fy_d + 20, 165, 26)
            f_atr = (self.input_foco == ('atr_derivado', None))
            pygame.draw.rect(self.tela, TEMA['hover'] if f_atr else TEMA['fundo'], r_atr, border_radius=3)
            pygame.draw.rect(self.tela, TEMA['borda'], r_atr, 1, border_radius=3)
            if clique and r_atr.collidepoint(mouse_pos):
                self.input_foco = ('atr_derivado', None); self.input_is_new_focus = True
            desenhar_texto(self.tela, f"{self.form_atr_derivado}{'_' if f_atr else ''}", fx + 180, fy_d + 22, self.fonte)

            # Peso & Bônus Crítico
            fy_p = fy_d + 58
            desenhar_texto(self.tela, "Peso (kg):", fx, fy_p, self.fonte)
            r_peso = pygame.Rect(fx, fy_p + 20, 150, 26)
            f_peso = (self.input_foco == ('peso', None))
            pygame.draw.rect(self.tela, TEMA['hover'] if f_peso else TEMA['fundo'], r_peso, border_radius=3)
            pygame.draw.rect(self.tela, TEMA['borda'], r_peso, 1, border_radius=3)
            if clique and r_peso.collidepoint(mouse_pos):
                self.input_foco = ('peso', None); self.input_is_new_focus = True
            desenhar_texto(self.tela, f"{self.form_peso}{'_' if f_peso else ''}", fx + 5, fy_p + 22, self.fonte)

            desenhar_texto(self.tela, "Bônus Crítico:", fx + 175, fy_p, self.fonte)
            r_crit = pygame.Rect(fx + 175, fy_p + 20, 165, 26)
            f_crit = (self.input_foco == ('critico', None))
            pygame.draw.rect(self.tela, TEMA['hover'] if f_crit else TEMA['fundo'], r_crit, border_radius=3)
            pygame.draw.rect(self.tela, TEMA['borda'], r_crit, 1, border_radius=3)
            if clique and r_crit.collidepoint(mouse_pos):
                self.input_foco = ('critico', None); self.input_is_new_focus = True
            desenhar_texto(self.tela, f"{self.form_critico}{'_' if f_crit else ''}", fx + 180, fy_p + 22, self.fonte)

            # Materiais (Dispostos de forma organizada e compacta na coluna esquerda, sem invadir o lado direito)
            fy_mat = fy_p + 58
            desenhar_texto(self.tela, "Material:", fx, fy_mat, self.fonte)
            mx = fx
            my = fy_mat + 20
            for i, mat in enumerate(self.materiais_db):
                r_mbtn = pygame.Rect(mx, my, 78, 26)
                escolhido = (self.form_material == mat['id'])
                if desenhar_botao(self.tela, mat['nome'][:8], r_mbtn, mouse_pos, clique, self.fonte, TEMA['ativo'] if escolhido else TEMA['fundo']):
                    self.form_material = mat['id']
                mx += 85
                if (i + 1) % 4 == 0:  # Quebra de linha a cada 4 botões para manter na largura segura (< 720px)
                    mx = fx
                    my += 30

            # Preço Base e Final
            fy_pr = my + 38
            desenhar_texto(self.tela, "Preço Base:", fx, fy_pr, self.fonte)
            r_preco = pygame.Rect(fx, fy_pr + 20, 150, 26)
            f_preco = (self.input_foco == ('preco', None))
            pygame.draw.rect(self.tela, TEMA['hover'] if f_preco else TEMA['fundo'], r_preco, border_radius=3)
            pygame.draw.rect(self.tela, TEMA['borda'], r_preco, 1, border_radius=3)
            if clique and r_preco.collidepoint(mouse_pos):
                self.input_foco = ('preco', None); self.input_is_new_focus = True
            desenhar_texto(self.tela, f"{self.form_preco}{'_' if f_preco else ''}", fx + 5, fy_pr + 22, self.fonte)

            mult_atual = 1.0
            for m in self.materiais_db:
                if m['id'] == self.form_material:
                    mult_atual = m.get('preco_multiplicador', 1.0)
                    break
            preco_base_val = int(self.form_preco) if self.form_preco.isdigit() else 0
            preco_final = int(preco_base_val * mult_atual)
            desenhar_texto(self.tela, f"Preço Final: {preco_final} moedas", fx + 160, fy_pr + 25, self.fonte, TEMA['destaque'])

            # Item Reservado Checkbox
            fy_res = fy_pr + 58
            r_chk = pygame.Rect(fx, fy_res + 18, 20, 20)
            pygame.draw.rect(self.tela, TEMA['checkbox_on'] if self.form_reservado else TEMA['fundo'], r_chk)
            pygame.draw.rect(self.tela, TEMA['borda'], r_chk, 1)
            if clique and r_chk.collidepoint(mouse_pos):
                self.form_reservado = not self.form_reservado
            desenhar_texto(self.tela, "Item Reservado (Não pode ser vendido)", fx + 30, fy_res + 18, self.fonte)

            # ==========================================
            # COLUNA DIREITA DO FORMULÁRIO (Afastada com segurança em rx = 760)
            # ==========================================
            rx = 760
            ry = 115

            desenhar_texto(self.tela, "Modificadores de Atributos Primários:", rx, ry, self.fonte_titulo, TEMA['destaque'])
            m_y = ry + 28
            for atr in ["STR", "AGI", "VIT", "INT", "LCK", "CAR", "WILL"]:
                desenhar_texto(self.tela, f"{atr}:", rx, m_y, self.fonte)
                r_mod = pygame.Rect(rx + 60, m_y - 3, 65, 24)
                f_mod = (self.input_foco == ('mod', atr))
                pygame.draw.rect(self.tela, TEMA['hover'] if f_mod else TEMA['fundo'], r_mod, border_radius=3)
                pygame.draw.rect(self.tela, TEMA['borda'], r_mod, 1, border_radius=3)
                if clique and r_mod.collidepoint(mouse_pos):
                    self.input_foco = ('mod', atr); self.input_is_new_focus = True
                
                val_mod_str = self.form_mods.get(atr, "0")
                desenhar_texto(self.tela, f"{val_mod_str}{'_' if f_mod else ''}", rx + 67, m_y, self.fonte)
                m_y += 30

            ry_el = m_y + 10
            desenhar_texto(self.tela, "Dano Elemental (Marcar):", rx, ry_el, self.fonte_titulo, TEMA['destaque'])
            el_y = ry_el + 26
            for el in self.elementos_db:
                el_id = el['id']
                el_nome = el['nome']
                marcado = el_id in self.form_elementos
                
                r_elbox = pygame.Rect(rx, el_y, 18, 18)
                pygame.draw.rect(self.tela, TEMA['checkbox_on'] if marcado else TEMA['fundo'], r_elbox)
                pygame.draw.rect(self.tela, TEMA['borda'], r_elbox, 1)
                if clique and r_elbox.collidepoint(mouse_pos):
                    if marcado: self.form_elementos.remove(el_id)
                    else: self.form_elementos.append(el_id)
                
                desenhar_texto(self.tela, el_nome, rx + 28, el_y - 2, self.fonte)
                el_y += 24

            pygame.display.flip()
            clock.tick(30)

if __name__ == "__main__":
    app = GerenciadorEquipamentos()
    app.rodar()