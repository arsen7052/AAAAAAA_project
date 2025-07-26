import pygame
import sys
import random
import points_obj
from pygame.locals import *

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Игра с Яной")

# Цвета
WHITE = (255, 255, 255)
YELLOW = (255, 215, 0)
BROWN = (139, 69, 19)
GREEN = (50, 205, 50)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
BUTTON_COLOR = (100, 150, 255)

# Шрифт
font = pygame.font.SysFont("Arial", 24)
button_font = pygame.font.SysFont("Arial", 30)

# Загрузка изображений
YANA_IMG = pygame.image.load("yana.png")
SUN_IMG = pygame.image.load("sun.png")
HOUSE_IMG = pygame.image.load("house.png")
FLOWER_IMG = pygame.image.load("flower.png")
HOME_IMG = pygame.image.load("home.png")  # маленькое изображение дома
SQURE_IMG = pygame.image.load("squre.png")
CIRCLE_IMG = pygame.image.load("circle.png")

RED_IMG = pygame.image.load("red.png")
GREEN_IMG = pygame.image.load("green.png")
BLUE_IMG = pygame.image.load("blue.png")
YELLOW_IMG = pygame.image.load("yellow.png")
GREEN_IMG = pygame.transform.scale(GREEN_IMG, (100, 288))
BLUE_IMG = pygame.transform.scale(BLUE_IMG, (100, 260))
YELLOW_IMG = pygame.transform.scale(YELLOW_IMG, (100, 300))
RED_IMG = pygame.transform.scale(RED_IMG, (100, 344))
SP_IMG = [RED_IMG, GREEN_IMG, BLUE_IMG, YELLOW_IMG]

# Масштабирование
YANA_IMG = pygame.transform.scale(YANA_IMG, (200, 200))
SUN_IMG = pygame.transform.scale(SUN_IMG, (200, 200))
HOUSE_IMG = pygame.transform.scale(HOUSE_IMG, (200, 200))
FLOWER_IMG = pygame.transform.scale(FLOWER_IMG, (200, 200))
HOME_IMG = pygame.transform.scale(HOME_IMG, (60, 60))
SQURE_IMG = pygame.transform.scale(SQURE_IMG, (200, 200))
CIRCLE_IMG = pygame.transform.scale(CIRCLE_IMG, (200, 200))

# Звуки
applause_sound = pygame.mixer.Sound("applause.wav")

# Переменные
current_round = 0
drawing = False
points_left = []
points_right = []
middle_line_x = WIDTH // 2

