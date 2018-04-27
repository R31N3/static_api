import pygame
import requests
import sys
import os
# user imports
from some_ui import *


def main():
    def reMakeImage(cords, z, dop_args):
        try:
            map_request = "https://static-maps.yandex.ru/1.x/?ll={}&size=650,450&z={}&l={}{}".format(cords, z,
                                                                                                   map_types[map_type],
                                                                                                     dop_args)
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

    def search_and_correct_coords_and_adress(request):
        try:
            query = "https://geocode-maps.yandex.ru/1.x/?format=json&geocode=" + request
            response = requests.get(query)
            if response:
                response_json = response.json()["response"]['GeoObjectCollection']['featureMember'][0]['GeoObject']
                index = response_json['metaDataProperty']['GeocoderMetaData']['Address']['postal_code'] if \
                    "postal_code" in response_json['metaDataProperty']['GeocoderMetaData']['Address'].keys() else \
                    "отсутствует"
                return (",".join(response_json['Point']['pos'].split()),
                       "".join(response_json['metaDataProperty']['GeocoderMetaData']['Address']['formatted']), index)

        except:
            pass

# coords, z = input(), input()
# '''
# 33.4534,43.5654
# 5
# '''
    coords, z = '33.4534,43.5654', 5
    map_type = 0
    map_types = ["map", "sat", "sat,skl"]
    map_file = "map.png"
    dop_args = ""
    address = ""
    reMakeImage(coords, z, dop_args)
    pygame.init()
    surface = pygame.display.set_mode((650, 500))
    surface.blit(pygame.image.load(map_file), (0, 0))
    gui = GUI()
    gui.add_element(TextBox((10, 460, 300, 30), ''))
    gui.add_element(Label((10,10, 450, 30), address))
    index_button = Button((470, 10, 180, 30), "Показать индекс")
    gui.add_element(index_button)
    pygame.display.flip()
    flag = 0
    index = ""
    current_index = ""
    scale_const = 0.026211385*int(z)
    while True:
        indexes = ["", " Индекс - "+index]
        for event in pygame.event.get():
            const = [float(i) for i in coords.split(",")]
            if event.type == pygame.QUIT:
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAGEDOWN:
                    z = str(int(z)-1) if int(z) > 1 else z
                    reMakeImage(coords, z, dop_args)
                    scale_const = 0.026211385 * int(z)
                if event.key == pygame.K_PAGEUP:
                    z = str(int(z)+1) if int(z) < 17 else z
                    reMakeImage(coords, z, dop_args)
                    scale_const = 0.026211385 * int(z)
                if event.key == pygame.K_DOWN:
                    z = str(int(z)+1) if int(z) < 16 else z
                    reMakeImage(coords, z, dop_args)
                    scale_const = 0.026211385 * int(z)
                if event.key == pygame.K_LEFT:
                    coords = str(const[0] - scale_const) + "," + str(const[1])
                    reMakeImage(coords, z, dop_args)
                if event.key == pygame.K_RIGHT:
                    coords = str(const[0] + scale_const) + "," + str(const[1])
                    reMakeImage(coords, z, dop_args)
                if event.key == pygame.K_DOWN:
                    coords = str(const[0]) + "," + str(const[1] - scale_const)
                    reMakeImage(coords, z, dop_args)
                if event.key == pygame.K_UP:
                    coords = str(const[0]) + "," + str(const[1] + scale_const)
                    reMakeImage(coords, z, dop_args)
                if event.key == pygame.K_TAB:
                    map_type = (map_type+1)%3
                    reMakeImage(coords, z, dop_args)
            gui.get_event(event)
            for obj in gui.elements:
                if "Label" not in str(type(obj)) and "Button" not in str(type(obj)):
                    if obj.submit_button_pressed:
                        coords, address, index = search_and_correct_coords_and_adress(obj.text)
                        dop_args = "&pt={},ya_ru1".format(coords)
                        reMakeImage(coords, z, dop_args)
                    if obj.reset_button_pressed:
                        dop_args = ""
                        address = ""
                        current_index = ""
                        reMakeImage(coords, z, dop_args)
                elif "Button" in str(type(obj)):
                    flag = (flag+1)%2 if obj.pressed else flag
                    if obj.pressed and address:
                        current_index = indexes[flag]


        # передаем события пользователя GUI-элементам
        # обновляеем все GUI-элементы
        surface.blit(pygame.image.load(map_file), (0, 0))
        gui.render(surface, address+" "+current_index)  # отрисовываем все GUI-элементы
        gui.update()
        pygame.display.flip()

    pygame.quit()

    os.remove(map_file)  # Удаляем за собой файл с изображением.


if __name__ == '__main__':
    main()

