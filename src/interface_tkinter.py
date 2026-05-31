import customtkinter as ctk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import djikstra_geometrico as dg

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Trabalho AED2")
        self.geometry("900x600")
        
        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure(0,weight=1)

        self.barra_lateral = ctk.CTkFrame(self,width=200)
        self.barra_lateral.grid(row=0, column=0,stick="nsew",padx=10)

        self.barra_ilustracao = ctk.CTkFrame(self,width=400)
        self.barra_ilustracao.grid(row=0,column=1,stick="nsew",pady=10,padx=5)

        self.canvas = None
        self.definir_barra_funcionalidades()


        
    def definir_barra_funcionalidades(self):
        self.label_grafo = ctk.CTkLabel(self.barra_lateral,text="Algoritmo de Dijkstra",font=ctk.CTkFont(size=20,weight="bold"))
        self.label_grafo.pack(padx=10,pady=(20,10))

    
        self.vertice_inicial = ctk.CTkEntry(self.barra_lateral,placeholder_text="Insira o vertice inicial")
        self.vertice_inicial.pack(padx=10,pady=5)

        self.vertice_final = ctk.CTkEntry(self.barra_lateral,placeholder_text="Insira o vertice final")
        self.vertice_final.pack(padx=10,pady=5)

        self.botao_gerar_grafo = ctk.CTkButton(self.barra_lateral,text='Gerar Grafo',width=100,command=self.gerar_grafo)
        self.botao_gerar_grafo.pack(padx=10,pady=(20,20)) 

        self.botao_dijkistra = ctk.CTkButton(self.barra_lateral,text='Testar Algoritmo',width=100,command=self.calcular_caminho)
        self.botao_dijkistra.pack(padx=10,pady=(0,20)) 
    
    def gerar_grafo(self, caminho=None):

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.grafo = nx.gnp_random_graph(n=8, p=0.4,seed=1)
        

        self.pos = nx.spring_layout(self.grafo,seed=1)


        self.fig, self.ax = plt.subplots(figsize=(6, 6), facecolor="#2b2b2b")
        self.ax.set_facecolor("#2b2b2b")
        self.ax.axis("off")

        nx.draw_networkx_edges(self.grafo, self.pos, ax=self.ax, edge_color="#555555", width=1.5)

        nx.draw_networkx_nodes(self.grafo,self.pos,ax=self.ax,node_size=400,edgecolors="white",linewidths=1)

        nx.draw_networkx_labels(self.grafo,self.pos,ax=self.ax)

        if caminho:
            
            aresta_caminho = list(zip(caminho[:-1],caminho[1:]))
            label_caminho = nx.get_edge_attributes(self.grafo,"weight")

            nx.draw_networkx_nodes(self.grafo,pos=self.pos,nodelist=caminho,node_color="#FF0000")
            nx.draw_networkx_edges(self.grafo,pos=self.pos,edgelist=aresta_caminho,ax=self.ax,edge_color="#ff0000")
            nx.draw_networkx_edge_labels(self.grafo,pos=self.pos,ax=self.ax,edge_labels=label_caminho)

        self.canvas = FigureCanvasTkAgg(self.fig,master=self.barra_ilustracao)
        self.canvas.draw()

        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def calcular_caminho(self):

        # caminho = dg.dijkstra(
        #     dg.construir_grafo(self.grafo.nodes(),self.grafo.edges()),
        #     self.grafo.nodes(),
        #     self.vertice_inicial,
        #     self.vertice_final) 


        comprimento ,caminho = nx.single_source_dijkstra(
            self.grafo,source=int(self.vertice_inicial.get()),target=int(self.vertice_final.get()))

        self.gerar_grafo(caminho=caminho)


        

    

janela = App()
janela.mainloop()
