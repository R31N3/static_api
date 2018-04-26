import pygame, platform, os


class GUI:
    def __init__(self):
        self.elements = []

    def add_element(self, element):
        self.elements.append(element)

    def render(self, surface):
        for element in self.elements:
            render = getattr(element, "render", None)
            if callable(render):
                element.render(surface)

    def update(self):
        for element in self.elements:
            update = getattr(element, "update", None)
            if callable(update):
                element.update()

    def get_event(self, event):
        for element in self.elements:
            get_event = getattr(element, "get_event", None)
            if callable(get_event):
                element.get_event(event)


class Label:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bgcolor = pygame.Color("grey")
        self.font_color = pygame.Color("red")
        # Рассчитываем размер шрифта в зависимости от высоты
        if platform.system() == "Windows":
            self.font = pygame.font.SysFont("ds_pixel_cyr", self.rect.height - 11)
        else:
            self.font = pygame.font.Font(os.path.abspath('data/fonts/{}.ttf'.format("ds_pixel_cyr")),
                                         self.rect.height - 11)
        self.rendered_text = None
        self.rendered_rect = None

    def render(self, surface):
        surface.fill(self.bgcolor, self.rect)
        self.rendered_text = self.font.render(self.text, 1, self.font_color)
        self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 2, centery=self.rect.centery)
        surface.blit(self.rendered_text, self.rendered_rect)  # выводим текст


class Button(Label):
    def __init__(self, rect, text):
        super().__init__(rect, text)
        self.bgcolor = pygame.Color("blue")
        self.pressed = False  # при создании кнопка не нажата

    def render(self, surface, replace_params=None):
        if replace_params is not None:
            self.text = replace_params['text']
            self.rect = replace_params['rect']
            self.font_color = replace_params['font_color']
            self.bgcolor = replace_params['bgcolor']
            self.pressed = replace_params['pressed']
        surface.fill(self.bgcolor, self.rect)
        self.rendered_text = self.font.render(self.text, 1, self.font_color)
        if not self.pressed:
            color1 = pygame.Color("white")
            color2 = pygame.Color("black")
            self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 5, centery=self.rect.centery)
        else:
            color1 = pygame.Color("black")
            color2 = pygame.Color("white")
            self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 7, centery=self.rect.centery + 2)

        # рисуем границу
        pygame.draw.rect(surface, color1, self.rect, 2)
        pygame.draw.line(surface, color2, (self.rect.right - 1, self.rect.top), (self.rect.right - 1, self.rect.bottom), 2)
        pygame.draw.line(surface, color2, (self.rect.left, self.rect.bottom - 1),
                         (self.rect.right, self.rect.bottom - 1), 2)
        # выводим текст
        surface.blit(self.rendered_text, self.rendered_rect)

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.pressed = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.pressed = False


class TextBox(Label):
    def __init__(self, rect, text):
        super().__init__(rect, text)
        self.active = True
        self.blink = True
        self.blink_timer = 0
        self.submit_button_rect = pygame.Rect.copy(self.rect)
        self.submit_button_rect = self.submit_button_rect.move(self.rect.width + 10, 0)
        self.submit_button_rect.width = 150
        self.submit_button_pressed = False
        self.reset_button_rect = pygame.Rect.copy(self.submit_button_rect)
        self.reset_button_rect = self.reset_button_rect.move(self.submit_button_rect.width + 10, 0)
        self.reset_button_rect.width = 150
        self.reset_button_pressed = False

    def get_event(self, event):
        if event.type == pygame.KEYDOWN and self.active:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                pass  # self.execute() - что это было и зачем?
            elif event.key == pygame.K_BACKSPACE:
                if len(self.text) > 0:
                    self.text = self.text[:-1]
            else:
                self.text += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
            self.submit_button_pressed = self.submit_button_rect.collidepoint(event.pos)
            self.reset_button_pressed = self.reset_button_rect.collidepoint(event.pos)
            if self.reset_button_pressed:
                self.text = ''
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.submit_button_pressed = False
            self.reset_button_pressed = False

    def update(self):
        if pygame.time.get_ticks() - self.blink_timer > 200:
            self.blink = not self.blink
            self.blink_timer = pygame.time.get_ticks()

    def render(self, surface):
        super(TextBox, self).render(surface)
        if self.blink and self.active:
            pygame.draw.line(surface, pygame.Color("black"),
                             (self.rendered_rect.right + 2, self.rendered_rect.top + 2),
                             (self.rendered_rect.right + 2, self.rendered_rect.bottom - 2))

        Button.render(Button(self.submit_button_rect, ''), surface, {
            'text': 'Искать!', 'rect': self.submit_button_rect,
            'font_color': self.font_color, 'bgcolor': self.bgcolor,
            'pressed': self.submit_button_pressed
        })
        Button.render(Button(self.submit_button_rect, ''), surface, {
            'text': 'Сброс данных', 'rect': self.reset_button_rect,
            'font_color': self.font_color, 'bgcolor': self.bgcolor,
            'pressed': self.reset_button_pressed
        })


def main():
    print('А зачем этот модуль вообще запускать?')


if __name__ == '__main__':
    main()
