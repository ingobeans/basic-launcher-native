import sources, pygame, pygame_gui, datetime

class Window:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode([1196, 675],vsync=True,flags=pygame.RESIZABLE)#|pygame.NOFRAME)
        self.running = False
        self.background_color = (25,25,27)
        self.card_color = (61,61,67)
        self.ui_manager = pygame_gui.UIManager([1196, 675])
        pygame.display.set_caption("Basic Launcher")
        self.scrollbox = pygame_gui.elements.UIScrollingContainer(self.screen.get_rect(),self.ui_manager)
        self.scrollbox.vert_scroll_bar.scroll_wheel_speed = 240
        self.buttons = []
        self.corners_image = pygame.image.load("assets/corners.png")
        self.font = pygame.font.SysFont("Arial",16)

        self.card_width = 150
        self.card_height = 257
        self.card_gap_x = 10
        self.card_gap_y = 10

    def run(self):
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
                    self.ui_manager.set_window_resolution((self.screen.width, self.screen.height))
                    self.update_buttons()
                elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                    for button in self.buttons:
                        if button[0] == event.ui_element:
                            print(button[1])
                            button[1].parent_source.run_game(button[1].id)          
                self.ui_manager.process_events(event)
            
            self.ui_manager.update(time_delta)
            self.screen.fill(self.background_color)
            self.draw_buttons()
            #self.ui_manager.draw_ui(self.screen)
            pygame.display.update()
        
        pygame.quit()

    def draw_buttons(self):
        for button,_,card in self.buttons:
            self.screen.blit(card,button.rect)

    def calc_button_pos(self, index):
        buttons_per_row = (self.screen.width + self.card_gap_x) // (self.card_width + self.card_gap_x)
        x = int(index % buttons_per_row) * (self.card_width + self.card_gap_x)
        y = int(index / buttons_per_row) * (self.card_height + self.card_gap_y)
        return (x, y)

    def update_buttons(self):
        for index, button in enumerate(self.buttons):
            button[0].set_position(self.calc_button_pos(index))

    def create_game_button(self, game:sources.game.Game):
        button = pygame_gui.elements.UIButton(pygame.Rect(self.calc_button_pos(len(self.buttons)),(self.card_width,self.card_height)),text=game.name,manager=self.ui_manager,container=self.scrollbox)
        return button

    def add_game_button(self, game:sources.game.Game):
        button = self.create_game_button(game)

        card = pygame.Surface((button.rect[2],button.rect[3]))
        card.fill(self.card_color)
        
        text = self.font.render(game.name,True,(255,255,255))
        card.blit(text,((self.card_width - text.width) / 2,225+5))
        card.blit(self.corners_image)
        artwork = None
        if game.illustration_path:
            artwork = pygame.image.load(game.illustration_path)
            artwork = pygame.transform.scale(artwork,(self.card_width, 225))
            card.blit(artwork)
        
        self.buttons.append([button,game,card])

window = Window()
for game in sources.get_games():
    window.add_game_button(game)
window.run()