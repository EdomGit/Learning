import math
import random
from typing import List, Tuple, Optional


class Ball:
    """Класс для представления шарика в игре."""
    
    def __init__(self, x: float, y: float, radius: float = 15, 
                 color: Tuple[int, int, int] = None, 
                 velocity: Tuple[float, float] = None):
        """
        Инициализация шарика.
        
        Args:
            x, y: Позиция шарика
            radius: Радиус шарика
            color: RGB цвет (r, g, b) от 0 до 255
            velocity: Вектор скорости (vx, vy)
        """
        self.x = x
        self.y = y
        self.radius = radius
        
        # Случайный цвет, если не указан
        if color is None:
            self.color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            )
        else:
            self.color = color
        
        # Случайная скорость, если не указана
        if velocity is None:
            speed = random.uniform(1, 3)
            angle = random.uniform(0, 2 * math.pi)
            self.velocity = (speed * math.cos(angle), speed * math.sin(angle))
        else:
            self.velocity = velocity
    
    def update(self, screen_width: int, screen_height: int, 
               friction: float = 0.98) -> None:
        """
        Обновление позиции шарика с учетом границ экрана.
        
        Args:
            screen_width: Ширина экрана
            screen_height: Высота экрана
            friction: Коэффициент трения (по умолчанию 0.98)
        """
        vx, vy = self.velocity
        
        # Применяем трение
        vx *= friction
        vy *= friction
        
        # Обновляем позицию
        self.x += vx
        self.y += vy
        
        # Отскок от границ (мягкий, чтобы не застревать)
        if self.x - self.radius < 0:
            self.x = self.radius
            vx = abs(vx) * 0.8
        elif self.x + self.radius > screen_width:
            self.x = screen_width - self.radius
            vx = -abs(vx) * 0.8
        
        if self.y - self.radius < 0:
            self.y = self.radius
            vy = abs(vy) * 0.8
        elif self.y + self.radius > screen_height:
            self.y = screen_height - self.radius
            vy = -abs(vy) * 0.8
        
        self.velocity = (vx, vy)
    
    def distance_to(self, other: 'Ball') -> float:
        """Вычисляет расстояние до другого шарика."""
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)
    
    def is_colliding(self, other: 'Ball') -> bool:
        """Проверяет, касается ли шарик другого шарика."""
        return self.distance_to(other) <= (self.radius + other.radius)
    
    def is_point_inside(self, x: float, y: float) -> bool:
        """Проверяет, находится ли точка внутри шарика."""
        dx = x - self.x
        dy = y - self.y
        return dx * dx + dy * dy <= self.radius * self.radius


