from ursina import *
import math
import random

app = Ursina()

# ==========================================
# 1. НАСТРОЙКИ КАЧЕСТВА
# ==========================================
window.size = (1280, 720)        
window.fullscreen = False         
window.borderless = False
application.development_mode = False 

texture.default_filtering = 'trilinear' 

# --- 2. Настройка сцены ---
Sky(color=color.black)
window.color = color.black

# Камера смотрит на центр системы
camera.position = (0, 150, -400) 
camera.look_at(Vec3(0, 150, 0)) 
camera.fov = 60

EditorCamera()

# --- 3. Звездное небо ---
for _ in range(2000):
    Entity(model='quad', color=color.white, 
           scale=random.uniform(0.1, 0.4), 
           position=(random.uniform(-800, 800), random.uniform(-800, 800), random.uniform(-800, 800)),
           billboard=True, unlit=True)

# --- 4. Солнце ---
sun = Entity(model='sphere', scale=30, position=(0, 150, 0), texture='textures/2k_Солнце.jpg')
sun_light = PointLight(parent=sun, color=color.rgba(255, 255, 200, 255), range=500)

# --- 5. Данные планет ---
# ВАЖНО: Мы изменили "скорость" на "период обращения в днях" (как в реальности)
# (Имя, Расстояние, Размер, Период в днях, Текстура)
planets_data = [
    ("Меркурий", 40, 1.2, 88, 'textures/2k_Меркурий.jpg'),
    ("Венера", 60, 1.8, 225, 'textures/2k_Венера.jpg'),
    ("Земля", 80, 2.0, 365, 'textures/2k_Земля.jpg'),
    ("Марс", 100, 1.6, 687, 'textures/2k_Марс.jpg'),
    ("Юпитер", 140, 6.0, 4333, 'textures/2k_Юпитер.jpg'),
    ("Сатурн", 180, 5.5, 10759, 'textures/2k_Сатурн.jpg'),
    ("Уран", 220, 4.0, 30687, 'textures/2k_Уран.jpg'),
    ("Нептун", 260, 3.8, 60190, 'textures/2k_Нептун.jpg'),
]

planets = []

for name, dist, size, period, tex_path in planets_data:
    try:
        p = Entity(model='sphere', scale=size, texture=tex_path, unlit=False)
    except:
        p = Entity(model='sphere', scale=size, color=color.white, unlit=False)
    
    p.name = name
    p.dist = dist
    p.period = period # Сохраняем период
    p.angle = random.uniform(0, 360) 
    planets.append(p)

    # Кольца Сатурна
    if name == "Сатурн":
        ring = Entity(
            model='torus', 
            scale=(size * 1.8, size * 0.1, size * 1.8), 
            rotation_x=15, 
            color=color.rgba(200, 180, 140, 150), 
            unlit=False
        )
        ring.parent = p
        ring.position = (0, 0, 0)

# --- 6. ПОЛЗУНОК УСКОРЕНИЯ ВРЕМЕНИ ---
# Создаем ползунок внизу экрана
time_scale_slider = Slider(min=1, max=50, default=1, text='Ускорение времени', y=-0.45)
time_label = Text(text='x1', position=(-0.1, -0.45), origin=(0, 0), scale=1.2, color=color.yellow)

# --- 7. Вращение ---
def update():
    # Получаем текущее значение ползунка
    time_scale = time_scale_slider.value
    time_label.text = f"x{int(time_scale)}"
    
    # Базовое время: 1 "игровой" день проходит за 0.05 секунды при скорости 1x
    # (Благодаря этому Нептун делает оборот примерно за 60 секунд)
    days_per_second = 20 * time_scale
    
    for p in planets:
        # Вычисляем изменение угла в зависимости от периода планеты
        # (Чем больше период, тем медленнее она движется)
        angle_change = (days_per_second / p.period) * 360 * time.dt
        p.angle += angle_change
        
        # Движение по эллипсу
        p.x = math.cos(math.radians(p.angle)) * p.dist
        p.z = math.sin(math.radians(p.angle)) * (p.dist * 0.7) 
        
        # Поднимаем орбиту
        p.y = math.sin(math.radians(p.angle)) * (p.dist * 0.15) + 150
        
        p.rotation_y += 30 * time.dt

app.run()