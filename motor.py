import random

class MotorBatalha:
    def __init__(self, grupo_jogadores, grupo_inimigos):
        self.jogadores = grupo_jogadores
        self.inimigos = grupo_inimigos
        self.todos_combatentes = self.jogadores + self.inimigos
        self.fila_iniciativa = []
        self.turno_atual = 0
        self.combatente_atual = None
        self.estado_atual = 'INICIANDO'
        self.log_batalha = []
        self.recompensas_acumuladas = {'xp_geral': 0, 'ouro': 0, 'itens': []}

    def adicionar_log(self, mensagem):
        self.log_batalha.append(mensagem)

    def iniciar_batalha(self):
        self.adicionar_log("A batalha começou!")
        for c in self.todos_combatentes:
            bonus_reflexos = c.skills['REFLEXOS']['nivel'] if 'REFLEXOS' in c.skills else 0
            c.iniciativa = c.atributos['AGI'] + bonus_reflexos + random.randint(1, 20)
            c.defendendo = False
            c.condicoes = {}
        self.fila_iniciativa = sorted(self.todos_combatentes, key=lambda x: x.iniciativa, reverse=True)
        self.estado_atual = 'FIM_TURNO'

    def atualizar_estado(self):
        if self.estado_atual in ['VITORIA', 'DERROTA', 'FUGA']: return
        
        if self.estado_atual == 'FIM_TURNO':
            self.avancar_fila()
        elif self.estado_atual == 'INICIO_TURNO':
            self.processar_inicio_turno()
        elif self.estado_atual == 'AGUARDANDO_ACAO':
            if self.combatente_atual in self.inimigos:
                self.inteligencia_artificial_inimigo()

    def avancar_fila(self):
        if self.combatente_atual:
            self.fila_iniciativa.append(self.fila_iniciativa.pop(0))
        self.combatente_atual = self.fila_iniciativa[0]
        
        if self.combatente_atual.vida_atual <= 0:
            self.estado_atual = 'FIM_TURNO'
            return

        self.turno_atual += 1
        self.estado_atual = 'INICIO_TURNO'

    def processar_inicio_turno(self):
        self.adicionar_log(f"--- Turno de {self.combatente_atual.nome} ---")
        c = self.combatente_atual
        c.defendendo = False
        pode_agir = True

        condicoes_remover = []
        for nome_cond, dados in c.condicoes.items():
            if nome_cond in ['envenenado', 'sangrando']:
                dano = dados['potencia']
                c.vida_atual -= dano
                self.adicionar_log(f"{c.nome} sofreu {dano} de dano devido a {nome_cond}.")
            if nome_cond in ['atordoado', 'congelado']:
                self.adicionar_log(f"{c.nome} está {nome_cond} e não pode agir!")
                pode_agir = False

            dados['duracao'] -= 1
            if dados['duracao'] <= 0: condicoes_remover.append(nome_cond)

        for cond in condicoes_remover:
            del c.condicoes[cond]
            self.adicionar_log(f"{c.nome} se recuperou de {cond}.")

        if self.verificar_morte(c):
            self.estado_atual = 'FIM_TURNO'
            return

        self.estado_atual = 'AGUARDANDO_ACAO' if pode_agir else 'FIM_TURNO'

    def executar_acao_jogador(self, tipo_acao, alvo=None, habilidade=None, item=None):
        if self.estado_atual != 'AGUARDANDO_ACAO' or self.combatente_atual not in self.jogadores: return False
        self.estado_atual = 'RESOLVENDO_ACAO'
        self.resolver_acao(self.combatente_atual, tipo_acao, alvo, habilidade, item)
        self.verificar_fim_batalha()
        if self.estado_atual == 'RESOLVENDO_ACAO': self.estado_atual = 'FIM_TURNO'
        return True

    def resolver_acao(self, atacante, tipo_acao, alvo, habilidade, item):
        if tipo_acao == 'ATACAR': self.acao_atacar(atacante, alvo)
        elif tipo_acao == 'DEFENDER':
            atacante.defendendo = True
            self.adicionar_log(f"{atacante.nome} assumiu postura defensiva.")
        elif tipo_acao == 'MAGIA' and habilidade: self.acao_usar_magia(atacante, alvo, habilidade)
        elif tipo_acao == 'FUGIR': self.acao_fugir(atacante)
        elif tipo_acao == 'ITEM': self.adicionar_log(f"{atacante.nome} procurou itens, mas não tinha nada.")

    def acao_atacar(self, atacante, alvo):
        chance_esquiva = alvo.calcular_esquiva()
        if random.randint(1, 100) <= chance_esquiva:
            self.adicionar_log(f"{atacante.nome} tentou atacar {alvo.nome} e ERROU (Esquiva)!")
            return

        ataque_bruto = atacante.calcular_ataque_fisico(atacante.arma_equipada['dano'], atacante.arma_equipada['tipo_skill'])
        dano_mitigado = alvo.calcular_dano_fisico_mitigado(ataque_bruto)
        if alvo.defendendo: dano_mitigado /= 2
        dano_final = int(atacante.calcular_dano_final(dano_mitigado))
        
        alvo.vida_atual -= dano_final
        self.adicionar_log(f"{atacante.nome} causou {dano_final} de dano físico em {alvo.nome}!")
        
        atacante.ganhar_xp_skill(atacante.arma_equipada['tipo_skill'], dano_final)
        if alvo.vida_atual > 0: alvo.ganhar_xp_skill('RESISTENCIA FISICA', dano_final // 2)

        self.verificar_morte(alvo)

    def acao_usar_magia(self, conjurador, alvo, magia):
        if conjurador.mana_atual < magia['custo_mp']:
            self.adicionar_log(f"{conjurador.nome} falhou: MP Insuficiente.")
            return
        
        conjurador.mana_atual -= magia['custo_mp']
        
        # A magia não falha mais por skill. A skill apenas escala a eficiência.

        if magia['tipo'] == 'dano':
            # Usa o calcular_ataque_magico que já aplica: INT + [Poder * (1 + (Skill / 100))]
            ataque_magico = conjurador.calcular_ataque_magico(magia['poder'], magia['escola'])
            dano_final = int(conjurador.calcular_dano_final(alvo.calcular_dano_magico_mitigado(ataque_magico)))
            
            alvo.vida_atual -= dano_final
            self.adicionar_log(f"{conjurador.nome} conjurou {magia['nome']}! {dano_final} dano em {alvo.nome}.")
            
            # Ganha XP na escola de magia equivalente ao dano causado
            conjurador.ganhar_xp_skill(magia['escola'], dano_final)
        
        elif magia['tipo'] == 'cura':
            # Cure também se beneficia do multiplicador da escola (ex: ALTERACAO)
            multiplicador = 1 + (conjurador.skills[magia['escola']]['nivel'] / 100)
            cura = int((magia['poder'] * multiplicador) + conjurador.atributos['INT'])
            
            alvo.vida_atual = min(alvo.vida_maxima, alvo.vida_atual + cura)
            self.adicionar_log(f"{conjurador.nome} conjurou {magia['nome']} curando {cura} de HP em {alvo.nome}.")
            
            # Ganha XP na escola de magia
            conjurador.ganhar_xp_skill(magia['escola'], cura)

        self.verificar_morte(alvo)

    def acao_fugir(self, fugitivo):
        bonus_fuga = fugitivo.skills.get('FURTIVIDADE', {}).get('nivel', 0)
        chance = fugitivo.atributos['AGI'] + bonus_fuga + random.randint(1, 100)
        if chance > 50:
            self.adicionar_log(f"{fugitivo.nome} conseguiu escapar com sucesso!")
            self.estado_atual = 'FUGA'
        else:
            self.adicionar_log(f"{fugitivo.nome} tentou fugir, mas falhou!")

    def verificar_morte(self, combatente):
        if combatente.vida_atual <= 0:
            combatente.vida_atual = 0
            self.adicionar_log(f"> {combatente.nome} MORREU!")
            if combatente in self.inimigos:
                self.recompensas_acumuladas['xp_geral'] += getattr(combatente, 'xp_drop', 50)
            return True
        return False

    def verificar_fim_batalha(self):
        jogadores_vivos = [j for j in self.jogadores if j.vida_atual > 0]
        inimigos_vivos = [i for i in self.inimigos if i.vida_atual > 0]

        if not inimigos_vivos:
            self.estado_atual = 'VITORIA'
            self.adicionar_log("VITÓRIA! Você derrotou os inimigos.")
            self.adicionar_log(f"Recompensa: {self.recompensas_acumuladas['xp_geral']} XP.")
        elif not jogadores_vivos:
            self.estado_atual = 'DERROTA'
            self.adicionar_log("DERROTA! O seu grupo foi aniquilado.")

    def inteligencia_artificial_inimigo(self):
        self.estado_atual = 'RESOLVENDO_ACAO'
        inimigo = self.combatente_atual
        alvos_vivos = [j for j in self.jogadores if j.vida_atual > 0]
        if not alvos_vivos: return
        alvo = random.choice(alvos_vivos)
        
        if (inimigo.vida_atual / inimigo.vida_maxima) < 0.3 and random.random() < 0.5:
            self.resolver_acao(inimigo, 'DEFENDER', None, None, None)
        else:
            self.resolver_acao(inimigo, 'ATACAR', alvo, None, None)
            
        self.verificar_fim_batalha()
        if self.estado_atual == 'RESOLVENDO_ACAO': self.estado_atual = 'FIM_TURNO'