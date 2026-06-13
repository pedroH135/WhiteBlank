from elementos import Texto, Imagem

class ElementoFactory:

    @staticmethod
    def criar_elemento(tipo, **dados):
        if tipo == "texto":
            return Texto(
                conteudo=dados.get("conteudo", ""),
                fonte=dados.get("fonte", "Arial"),
                tamanho=dados.get("tamanho", 16),
                cor=dados.get("cor", "preto"),
                largura=dados.get("largura", 200),
                altura=dados.get("altura", 50),
                x=dados.get("x", 100),
                y=dados.get("y", 100)
            )

        elif tipo == "imagem":
            return Imagem(
                nome=dados.get("nome", ""),
                largura=dados.get("largura", 200),
                altura=dados.get("altura", 150),
                x=dados.get("x", 150),
                y=dados.get("y", 150)
            )

        raise ValueError(f"Tipo de elemento inválido: {tipo}")