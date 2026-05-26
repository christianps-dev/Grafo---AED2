//Breadth First Search - C Program Source Code

#include<stdio.h>
#include<stdlib.h>
#include<assert.h>
/* maxVertices represents maximum number of vertices that can be present in the graph. */
#define maxVertices   100
/*Queue has five properties. capacity stands for the maximum number of elements Queue can hold.
  Size stands for the current size of the Queue and elements is the array of elements. front is the
 index of first element (the index at which we remove the element) and rear is the index of last element
 (the index at which we insert the element) */
typedef struct Queue
{
        int capacity;
        int size;
        int front;
        int rear;
        int *elements;
}Queue;
/* crateQueue function takes argument the maximum number of elements the Queue can hold, creates
   a Queue according to it and returns a pointer to the Queue. */
Queue * CreateQueue(int maxElements)
{
        /* Create a Queue */
        Queue *Q;
        Q = (Queue *)malloc(sizeof(Queue));
        /* Initialise its properties */
        Q->elements = (int *)malloc(sizeof(int)*maxElements);
        Q->size = 0;
        Q->capacity = maxElements;
        Q->front = 0;
        Q->rear = -1;
        /* Return the pointer */
        return Q;
}
void Dequeue(Queue *Q)
{
        /* If Queue size is zero then it is empty. So we cannot pop */
        if(Q->size==0)
        {
                printf("Queue is Empty\n");
                return;
        }
        /* Removing an element is equivalent to incrementing index of front by one */
        else
        {
                Q->size--;
                Q->front++;
                /* As we fill elements in circular fashion */
                if(Q->front==Q->capacity)
                {
                        Q->front=0;
                }
        }
        return;
}
int Front(Queue *Q)
{
        if(Q->size==0)
        {
                printf("Queue is Empty\n");
                exit(0);
        }
        /* Return the element which is at the front*/
        return Q->elements[Q->front];
}
void Enqueue(Queue *Q,int element)
{
        /* If the Queue is full, we cannot push an element into it as there is no space for it.*/
        if(Q->size == Q->capacity)
        {
                printf("Queue is Full\n");
        }
        else
        {
                Q->size++;
                Q->rear = Q->rear + 1;
                /* As we fill the queue in circular fashion */
                if(Q->rear == Q->capacity)
                {
                        Q->rear = 0;
                }
                /* Insert the element in its rear side */ 
                Q->elements[Q->rear] = element;
        }
        return;
}


// http://www.thelearningpoint.net/computer-science/algorithms-graph-traversal---breadth-first-search-with-c-program-source-code
void Bfs(int graph[][maxVertices], int *size, int presentVertex,int *visited)
{
        visited[presentVertex] = 1;
        /* Iterate through all the vertices connected to the presentVertex and perform bfs on those
           vertices if they are not visited before */
        Queue *Q = CreateQueue(maxVertices);
        Enqueue(Q,presentVertex);
        while(Q->size)
        {
                presentVertex = Front(Q);
                printf("Now visiting vertex %d\n",presentVertex);
                Dequeue(Q);
                int iter;
                for(iter=0;iter<size[presentVertex];iter++)
                {
                        if(!visited[graph[presentVertex][iter]])
                        {
                                visited[graph[presentVertex][iter]] = 1;
                                Enqueue(Q,graph[presentVertex][iter]);
                        }
                }
        }
        return;
        

}


// https://www.thelearningpoint.net/computer-science/algorithms-graph-traversal--depth-first-search--with-c-program-source-code
void Dfs(int graph[][maxVertices], int *size, int presentVertex,int *visited)
{
        printf("Now visiting vertex %d\n",presentVertex);
        visited[presentVertex] = 1;
        /* Iterate through all the vertices connected to the presentVertex and perform dfs on those
           vertices if they are not visited before */
        int iter;
        for(iter=0;iter<size[presentVertex];iter++)
        {
                if(!visited[graph[presentVertex][iter]])
                {
                        Dfs(graph,size,graph[presentVertex][iter],visited);
                }
        }
        return;
}


/* Input Format: Graph is directed and unweighted. First two integers must be number of vertces and edges 
   which must be followed by pairs of vertices which has an edge between them. */
