import pygame, math
import requests
import sys
import os
# user imports
from some_ui import *


def lonlat_distance(a, b):

    degree_to_meters_factor = 111 * 1000 # 111 километров в метрах
    a_lon, a_lat = a
    b_lon, b_lat = b

    # Берем среднюю по широте точку и считаем коэффициент для нее.
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали.
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    distance = math.sqrt(dx * dx + dy * dy)

    return distance

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

    def search_organization(ll_center):
        try:
            query = "https://search-maps.yandex.ru/v1/?apikey=" \
                    + organisation_api_key \
                    + "&type=biz" \
                    + "&lang=ru_RU" \
                    + "&ll=" + ll_center \
                    + "&spn=0.000031,0.000646"
            response = requests.get(query)
            json_response = response.json()
            organization = json_response["features"][0]["properties"]["CompanyMetaData"]
            org_name = organization["name"]
            org_address = organization["address"]
            query = "https://geocode-maps.yandex.ru/1.x/?format=json&geocode=" + org_address
            response = requests.get(query)
            if response:
                response_json = response.json()["response"]['GeoObjectCollection']['featureMember'][0]['GeoObject']
                return (",".join(response_json['Point']['pos'].split()), org_name)
        except:
            pass

    coords, z = '45.0183,53.1951', 17
    map_type = 0
    map_types = ["map", "sat", "sat,skl"]
    map_file = "map.png"
    dop_args = ""
    address = "Поле адреса"
    nothing = ""
    organisation_api_key = '3c4a592e-c4c0-4949-85d1-97291c87825c'
    reMakeImage(coords, z, dop_args)
    pygame.init()
    surface = pygame.display.set_mode((650, 485))
    surface.blit(pygame.image.load(map_file), (0, 0))
    gui = GUI()
    gui.add_element(TextBox((10, 450, 300, 30), '', 'Искать!', "Search"))
    gui.add_element(Label((10,10, 450, 30), address))
    index_button = Button((475, 10, 180, 30), "Показать индекс")
    gui.add_element(index_button)
    pygame.display.flip()
    flag = 0
    index = ""
    current_index = ""
    dop_arg = ""
    while True:
        indexes = ["", " Индекс - " + index]
        for event in pygame.event.get():
            const = [float(i) for i in coords.split(",")]
            if event.type == pygame.QUIT:
                break
            if event.type == pygame.MOUSEBUTTONDOWN \
                    and not pygame.Rect((0, 0, 650, 40)).collidepoint(pygame.mouse.get_pos()) \
                    and not pygame.Rect((10, 450, 650, 70)).collidepoint(pygame.mouse.get_pos()):

                pos = pygame.mouse.get_pos()
                # Адские числа в следующих строках - волшебные, они равны смещению координаты при перемещении на 1
                # пиксель при Z=1.
                delta_x = (pos[0]-325)/2**int(z)*1.4063671351351351351351351351351
                delta_y = -((pos[1]-225)/2**int(z)*0.97363878586278586278586278586276)
                dop_coords = str(round(float(coords.split(",")[0])+delta_x, 4)) + "," + str(round(float(coords.split(",")[1]) + delta_y, 4))
                print(dop_coords)
                if pygame.mouse.get_pressed()[0]:
                    if dop_args:
                        dop_arg = "~" + dop_args[4:]
                    dop_args = "&pt={},ya_ru1".format(dop_coords)
                    nothing, address, index = search_and_correct_coords_and_adress(dop_coords)
                    print(dop_args+dop_arg)

                    reMakeImage(coords, z, dop_args+dop_arg)
                elif pygame.mouse.get_pressed()[2]:
                    point, address = search_organization(dop_coords)
                    if dop_args:
                        if "pm2" in dop_args:
                            dop_args = "&pt={},pm2gnm".format(point)
                        else:
                            dop_arg = "~" + point + ",pm2gnm"
                    else:
                        dop_args = "&pt={},pm2gnm".format(point)
                    print(dop_args+dop_arg)
                    reMakeImage(coords, z, dop_args+dop_arg)


            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAGEDOWN:
                    z = str(int(z)-1) if int(z) > 2 else z
                    reMakeImage(coords, z, dop_args)
                if event.key == pygame.K_PAGEUP:
                    z = str(int(z)+1) if int(z) < 19 else z
                    reMakeImage(coords, z, dop_args)
                if event.key == pygame.K_LEFT and const[0] + ((-325)/2**int(z)*1.4063671351351351351351351351351) >= -90:
                    coords = str(const[0] + ((-325)/2**int(z)*1.4063671351351351351351351351351)) + "," + str(const[1])
                    reMakeImage(coords, z, dop_args)
                if event.key == pygame.K_RIGHT and const[0] + ((325)/2**int(z)*1.4063671351351351351351351351351) <= 90:
                    coords = str(const[0] + (325/2**int(z)*1.4063671351351351351351351351351)) + "," + str(const[1])
                    reMakeImage(coords, z, dop_args)
                if event.key == pygame.K_DOWN:
                    coords = str(const[0])+","+ str(const[1] + ((-225)/2**int(z)*0.84311178378378378378378378378378))
                    reMakeImage(coords, z, dop_args)
                if event.key == pygame.K_UP:
                    coords = str(const[0])+","+ str(const[1] + (225/2**int(z)*0.84311178378378378378378378378378))
                    reMakeImage(coords, z, dop_args)
                if event.key == pygame.K_TAB:
                    map_type = (map_type+1) % 3
                    reMakeImage(coords, z, dop_args)
            gui.get_event(event)
            for obj in gui.elements:
                if "Label" not in str(type(obj)) and "Button" not in str(type(obj)):
                    if obj.submit_button_pressed:
                        if obj.text and obj.name == "Search":
                            coords, address, index = search_and_correct_coords_and_adress(obj.text)
                            if dop_args:
                                dop_arg = "~" + dop_args[4:]
                            dop_args = "&pt={},ya_ru1".format(coords)
                            reMakeImage(coords, z, dop_args+dop_arg)
                    if obj.reset_button_pressed:
                        dop_args = ""
                        dop_arg = ""
                        address = "Поле адреса"
                        current_index = ""
                        reMakeImage(coords, z, dop_args)
                elif "Button" in str(type(obj)):
                    flag = (flag+1) % 2 if obj.pressed else flag
                    if obj.pressed and address:
                        if address != "Поле адреса":
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

