import os
import sys

# Importação das funções desenvolvidas nos módulos da P1 e P2
from conversor_osm import parse_osm
from djikstra_geometrico import carregar_mapa_poly, construir_grafo, dijkstra

def limpar_tela():
    """Limpa o terminal garantindo suporte multiplataforma (Windows/Linux)."""
    os.system('cls' if os.name == 'nt' else 'clear')

def pausar():
    """Pausa a execução até o usuário pressionar Enter."""
    input("\nPressione [Enter] para continuar...")

def exibir_menu():
    limpar_tela()
    print("=" * 55)
    print("      SISTEMA DE NAVEGAÇÃO INTEGRADO - PIPELINE      ")
    print("=" * 55)
    print("1. Importar novo mapa (.osm) -> Gerar .poly e calcular rota")
    print("2. Carregar mapa estruturado existente (.poly) e calcular rota")
    print("3. Sair")
    print("=" * 55)
    return input("Escolha uma opção (1-3): ").strip()

def executar_sistema():
    while True:
        opcao = exibir_menu()
        
        if opcao == "1":
            #arq_osm = input("Introduza o caminho do arquivo .osm (ex: ../maps/mapa.osm): ").strip()
            arq_osm = "../maps/mapaUFG.osm"

            if not os.path.exists(arq_osm):
                print("Erro: O ficheiro .osm especificado não foi encontrado.")
                pausar()
                continue
            
            limpar_tela()
            print("\n[P2] A processar o arquivo OSM e a projetar coordenadas UTM...")
            parse_osm(arq_osm)
            
           
            nome_base = os.path.splitext(os.path.basename(arq_osm))[0]
            arq_poly = f"../out/{nome_base}.poly"
            
        elif opcao == "2":
            #arq_poly = input("Introduza o caminho do arquivo .poly (ex: ../out/mapa.poly): ").strip()
            arq_poly = "../out/mapaUFG.poly"
        elif opcao == "3":
            print("A encerrar o sistema de navegação. Até breve!")
            sys.exit(0)
        else:
            print("Opção inválida! Por favor, escolha 1, 2 ou 3.")
            pausar()
            continue
        
        
        if not os.path.exists(arq_poly):
            print(f"Erro: O ficheiro estruturado '{arq_poly}' não foi localizado.")
            pausar()
            continue
            
        print("\n[P1] A carregar vértices e arestas para a memória RAM...")
        vertices, arestas = carregar_mapa_poly(arq_poly)
        
        print("[P1] A estruturar a Lista de Adjacência com restrições direcionais...")
        grafo = construir_grafo(vertices, arestas)
        
        total_vertices = len(vertices)
        total_arestas = len(arestas)
        
        print(f"\nGrafo configurado com sucesso!")
        print(f"Total de vértices disponíveis: {total_vertices}")
        print(f"Total de arestas processadas : {total_arestas}")
        print("-" * 55)
        
        try:
            origem = int(input(f"Digite o vértice de origem (0 a {total_vertices - 1}): "))
            destino = int(input(f"Digite o vértice de destino (0 a {total_vertices - 1}): "))

            if 0 <= origem < total_vertices and 0 <= destino < total_vertices:
                print("\n[P1] A executar o Algoritmo de Dijkstra...")
                resultado = dijkstra(grafo, vertices, origem, destino)
                
                if resultado:
                    print("Processamento concluído.")
                    
            else:
                print("Erro: Os índices de origem ou destino estão fora dos limites do mapa.")
                
        except ValueError:
            print("Erro: Entrada inválida. Certifique-se de introduzir números inteiros.")
            
        print("\n" + "-" * 55)
        
        
        pausar()

if __name__ == "__main__":
    executar_sistema()