int main()
{
        int graph[maxVertices][maxVertices],size[maxVertices]={0},visited[maxVertices]={0};
        int vertices,edges,iter;
        /* vertices represent number of vertices and edges represent number of edges in the graph. */
        //scanf("%d%d",&vertices,&edges);
        
        //
        /*
        int vet_vertices[][2] = {{0, 1}, {0, 4}, {2, 0}, {2, 3}, {2, 4}, {3, 4}, {3, 5}, {4, 1}, {4, 5}, {5, 1}};
        vertices = 6;
        edges = 10;
		*/
		
		/*
        int vet_vertices[][2] = {{0, 1}, {1, 2}, {1, 3}, {2, 4}, {3, 0}, {3, 4}, {4, 1}};        
        vertices = 5;
        edges = 7;
		*/
		
		/*
  		int vet_vertices[][2] = {{0,1}, {0,2}, {1,3}, {2,3}, {2,4}, {}, {7,0}, {7,5}, {7,6}};        
        vertices = 5;
        edges = 6;		
		*/

		/*
        int vet_vertices[][2] = {{1,4}, {1,6}, {2,7}, {3,4}, {3,7}, {4,5}, {7,0}, {7,5}, {7,6}};        
        vertices = 8;
        edges = 9;
		*/		

		/*
       	//int vet_vertices[][2] = {{1,2}, {1,9}, {2,3}, {3,5}, {3,6}, {4,2}, {4,7}, {5,3}, {5,4}, {6,8}, {7,8}, {8,5}, {9,1}};        
       	int vet_vertices[][2] = {{0,1}, {0,8}, {1,2}, {2,4}, {2,5}, {3,1}, {3,6}, {4,2}, {4,3}, {5,7}, {6,7}, {7,4}, {8,0}};        
        vertices = 9;
        edges = 13;
		*/
		
		/*
       	int vet_vertices[][2] = {{0,1}, {0,2}, {0,3}, {1,2}, {1,3}, {1,4}, {2,4}, {2,5}, {3,6}, {4,3}, {5,2}, {5,4}, {5,8}, {6,4}, {6,8}, {7,4}, {7,6}, {7,8}};        
        vertices = 9;
        edges = 18;
		*/
		
		/*
		// É NECESSÁRIO INCLUIR AS ARESTAS EM DOIS SENTIDOS QUANDO O GRAFO FOR NÃO DIRECIONADO
       	//int vet_vertices[][2] = {{0,1}, {0,2}, {0,5}, {0,6}, {3,4}, {3,5}, {4,5}, {4,6}};
        //vertices = 7;
        //edges = 8;
        int vet_vertices[][2] = {{0,1}, {0,2}, {0,5}, {0,6}, {1,0}, {2,0}, {3,4}, {3,5}, {4,3}, {4,5}, {4,6}, {5,0}, {5,3}, {5,4}, {6,0}, {6,4}};
        vertices = 7;
        edges = 16;
        */
        
        //int vet_vertices[][2] = {{1,2},{1,3},{2,4},{2,5},{3,4},{4,5},{4,6},{6,7},{6,8},{7,8},{2,1},{3,1},{4,2},{5,2},{4,3},{5,4},{6,4},{7,6},{8,6},{8,7}};
        int vet_vertices[][2] = {{0,1},{0,2},{1,3},{1,4},{2,3},{3,4},{3,5},{5,6},{5,7},{6,7},{1,0},{2,0},{3,1},{4,1},{3,2},{4,3},{5,3},{6,5},{7,5},{7,6}};
        vertices=8,
        edges=20;

		
		int vertex1,vertex2;
        //@ 24/11/2019 - 19h38
 		int i;
 		
        for(iter=0;iter<edges;iter++)
        {
            //scanf("%d%d",&vertex1,&vertex2);
            vertex1 = vet_vertices[iter][0];
            vertex2 = vet_vertices[iter][1];
            //printf("%d-%d\n", vertex1, vertex2);
            assert(vertex1>=0 && vertex1<vertices);
            assert(vertex2>=0 && vertex2<vertices);
            graph[vertex1][size[vertex1]++] = vertex2;
        }
        
        
        int presentVertex;
                
        printf("\nBusca em largura:\n");
        printf("vertices: %i  edges: %i\n", vertices, edges);
		printf("visited:\n");
		for (i=0;i<vertices;i++)
			printf("%i ", visited[i]);
		printf("\n");
		printf("size:\n");
		for (i=0;i<vertices;i++)
			printf("%i ", size[i]);
		printf("\n");

        for(presentVertex=0;presentVertex<vertices;presentVertex++)
        {
                if(!visited[presentVertex])
                {
                        Bfs(graph,size,presentVertex,visited);
                }
        }
      
      	//@ 25/11/2019 - 20h10
 		for (i=0; i<maxVertices; i++) {
 			visited[i] = 0;
 			//size[i] = 0;
 		}	
 		//@
 		
 		
 		printf("\nBusca em profundidade:\n");
 		printf("vertices: %i  edges: %i\n", vertices, edges);
		printf("visited:\n");
		for (i=0;i<vertices;i++)
			printf("%i ", visited[i]);
		printf("\n");
		printf("size:\n");
		for (i=0;i<vertices;i++)
			printf("%i ", size[i]);
		printf("\n");

   		for(presentVertex=0;presentVertex<vertices;presentVertex++)
        {
                if(!visited[presentVertex])
                {
                        Dfs(graph,size,presentVertex,visited);
                }
        }
       return 0;		
}

