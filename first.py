import requests, os, pygame, sys


def reMakeImage(coords, z):
    try:
        map_request = "https://static-maps.yandex.ru/1.x/?ll={}&size=650,450&z={}&l=map".format(coords, z)
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
    except:
        print("Запрос не удалось выполнить. Проверьте наличие сети Интернет.")
        sys.exit(1)
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)

coords,z = input(), input()


map_file = "map.png"

reMakeImage(coords, z)

pygame.init()
screen = pygame.display.set_mode((650, 450))
screen.blit(pygame.image.load(map_file), (0, 0))
pygame.display.flip()
Const = 0.026211385*int(z)
while True:
    for event in pygame.event.get():
        const = [float(i) for i in coords.split(",")]
        if event.type == pygame.QUIT:
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEDOWN:
                z = str(int(z)-1) if int(z) > 1 else z
                reMakeImage(coords, z)
                Const = 0.026211385 * int(z)
            if event.type == pygame.K_DOWN:
                z = str(int(z)+1) if int(z) < 16 else z
                reMakeImage(coords, z)
                Const = 0.026211385 * int(z)
            if event.type == pygame.K_LEFT:
                coords = str(const[0]-Const)+","+str(const[1])
                reMakeImage(coords, z)
    screen.blit(pygame.image.load(map_file), (0, 0))
    pygame.display.flip()

pygame.quit()

# Удаляем за собой файл с изображением.
os.remove(map_file)