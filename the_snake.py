
from random import choice

import pygame as pg


SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

SPEED = 20

screen = None
clock = None


class GameObject:
    """Базовый класс игровых объектов."""

    def __init__(self, body_color=BOARD_BACKGROUND_COLOR):
        self.position = (
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2
        )
        self.body_color = body_color

    def draw_cell(self, position):
        """Отрисовать клетку игрового объекта."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Отрисовать игровой объект."""
        self.draw_cell(self.position)


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self, body_color=APPLE_COLOR, occupied_positions=None):
        super().__init__(body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=None):
        """Выбрать свободную позицию для яблока."""
        if occupied_positions is None:
            occupied_positions = []

        occupied = set(occupied_positions)

        free_positions = [
            (x * GRID_SIZE, y * GRID_SIZE)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x * GRID_SIZE, y * GRID_SIZE) not in occupied
        ]

        if not free_positions:
            return False

        self.position = choice(free_positions)
        return True


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self, body_color=SNAKE_COLOR):
        super().__init__(body_color)
        self.reset()

    def update_direction(self, new_direction=None):
        """Обновить направление движения."""
        if new_direction is not None:
            direction_x, direction_y = self.direction
            opposite = (-direction_x, -direction_y)

            if new_direction != opposite:
                self.direction = new_direction

    def move(self):
        """Переместить змейку на одну клетку."""
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction

        new_x = (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT

        new_head = (new_x, new_y)
        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

        self.position = new_head

    def get_head_position(self):
        """Получить координаты головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбросить змейку в начальное состояние."""
        self.length = 1
        self.position = (
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2
        )
        self.positions = [self.position]
        self.direction = RIGHT
        self.last = None

    def draw(self):
        """Отрисовать змейку и удалить старый хвост."""
        if self.last is not None:
            rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)

        for position in self.positions:
            self.draw_cell(position)


def handle_keys(game_object):
    """Обработать нажатия клавиш."""
    directions = {
        (pg.K_UP, LEFT): UP,
        (pg.K_UP, RIGHT): UP,
        (pg.K_UP, UP): UP,
        (pg.K_DOWN, LEFT): DOWN,
        (pg.K_DOWN, RIGHT): DOWN,
        (pg.K_DOWN, DOWN): DOWN,
        (pg.K_LEFT, UP): LEFT,
        (pg.K_LEFT, DOWN): LEFT,
        (pg.K_LEFT, LEFT): LEFT,
        (pg.K_RIGHT, UP): RIGHT,
        (pg.K_RIGHT, DOWN): RIGHT,
        (pg.K_RIGHT, RIGHT): RIGHT,
    }

    available_keys = {key for key, _ in directions}
    new_direction = game_object.direction

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit

        if event.type != pg.KEYDOWN:
            continue

        if event.key == pg.K_ESCAPE:
            pg.quit()
            raise SystemExit

        if event.key in available_keys:
            new_direction = directions.get(
                (event.key, game_object.direction),
                game_object.direction
            )

    return new_direction


def main():
    """Запустить главный игровой цикл."""
    global screen, clock

    pg.init()
    screen = pg.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )
    pg.display.set_caption('Змейка')
    clock = pg.time.Clock()

    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)

    screen.fill(BOARD_BACKGROUND_COLOR)
    snake.draw()
    apple.draw()
    pg.display.update()

    while True:
        new_direction = handle_keys(snake)
        snake.update_direction(new_direction)

        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1

            if not apple.randomize_position(snake.positions):
                snake.draw()
                pg.display.update()
                print('Победа! Всё поле заполнено.')
                pg.quit()
                return

        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        snake.draw()
        apple.draw()

        pg.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
