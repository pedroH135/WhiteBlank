from abc import ABC, abstractmethod

class ElementoGrafico(ABC):
    def __init__(self, largura: int, altura: int, x: int = 100, y: int = 100):
        self.largura = largura
        self.altura  = altura
        self._x = x
        self._y = y

    # Getter e Setter para interceptar os movimentos!
    @property
    def x(self): return self._x
    @x.setter
    def x(self, val): self._x = val

    @property
    def y(self): return self._y
    @y.setter
    def y(self, val): self._y = val

    @abstractmethod
    def alterar_proporcoes(self, nova_largura: int, nova_altura: int): pass

    @abstractmethod
    def renderizar(self) -> str: pass

    @abstractmethod
    def to_dict(self, idx: int) -> dict: pass

    def info(self):
        return (
            f"[{self.__class__.__name__}] "
            f"{self.largura}x{self.altura}px em ({self.x},{self.y})"
        )

class Texto(ElementoGrafico):
    def __init__(self, conteudo: str, fonte: str = "Arial", tamanho: int = 16, 
                 cor: str = "preto", largura: int = 200, altura: int = 50, x: int = 100, y: int = 100):
        super().__init__(largura, altura, x, y)
        self.conteudo = conteudo
        self.fonte    = fonte
        self.tamanho  = tamanho
        self.cor      = cor

    def alterar_proporcoes(self, nova_largura: int, nova_altura: int):
        self.largura, self.altura = nova_largura, nova_altura

    def renderizar(self) -> str:
        return f"[{self.conteudo}]"
        
    def to_dict(self, idx: int) -> dict:
        return {
            "id": idx, "tipo": "texto", "conteudo": self.conteudo,
            "largura": self.largura, "altura": self.altura, "x": self.x, "y": self.y
        }

class Imagem(ElementoGrafico):
    def __init__(self, nome: str, largura: int = 200, altura: int = 150, x: int = 150, y: int = 150):
        super().__init__(largura, altura, x, y)
        self.nome      = nome
        self.proporcao = largura / altura if altura else 1

    def alterar_proporcoes(self, nova_largura: int, nova_altura: int):
        self.largura, self.altura = nova_largura, nova_altura

    def renderizar(self) -> str:
        return f"[IMG] {self.nome}"
        
    def to_dict(self, idx: int) -> dict:
        return {
            "id": idx, "tipo": "imagem", "conteudo": self.nome,
            "largura": self.largura, "altura": self.altura, "x": self.x, "y": self.y
        }
    

class GrupoElementos(ElementoGrafico):
    def __init__(self):
        super().__init__(0, 0, x=0, y=0)
        self.elementos = []

    def adicionar(self, elemento):
        self.elementos.append(elemento)

    def remover(self, elemento):
        if elemento in self.elementos:
            self.elementos.remove(elemento)

    @property
    def x(self): return self._x
    @x.setter
    def x(self, novo_x):
        delta = novo_x - self._x
        self._x = novo_x
        # Se eu movo o grupo para a direita, todos os filhos andam para a direita juntos!
        for el in self.elementos: el.x += delta  

    @property
    def y(self): return self._y
    @y.setter
    def y(self, novo_y):
        delta = novo_y - self._y
        self._y = novo_y
        for el in self.elementos: el.y += delta  

    def alterar_proporcoes(self, nova_largura, nova_altura): pass

    def renderizar(self):
        return "\n".join([el.renderizar() for el in self.elementos])
        
    def to_dict(self, idx: int) -> dict:
        return {
            "id": idx, "tipo": "grupo",
            "elementos": [el.to_dict(i) for i, el in enumerate(self.elementos)],
            "x": self.x, "y": self.y
        }