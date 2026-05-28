import customtkinter as ctk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

        self.botao_dijkistra = ctk.CTkButton(self.barra_lateral,text='Testar Algoritmo',width=100)
        self.botao_dijkistra.pack(padx=10,pady=(0,20)) 
    
    def gerar_grafo(self):

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        grafo = nx.erdos_renyi_graph(n=5,p=0.6)
        pos = nx.spring_layout(grafo,seed=42)



        fig, ax = plt.subplots(figsize=(6, 6), facecolor="#2b2b2b")
        ax.set_facecolor("#2b2b2b")
        ax.axis("off")

        nx.draw_networkx_edges(grafo, pos, ax=ax, edge_color="#555555", width=1.5)

        nx.draw_networkx_nodes(grafo,pos,ax=ax,node_size=400,edgecolors="white",linewidths=1)

        nx.draw_networkx_labels(grafo,pos,ax=ax)

        self.canvas = FigureCanvasTkAgg(fig,master=self.barra_ilustracao)
        self.canvas.draw()

        self.canvas.get_tk_widget().pack(fill="both", expand=True)


        

    

janela = App()
janela.mainloop()