class Shape:
    def __init__(self, shape_type, color, x, y, size=50):
        self.shape_type = shape_type  # 'circle', 'square', 'triangle'
        self.color = color
        self.x = x
        self.y = y
        self.size = size
        self.selected = False
        self.original_pos = (x, y)
    
    def draw(self, surface):
        if self.shape_type == 'circle':
            pygame.draw.circle(surface, self.color, (self.x, self.y), self.size)
            if self.selected:
                pygame.draw.circle(surface, BLACK, (self.x, self.y), self.size + 5, 2)
        elif self.shape_type == 'square':
            rect = pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)
            pygame.draw.rect(surface, self.color, rect)
            if self.selected:
                self.size+=5
                rect = pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)
                pygame.draw.rect(surface, BLACK, rect,2)
                self.size-=5
        elif self.shape_type == 'triangle':
            points = [
                (self.x, self.y - self.size),
                (self.x - self.size, self.y + self.size),
                (self.x + self.size, self.y + self.size)
            ]
            pygame.draw.polygon(surface, self.color, points)
        
            if self.selected:
                self.size+=5
                points = [
                (self.x, self.y - self.size),
                (self.x - self.size-5, self.y + self.size),
                (self.x + self.size, self.y + self.size)
            ]
                pygame.draw.polygon(surface, BLACK, points,2)
                self.size-=5
    
    def is_clicked(self, pos):
        if self.shape_type == 'circle':
            distance = ((pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2) ** 0.5
            return distance <= self.size
        elif self.shape_type == 'square':
            return (self.x - self.size <= pos[0] <= self.x + self.size and 
                    self.y - self.size <= pos[1] <= self.y + self.size)
        elif self.shape_type == 'triangle':
            # Простая проверка для треугольника
            return (abs(pos[0] - self.x) <= self.size and 
                    self.y - self.size <= pos[1] <= self.y + self.size)

def draw_text(text, y):
    lines = text.splitlines()
    for i, line in enumerate(lines):
        txt = font.render(line, True, BLACK)
        screen.blit(txt, (20, y + i * 30))

def reset_drawing():
    global points_left, points_right, drawing
    points_left.clear()
    points_right.clear()
    drawing = False

def play_applause():
    applause_sound.play()

def show_balloons():
    balloons = []
    for _ in range(20):
        x = random.randint(0, WIDTH)
        y = random.randint(-HEIGHT, -50)
        balloon = SP_IMG[random.randint(0,3)]
        balloons.append([x, y, balloon])

    clock = pygame.time.Clock()
    running = True
    while running:
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for b in balloons:
                    dist = ((mx - b[0]+b[2].get_width())**2 + (my - b[1]+b[2].get_height()/2)**2)**0.5
                    if dist < 40:
                        balloons.remove(b)
                        break

        # Движение шаров
        for b in balloons:
            b[1] += 3
            screen.blit(b[2], (b[0], b[1]))

        pygame.display.flip()
        clock.tick(60)

        if not balloons:
            pygame.time.wait(2000)
            running = False

def game_loop(image):
    global current_round, drawing
    reset_drawing()
    clock = pygame.time.Clock()
    running = True
    is_drawing = False  # Текущее состояние рисования

    while running:
        screen.fill(WHITE)

        # Отображение Яны
        screen.blit(YANA_IMG, (WIDTH - 180, 0))

        # Центральная линия
        pygame.draw.line(screen, BLACK, (middle_line_x, 0), (middle_line_x, HEIGHT), 2)

        # Объект для обводки
        img_rect = image.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(image, img_rect.topleft)

        # Рисование линий
        for point in points_left:
            pygame.draw.circle(screen, BLACK, point, 2)
        for point in points_right:
            pygame.draw.circle(screen, BLACK, point, 2)

        # Кнопка "Готово"
        button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 50)
        pygame.draw.rect(screen, BUTTON_COLOR, button_rect)
        txt = button_font.render("Готово", True, WHITE)
        txt_rect = txt.get_rect(center=button_rect.center)
        screen.blit(txt, txt_rect)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if button_rect.collidepoint(pos):
                    running = False  # Завершение раунда
                else:
                    is_drawing = True
            elif event.type == pygame.MOUSEBUTTONUP:
                is_drawing = False

        # Плавное рисование при удержании мыши
        if is_drawing:
            pos = pygame.mouse.get_pos()
            x, y = pos

            # Ограничение области рисования вокруг изображения
            distance_to_center = ((x - WIDTH//2)**2 + (y - HEIGHT//2)**2)**0.5
            if distance_to_center < 400:
                mirrored_point = (middle_line_x * 2 - x, y)

                if x < middle_line_x:  # Левая сторона
                    points_left.append((x, y))
                    points_right.append(mirrored_point)
                else:  # Правая сторона
                    points_right.append((x, y))
                    points_left.append(mirrored_point)

                # Однократное рисование круга
                pygame.draw.circle(screen, BLACK, (x, y), 2)
                pygame.draw.circle(screen, BLACK, mirrored_point, 2)

        pygame.display.flip()
        clock.tick(60)

def calculate_accuracy(points, number):
    """Вычисляет процент правильности по точкам."""
    kol = 0
    for i in points:
        for j in points_obj.points()[number]:
            if distance(i,j) < 7:
                kol += 1
                break
    try:
        return round(kol/len(points)*100, 1)
    except:
        return 0


def distance(p1, p2):
    """Расстояние между двумя точками."""
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

def shapes_game():
    global current_round
    
    # Начальные фигуры
    shapes_order = [
        [('circle', RED), ('triangle', BLUE), ('square', GREEN)],
        [('circle', RED), ('triangle', BLUE), ('square', GREEN), ('triangle', BLACK)],
        [('circle', RED), ('triangle', BLUE), ('square', GREEN), ('triangle', BLACK), ('square', ORANGE)]
    ]
    
    current_shapes = []
    selected_shapes = []
    round_completed = False
    message = ""
    
    for round_num in range(3):
        # Создаем фигуры для текущего раунда
        current_shapes = []
        correct_order = shapes_order[round_num]
        
        # Верхний ряд - правильный порядок
        for i, (shape_type, color) in enumerate(correct_order):
            x = WIDTH // (len(correct_order) + 1) * (i + 1)
            current_shapes.append(Shape(shape_type, color, x, 150))
        
        # Нижний ряд - перемешанный порядок
        shuffled_order = correct_order.copy()
        random.shuffle(shuffled_order)
        
        # Проверяем условия для черного треугольника и оранжевого квадрата
        if round_num >= 1:
            # Черный треугольник не рядом с синим
            blue_index = next(i for i, (t, c) in enumerate(shuffled_order) if c == BLUE)
            black_index = next(i for i, (t, c) in enumerate(shuffled_order) if c == BLACK)
            if abs(blue_index - black_index) == 1:
                # Меняем местами с другим элементом
                swap_with = (black_index + 1) % len(shuffled_order)
                shuffled_order[black_index], shuffled_order[swap_with] = shuffled_order[swap_with], shuffled_order[black_index]
        
        if round_num >= 2:
            # Оранжевый квадрат не рядом с зеленым квадратом
            green_index = next(i for i, (t, c) in enumerate(shuffled_order) if c == GREEN)
            orange_index = next(i for i, (t, c) in enumerate(shuffled_order) if c == ORANGE)
            if abs(green_index - orange_index) == 1:
                # Меняем местами с другим элементом
                swap_with = (orange_index + 1) % len(shuffled_order)
                shuffled_order[orange_index], shuffled_order[swap_with] = shuffled_order[swap_with], shuffled_order[orange_index]
        
        for i, (shape_type, color) in enumerate(shuffled_order):
            x = WIDTH // (len(shuffled_order) + 1) * (i + 1)
            current_shapes.append(Shape(shape_type, color, x, 450))
        
        selected_shapes = []
        round_completed = False
        
        # Сообщение с инструкцией
        if round_num == 0:
            message = "Наведи порядок в фигурках!\nСоедини их в правильном порядке."
        elif round_num == 1:
            message = "Отлично! Теперь добавлен черный треугольник.\nОн не должен быть рядом с синим."
        else:
            message = "Превосходно! Добавлен оранжевый квадрат.\nОн не должен быть рядом с зеленым."
        
        clock = pygame.time.Clock()
        running = True
        
        while running and not round_completed:
            screen.fill(WHITE)
            
            # Рисуем все фигуры
            for shape in current_shapes:
                shape.draw(screen)
            
            # Рисуем линии между выбранными фигурами

            
            for i in range(len(selected_shapes)):
                if len(selected_shapes[i])==2:
                    pygame.draw.line(screen, BLACK, 
                                    (selected_shapes[i][0].x, selected_shapes[i][0].y),
                                    (selected_shapes[i][1].x, selected_shapes[i][1].y), 2)
            
            # Отображаем сообщение
            draw_text(message, 20)
            
            # Отображаем Яну
            screen.blit(YANA_IMG, (WIDTH - 200, HEIGHT - 200))
            

            # Проверка правильности порядка
            if len(selected_shapes) == len(correct_order) and len(selected_shapes[-1]) == 2:
                correct = False
                for i in selected_shapes:
                    if (i[0].shape_type == i[1].shape_type and
                        i[0].color == i[1].color):
                        correct = True
                    else:
                        correct = False
                        break
        
                if correct:
                    for shape in current_shapes:
                        shape.draw(screen)
                    round_completed = True
                    for i in range(len(selected_shapes)):
                        if len(selected_shapes[i])==2:
                            pygame.draw.line(screen, BLACK, 
                                        (selected_shapes[i][0].x, selected_shapes[i][0].y),
                                        (selected_shapes[i][1].x, selected_shapes[i][1].y), 2)
                    pygame.display.flip()
                    message = "Молодец! Все правильно!\nЯна благодарит тебя!"
                    pygame.time.wait(1000)
                    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for shape in current_shapes:
                        if shape.is_clicked(pos):
                            shape.selected = not shape.selected
                            if shape.selected and shape not in selected_shapes:
                                if len(selected_shapes)==0 or len(selected_shapes[-1])==2:
                                    selected_shapes.append([shape])
                                else: 
                                    selected_shapes[-1].append(shape)
                            elif not shape.selected:
                                for i in selected_shapes:
                                    if shape == i[0] or shape == i[1]:
                                        if shape == i[0]:
                                            i[1].selected = False
                                        else:
                                            i[0].selected = False
                                        selected_shapes.remove(i)                                           
                                        break
            pygame.display.flip()
            clock.tick(60)
            
        
        # Показываем сообщение о завершении раунда
        screen.fill(WHITE)
        draw_text(message, HEIGHT // 2 - 50)
        screen.blit(YANA_IMG, (WIDTH - 200, HEIGHT - 200))
        pygame.display.flip()
        pygame.time.wait(2000)
    

# Основной цикл игры
def main():
    # Первая часть игры (ваш оригинальный код)
    for i in range(4):
        screen.fill(WHITE)
        pygame.display.flip()
        pygame.time.wait(2000)

        if i == 0:
            game_loop(SQURE_IMG)
        elif i == 1:
            game_loop(CIRCLE_IMG)
        elif i == 2:
            game_loop(SUN_IMG)
        elif i == 3:
            game_loop(HOUSE_IMG)

        # Процент правильности
        accuracy = calculate_accuracy(points_left, i)
        screen.fill(WHITE)
        screen.blit(YANA_IMG, (WIDTH - 160, 0))
        draw_text(f"Ты выполнил {accuracy}% правильно!", 20)
        pygame.display.flip()
        pygame.time.wait(2000)

        # Сообщение поддержки
        screen.fill(WHITE)
        screen.blit(YANA_IMG, (WIDTH - 160, 0))
        pygame.display.flip()
        pygame.time.wait(2000)

    # Вторая часть игры - с фигурками
    shapes_game()

    # Концовка с шариками и аплодисментами
    play_applause()
    show_balloons()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()