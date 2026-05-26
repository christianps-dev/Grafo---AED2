#include <stdio.h>
#include <stdlib.h>
#include "Grafo.h"

int main(int argc, char *argv[]) 
{
   int eh_digrafo = 0;
   int i, vis[5];
	
	Grafo* gr = cria_Grafo(5, 5, 0);
   insereAresta(gr, 0, 1, eh_digrafo, 0);	// 1 2
   insereAresta(gr, 0, 4, eh_digrafo, 0);  // 1 5
   insereAresta(gr, 1, 2, eh_digrafo, 0);  // 2 3
	insereAresta(gr, 1, 3, eh_digrafo, 0);	// 2 4
	insereAresta(gr, 1, 4, eh_digrafo, 0);	// 2 5
	insereAresta(gr, 2, 3, eh_digrafo, 0);	// 3 4
	insereAresta(gr, 3, 4, eh_digrafo, 0);	// 4 5
	
	printf("Lista de adjacência ref. ao grafo:\n");
   imprime_Grafo(gr);

   printf("\nBusca em profundidade:\n");
   buscaProfundidade_Grafo(gr, 0, vis);
   printf("\n\nBusca em largura:\n");
   buscaLargura_Grafo(gr, 0, vis);
   printf("\n");

   libera_Grafo(gr);

   system("pause");

	return 0;
}
