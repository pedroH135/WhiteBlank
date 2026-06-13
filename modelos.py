from elementos import (
    ElementoGrafico,
    Texto,
    Imagem,
    GrupoElementos
)
from factory import ElementoFactory
from banco import conectar
from command import HistoricoComandos


class Template:
    def __init__(self, nome: str, elementos: list, criador):
        self.nome      = nome
        self.elementos = elementos
        self.criador   = criador
        self.estado    = "privado"

    def publicar(self):
        self.estado = "publicado"
        print(f"  + Template '{self.nome}' publicado na biblioteca!")

    def info(self):
        print(f"  {self.nome} [{self.estado}] -- {self.criador.email} -- {len(self.elementos)} elem.")


class Slide:

    def __init__(self, ordem):

        self.ordem = ordem

        self.elementos = []

        self.historico = HistoricoComandos()

    def adicionar_elemento(self, el):

        self.elementos.append(el)

        print(
            f"  + {el.info()} "
            f"adicionado ao Slide {self.ordem}"
        )

    def criar_texto(self, conteudo, fonte="Arial", tamanho=16, cor="preto", x=100, y=100):
        texto = ElementoFactory.criar_elemento(
            "texto", conteudo=conteudo, fonte=fonte, tamanho=tamanho, cor=cor, x=x, y=y
        )
        from command import AdicionarElementoCommand
        cmd = AdicionarElementoCommand(self, texto)
        self.historico.executar(cmd)
        return texto
    
    def criar_imagem(self, nome, largura=200, altura=150, x=150, y=150):
        imagem = ElementoFactory.criar_elemento(
            "imagem", nome=nome, largura=largura, altura=altura, x=x, y=y
        )
        from command import AdicionarElementoCommand
        cmd = AdicionarElementoCommand(self, imagem)
        self.historico.executar(cmd)
        return imagem

    def desfazer(self):
        self.historico.desfazer()

    def refazer(self):
        self.historico.refazer()
    
    def desagrupar_elemento(self, indice: int):
        if not (0 <= indice < len(self.elementos)):
            print("  x Índice inválido.")
            return

        elemento = self.elementos[indice]

        if not isinstance(elemento, GrupoElementos):
            print("  x O elemento selecionado não é um grupo.")
            return

        # Remove o grupo da posição atual
        self.elementos.pop(indice)

        # Reinsere os filhos na mesma posição, mantendo ordem
        for i, filho in enumerate(elemento.elementos):
            self.elementos.insert(indice + i, filho)

        print(f"  + {len(elemento.elementos)} elemento(s) desagrupados.")


    def remover_elemento(self, idx):

        if 0 <= idx < len(self.elementos):

            from command import RemoverElementoCommand

            elemento = self.elementos[idx]

            cmd = RemoverElementoCommand(
                self,
                elemento
            )

            self.historico.executar(cmd)

        else:

            print("Indice invalido")


    def agrupar_elementos(self, indices):

        grupo = GrupoElementos()

        elementos = []

        for i in sorted(indices, reverse=True):

            elementos.append(
                self.elementos.pop(i)
            )

        for elemento in reversed(elementos):

            grupo.adicionar(elemento)

        self.elementos.append(grupo)

        print(
            f"  + Grupo criado com "
            f"{len(grupo.elementos)} elemento(s)"
        )

        return grupo

    def salvar_como_template(self, nome: str, criador) -> Template:

        def serializar_elemento(el):
            if isinstance(el, Texto):
                return {
                    "tipo": "texto",
                    "conteudo": el.conteudo,
                    "fonte": el.fonte,
                    "tamanho": el.tamanho,
                    "cor": el.cor,
                    "largura": el.largura,
                    "altura": el.altura,
                }
            elif isinstance(el, Imagem):
                return {
                    "tipo": "imagem",
                    "nome": el.nome,
                    "largura": el.largura,
                    "altura": el.altura,
                }
            elif isinstance(el, GrupoElementos):
                return {
                    "tipo": "grupo",
                    "elementos": [serializar_elemento(filho) for filho in el.elementos],
                }

        dados = [serializar_elemento(el) for el in self.elementos]
        t = Template(nome, dados, criador)
        print(f"  + Template '{nome}' criado com {len(dados)} elem.")
        return t

    def aplicar_template(self, t: Template):

        from command import AdicionarElementoCommand

        for d in t.elementos:

            el = ElementoFactory.criar_elemento(
                d["tipo"],
                **d
            )

            cmd = AdicionarElementoCommand(
                self,
                el
            )

            self.historico.executar(cmd)

        print(f"  + Template '{t.nome}' aplicado.")

    def renderizar(self):
        print("  " + "-" * 52)
        print(f"  SLIDE {self.ordem}  --  {len(self.elementos)} elemento(s)")
        print("  " + "-" * 52)
        if not self.elementos:
            print("  (vazio)")
            return
        for i, el in enumerate(self.elementos):
            print(f"\n  [{i}] {el.info()}")
            print(el.renderizar())

    def desfazer(self):
        self.historico.desfazer()

    def refazer(self):
        self.historico.refazer()


class Projeto:
    def __init__(self, nome: str, dono):
        self.nome    = nome
        self.dono    = dono
        self.slides: list[Slide] = [Slide(1)]
        self.membros: list       = [dono]

    def adicionar_slide(self) -> Slide:
        s = Slide(len(self.slides) + 1)
        self.slides.append(s)
        print(f"  + Slide {s.ordem} adicionado.")
        return s

    def remover_slide(self, idx: int):
        if len(self.slides) <= 1:
            print("  x Projeto precisa ter ao menos 1 slide.")
        elif 0 <= idx < len(self.slides):
            s = self.slides.pop(idx)
            for i, sl in enumerate(self.slides): sl.ordem = i + 1
            print(f"  - Slide {s.ordem} removido.")
        else:
            print("  x Indice invalido.")

    def adicionar_membro(self, u):
        if u in self.membros:
            print(f"  x {u.email} ja e membro.")
        else:
            self.membros.append(u)
            print(f"  + {u.email} adicionado ao projeto.")

    def remover_membro(self, u):
        if u is self.dono:
            print("  x O dono nao pode ser removido.")
        elif u in self.membros:
            self.membros.remove(u)
            print(f"  - {u.email} removido.")
        else:
            print(f"  x {u.email} nao e membro.")

    def info(self):
        print("  " + "-" * 52)
        print(f"  Projeto : {self.nome}")
        print(f"  Dono    : {self.dono.email}")
        print(f"  Slides  : {len(self.slides)}")
        print(f"  Membros : {', '.join(m.email for m in self.membros)}")


def salvar(self):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO projetos(
        nome,
        dono_id
    )

    VALUES (?, ?)

    """, (

        self.nome,

        self.dono.id
    ))

    conn.commit()

    conn.close()