class GameLogic:
    """Основной класс для управления игровой логикой."""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        """
        Инициализация игровой логики.
        
        Args:
            screen_width: Ширина игрового экрана
            screen_height: Высота игрового экрана
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.balls: List[Ball] = []
        self.inventory: List[Ball] = []  # Инвентарь для всасывания шариков
        
        # Зона удаления (правый верхний угол, например)
        self.delete_zone_size = 100  # Размер зоны удаления
        self.delete_zone_x = screen_width - self.delete_zone_size
        self.delete_zone_y = 0
        
        # Параметры всасывания
        self.suction_range = 100  # Радиус всасывания
        self.suction_active = False
        self.suction_mouse_pos = (0, 0)
    
    def add_ball(self, x: float = None, y: float = None, 
                 color: Tuple[int, int, int] = None) -> Ball:
        """
        Добавляет новый шарик на экран.
        
        Args:
            x, y: Позиция шарика (если None, случайная позиция)
            color: Цвет шарика (если None, случайный цвет)
        """
        if x is None:
            x = random.uniform(50, self.screen_width - 50)
        if y is None:
            y = random.uniform(50, self.screen_height - 50)
        
        ball = Ball(x, y, color=color)
        self.balls.append(ball)
        return ball
    
    def update(self) -> None:
        """Обновляет всю игровую логику за один кадр."""
        # Обновляем позиции всех шариков
        for ball in self.balls:
            ball.update(self.screen_width, self.screen_height)
        
        # Проверяем столкновения и смешиваем цвета
        self._handle_collisions()
        
        # Обрабатываем всасывание
        if self.suction_active:
            self._process_suction()
        
        # Проверяем зону удаления
        self._check_delete_zone()
    
    def _handle_collisions(self) -> None:
        """Обрабатывает столкновения шариков и смешивает их цвета."""
        checked_pairs = set()
        
        for i, ball1 in enumerate(self.balls):
            for j, ball2 in enumerate(self.balls[i + 1:], start=i + 1):
                # Избегаем повторной проверки
                pair = (min(i, j), max(i, j))
                if pair in checked_pairs:
                    continue
                checked_pairs.add(pair)
                
                if ball1.is_colliding(ball2):
                    # Смешиваем цвета
                    self._mix_colors(ball1, ball2)
    
    def _mix_colors(self, ball1: Ball, ball2: Ball) -> None:
        """
        Смешивает цвета двух шариков при касании.
        Использует интересный алгоритм смешивания, избегая белого цвета.
        
        Args:
            ball1, ball2: Шарики для смешивания цветов
        """
        r1, g1, b1 = ball1.color
        r2, g2, b2 = ball2.color
        
        # Используем нелинейное смешивание для более интересных результатов
        # Среднее значение с небольшим смещением
        mixed_r = int((r1 * 0.6 + r2 * 0.4) % 255)
        mixed_g = int((g1 * 0.6 + g2 * 0.4) % 255)
        mixed_b = int((b1 * 0.6 + b2 * 0.4) % 255)
        
        # Проверяем, не слишком ли светлый цвет (близок к белому)
        brightness = (mixed_r + mixed_g + mixed_b) / 3
        
        # Если цвет слишком светлый (близок к белому), делаем его более насыщенным
        if brightness > 200:
            # Усиливаем один из каналов для создания более интересного цвета
            if mixed_r > mixed_g and mixed_r > mixed_b:
                mixed_g = max(50, mixed_g - 50)
                mixed_b = max(50, mixed_b - 50)
            elif mixed_g > mixed_r and mixed_g > mixed_b:
                mixed_r = max(50, mixed_r - 50)
                mixed_b = max(50, mixed_b - 50)
            else:
                mixed_r = max(50, mixed_r - 50)
                mixed_g = max(50, mixed_g - 50)
        
        # Применяем новый цвет к обоим шарикам
        ball1.color = (mixed_r, mixed_g, mixed_b)
        ball2.color = (mixed_r, mixed_g, mixed_b)
    
    def start_suction(self, mouse_x: float, mouse_y: float) -> None:
        """
        Начинает процесс всасывания шариков в инвентарь.
        
        Args:
            mouse_x, mouse_y: Позиция мыши
        """
        self.suction_active = True
        self.suction_mouse_pos = (mouse_x, mouse_y)
    
    def stop_suction(self) -> None:
        """Останавливает процесс всасывания."""
        self.suction_active = False
    
    def _process_suction(self) -> None:
        """Обрабатывает всасывание шариков в инвентарь."""
        mouse_x, mouse_y = self.suction_mouse_pos
        balls_to_remove = []
        
        for ball in self.balls:
            # Проверяем, находится ли шарик в радиусе всасывания
            dx = ball.x - mouse_x
            dy = ball.y - mouse_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance <= self.suction_range:
                # Притягиваем шарик к мыши
                pull_strength = (self.suction_range - distance) / self.suction_range
                pull_strength = min(pull_strength * 5, 10)  # Ограничиваем силу
                
                # Вычисляем направление
                if distance > 0:
                    dir_x = dx / distance
                    dir_y = dy / distance
                else:
                    dir_x = 0
                    dir_y = 0
                
                # Применяем притяжение
                vx, vy = ball.velocity
                ball.velocity = (
                    vx + dir_x * pull_strength * 0.3,
                    vy + dir_y * pull_strength * 0.3
                )
                
                # Если шарик очень близко к мыши, добавляем в инвентарь
                if distance < ball.radius + 10:
                    self.inventory.append(ball)
                    balls_to_remove.append(ball)
        
        # Удаляем шарики, попавшие в инвентарь
        for ball in balls_to_remove:
            if ball in self.balls:
                self.balls.remove(ball)
    
    def eject_ball(self, mouse_x: float, mouse_y: float, 
                   velocity: Tuple[float, float] = None) -> Optional[Ball]:
        """
        Выплевывает шарик из инвентаря обратно на экран.
        
        Args:
            mouse_x, mouse_y: Позиция мыши (куда выплюнуть)
            velocity: Начальная скорость шарика (если None, случайная)
        
        Returns:
            Выплюнутый шарик или None, если инвентарь пуст
        """
        if not self.inventory:
            return None
        
        # Берем последний шарик из инвентаря
        ball = self.inventory.pop()
        
        # Устанавливаем позицию
        ball.x = mouse_x
        ball.y = mouse_y
        
        # Устанавливаем скорость
        if velocity is None:
            speed = random.uniform(2, 5)
            angle = random.uniform(0, 2 * math.pi)
            ball.velocity = (speed * math.cos(angle), speed * math.sin(angle))
        else:
            ball.velocity = velocity
        
        # Добавляем обратно на экран
        self.balls.append(ball)
        return ball
    
    def _check_delete_zone(self) -> None:
        """Проверяет, находятся ли шарики в зоне удаления, и удаляет их."""
        balls_to_remove = []
        
        for ball in self.balls:
            # Проверяем, находится ли шарик в зоне удаления
            if (self.delete_zone_x <= ball.x <= self.screen_width and
                0 <= ball.y <= self.delete_zone_size):
                balls_to_remove.append(ball)
        
        # Удаляем шарики
        for ball in balls_to_remove:
            self.balls.remove(ball)
    
    def is_in_delete_zone(self, x: float, y: float) -> bool:
        """
        Проверяет, находится ли точка в зоне удаления.
        
        Args:
            x, y: Координаты точки
        
        Returns:
            True, если точка в зоне удаления
        """
        return (self.delete_zone_x <= x <= self.screen_width and
                0 <= y <= self.delete_zone_size)
    
    def get_ball_at_position(self, x: float, y: float) -> Optional[Ball]:
        """
        Возвращает шарик в указанной позиции, если он есть.
        
        Args:
            x, y: Координаты позиции
        
        Returns:
            Шарик или None
        """
        for ball in self.balls:
            if ball.is_point_inside(x, y):
                return ball
        return None
    
    def get_delete_zone_bounds(self) -> Tuple[int, int, int, int]:
        """
        Возвращает границы зоны удаления.
        
        Returns:
            (x, y, width, height) зоны удаления
        """
        return (self.delete_zone_x, self.delete_zone_y, 
                self.delete_zone_size, self.delete_zone_size)

