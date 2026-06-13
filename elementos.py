from abc import ABC, abstractmethod

class ElementoGrafico(ABC):
    def __init__(self, largura: int, altura: int, x: int = 100, y: int = 100):
        self.largura = largura
        self.altura  = altura
        self.x       = x  # Alinhado com o banco.py
        self.y       = y  # Alinhado com o banco.py

    @abstractmethod
    def alterar_proporcoes(self, nova_largura: int, nova_altura: int):
        pass

    @abstractmethod
    def renderizar(self) -> str:
        pass

    def info(self):
        return (
            f"[{self.__class__.__name__}] "
            f"{self.largura}x{self.altura}px em ({self.x},{self.y})"
        )

class Texto(ElementoGrafico):
    def __init__(self, conteudo: str, fonte: str = "Arial",
                 tamanho: int = 16, cor: str = "preto",
                 largura: int = 200, altura: int = 50,
                 x: int = 100, y: int = 100):
        super().__init__(largura, altura, x, y)
        self.conteudo = conteudo
        self.fonte    = fonte
        self.tamanho  = tamanho
        self.cor      = cor

    def alterar_proporcoes(self, nova_largura: int, nova_altura: int):
        escala = nova_altura / self.altura if self.altura else 1
        self.tamanho = max(8, int(self.tamanho * scala))
        self.largura, self.altura = nova_largura, nova_altura

    def renderizar(self) -> str:
        b = "-" * (len(self.conteudo) + 4)
        return (f"  +{b}+\n"
                f"  |  {self.conteudo}  |  [{self.fonte}, {self.tamanho}pt, {self.cor}]\n"
                f"  +{b}+")

class Imagem(ElementoGrafico):
    def __init__(self, nome: str, largura: int = 200, altura: int = 150,
                 x: int = 150, y: int = 150):
        super().__init__(largura, altura, x, y)
        self.nome      = nome
        self.proporcao = largura / altura if altura else 1

    def alterar_proporcoes(self, nova_largura: int, nova_altura: int):
        self.largura, self.altura = nova_largura, nova_altura

    def renderizar(self) -> str:
        w = max(20, min(self.largura // 10, 36))
        return (f"  +{'='*w}+\n"
                f"  | {'[IMG] ' + self.nome:^{w-1}}|\n"
                f"  | {f'{self.largura}x{self.altura}px':^{w-1}}|\n"
                f"  +{'='*w}+")
    

class GrupoElementos(ElementoGrafico):

    def __init__(self):

        super().__init__(0, 0)

        self.elementos = []

    def adicionar(self, elemento):

        self.elementos.append(elemento)

    def remover(self, elemento):

        if elemento in self.elementos:

            self.elementos.remove(elemento)

    def alterar_proporcoes(
        self,
        nova_largura,
        nova_altura
    ):

        for elemento in self.elementos:

            elemento.alterar_proporcoes(
                nova_largura,
                nova_altura
            )

    def renderizar(self):

        resultado = "GRUPO:\n"

        for elemento in self.elementos:

            resultado += elemento.renderizar()
            resultado += "\n"

        return resultado
    
    def info(self):

        return (
            f"[Grupo] "
            f"{len(self.elementos)} elemento(s)"
        )