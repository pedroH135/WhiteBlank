from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def executar(self):
        pass

    @abstractmethod
    def desfazer(self):
        pass

class AdicionarElementoCommand(Command):
    def __init__(self, slide, elemento):
        self.slide = slide
        self.elemento = elemento

    def executar(self):
        self.slide.elementos.append(self.elemento)

    def desfazer(self):
        self.slide.elementos.remove(self.elemento)

class RemoverElementoCommand(Command):
    def __init__(self, slide, elemento):
        self.slide = slide
        self.elemento = elemento

    def executar(self):
        self.slide.elementos.remove(self.elemento)

    def desfazer(self):
        self.slide.elementos.append(self.elemento)

class MoverElementoCommand(Command):
    def __init__(self, elemento, x_antigo, y_antigo, x_novo, y_novo):
        self.elemento = elemento
        self.x_antigo = x_antigo
        self.y_antigo = y_antigo
        self.x_novo = x_novo
        self.y_novo = y_novo

    def executar(self):
        self.elemento.x = self.x_novo
        self.elemento.y = self.y_novo

    def desfazer(self):
        self.elemento.x = self.x_antigo
        self.elemento.y = self.y_antigo

class EditarConteudoCommand(Command):
    def __init__(self, elemento, conteudo_antigo, conteudo_novo):
        self.elemento = elemento
        self.conteudo_antigo = conteudo_antigo
        self.conteudo_novo = conteudo_novo

    def executar(self):
        self.elemento.conteudo = self.conteudo_novo

    def desfazer(self):
        self.elemento.conteudo = self.conteudo_antigo

class HistoricoComandos:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def executar(self, comando):
        comando.executar()
        self.undo_stack.append(comando)
        self.redo_stack.clear()

    def desfazer(self):
        if not self.undo_stack:
            return
        comando = self.undo_stack.pop()
        comando.desfazer()
        self.redo_stack.append(comando)

    def refazer(self):
        if not self.redo_stack:
            return
        comando = self.redo_stack.pop()
        comando.executar()
        self.undo_stack.append(comando)