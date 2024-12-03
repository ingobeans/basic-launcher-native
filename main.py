import sources, pygame, datetime, os, sys, config

def real_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, os.path.join("assets", relative_path))
    return os.path.join("assets", relative_path)

asset_corners = real_path("corners.png")

class Card:
    def __init__(self, game, position, size, card_color, corners_image, card_font):
        self.surface = pygame.Surface(size)
        self.position = position
        self.size = size
        self.game = game

        self.surface.fill(card_color)
        
        text = card_font.render(game.name,True,(255,255,255))
        self.surface.blit(text,((size[0] - text.width) / 2,225+5))
        artwork = None
        if game.illustration_path:
            artwork = pygame.image.load(game.illustration_path)
            artwork = pygame.transform.smoothscale(artwork,(size[0], 225))
            self.surface.blit(artwork)
        self.surface.blit(corners_image)

class Window:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode([1120+10, 675],vsync=True,flags=pygame.RESIZABLE)#|pygame.NOFRAME)

        if config.get_system() == "Windows":
            import dark_titlebar
            dark_titlebar.make_title_bar_dark(pygame.display.get_wm_info()["window"])
        
        self.running = False
        self.background_color = (25,25,27)
        self.card_color = (61,61,67)
        pygame.display.set_caption("Basic Launcher")

        self.buttons:list[Card] = []
        self.corners_image = pygame.image.load(asset_corners)
        self.card_font = pygame.font.SysFont("Arial",16)
        self.header_font = pygame.font.SysFont("Arial",32,bold=True)

        self.start_press_button = None
        self.scroll_position = 0
        self.scroll_amount = 40

        self.card_width = 150
        self.card_height = 257
        self.card_gap_x = 10
        self.card_gap_y = 10

        self.padding_x = 10
        self.padding_y = 80

    def button_at(self, position):
        for button in self.buttons:
            if position[0] > button.position[0] and position[0] < button.position[0] + button.size[0]:
                if position[1] > button.position[1] + self.scroll_position and position[1] < button.position[1] + button.size[1] + self.scroll_position:
                    return button

    def run(self):
        self.update_buttons()
        self.last_frame = datetime.datetime.now()
        self.running = True
        while self.running:
            now = datetime.datetime.now()
            time_delta = (now - self.last_frame).total_seconds()
            self.last_frame = now
            #print(f"FPS: {round(1/time_delta)}")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.update_buttons()
                elif event.type == pygame.MOUSEWHEEL:
                    self.scroll_position += self.scroll_amount * event.y
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.start_press_button = self.button_at(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        button = self.button_at(event.pos)
                        if button and button == self.start_press_button:
                            button.game.parent_source.run_game(button.game.id)

            self.screen.fill(self.background_color)
            self.draw_buttons()
            
            # hide overflow
            pygame.draw.rect(self.screen, self.background_color, pygame.Rect(0,0,self.screen.width,self.padding_y))
            
            text = self.header_font.render("Library",True,(255,255,255))
            self.screen.blit(text,((self.screen.width - text.width)/2,(self.padding_y - text.height)/2))

            #self.ui_manager.draw_ui(self.screen)
            pygame.display.update()
        
        pygame.quit()

    def draw_buttons(self):
        for button in self.buttons:
            position = (button.position[0], button.position[1]+self.scroll_position)
            self.screen.blit(button.surface,position)

    def calc_button_pos(self, index):
        container_width = self.screen.width - self.padding_x * 2
        buttons_per_row = (container_width + self.card_gap_x) // (self.card_width + self.card_gap_x)
        x = int(index % buttons_per_row) * (self.card_width + self.card_gap_x) + self.padding_x
        y = int(index / buttons_per_row) * (self.card_height + self.card_gap_y) + self.padding_y
        return (x, y)

    def update_buttons(self):
        for index, button in enumerate(self.buttons):
            button.position = self.calc_button_pos(index)

    def create_game_button(self, game:sources.game.Game):
        #button = pygame_gui.elements.UIButton(pygame.Rect(self.calc_button_pos(len(self.buttons)),(self.card_width,self.card_height)),text=game.name,manager=self.ui_manager,container=self.scrollbox)
        card = Card(game,self.calc_button_pos(len(self.buttons)),(self.card_width,self.card_height),self.card_color,self.corners_image,self.card_font)
        return card

    def add_game_button(self, game:sources.game.Game):
        card = self.create_game_button(game)
        
        self.buttons.append(card)

window = Window()
for game in sources.get_games():
    window.add_game_button(game)
window.run()