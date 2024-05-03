from itertools import product
from random import *


# исключения
class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardWrongShipException(BoardException):
    pass


class ErrorEnter(ValueError):
    def __str__(self):
        return 'Ошибка ввода'


def game():
    Game()


class Player:
    def __init__(self, b, b_2):
        self.board = b
        self.b_2 = b_2

    def ask(self):
        pass

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.b_2.shot(target)

            except Exception as ex:
                print(ex)
                continue
            return repeat


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход AI: {d.x + 1} - {d.y + 1}')
        return d


class User(Player):
    def ask(self):
        while True:
            coord = input('Ваш ход: ').split()

            if len(coord) != 2:
                raise ErrorEnter()
            x, y = coord
            x = int(x)
            y = int(y)
            return Dot(x - 1, y - 1)


class Ship:
    """
    Принимает начальное положение корабля Dot(x, y) (левый верхний угол)
    расположение r вертикально ('v') или горизонтально ('h')
    количество жизней (клеток) у корабля lf
    Dot:d
    str:r
    int:lf
    """

    def __init__(self, d, r='h', lf=1):
        if r != 'h' and r != 'v':
            raise ErrorEnter
        if r == 'h':
            self.ds = [Dot(i, j) for j in range(d.y, d.y + lf) for i in range(d.x, d.x + 1)]
        else:
            self.ds = [Dot(i, j) for j in range(d.y, d.y + 1) for i in range(d.x, d.x + lf)]
        self.lf = lf
        self.r = r
        self.life = lf

    @property
    def dots(self):
        return self.ds

    def shoot(self, d):
        return d in self.ds

    def __repr__(self):
        return f'Корабль длины {self.lf}, расположен {"вертикально" if self.r == "v" else "горизонатльно"}'


class Board:
    def __init__(self, hid=False):
        self.pole = [['□'] * 6 for _ in range(6)]
        self.ships = []
        self.busy = []
        self.count = 0
        self.hid = hid

    def __repr__(self):
        p = "\n".join(
            ['\t|\t'.join([' '] + [str(i) for i in range(1, 7)])] + ["\t|\t".join([str(n + 1)] + i) for n, i in
                                                                     enumerate(self.pole)])
        return p.replace('■', '□') if self.hid else p

    def add_ship(self, sh, r=False):
        if any([d in self.busy for d in sh.ds]) or any([self.out(d) for d in sh.ds]):
            if r:
                print('Нельзя расположить корабль в данном месте')
            return False

        for d in sh.ds:
            if not self.hid:
                self.pole[d.x][d.y] = '■'
            self.busy.append(d)
        self.contour(sh)
        self.ships.append(sh)
        return True

    def contour(self, sh):
        for d in sh.ds:
            for i, j in product([-1, 0, 1], repeat=2):
                if self.out(Dot(d.x + i, d.y + j)):
                    continue
                if self.pole[d.x + i][d.y + j] not in ['🗷', '■']:
                    if not self.hid:
                        self.pole[d.x + i][d.y + j] = '•'
                    self.busy.append(Dot(d.x + i, d.y + j))

    def clear_contour(self):
        for i in range(6):
            for j in range(6):
                if self.pole[i][j] == '•':
                    self.pole[i][j] = '□'

    @staticmethod
    def out(d):
        return not (0 <= d.x < 6 and 0 <= d.y < 6)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()
        if self.pole[d.x][d.y] in ['🗷', '•']:
            if self.hid:
                print('Вы уже стреляли в данную клетку, повторите ход!')

            return True

        for sh in self.ships:
            if sh.shoot(d):
                sh.life -= 1
                self.pole[d.x][d.y] = "🗷"
                if sh.life:
                    print('Корабль ранен!')
                    return True
                else:
                    print('Корабль убит!')
                    self.contour(sh)
                    self.count += 1
                    return True

        else:
            print('Промах')
            self.pole[d.x][d.y] = '•'
            return False

    def begin(self):
        self.busy = []


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Точка {self.x, self.y}'


class Game:
    def __init__(self):
        r = self.random_board()
        if r:
            pl_b = self.try_board(False)
        else:
            pl_b = self.user_board()
        ai_b = self.try_board(True)

        self.player = User(pl_b, ai_b)
        self.ai = AI(ai_b, pl_b)
        self.start()

    @staticmethod
    def user_board():
        sh = [3, 2, 2, 1, 1, 1, 1]
        board = Board(hid=False)
        for i in sh:
            print('Ваше поле')
            print(board)

            while True:
                try:
                    s = Ship(Dot(int(input('ведите одно целое число (номер строки)')) - 1,
                                 int(input('ведите одно целое число (номер столбца)')) - 1),
                             r=input('ведите одну букву h (горизонтально) или v (вертикально)'), lf=i)
                except ValueError as ex:
                    print(f'Ошибка ввода, пожалуйста, следуйте инструкциям. "{ex}", ')
                    continue
                f = board.add_ship(s, r=True)
                if f:
                    break
        board.clear_contour()
        return board

    def try_board(self, h):
        sh = [3, 2, 2, 1, 1, 1, 1]
        board = Board(hid=h)
        for i in sh:
            tr = 0
            while True:
                tr += 1
                s = Ship(Dot(randint(0, 6), randint(0, 6)), r=choice(['v', 'h']), lf=i)
                f = board.add_ship(s)
                if f:
                    break
                if tr > 2000:
                    break
            if tr > 2000:
                self.try_board(h)
        board.clear_contour()

        return board

    @staticmethod
    def random_board():
        print('Игра "морской бой" имеет два режима расстановки кораблей\n')
        ans = input('Выберете вариант расстановки кораблей,\nсамостоятельно ([A]), случайным образом ([B])').upper()
        while ans != 'A' and ans != 'А' and ans != 'B' and ans != 'В':
            print(
                'Введите [A] или [B]!\nВыберете вариант расстановки кораблей,'
                '\nсамостоятельно ([A]), случайным образом ([B])')
            ans = input().upper()
        return True if ans == 'B' or ans == 'В' else False

    @staticmethod
    def greet():
        print('Приветствую Вас в игре "Морской бой"!\nДля выстрела напишите номер строки и номер столбца через пробел')

    def loop(self):
        num = 0
        while True:
            print('Ваше поле')
            print(self.player.board)
            print('Поле врага')
            print(self.ai.board)
            if num % 2 == 0:
                print('Ваш ход')
                x_y = self.player.move()
            else:
                print('Ход AI')
                x_y = self.ai.move()

            if not x_y:
                num += 1
            if self.ai.board.count == len(self.ai.board.ships):
                print('Вы победили!')
                break
            if self.player.board.count == len(self.player.board.ships):
                print('Компьютер победил!')
                break

    def start(self):
        self.greet()
        self.loop()


if __name__ == '__main__':
    game()
