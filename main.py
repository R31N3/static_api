import pygame
import requests
import sys
import os
# user imports
from some_ui import *


def main():
    def reMakeImage(cords, z):
        try:
            map_request = "https://static-maps.yandex.ru/1.x/?ll={}&size=650,450&z={}&l={}".format(cords, z,
                                                                                                   map_types[map_type])
            response = requests.get(map_request)

            if not response:
                print("Ошибка выполнения запроса:")
                print("Http статус:", response.status_code, "(", response.reason, ")")
                sys.exit(1)
        except Exception:
            print("Запрос не удалось выполнить. Проверьте наличие сети Интернет.")
            sys.exit(1)
        try:
            with open(map_file, "wb") as file:
                file.write(response.content)
        except IOError as ex:
            print("Ошибка записи временного файла:", ex)
            sys.exit(2)

# coords, z = input(), input()
# '''
# 33.4534,43.5654
# 5
# '''
    coords, z = '33.4534,43.5654', 5
    map_type = 0
    map_types = ["map", "sat", "sat,skl"]
    map_file = "map.png"
    reMakeImage(coords, z)
    pygame.init()
    surface = pygame.display.set_mode((650, 500))
    surface.blit(pygame.image.load(map_file), (0, 0))
    gui = GUI()
    gui.add_element(TextBox((10, 460, 300, 30), ''))
    pygame.display.flip()
    scale_const = 0.026211385*int(z)
    while True:
        for event in pygame.event.get():
            const = [float(i) for i in coords.split(",")]
            if event.type == pygame.QUIT:
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAGEDOWN:
                    z = str(int(z)-1) if int(z) > 1 else z
                    reMakeImage(coords, z)
                    scale_const = 0.026211385 * int(z)
                if event.key == pygame.K_PAGEUP:
                    z = str(int(z)+1) if int(z) < 17 else z
                    reMakeImage(coords, z)
                    scale_const = 0.026211385 * int(z)
                if event.key == pygame.K_DOWN:
                    z = str(int(z)+1) if int(z) < 16 else z
                    reMakeImage(coords, z)
                    scale_const = 0.026211385 * int(z)
                if event.key == pygame.K_LEFT:
                    coords = str(const[0] - scale_const) + "," + str(const[1])
                    reMakeImage(coords, z)
                if event.key == pygame.K_RIGHT:
                    coords = str(const[0] + scale_const) + "," + str(const[1])
                    reMakeImage(coords, z)
                if event.key == pygame.K_DOWN:
                    coords = str(const[0]) + "," + str(const[1] - scale_const)
                    reMakeImage(coords, z)
                if event.key == pygame.K_UP:
                    coords = str(const[0]) + "," + str(const[1] + scale_const)
                    reMakeImage(coords, z)
                if event.key == pygame.K_c:
                    map_type = (map_type+1)%3
                    reMakeImage(coords, z)
            gui.get_event(event)  # передаем события пользователя GUI-элементам
        gui.render(surface)  # отрисовываем все GUI-элементы
        gui.update()  # обновляеем все GUI-элементы
        surface.blit(pygame.image.load(map_file), (0, 0))
        pygame.display.flip()

    pygame.quit()

    os.remove(map_file)  # Удаляем за собой файл с изображением.


if __name__ == '__main__':
    main()

