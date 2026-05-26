class Heap:
    
    def __init__(self):
        self.__heap = []

    def __parente(self, index: int) -> int: return (index - 1) // 2 
    def __esq(self, index: int) -> int: return (2 * index + 1) 
    def __dir(self, index: int) -> int: return (2 * index + 2) 

    def heapifyUp(self, index: int):
        heap = self.__heap
        while index > 0:
            par_idx = self.__parente(index)
            
            if heap[index] < heap[par_idx]:
                heap[index], heap[par_idx] = heap[par_idx], heap[index]
                index = par_idx
            else: 
                break

    def heapifyDown(self, index: int, tam: int):
        heap = self.__heap
        esq = self.__esq(index)
        dir = self.__dir(index)
        p = index

        if esq < tam and heap[esq] < heap[p]:
            p = esq
        
        if dir < tam and heap[dir] < heap[p]:
            p = dir

        if p != index:
            heap[index], heap[p] = heap[p], heap[index]
            self.heapifyDown(p, tam)
            
    def size(self) -> int: return len(self.__heap)
    
    def isEmpty(self) -> bool: return self.size() == 0

    def peekMin(self) -> tuple:
        if self.isEmpty():
            raise RuntimeError("Heap está vazia")
        return self.__heap[0]
        
    def insert(self, key: tuple):
        self.__heap.append(key)        
        self.heapifyUp(self.size() - 1)

    def extractMin(self) -> tuple:
        if self.isEmpty():
            raise RuntimeError("Heap está vazia")
        heap = self.__heap

        root = heap[0]
        last = heap.pop()

        if self.size() > 0:
            heap[0] = last
            self.heapifyDown(0, self.size())
            
        return root