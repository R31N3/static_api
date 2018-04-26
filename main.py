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
                response_json = response.json()
                print(response_json["response"]['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point'][
                    'pos'])
                return ",".join(response_json["response"]['GeoObjectCollection']['featureMember'][0]
                                ['GeoObject']['Point']['pos'].split()),\
                       ",".join(response_json["response"]['GeoObjectCollection']['featureMember'][0]
                                ['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['formatted']),\
                       ",".join(response_json["response"]['GeoObjectCollection']['featureMember'][0]['GeoObject']
                                ['metaDataProperty']['GeocoderMetaData']['Address']['postal_code'])
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
    addres = ""
    reMakeImage(coords, z, dop_args)
    pygame.init()
    surface = pygame.display.set_mode((650, 500))
    surface.blit(pygame.image.load(map_file), (0, 0))
    gui = GUI()
    gui.add_element(TextBox((10, 460, 300, 30), ''))
    gui.add_element(Label((10,10, 300, 30), addres))
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
                print(str(type(obj)))
                if "Label" not in str(type(obj)):
                    if obj.submit_button_pressed:
                        coords, adress, post_index = search_and_correct_coords_and_adress(obj.text)
                        dop_args = "&pt={},ya_ru1".format(coords)
                        reMakeImage(coords, z, dop_args)
                    if obj.reset_button_pressed:
                        dop_args = ""
                        addres = ""
                        reMakeImage(coords, z, dop_args)
        # передаем события пользователя GUI-элементам
        gui.render(surface)  # отрисовываем все GUI-элементы
        gui.update()  # обновляеем все GUI-элементы
        surface.blit(pygame.image.load(map_file), (0, 0))
        pygame.display.flip()

    pygame.quit()

    os.remove(map_file)  # Удаляем за собой файл с изображением.


if __name__ == '__main__':
    main()

