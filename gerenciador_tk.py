import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# ==========================================
# UTILITÁRIOS E CONFIGURAÇÕES
# ==========================================
TEMA = {
    'fundo': "#14161E", 'painel': "#202330", 'borda': "#788296", 'texto': "#FFFFFF",
    'destaque': "#FFD700", 'ativo': "#3C5A8C", 'hover': "#506FA1", 'botao': "#323C5A",
    'botao_salvar': "#28823C", 'botao_deletar': "#822828", 'botao_auto': "#8C5A28", 'botao_config': "#5A3C8C"
}

def safe_int(val, padrao=0):
    try: return int(val)
    except: return padrao

def safe_float(val, padrao=1.0):
    try: return float(val)
    except: return padrao

def carregar_json(caminho, padrao):
    if os.path.exists(caminho):
        try:
            with open(caminho, 'r', encoding='utf-8') as f: return json.load(f)
        except: pass
    return padrao

def salvar_json(caminho, dados):
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# ==========================================
# CLASSE PRINCIPAL
# ==========================================
class GerenciadorEquipamentosTK:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Equipamentos - Elder SIM")
        self.root.geometry("1100x720")
        self.root.configure(bg=TEMA['fundo'])
        
        self.categoria_atual = "armas"
        self.item_selecionado_idx = 0
        self.botoes_abas = {}
        
        self.carregar_bases()
        self.criar_estilos()
        self.criar_layout()
        self.atualizar_lista_itens()
        self.carregar_dados_no_formulario()

    def carregar_bases(self):
        self.elementos_db = carregar_json('elementos.json', [{"id": "fogo", "nome": "Fogo"}])
        self.materiais_db = carregar_json('materiais.json', [{"id": "ferro", "nome": "Ferro", "preco_multiplicador": 1.0}])
        self.tipos_armadura_db = carregar_json('tipos_armadura.json', [{"id": "elmo", "nome": "Elmo"}, {"id": "peitoral", "nome": "Peitoral"}, {"id": "grevas", "nome": "Grevas"}, {"id": "bracos", "nome": "Braços"}])
        
        skills_data = carregar_json('skills.json', {"ARMA-CONTUSAO": "", "ARMA-CORTE": ""})
        self.skills_list = list(skills_data.keys())
        
        self.dados = carregar_json("equipamentos.json", {"armas": [], "armaduras": [], "equipaveis": []})
        
        def_templates = {
            "armas": [{"nome": "Espada", "dano_base": 15, "dano_escalavel": 3, "preco_base": 100, "ativo": True}],
            "armaduras": [{"nome": "Viajante", "dano_base": 10, "dano_escalavel": 2, "preco_base": 80, "ativo": True}],
            "equipaveis": [{"nome": "Rubi", "preco_base": 50, "ativo": True}]
        }
        temps_load = carregar_json("templates.json", def_templates)
        self.templates_dict = temps_load if isinstance(temps_load, dict) else def_templates

    def salvar_tudo(self, silent=False):
        self.sincronizar_formulario_para_item()
        try:
            salvar_json("equipamentos.json", self.dados)
            salvar_json("templates.json", self.templates_dict)
            salvar_json("elementos.json", self.elementos_db)
            salvar_json("materiais.json", self.materiais_db)
            salvar_json("tipos_armadura.json", self.tipos_armadura_db)
            if not silent: messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")

    def criar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background=TEMA['painel'], foreground=TEMA['texto'], font=("Consolas", 10))
        style.configure("TCheckbutton", background=TEMA['painel'], foreground=TEMA['texto'], font=("Consolas", 10))
        style.map("TCheckbutton", background=[('active', TEMA['painel'])])

    def criar_layout(self):
        top_frame = tk.Frame(self.root, bg=TEMA['fundo'], height=50)
        top_frame.pack(fill="x", padx=15, pady=10)
        
        for cat, texto in [("armas", "Armas"), ("armaduras", "Armaduras"), ("equipaveis", "Equipáveis")]:
            btn = tk.Button(top_frame, text=texto, font=("Consolas", 10, "bold"), fg=TEMA['texto'], relief="flat", command=lambda c=cat: self.trocar_categoria(c))
            btn.pack(side="left", padx=5, ipadx=15, ipady=5)
            self.botoes_abas[cat] = btn
            
        self.btn_auto = tk.Button(top_frame, text="⚡ Auto-Criação", font=("Consolas", 10, "bold"), bg=TEMA['botao_auto'], fg=TEMA['texto'], relief="flat", command=self.abrir_modal_autocriacao)
        self.btn_auto.pack(side="left", padx=10, ipadx=10, ipady=5)

        btn_gerenciar_bases = tk.Button(top_frame, text="⚙️ Gerenciar Bases", font=("Consolas", 10, "bold"), bg=TEMA['botao_config'], fg=TEMA['texto'], relief="flat", command=self.abrir_modal_gerenciador_bases)
        btn_gerenciar_bases.pack(side="left", padx=10, ipadx=10, ipady=5)

        tk.Button(top_frame, text="SALVAR JSON", font=("Consolas", 10, "bold"), bg=TEMA['botao_salvar'], fg=TEMA['texto'], relief="flat", command=self.salvar_tudo).pack(side="right", ipadx=15, ipady=5)

        main_frame = tk.Frame(self.root, bg=TEMA['fundo'])
        main_frame.pack(fill="both", expand=True, padx=15, pady=5)

        left_panel = tk.Frame(main_frame, bg=TEMA['painel'], bd=1, relief="solid")
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        tk.Label(left_panel, text="Lista de Itens", bg=TEMA['painel'], fg=TEMA['destaque'], font=("Consolas", 11, "bold")).pack(padx=10, pady=10, anchor="w")
        tk.Button(left_panel, text="+ Criar Novo Item", bg=TEMA['botao'], fg=TEMA['texto'], font=("Consolas", 9, "bold"), relief="flat", command=self.adicionar_novo_item).pack(fill="x", padx=10, pady=5, ipady=3)
        
        list_frame = tk.Frame(left_panel, bg=TEMA['painel'])
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.listbox_itens = tk.Listbox(list_frame, bg=TEMA['fundo'], fg=TEMA['texto'], selectbackground=TEMA['hover'], font=("Consolas", 10), bd=0, highlightthickness=0)
        self.listbox_itens.pack(side="left", fill="both", expand=True)
        self.listbox_itens.bind("<<ListboxSelect>>", self.on_item_selecionado)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.listbox_itens.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox_itens.configure(yscrollcommand=scrollbar.set)
        
        tk.Button(left_panel, text="Deletar Item Atual", bg=TEMA['botao_deletar'], fg=TEMA['texto'], font=("Consolas", 9, "bold"), relief="flat", command=self.deletar_item_atual).pack(fill="x", padx=10, pady=10, ipady=3)

        self.right_panel = tk.Frame(main_frame, bg=TEMA['painel'], bd=1, relief="solid")
        self.right_panel.pack(side="right", fill="both", expand=True)
        self.criar_formulario()

    def _add_campo(self, parent, text, row, col, widget_type="entry", **kwargs):
        tk.Label(parent, text=text, bg=TEMA['painel'], fg=TEMA['texto'], font=("Consolas", 10)).grid(row=row, column=col, sticky="w", pady=5)
        if widget_type == "entry":
            w = tk.Entry(parent, bg=TEMA['fundo'], fg=TEMA['texto'], insertbackground="white", font=("Consolas", 10), bd=1, relief="solid", **kwargs)
        else:
            w = ttk.Combobox(parent, state="readonly", font=("Consolas", 9), **kwargs)
        w.grid(row=row, column=col+1, sticky="ew", pady=5, padx=5)
        return w

    def criar_formulario(self):
        f = tk.Frame(self.right_panel, bg=TEMA['painel'])
        f.pack(fill="both", expand=True, padx=15, pady=15)
        tk.Label(f, text="Propriedades do Equipamento", bg=TEMA['painel'], fg=TEMA['destaque'], font=("Consolas", 12, "bold")).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 15))

        self.ent_nome = self._add_campo(f, "Nome do Objeto:", 1, 0)
        self.ent_nome.grid(columnspan=3)
        self.lbl_dano = tk.Label(f, text="Dano Base:", bg=TEMA['painel'], fg=TEMA['texto'], font=("Consolas", 10))
        self.lbl_dano.grid(row=2, column=0, sticky="w", pady=5)
        self.ent_val_princ = tk.Entry(f, bg=TEMA['fundo'], fg=TEMA['texto'], insertbackground="white", font=("Consolas", 10), bd=1, relief="solid")
        self.ent_val_princ.grid(row=2, column=1, sticky="ew", pady=5, padx=5)

        self.lbl_derivado = tk.Label(f, text="Atributo Derivado:", bg=TEMA['painel'], fg=TEMA['texto'], font=("Consolas", 10))
        self.lbl_derivado.grid(row=2, column=2, sticky="w", pady=5)
        self.combo_derivado = ttk.Combobox(f, values=self.skills_list, state="readonly", font=("Consolas", 9))
        self.combo_derivado.grid(row=2, column=3, sticky="ew", pady=5, padx=5)

        self.ent_peso = self._add_campo(f, "Peso (kg):", 3, 0)
        self.lbl_extra = tk.Label(f, text="Bônus Crítico:", bg=TEMA['painel'], fg=TEMA['texto'], font=("Consolas", 10))
        self.lbl_extra.grid(row=3, column=2, sticky="w", pady=5)
        self.ent_critico = tk.Entry(f, bg=TEMA['fundo'], fg=TEMA['texto'], insertbackground="white", font=("Consolas", 10), bd=1, relief="solid")
        self.ent_critico.grid(row=3, column=3, sticky="ew", pady=5, padx=5)
        self.combo_tipo = ttk.Combobox(f, state="readonly", font=("Consolas", 9))

        self.lbl_material = tk.Label(f, text="Material:", bg=TEMA['painel'], fg=TEMA['texto'], font=("Consolas", 10))
        self.lbl_material.grid(row=4, column=0, sticky="w", pady=5)
        self.combo_material = ttk.Combobox(f, values=[m['nome'] for m in self.materiais_db], state="readonly", font=("Consolas", 9))
        self.combo_material.grid(row=4, column=1, sticky="ew", pady=5, padx=5)
        self.combo_material.bind("<<ComboboxSelected>>", lambda e: self.calcular_preco_final())

        self.ent_preco = self._add_campo(f, "Preço Base:", 5, 0)
        self.ent_preco.bind("<KeyRelease>", lambda e: self.calcular_preco_final())
        self.lbl_preco_final = tk.Label(f, text="Preço Final: 0", bg=TEMA['painel'], fg=TEMA['destaque'], font=("Consolas", 10, "bold"))
        self.lbl_preco_final.grid(row=5, column=2, columnspan=2, sticky="w", pady=5, padx=5)

        self.var_reservado = tk.BooleanVar()
        tk.Checkbutton(f, text="Item Reservado", variable=self.var_reservado, bg=TEMA['painel'], fg=TEMA['texto'], selectcolor=TEMA['fundo'], font=("Consolas", 9)).grid(row=6, column=0, columnspan=3, sticky="w", pady=10)

        tk.Label(f, text="Modificadores:", bg=TEMA['painel'], fg=TEMA['destaque'], font=("Consolas", 10, "bold")).grid(row=7, column=0, columnspan=4, sticky="w", pady=(15, 5))
        self.mods_entries = {}
        for idx, atr in enumerate(["STR", "AGI", "VIT", "INT", "LCK", "CAR", "WILL"]):
            self.mods_entries[atr] = self._add_campo(f, f"{atr}:", 8 + (idx//2), (idx%2)*2, width=10)

        self.lbl_elem_tit = tk.Label(f, text="Dano Elemental:", bg=TEMA['painel'], fg=TEMA['destaque'], font=("Consolas", 10, "bold"))
        self.lbl_elem_tit.grid(row=12, column=0, columnspan=4, sticky="w", pady=(15, 5))
        self.atualizar_checkboxes_elementos(f)

    def atualizar_checkboxes_elementos(self, parent_frame=None):
        if not parent_frame:
            # Encontra o frame principal do formulário
            parent_frame = self.ent_nome.master
        
        # Remove widgets antigos de elementos se houver
        for widget in parent_frame.winfo_children():
            if widget.grid_info().get('row', 0) >= 13:
                widget.destroy()

        self.elementos_vars = {}
        for idx, el in enumerate(self.elementos_db):
            var = tk.BooleanVar()
            tk.Checkbutton(parent_frame, text=el['nome'], variable=var, bg=TEMA['painel'], fg=TEMA['texto'], selectcolor=TEMA['fundo'], font=("Consolas", 9)).grid(row=13+(idx//3), column=idx%3, sticky="w", pady=2)
            self.elementos_vars[el['id']] = var

    def atualizar_visibilidade_campos(self):
        for k, btn in self.botoes_abas.items(): btn.config(bg=TEMA['ativo'] if k == self.categoria_atual else TEMA['botao'])

        if self.categoria_atual == "equipaveis":
            for w in [self.lbl_dano, self.ent_val_princ, self.lbl_derivado, self.combo_derivado, self.lbl_material, self.combo_material]: w.grid_remove()
            self.lbl_extra.config(text="Tipo:"); self.ent_critico.grid_remove()
            self.combo_tipo.config(values=["Anel", "Cordão"])
            self.combo_tipo.grid(row=3, column=3, sticky="ew", pady=5, padx=5)
            self.btn_auto.pack_forget()
            self.lbl_elem_tit.config(text="Resistência Elemental:")
        else:
            for w in [self.lbl_dano, self.ent_val_princ, self.lbl_material, self.combo_material]: w.grid()
            self.btn_auto.pack(side="left", padx=10, ipadx=10, ipady=5)
            if self.categoria_atual == "armaduras":
                self.lbl_dano.config(text="Índice Armadura:")
                self.lbl_derivado.grid_remove(); self.combo_derivado.grid_remove(); self.ent_critico.grid_remove()
                self.lbl_extra.config(text="Tipo de Peça:")
                self.combo_tipo.config(values=[t['nome'] for t in self.tipos_armadura_db])
                self.combo_tipo.grid(row=3, column=3, sticky="ew", pady=5, padx=5)
                self.lbl_elem_tit.config(text="Resistência Elemental:")
            else:
                self.lbl_dano.config(text="Dano Base:")
                self.lbl_derivado.grid(); self.combo_derivado.grid(); self.combo_tipo.grid_remove()
                self.lbl_extra.config(text="Bônus Crítico:")
                self.ent_critico.grid(row=3, column=3, sticky="ew", pady=5, padx=5)
                self.lbl_elem_tit.config(text="Dano Elemental:")

    def criar_item_vazio(self):
        base = {
            "nome": "Novo Item", "peso": 1.5, "preco": 50, "reservado": False,
            "modificador_atributo": {a: 0 for a in self.mods_entries}
        }
        mat = self.materiais_db[0]['id'] if self.materiais_db else "ferro"
        if self.categoria_atual == "armaduras":
            tp_def = self.tipos_armadura_db[0]['nome'] if self.tipos_armadura_db else "Peitoral"
            base.update({"indice_armadura": 10, "tipo": tp_def, "material": mat, "resistencia_elemental": []})
        elif self.categoria_atual == "armas":
            base.update({"dano_base": 10, "atributo_derivado": self.skills_list[0] if self.skills_list else "STR", "material": mat, "bonus_critico": 5, "dano_elemental": []})
        else:
            base.update({"tipo": "Anel", "resistencia_elemental": []})
        return base

    def carregar_dados_no_formulario(self):
        self.atualizar_visibilidade_campos()
        
        # Atualiza combobox de materiais com a base atualizada
        self.combo_material.config(values=[m['nome'] for m in self.materiais_db])
        if self.categoria_atual == "armaduras":
            self.combo_tipo.config(values=[t['nome'] for t in self.tipos_armadura_db])

        lista = self.dados[self.categoria_atual]
        if not lista: lista.append(self.criar_item_vazio()); self.item_selecionado_idx = 0
        self.item_selecionado_idx = min(self.item_selecionado_idx, len(lista) - 1)
        item = lista[self.item_selecionado_idx]
        
        self.ent_nome.delete(0, tk.END); self.ent_nome.insert(0, str(item.get("nome", "")))
        self.ent_peso.delete(0, tk.END); self.ent_peso.insert(0, str(item.get("peso", 1.0)))
        self.ent_preco.delete(0, tk.END); self.ent_preco.insert(0, str(item.get("preco", 0)))
        self.var_reservado.set(bool(item.get("reservado", False)))
        
        self.ent_val_princ.delete(0, tk.END)
        self.ent_val_princ.insert(0, str(item.get("indice_armadura", item.get("dano_base", 0))))
        
        if self.categoria_atual in ["armas", "armaduras"]:
            m_nome = next((m['nome'] for m in self.materiais_db if m['id'] == item.get("material")), self.materiais_db[0]['nome'] if self.materiais_db else "")
            self.combo_material.set(m_nome)
            
        if self.categoria_atual == "armas":
            self.combo_derivado.set(item.get("atributo_derivado", self.skills_list[0] if self.skills_list else ""))
            self.ent_critico.delete(0, tk.END); self.ent_critico.insert(0, str(item.get("bonus_critico", 0)))
        else:
            default_tp = self.tipos_armadura_db[0]['nome'] if self.categoria_atual == "armaduras" and self.tipos_armadura_db else "Anel"
            self.combo_tipo.set(item.get("tipo", default_tp))

        for atr, ent in self.mods_entries.items():
            ent.delete(0, tk.END); ent.insert(0, str(item.get("modificador_atributo", {}).get(atr, 0)))
            
        chave_el = "resistencia_elemental" if self.categoria_atual != "armas" else "dano_elemental"
        for el_id, var in self.elementos_vars.items(): var.set(el_id in item.get(chave_el, []))
        self.calcular_preco_final()

    def sincronizar_formulario_para_item(self):
        if not self.dados[self.categoria_atual]: return
        mods = {atr: safe_int(ent.get()) for atr, ent in self.mods_entries.items()}
        elem = [el for el, var in self.elementos_vars.items() if var.get()]
        
        item = {
            "nome": self.ent_nome.get(), "peso": safe_float(self.ent_peso.get()),
            "preco": safe_int(self.ent_preco.get()), "reservado": self.var_reservado.get(),
            "modificador_atributo": mods
        }
        
        if self.categoria_atual in ["armas", "armaduras"]:
            mat_nome = self.combo_material.get()
            mat_id = next((m['id'] for m in self.materiais_db if m['nome'] == mat_nome), self.materiais_db[0]['id'] if self.materiais_db else "ferro")
            item["material"] = mat_id
            
        if self.categoria_atual == "armaduras":
            item.update({"indice_armadura": safe_int(self.ent_val_princ.get()), "tipo": self.combo_tipo.get(), "resistencia_elemental": elem})
        elif self.categoria_atual == "armas":
            item.update({"dano_base": safe_int(self.ent_val_princ.get()), "atributo_derivado": self.combo_derivado.get(), "bonus_critico": safe_int(self.ent_critico.get()), "dano_elemental": elem})
        else:
            item.update({"tipo": self.combo_tipo.get(), "resistencia_elemental": elem})
            
        self.dados[self.categoria_atual][self.item_selecionado_idx] = item

    def calcular_preco_final(self):
        pb = safe_int(self.ent_preco.get())
        if self.categoria_atual == "equipaveis":
            self.lbl_preco_final.config(text=f"Preço Final: {pb} moedas")
        else:
            mat_nome = self.combo_material.get()
            mult = next((m.get('preco_multiplicador', 1.0) for m in self.materiais_db if m['nome'] == mat_nome), 1.0)
            self.lbl_preco_final.config(text=f"Preço Final: {int(pb * mult)} moedas")

    def trocar_categoria(self, nova_cat):
        self.sincronizar_formulario_para_item()
        self.categoria_atual, self.item_selecionado_idx = nova_cat, 0
        self.atualizar_lista_itens()
        self.carregar_dados_no_formulario()

    def atualizar_lista_itens(self):
        self.listbox_itens.delete(0, tk.END)
        for i, item in enumerate(self.dados[self.categoria_atual]): self.listbox_itens.insert(tk.END, f"{i+1}. {item.get('nome', '')}")
        if self.dados[self.categoria_atual]: self.listbox_itens.selection_set(self.item_selecionado_idx)

    def on_item_selecionado(self, event):
        if sel := self.listbox_itens.curselection():
            if sel[0] != self.item_selecionado_idx:
                self.sincronizar_formulario_para_item()
                self.item_selecionado_idx = sel[0]
                self.carregar_dados_no_formulario()

    def adicionar_novo_item(self):
        self.sincronizar_formulario_para_item()
        self.dados[self.categoria_atual].append(self.criar_item_vazio())
        self.item_selecionado_idx = len(self.dados[self.categoria_atual]) - 1
        self.atualizar_lista_itens()
        self.carregar_dados_no_formulario()

    def deletar_item_atual(self):
        if len(self.dados[self.categoria_atual]) > 1:
            self.dados[self.categoria_atual].pop(self.item_selecionado_idx)
            self.item_selecionado_idx = max(0, self.item_selecionado_idx - 1)
            self.atualizar_lista_itens()
            self.carregar_dados_no_formulario()

    # ==========================================
    # MODAL DE GERENCIAMENTO DE BASES (Materiais, Tipos, Elementos)
    # ==========================================
    def abrir_modal_gerenciador_bases(self):
        modal = tk.Toplevel(self.root)
        modal.title("⚙️ Gerenciador de Bases (Materiais, Tipos, Elementos)")
        modal.geometry("750x550")
        modal.configure(bg=TEMA['fundo'])
        modal.transient(self.root)
        modal.grab_set()

        notebook = ttk.Notebook(modal)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Helper para criar a interface de listagem e edição de uma lista de dicionários
        def criar_aba_gerenciador(parent, dados_lista, campos_config):
            frame = tk.Frame(parent, bg=TEMA['painel'])
            frame.pack(fill="both", expand=True)

            # Esquerda: Lista
            f_esq = tk.Frame(frame, bg=TEMA['painel'])
            f_esq.pack(side="left", fill="both", expand=True, padx=10, pady=10)

            lb = tk.Listbox(f_esq, bg=TEMA['fundo'], fg=TEMA['texto'], selectbackground=TEMA['hover'], font=("Consolas", 10), bd=0)
            lb.pack(side="left", fill="both", expand=True)
            sc = tk.Scrollbar(f_esq, orient="vertical", command=lb.yview)
            sc.pack(side="right", fill="y")
            lb.config(yscrollcommand=sc.set)

            def atualizar_lb():
                lb.delete(0, tk.END)
                for item in dados_lista:
                    desc = f"{item.get('nome', '')}"
                    if 'preco_multiplicador' in item:
                        desc += f" (Mult: x{item['preco_multiplicador']})"
                    elif 'id' in item and campos_config.get('mostrar_id'):
                        desc += f" [id: {item['id']}]"
                    lb.insert(tk.END, desc)

            atualizar_lb()

            # Direita: Formulário de Edição e Controles
            f_dir = tk.Frame(frame, bg=TEMA['painel'], width=300)
            f_dir.pack(side="right", fill="both", padx=10, pady=10)

            entries = {}
            r = 0
            for campo, rotulo in campos_config['campos'].items():
                tk.Label(f_dir, text=rotulo, bg=TEMA['painel'], fg=TEMA['texto'], font=("Consolas", 9)).grid(row=r, column=0, sticky="w", pady=5)
                ent = tk.Entry(f_dir, bg=TEMA['fundo'], fg=TEMA['texto'], insertbackground="white", font=("Consolas", 9), bd=1, relief="solid")
                ent.grid(row=r, column=1, sticky="ew", pady=5, padx=5)
                entries[campo] = ent
                r += 1

            def preencher_form(e):
                sel = lb.curselection()
                if sel:
                    idx = sel[0]
                    item = dados_lista[idx]
                    for campo, ent in entries.items():
                        ent.delete(0, tk.END)
                        ent.insert(0, str(item.get(campo, "")))

            lb.bind("<<ListboxSelect>>", preencher_form)

            def salvar_item_atual():
                sel = lb.curselection()
                if not sel:
                    return messagebox.showwarning("Aviso", "Selecione um item para atualizar.", parent=modal)
                idx = sel[0]
                item = dados_lista[idx]
                for campo, ent in entries.items():
                    val = ent.get().strip()
                    if campo == 'preco_multiplicador':
                        item[campo] = safe_float(val, 1.0)
                    else:
                        item[campo] = val
                        if campo == 'nome' and 'id' in item and not item['id']:
                            item['id'] = val.lower().replace(" ", "_")
                atualizar_lb()
                lb.selection_set(idx)

            def adicionar_novo():
                novo = {}
                for campo in campos_config['campos']:
                    if campo == 'preco_multiplicador': novo[campo] = 1.0
                    elif campo == 'id': novo[campo] = "novo_id"
                    else: novo[campo] = "Novo Item"
                dados_lista.append(novo)
                atualizar_lb()
                lb.selection_set(len(dados_lista)-1)
                preencher_form(None)

            def excluir_item():
                sel = lb.curselection()
                if sel:
                    idx = sel[0]
                    if len(dados_lista) > 1:
                        dados_lista.pop(idx)
                        atualizar_lb()
                        for ent in entries.values(): ent.delete(0, tk.END)
                    else:
                        messagebox.showwarning("Aviso", "Você deve manter pelo menos um item.", parent=modal)

            def mover(direcao):
                sel = lb.curselection()
                if sel:
                    idx = sel[0]
                    novo_idx = idx + direcao
                    if 0 <= novo_idx < len(dados_lista):
                        item = dados_lista.pop(idx)
                        dados_lista.insert(novo_idx, item)
                        atualizar_lb()
                        lb.selection_set(novo_idx)

            tk.Button(f_dir, text="💾 Salvar Alterações", bg=TEMA['botao_salvar'], fg=TEMA['texto'], relief="flat", command=salvar_item_atual).grid(row=r, column=0, columnspan=2, sticky="ew", pady=10)
            r += 1
            tk.Button(f_dir, text="➕ Adicionar Novo", bg=TEMA['botao'], fg=TEMA['texto'], relief="flat", command=adicionar_novo).grid(row=r, column=0, columnspan=2, sticky="ew", pady=5)
            r += 1
            tk.Button(f_dir, text="🗑️ Excluir Selecionado", bg=TEMA['botao_deletar'], fg=TEMA['texto'], relief="flat", command=excluir_item).grid(row=r, column=0, columnspan=2, sticky="ew", pady=5)
            r += 1

            f_ordem = tk.Frame(f_dir, bg=TEMA['painel'])
            f_ordem.grid(row=r, column=0, columnspan=2, sticky="ew", pady=10)
            tk.Button(f_ordem, text="▲ Subir", bg=TEMA['botao'], fg=TEMA['texto'], command=lambda: mover(-1)).pack(side="left", expand=True, fill="x", padx=2)
            tk.Button(f_ordem, text="▼ Descer", bg=TEMA['botao'], fg=TEMA['texto'], command=lambda: mover(1)).pack(side="left", expand=True, fill="x", padx=2)

            return frame

        # Aba Materiais
        tab_mat = criar_aba_gerenciador(notebook, self.materiais_db, {
            'campos': {'nome': 'Nome:', 'id': 'ID:', 'preco_multiplicador': 'Mult. Preço:'},
            'mostrar_id': True
        })
        notebook.add(tab_mat, text="Materiais")

        # Aba Tipos de Armadura
        tab_tipo = criar_aba_gerenciador(notebook, self.tipos_armadura_db, {
            'campos': {'nome': 'Nome do Tipo:', 'id': 'ID:'},
            'mostrar_id': True
        })
        notebook.add(tab_tipo, text="Tipos de Armadura")

        # Aba Elementos
        tab_elem = criar_aba_gerenciador(notebook, self.elementos_db, {
            'campos': {'nome': 'Nome do Elemento:', 'id': 'ID:'},
            'mostrar_id': True
        })
        notebook.add(tab_elem, text="Elementos")

        # Botão Fechar / Atualizar Geral
        def fechar_e_atualizar():
            self.salvar_tudo(silent=True)
            self.atualizar_checkboxes_elementos()
            self.carregar_dados_no_formulario()
            modal.destroy()
            messagebox.showinfo("Sucesso", "Bases atualizadas e salvas com sucesso!")

        tk.Button(modal, text="✔ Concluir e Atualizar Aplicação", bg=TEMA['botao_salvar'], fg=TEMA['texto'], font=("Consolas", 10, "bold"), relief="flat", command=fechar_e_atualizar).pack(fill="x", padx=15, pady=10, ipady=5)

    # ==========================================
    # MODAL DE AUTO-CRIAÇÃO (Templates)
    # ==========================================
    def abrir_modal_autocriacao(self):
        modal = tk.Toplevel(self.root)
        modal.title(f"⚡ Auto-Criação ({self.categoria_atual.capitalize()})")
        modal.geometry("980x700")
        modal.configure(bg=TEMA['fundo'])
        modal.transient(self.root)
        modal.grab_set()

        is_armadura = (self.categoria_atual == "armaduras")
        t_lista = self.templates_dict[self.categoria_atual]

        frame_esq = tk.Frame(modal, bg=TEMA['painel'], bd=1, relief="solid")
        frame_esq.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        lbl_titulo_valor = "Armadura" if is_armadura else "Dano"
        tk.Label(frame_esq, text=f"Templates ({self.categoria_atual.capitalize()}): Nome, {lbl_titulo_valor}, Escala & Preço", bg=TEMA['painel'], fg=TEMA['destaque'], font=("Consolas", 10, "bold")).pack(padx=10, pady=10, anchor="w")

        f_novo_t = tk.Frame(frame_esq, bg=TEMA['painel'])
        f_novo_t.pack(fill="x", padx=10, pady=5)

        ents_temp = [self._add_campo(f_novo_t, l, 0, c*2, width=w) for c, (l, w) in enumerate([("N:",10), ("B:",4), ("E:",4), ("P:",5)])]
        for e, v in zip(ents_temp[1:], ["15", "3", "100"]): e.insert(0, v)

        def adicionar_template():
            nome_t = ents_temp[0].get().strip()
            if nome_t:
                t_lista.append({"nome": nome_t, "dano_base": safe_int(ents_temp[1].get()), "dano_escalavel": safe_int(ents_temp[2].get()), "preco_base": safe_int(ents_temp[3].get()), "ativo": True})
                self.salvar_templates(); atualizar_canvas_templates(); ents_temp[0].delete(0, tk.END)

        tk.Button(f_novo_t, text="Adicionar", bg=TEMA['botao'], fg=TEMA['texto'], relief="flat", command=adicionar_template).pack(side="right", padx=5)

        cv_t = tk.Canvas(frame_esq, bg=TEMA['fundo'], highlightthickness=0)
        scr_t = tk.Scrollbar(frame_esq, orient="vertical", command=cv_t.yview)
        sf_t = tk.Frame(cv_t, bg=TEMA['fundo'])
        sf_t.bind("<Configure>", lambda e: cv_t.configure(scrollregion=cv_t.bbox("all")))
        cv_t.create_window((0,0), window=sf_t, anchor="nw")
        cv_t.configure(yscrollcommand=scr_t.set)
        cv_t.pack(side="top", fill="both", expand=True, padx=10, pady=5)
        scr_t.pack(side="right", fill="y")

        selected_template_idx = tk.IntVar(value=-1)

        def atualizar_canvas_templates():
            for w in sf_t.winfo_children(): w.destroy()
            for idx, t_obj in enumerate(t_lista):
                bg_col = TEMA['ativo'] if selected_template_idx.get() == idx else TEMA['fundo']
                row_f = tk.Frame(sf_t, bg=bg_col)
                row_f.pack(fill="x", pady=2, padx=2)

                var_chk = tk.BooleanVar(value=t_obj.get("ativo", True))
                tk.Checkbutton(row_f, variable=var_chk, bg=bg_col, selectcolor=TEMA['painel'], activebackground=bg_col, command=lambda t_=t_obj, v_=var_chk: t_.update({"ativo": v_.get()})).pack(side="left", padx=5)

                texto_exibicao = f"{t_obj['nome']} ({lbl_titulo_valor}: {t_obj.get('dano_base', 15)} | Escala: {t_obj.get('dano_escalavel', 3)} | Preço: {t_obj.get('preco_base', 100)})"
                lbl = tk.Label(row_f, text=texto_exibicao, bg=bg_col, fg=TEMA['texto'], font=("Consolas", 9), anchor="w")
                lbl.pack(side="left", fill="x", expand=True, padx=5)

                for wdg in (row_f, lbl): wdg.bind("<Button-1>", lambda e, i=idx: [selected_template_idx.set(i), atualizar_canvas_templates()])

        atualizar_canvas_templates()

        def mover_template(direcao):
            idx = selected_template_idx.get()
            if 0 <= idx + direcao < len(t_lista):
                t_lista.insert(idx + direcao, t_lista.pop(idx))
                self.salvar_templates(); selected_template_idx.set(idx + direcao); atualizar_canvas_templates()

        f_botoes = tk.Frame(frame_esq, bg=TEMA['painel']); f_botoes.pack(fill="x", padx=10, pady=5)
        tk.Button(f_botoes, text="▲ Subir", bg=TEMA['botao'], fg=TEMA['texto'], command=lambda: mover_template(-1)).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(f_botoes, text="▼ Descer", bg=TEMA['botao'], fg=TEMA['texto'], command=lambda: mover_template(1)).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(frame_esq, text="Remover Selecionado", bg=TEMA['botao_deletar'], fg=TEMA['texto'], command=lambda: [t_lista.pop(selected_template_idx.get()), self.salvar_templates(), selected_template_idx.set(-1), atualizar_canvas_templates()] if 0<=selected_template_idx.get()<len(t_lista) else None).pack(fill="x", padx=10, pady=10)

        # Frame Direito: Opções
        frame_dir = tk.Frame(modal, bg=TEMA['painel'], bd=1, relief="solid")
        frame_dir.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)
        tk.Label(frame_dir, text="Configuração de Geração", bg=TEMA['painel'], fg=TEMA['destaque'], font=("Consolas", 11, "bold")).pack(padx=10, pady=10, anchor="w")

        var_usar_template = tk.BooleanVar(value=True)
        var_incluir_material = tk.BooleanVar(value=True)

        if is_armadura:
            f_opts = tk.Frame(frame_dir, bg=TEMA['painel']); f_opts.pack(fill="x", padx=10, pady=5)
            tk.Checkbutton(f_opts, text="Usar Templates de Nome", variable=var_usar_template, bg=TEMA['painel'], fg=TEMA['texto'], selectcolor=TEMA['fundo']).pack(anchor="w", pady=2)
            tk.Checkbutton(f_opts, text="Incluir material no nome", variable=var_incluir_material, bg=TEMA['painel'], fg=TEMA['texto'], selectcolor=TEMA['fundo']).pack(anchor="w", pady=2)

        combo_modal_derivado = None
        if not is_armadura:
            combo_modal_derivado = self._add_campo(frame_dir, "Atributo Lote:", 0, 0, "combo", values=self.skills_list)
            combo_modal_derivado.set(self.combo_derivado.get() if self.combo_derivado.get() in self.skills_list else self.skills_list[0])
            combo_modal_derivado.pack(padx=10, pady=5)

        tipo_vars = {}
        if is_armadura:
            tk.Label(frame_dir, text="Selecione os Tipos de Peça:", bg=TEMA['painel'], fg=TEMA['texto'], font=("Consolas", 10, "bold")).pack(padx=10, pady=(5, 0), anchor="w")
            f_tp = tk.Frame(frame_dir, bg=TEMA['painel']); f_tp.pack(fill="x", padx=10, pady=5)
            for tp_obj in self.tipos_armadura_db:
                tp = tp_obj['nome']
                tipo_vars[tp] = tk.BooleanVar(value=True)
                tk.Checkbutton(f_tp, text=tp, variable=tipo_vars[tp], bg=TEMA['painel'], fg=TEMA['texto'], selectcolor=TEMA['fundo']).pack(anchor="w", pady=2)

        tk.Label(frame_dir, text="Selecione os Materiais:", bg=TEMA['painel'], fg=TEMA['texto'], font=("Consolas", 10, "bold")).pack(padx=10, pady=(10, 0), anchor="w")
        mats_vars = {}
        f_mats = tk.Frame(frame_dir, bg=TEMA['painel']); f_mats.pack(fill="x", padx=10, pady=5)
        for mat in self.materiais_db:
            mats_vars[mat['id']] = tk.BooleanVar(value=True)
            tk.Checkbutton(f_mats, text=mat['nome'], variable=mats_vars[mat['id']], bg=TEMA['painel'], fg=TEMA['texto'], selectcolor=TEMA['fundo']).pack(anchor="w", pady=2)

        def gerar():
            m_sels = [m for m in self.materiais_db if mats_vars[m['id']].get()]
            tp_sels = [tp for tp, v in tipo_vars.items() if v.get()] if is_armadura else [None]
            ativos = [t for t in t_lista if t.get("ativo")] if (not is_armadura or var_usar_template.get()) else [{"nome": "", "dano_base": 10, "dano_escalavel": 2, "preco_base": 50}]
            
            if not m_sels or (is_armadura and not tp_sels) or not ativos:
                return messagebox.showwarning("Aviso", "Selecione material, tipo (armadura) e templates ativos.", parent=modal)

            self.sincronizar_formulario_para_item()
            mod_item = self.dados[self.categoria_atual][self.item_selecionado_idx] if self.dados[self.categoria_atual] else self.criar_item_vazio()
            
            cont = 0
            for t_obj in ativos:
                for idx_m, mat in enumerate(m_sels):
                    for tp in tp_sels:
                        v_calc = t_obj.get('dano_base', 15) + (idx_m * t_obj.get('dano_escalavel', 3))
                        p_calc = int(t_obj.get('preco_base', 100) * mat.get('preco_multiplicador', 1.0))
                        
                        novo = dict(mod_item)
                        novo.update({"material": mat['id'], "preco": p_calc})
                        
                        if is_armadura:
                            t_nome = t_obj.get('nome', '')
                            if var_usar_template.get():
                                nome_gerado = f"{tp} do {t_nome}" + (f" de {mat['nome']}" if var_incluir_material.get() else "")
                            else:
                                nome_gerado = f"{tp}" + (f" de {mat['nome']}" if var_incluir_material.get() else "")
                            novo.update({"nome": nome_gerado.strip(), "indice_armadura": v_calc, "tipo": tp})
                        else:
                            novo.update({"nome": f"{t_obj['nome']} de {mat['nome']}", "dano_base": v_calc, "atributo_derivado": combo_modal_derivado.get()})
                        
                        self.dados[self.categoria_atual].append(novo); cont += 1

            self.atualizar_lista_itens(); self.carregar_dados_no_formulario(); modal.destroy()
            messagebox.showinfo("Sucesso", f"{cont} itens gerados!")

        tk.Button(frame_dir, text="✨ Gerar", bg=TEMA['botao_salvar'], fg=TEMA['texto'], font=("Consolas", 10, "bold"), command=gerar).pack(fill="x", padx=10, pady=20, ipady=5)

    def salvar_templates(self):
        salvar_json("templates.json", self.templates_dict)

    def trocar_categoria(self, nova_cat):
        self.sincronizar_formulario_para_item()
        self.categoria_atual, self.item_selecionado_idx = nova_cat, 0
        self.atualizar_lista_itens()
        self.carregar_dados_no_formulario()

    def atualizar_lista_itens(self):
        self.listbox_itens.delete(0, tk.END)
        for i, item in enumerate(self.dados[self.categoria_atual]): self.listbox_itens.insert(tk.END, f"{i+1}. {item.get('nome', '')}")
        if self.dados[self.categoria_atual]: self.listbox_itens.selection_set(self.item_selecionado_idx)

    def on_item_selecionado(self, event):
        if sel := self.listbox_itens.curselection():
            if sel[0] != self.item_selecionado_idx:
                self.sincronizar_formulario_para_item()
                self.item_selecionado_idx = sel[0]
                self.carregar_dados_no_formulario()

    def adicionar_novo_item(self):
        self.sincronizar_formulario_para_item()
        self.dados[self.categoria_atual].append(self.criar_item_vazio())
        self.item_selecionado_idx = len(self.dados[self.categoria_atual]) - 1
        self.atualizar_lista_itens()
        self.carregar_dados_no_formulario()

    def deletar_item_atual(self):
        if len(self.dados[self.categoria_atual]) > 1:
            self.dados[self.categoria_atual].pop(self.item_selecionado_idx)
            self.item_selecionado_idx = max(0, self.item_selecionado_idx - 1)
            self.atualizar_lista_itens()
            self.carregar_dados_no_formulario()

if __name__ == "__main__":
    root = tk.Tk()
    app = GerenciadorEquipamentosTK(root)
    root.mainloop()