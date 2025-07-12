import pygame
import sys
import random

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
BUTTON_COLOR = (100, 150, 255)

# Радиус солнца
SUN_RADIUS = 100  # Радиус солнца в пикселях

# Шрифт
font = pygame.font.SysFont("Arial", 24)
button_font = pygame.font.SysFont("Arial", 30)

# Загрузка изображений
YANA_IMG = pygame.image.load("yana.png")
SUN_IMG = pygame.image.load("sun.png")
HOUSE_IMG = pygame.image.load("house.png")
FLOWER_IMG = pygame.image.load("flower.png")
HOME_IMG = pygame.image.load("home.png")  # маленькое изображение дома

# Масштабирование
YANA_IMG = pygame.transform.scale(YANA_IMG, (150, 200))
SUN_IMG = pygame.transform.scale(SUN_IMG, (200, 200))
HOUSE_IMG = pygame.transform.scale(HOUSE_IMG, (200, 200))
FLOWER_IMG = pygame.transform.scale(FLOWER_IMG, (200, 200))
HOME_IMG = pygame.transform.scale(HOME_IMG, (60, 60))

# Звуки
applause_sound = pygame.mixer.Sound("applause.wav")  # скачайте или создайте такой файл

# Переменные
current_round = 0
drawing = False
points_left = []
points_right = []
middle_line_x = WIDTH // 2

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
        r = random.randint(20, 40)
        color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        balloons.append([x, y, r, color])

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
                    dist = ((mx - b[0])**2 + (my - b[1])**2)**0.5
                    if dist < b[2]:
                        balloons.remove(b)
                        break

        # Движение шаров
        for b in balloons:
            b[1] += 3
            pygame.draw.circle(screen, b[3], (b[0], b[1]), b[2])
            pygame.draw.line(screen, BLACK, (b[0], b[1]+b[2]), (b[0], b[1]-10), 2)

        pygame.display.flip()
        clock.tick(60)

        if not balloons:
            pygame.time.wait(2000)
            running = False

    return

def game_loop(image, instruction):
    global current_round, drawing
    reset_drawing()
    clock = pygame.time.Clock()
    running = True

    is_drawing = False  # Текущее состояние рисования

    while running:
        screen.fill(WHITE)

        # Отображение Яны
        screen.blit(YANA_IMG, (WIDTH - 160, 0))

        # Инструкция
        draw_text(instruction, 20)

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
            if distance_to_center < SUN_RADIUS + 50:
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

def calculate_accuracy(points):
    """
    Вычисляет процент правильности по точкам.
    """
    total_points = len(points)
    if total_points == 0:
        return 0

    # Пример: считаем, что правильные точки должны быть близко к контуру солнца
    correct_points = sum(
        1 for p in points 
        if SUN_RADIUS - 5 <= distance(p, (WIDTH//2, HEIGHT//2)) <= SUN_RADIUS + 5
    )
    accuracy = (correct_points / total_points) * 100
    return round(accuracy, 2)

def distance(p1, p2):
    """Расстояние между двумя точками."""
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

def draw_path_screen():
    path_running = True
    button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 100, 200, 50)

    while path_running:
        screen.fill(WHITE)

        # Точка старта (Яна)
        start_pos = (100, HEIGHT - 100)
        end_pos = (WIDTH - 100, 100)

        # Статичный путь
        path_points = [
            start_pos,
            (start_pos[0] + 100, start_pos[1] - 50),
            (end_pos[0] - 100, end_pos[1] + 50),
            end_pos
        ]

        # Рисуем путь
        pygame.draw.lines(screen, BLACK, False, path_points, 3)

        # Препятствия
        obstacles = [(150, 150), (300, 250), (450, 350)]  # Фиксированные препятствия
        for obs in obstacles:
            pygame.draw.circle(screen, RED, obs, 10)

        # Яна и дом
        screen.blit(YANA_IMG, (start_pos[0]-75, start_pos[1]-200))
        screen.blit(HOME_IMG, (end_pos[0]-30, end_pos[1]-30))

        # Кнопка "Готово"
        pygame.draw.rect(screen, BUTTON_COLOR, button_rect)
        txt = button_font.render("Готово", True, WHITE)
        txt_rect = txt.get_rect(center=button_rect.center)
        screen.blit(txt, txt_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    path_running = False

        pygame.display.flip()

# === Основная логика ===
intro_text = """Привет, я Яна, мне нужна твоя помощь.
Мне нужно попасть домой, для этого ты должен
пройти игры, и тогда препятствия исчезнут."""

round_texts = [
    "Тебе надо обвести солнышко.",
    "Теперь тебе нужно обвести домик.",
    "Теперь тебе нужно обвести цветок."
]

end_texts = [
    "Молодец, продолжай в том же духе!",
    "У тебя отлично получается!",
    "Ты справился! Так держать!"
]

clock = pygame.time.Clock()

# Вступление
intro_running = True
while intro_running:
    screen.fill(WHITE)
    screen.blit(YANA_IMG, (WIDTH - 160, 0))
    draw_text(intro_text, 20)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            intro_running = False

# Экран пути
draw_path_screen()

# Игровые раунды
for i in range(3):
    screen.fill(WHITE)
    screen.blit(YANA_IMG, (WIDTH - 160, 0))
    draw_text(round_texts[i], 20)
    pygame.display.flip()
    pygame.time.wait(2000)

    if i == 0:
        game_loop(SUN_IMG, round_texts[i])
    elif i == 1:
        game_loop(HOUSE_IMG, round_texts[i])
    elif i == 2:
        game_loop(FLOWER_IMG, round_texts[i])

    # Процент правильности
    accuracy = calculate_accuracy(points_left)
    screen.fill(WHITE)
    screen.blit(YANA_IMG, (WIDTH - 160, 0))
    draw_text(f"Ты выполнил {accuracy}% правильно!", 20)
    pygame.display.flip()
    pygame.time.wait(2000)

    # Сообщение поддержки
    screen.fill(WHITE)
    screen.blit(YANA_IMG, (WIDTH - 160, 0))
    draw_text(end_texts[i], 20)
    pygame.display.flip()
    pygame.time.wait(2000)

# Концовка с шариками и аплодисментами
play_applause()
show_balloons()

pygame.quit()
sys.exit()