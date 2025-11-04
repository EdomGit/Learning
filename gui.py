import tkinter as tk
from tkinter import Canvas
from logic import GameLogic, Ball

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
UPDATE_INTERVAL = 1000 // FPS  # Интервал обновления в миллисекундах
STARTING_BALLS = 10  # Стартовое количество шариков

# Цвета (RGB в формате для tkinter: "#RRGGBB")
WHITE = "#FFFFFF"
BLACK = "#000000"
RED = "#FF0000"
GRAY = "#C8C8C8"
DARK_GRAY = "#969696"
SUCTION_COLOR = "#6496FF"
SUCTION_CENTER_COLOR = "#96C8FF"


class GameWindow:
    """Класс для управления графическим интерфейсом игры."""
    
    def __init__(self):
        """Инициализация окна игры."""
        self.root = tk.Tk()
        self.root.title("Игра с шариками")
        self.root.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        self.root.resizable(False, False)
        
        # Создаем canvas для рисования
        self.canvas = Canvas(self.root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, 
                            bg=WHITE, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Создаем игровую логику
        self.game = GameLogic(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Добавляем стартовые шарики
        for _ in range(STARTING_BALLS):
            self.game.add_ball()
        
        # Состояние игры
        self.mouse_pressed = False
        self.mouse_x = 0
        self.mouse_y = 0
        
        # Привязываем события мыши
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.root.bind("<KeyPress-space>", self.on_space_press)
        self.canvas.focus_set()
        
        # Запускаем игровой цикл
        self.update()
        
        # Запускаем главный цикл
        self.root.mainloop()
    
    def on_mouse_down(self, event):
        """Обработчик нажатия левой кнопки мыши."""
        self.mouse_pressed = True
        self.mouse_x = event.x
        self.mouse_y = event.y
        self.game.start_suction(self.mouse_x, self.mouse_y)
    
    def on_mouse_up(self, event):
        """Обработчик отпускания левой кнопки мыши."""
        self.mouse_pressed = False
        self.game.stop_suction()
    
    def on_mouse_move(self, event):
        """Обработчик движения мыши."""
        self.mouse_x = event.x
        self.mouse_y = event.y
        if self.mouse_pressed:
            self.game.start_suction(self.mouse_x, self.mouse_y)
    
    def on_right_click(self, event):
        """Обработчик правой кнопки мыши - выброс шарика."""
        self.game.eject_ball(event.x, event.y)
    
    def on_space_press(self, event):
        """Обработчик нажатия пробела - добавление шарика."""
        self.game.add_ball(self.mouse_x, self.mouse_y)
    
    def rgb_to_hex(self, rgb):
        """Конвертирует RGB кортеж в hex строку."""
        r, g, b = rgb
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def update(self):
        """Обновляет игровое состояние и перерисовывает экран."""
        # Обновляем игровую логику
        self.game.update()
        
        # Очищаем canvas
        self.canvas.delete("all")
        
        # Рисуем зону удаления
        delete_zone = self.game.get_delete_zone_bounds()
        delete_x, delete_y, delete_width, delete_height = delete_zone
        self.canvas.create_rectangle(delete_x, delete_y, 
                                    delete_x + delete_width, 
                                    delete_y + delete_height,
                                    fill="#FFC8C8", outline=RED, width=2)
        
        # Текст в зоне удаления
        self.canvas.create_text(delete_x + delete_width // 2,
                               delete_y + delete_height // 2,
                               text="Удалить", fill=BLACK,
                               font=("Arial", 12, "bold"))
        
        # Рисуем шарики
        for ball in self.game.balls:
            color = self.rgb_to_hex(ball.color)
            x, y = int(ball.x), int(ball.y)
            radius = int(ball.radius)
            
            # Рисуем шарик
            self.canvas.create_oval(x - radius, y - radius,
                                   x + radius, y + radius,
                                   fill=color, outline=BLACK, width=1)
        
        # Визуализация всасывания
        if self.game.suction_active:
            mouse_x, mouse_y = self.game.suction_mouse_pos
            mx, my = int(mouse_x), int(mouse_y)
            range_radius = self.game.suction_range
            
            # Рисуем круг всасывания
            self.canvas.create_oval(mx - range_radius, my - range_radius,
                                   mx + range_radius, my + range_radius,
                                   outline=SUCTION_COLOR, width=2)
            
            # Индикатор центра всасывания
            self.canvas.create_oval(mx - 5, my - 5, mx + 5, my + 5,
                                   fill=SUCTION_CENTER_COLOR, 
                                   outline=SUCTION_COLOR, width=1)
        
        # Показываем количество шариков в инвентаре
        if self.game.inventory:
            self.canvas.create_text(10, 15, anchor=tk.W,
                                   text=f"Инвентарь: {len(self.game.inventory)}",
                                   fill=BLACK, font=("Arial", 12))
        
        # Показываем количество шариков на экране
        self.canvas.create_text(10, 40, anchor=tk.W,
                               text=f"Шариков: {len(self.game.balls)}",
                               fill=BLACK, font=("Arial", 12))
        
        # Инструкция
        self.canvas.create_text(10, SCREEN_HEIGHT - 20, anchor=tk.W,
                               text="ЛКМ: всасывать | ПКМ: выброс | Пробел: добавить",
                               fill=DARK_GRAY, font=("Arial", 10))
        
        # Планируем следующее обновление
        self.root.after(UPDATE_INTERVAL, self.update)


def main():
    """Основная функция игры."""
    game_window = GameWindow()


if __name__ == "__main__":
    main()
