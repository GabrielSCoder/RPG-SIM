# Importa as classes dos nossos outros arquivos
from personagem import Personagem
from motor import MotorBatalha
from graficos import JogoGUI

def main():
    # 1. SETUP: Criar e configurar os Personagens Jogáveis
    heroi1 = Personagem("Guerreiro", raca_base_hp=30, raca_base_mp=10, dado_hp=5, dado_mp=2)
    heroi1.atributos['STR'] = 16
    heroi1.atributos['VIT'] = 14
    heroi1.inicializar_skills()
    heroi1.atualizar_status_derivados()
    heroi1.arma_equipada = {'dano': 8, 'tipo_skill': 'ARMA-CORTE'}

    heroi2 = Personagem("Mago", raca_base_hp=20, raca_base_mp=40, dado_hp=3, dado_mp=6)
    heroi2.atributos['INT'] = 18
    heroi2.atributos['AGI'] = 14
    heroi2.inicializar_skills()
    heroi2.atualizar_status_derivados()
    heroi2.magias_conhecidas = [
        {'nome': 'Raio de Gelo', 'escola': 'DESTRUICAO', 'poder': 15, 'custo_mp': 5, 'tipo': 'dano'},
        {'nome': 'Cura Leve', 'escola': 'ALTERACAO', 'poder': 20, 'custo_mp': 8, 'tipo': 'cura'}
    ]

    # 2. SETUP: Criar e configurar os Inimigos
    orc = Personagem("Orc Bruiser", raca_base_hp=45, raca_base_mp=0, dado_hp=4, dado_mp=0)
    orc.atributos['STR'] = 14
    orc.inicializar_skills()
    orc.atualizar_status_derivados()
    orc.arma_equipada = {'dano': 6, 'tipo_skill': 'ARMA-CONTUSAO'}
    orc.xp_drop = 30
    
    goblin = Personagem("Goblin Arqueiro", raca_base_hp=25, raca_base_mp=0, dado_hp=3, dado_mp=0)
    goblin.atributos['AGI'] = 15
    goblin.inicializar_skills()
    goblin.atualizar_status_derivados()
    goblin.arma_equipada = {'dano': 4, 'tipo_skill': 'ARCO'}
    goblin.xp_drop = 15

    # 3. LIGAÇÃO: Passar os personagens para o Motor de Batalha
    batalha = MotorBatalha(
        grupo_jogadores=[heroi1, heroi2], 
        grupo_inimigos=[orc, goblin]
    )
    
    # 4. EXECUÇÃO: Passar o Motor para a Interface e rodar
    interface = JogoGUI(batalha)
    interface.rodar()

# Só executa se for o arquivo principal chamado
if __name__ == "__main__":
    main()