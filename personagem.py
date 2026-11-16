import random

class Personagem:
    def __init__(self, nome, raca_base_hp=0, raca_base_mp=0, dado_hp=10, dado_mp=0, bonus_raca=None, bonus_classe=None, tipo_progressao='A', base_xp=100, multiplicador_mana=1.0):
        self.nome = nome
        self.raca_nome = "Humano"
        self.classe_nome = "Guerreiro"
        self.classe_id = "knight"
        self.nivel = 1
        
        self.raca_base_hp = raca_base_hp
        self.raca_base_mp = raca_base_mp
        self.dado_hp = dado_hp
        self.dado_mp = dado_mp
        self.multiplicador_mana = multiplicador_mana
        self.bonus_raca = bonus_raca if bonus_raca else {}
        self.bonus_classe = bonus_classe if bonus_classe else {}
        self.bonus_equipamento = {'esquiva': 0, 'resistencia_magica': 0, 'armadura': 0}
        
        # Atributos Primários (Sem PER; VIT representa Endurance, LCK representa Sorte)
        self.atributos = {
            'STR': 10, 'AGI': 10, 'VIT': 50, 'INT': 10, 
            'LCK': 50, 'CAR': 10, 'WILL': 10
        }
        
        self.pontos_atributo_livres = 0
        
        self.vida_maxima = 0
        self.vida_atual = 0
        self.mana_maxima = 0
        self.mana_atual = 0
        self.peso_maximo = 0
        
        self.hp_ganho_por_niveis = 0
        
        self.skills = {}
        self.inicializar_skills()
        
        self.hp_ganho_por_niveis = self.calcular_ganho_hp(nivel_um=True)
        self.atualizar_status_derivados()

        self.iniciativa = 0
        self.defendendo = False
        self.condicoes = {}
        self.arma_equipada = {'dano': 2, 'tipo_skill': 'DESARMADO'}
        self.magias_conhecidas = []
        
        self.xp_atual = 0
        self.xp_acumulada_total = 0 
        self.tipo_progressao = tipo_progressao 
        self.base_xp = base_xp
        self.historico_evolucao = []

    @classmethod
    def carregar_de_json(cls, dados_char, classes_db):
        """Monta uma instância completa de Personagem a partir do JSON, respeitando o limite de 100"""
        nome = dados_char.get("nome", "Sem Nome")
        raca_nome = dados_char.get("raca", "Humano")
        classe_nome = dados_char.get("classe", "Barbarian")
        
        classe_info = next((c for c in classes_db if c['name'].lower() == classe_nome.lower()), classes_db[0])
        
        dado_hp = classe_info.get('max_hp_per_level', 10)
        mult_mana = classe_info.get('multiplicador_mana', None)
        if mult_mana is None:
            mult_mana = {'mage': 5.0, 'monk': 1.5, 'thief': 1.0, 'knight': 0.8, 'barbarian': 0.5}.get(classe_info['id'], 1.0)
        
        prog = classe_info.get('tipo_progressao', 'A')
        
        char = cls(
            nome=nome,
            raca_base_hp=0,
            raca_base_mp=0,
            dado_hp=dado_hp,
            dado_mp=0,
            tipo_progressao=prog,
            multiplicador_mana=mult_mana
        )
        char.raca_nome = raca_nome
        char.classe_nome = classe_info['name']
        char.classe_id = classe_info['id']
        
        # Carrega Atributos Finais (Ignora PER caso exista num JSON antigo e trava em 100)
        for k, v in dados_char.get("atributos_finais", {}).items():
            chave = 'VIT' if k == 'END' else k
            if chave in char.atributos:
                char.atributos[chave] = min(100, int(v))
                
        # Carrega Skills Finais (Trava em 100)
        for k, v in dados_char.get("skills_finais", {}).items():
            char.skills[k] = {'nivel': min(100, int(v)), 'xp': 0}
            
        char.hp_ganho_por_niveis = char.calcular_ganho_hp(nivel_um=True)
        char.vida_atual = 0
        char.mana_atual = 0
        char.atualizar_status_derivados()
        char.historico_evolucao.append(f"Personagem {char.nome} ({char.classe_nome}) carregado no Nível 1.")
        return char

    def inicializar_skills(self):
        lista_skills = {
            'ARMA-CONTUSAO': 'STR', 'ARMA-CORTE': 'STR', 'ARCO': 'AGI', 'DESARMADO': 'STR',
            'RESISTENCIA FISICA': 'VIT', 'PERCEPCAO': 'WILL', 'MANIPULACAO': 'CAR', 
            'MANHA DA RUA': 'CAR', 'NATUREZA': 'INT', 'RASTREIO': 'WILL', 'REFLEXOS': 'AGI', 
            'NEGOCIACAO': 'CAR', 'MEDICINA': 'INT', 'ALQUIMIA': 'INT', 'FURTIVIDADE': 'AGI', 
            'PUNGA': 'AGI', 'DESTRUICAO': 'INT', 'CONTROLE': 'WILL', 'ALTERACAO': 'WILL', 
            'ORATORIA': 'CAR', 'ABRIR FECHADURA': 'AGI', 'ETIQUETA': 'CAR'
        }

        for skill, atr in lista_skills.items():
            valor_atr = self.atributos.get(atr, 10)
            
            if skill == 'DESARMADO': valor_atr = (self.atributos['STR'] + self.atributos['AGI']) / 2
            elif skill == 'ARMA-CORTE': valor_atr = max(self.atributos['STR'], self.atributos['AGI'])
            elif skill in ['MANIPULACAO', 'NEGOCIACAO', 'ORATORIA']: valor_atr = max(self.atributos['CAR'], self.atributos['INT'])
            elif skill == 'RASTREIO': valor_atr = max(self.atributos['WILL'], self.atributos['INT'])
            elif skill == 'ALTERACAO': valor_atr = max(self.atributos['INT'], self.atributos['WILL'])

            bonus_r = self.bonus_raca.get(skill, 0)
            bonus_c = self.bonus_classe.get(skill, 0)
            
            valor_inicial = min(100, int((valor_atr / 2) + bonus_c + bonus_r))
            self.skills[skill] = {'nivel': valor_inicial, 'xp': 0}

    def calcular_modificador_end(self):
        return (self.atributos['VIT'] - 50) // 10

    def calcular_ganho_hp(self, nivel_um=False):
        modificador_vit = self.calcular_modificador_end()
        
        if nivel_um:
            hp_final = (self.dado_hp * 2) + modificador_vit
            return max(1, int(hp_final))
        else:
            chance_dado_maximo = self.atributos['LCK'] * 0.95
            teste_sorte = random.uniform(1, 100)
            
            if teste_sorte <= chance_dado_maximo:
                dado_rolado = self.dado_hp
                self.historico_evolucao.append(f"[Sorte HP!] Crítico de Sorte: Dado cheio ({self.dado_hp})")
            else:
                dado_metade = max(1, self.dado_hp // 2)
                dado_rolado = random.randint(dado_metade, self.dado_hp)
                
            hp_final = int(modificador_vit + dado_rolado)
            return max(1, hp_final)

    def calcular_ganho_pontos_atributo(self):
        chance_maximo = self.atributos['LCK'] * 0.95
        teste_sorte = random.uniform(1, 100)
        
        if teste_sorte <= chance_maximo:
            self.historico_evolucao.append("[Sorte Atributo!] Crítico de Sorte: +6 Pontos!")
            return 6
        else:
            return random.randint(4, 6)

    def atualizar_status_derivados(self):
        self.vida_maxima = self.raca_base_hp + self.hp_ganho_por_niveis
        self.mana_maxima = int(self.raca_base_mp + (self.atributos['INT'] * self.multiplicador_mana) + (self.dado_mp * self.nivel))
        self.peso_maximo = self.atributos['STR'] + self.atributos['VIT']
        
        if self.vida_atual == 0 or self.vida_atual > self.vida_maxima: 
            self.vida_atual = self.vida_maxima
        if self.mana_atual == 0 or self.mana_atual > self.mana_maxima: 
            self.mana_atual = self.mana_maxima

    def calcular_xp_para_proximo_nivel(self):
        if self.tipo_progressao == 'A': return int(self.base_xp * (self.nivel ** 2.0))
        elif self.tipo_progressao == 'B': return int(self.base_xp * (self.nivel ** 2.4))
        elif self.tipo_progressao == 'C': return int(self.base_xp * (self.nivel ** 2.8))
        return 999999

    def calcular_xp_total_acumulada(self, nivel_alvo):
        if self.tipo_progressao == 'A': return int(self.base_xp * (nivel_alvo ** 2.5))
        elif self.tipo_progressao == 'B': return int(self.base_xp * (nivel_alvo ** 2.75))
        elif self.tipo_progressao == 'C': return int(self.base_xp * (nivel_alvo ** 3.0))
        return 999999

    def subir_um_nivel_direto(self):
        xp_faltando = self.calcular_xp_para_proximo_nivel() - self.xp_atual
        self.ganhar_xp_geral(xp_faltando)

    def ganhar_xp_geral(self, quantidade):
        self.xp_atual += quantidade
        self.xp_acumulada_total += quantidade
        
        xp_necessaria = self.calcular_xp_para_proximo_nivel()
        
        while self.xp_atual >= xp_necessaria:
            self.xp_atual -= xp_necessaria
            self.nivel += 1
            
            hp_ganho_no_nivel = self.calcular_ganho_hp(nivel_um=False)
            self.hp_ganho_por_niveis += hp_ganho_no_nivel
            
            pts_ganhos = self.calcular_ganho_pontos_atributo()
            self.pontos_atributo_livres += pts_ganhos
            
            msg = f"Nível {self.nivel}: +{hp_ganho_no_nivel} HP | +{pts_ganhos} Pts de Atributo"
            self.historico_evolucao.append(msg)
            
            xp_necessaria = self.calcular_xp_para_proximo_nivel()
            self.atualizar_status_derivados()
            
            self.vida_atual = self.vida_maxima
            self.mana_atual = self.mana_maxima

    def calcular_esquiva(self): 
        return (self.atributos['AGI'] / 2) + self.bonus_equipamento['esquiva']
        
    def calcular_defesa_fisica(self, bonus_extra=0): 
        return self.atributos['VIT'] + self.bonus_equipamento['armadura'] + bonus_extra
        
    def calcular_resistencia_magica(self): 
        resistencia = (self.atributos['WILL'] / 2) + self.bonus_raca.get('resistencia_magica', 0) + self.bonus_equipamento['resistencia_magica']
        return min(80, resistencia)
    
    def calcular_ataque_fisico(self, dano_arma=5, nome_skill_arma='DESARMADO'): 
        pericia = self.skills.get(nome_skill_arma, {'nivel': 0})['nivel']
        return self.atributos['STR'] + (dano_arma * (1 + (pericia / 100)))
        
    def calcular_ataque_magico(self, poder_magia=10, nome_skill_magia='DESTRUICAO'): 
        pericia = self.skills.get(nome_skill_magia, {'nivel': 0})['nivel']
        return self.atributos['INT'] + (poder_magia * (1 + (pericia / 100)))

    def calcular_dano_fisico_mitigado(self, ataque_fisico_inimigo): 
        return ataque_fisico_inimigo * (100 / (100 + self.calcular_defesa_fisica()))
        
    def calcular_dano_magico_mitigado(self, ataque_magico_inimigo): 
        return ataque_magico_inimigo * (1 - (self.calcular_resistencia_magica() / 100))
        
    def calcular_dano_final(self, dano_mitigado, multiplicador_fraqueza=1.0): 
        return dano_mitigado * multiplicador_fraqueza * random.uniform(0.90, 1.10)

    def teste_sucesso_skill(self, nome_skill, modificador_dificuldade=0): 
        return random.randint(1, 100) <= (self.skills[nome_skill]['nivel'] + modificador_dificuldade)

    def ganhar_xp_skill(self, nome_skill, quantidade_xp):
        if nome_skill not in self.skills: return
        
        # Trava no nível 100
        if self.skills[nome_skill]['nivel'] >= 100:
            self.skills[nome_skill]['nivel'] = 100
            self.skills[nome_skill]['xp'] = 0
            return
            
        self.skills[nome_skill]['xp'] += quantidade_xp
        
        xp_necessaria = self.skills[nome_skill]['nivel'] * 10
        while self.skills[nome_skill]['xp'] >= xp_necessaria and self.skills[nome_skill]['nivel'] < 100:
            self.skills[nome_skill]['xp'] -= xp_necessaria
            self.skills[nome_skill]['nivel'] += 1
            xp_necessaria = self.skills[nome_skill]['nivel'] * 10
            
        if self.skills[nome_skill]['nivel'] >= 100:
            self.skills[nome_skill]['xp'] = 0