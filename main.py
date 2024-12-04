import sources, pygame, datetime, os, sys, config

version = "1.3.0"

def real_path(relative_path):
    if path := getattr(sys, '_MEIPASS', False): # hey look its the walrus operator!
        return os.path.join(path, os.path.join("assets", relative_path))
    return os.path.join("assets", relative_path)

asset_corners = real_path("corners.png")
asset_glow = real_path("glow.png")

class Card:
    def __init__(self, game, position, size, card_color, corners_image, card_font):
        self.position = position
        self.size = size
        self.game = game

        self.surface = self.generate_surface(False,game,size,card_color,corners_image,card_font)
        self.surface_glow = self.generate_surface(True,game,size,card_color,corners_image,card_font)
    
    def generate_surface(self, glow, game, size, card_color, corners_image, card_font):
        surface = pygame.Surface(size)
        surface.fill((255,255,255) if glow else card_color)
        
        text = card_font.render(game.name,True,(0,0,0) if glow else(255,255,255))
        surface.blit(text,((size[0] - text.width) / 2,225+5))

        artwork = None
        if game.illustration_path:
            artwork = pygame.image.load(game.illustration_path)
            artwork = pygame.transform.smoothscale(artwork,(size[0], 225))
            surface.blit(artwork)
        
        surface.blit(corners_image)
        surface.set_colorkey((0,255,0))
        return surface

class Window:
    def __init__(self):
        pygame.init()

        system_is_windows = config.get_system() == "Windows"

        flags = pygame.HIDDEN if system_is_windows else pygame.RESIZABLE
        self.screen = pygame.display.set_mode([1120+10, 675],vsync=True,flags=flags)

        if system_is_windows:
            import dark_titlebar
            dark_titlebar.make_title_bar_dark(pygame.display.get_wm_info()["window"])
            pygame.display.set_mode(self.screen.size,vsync=True,flags=pygame.RESIZABLE)
        
        self.running = False
        self.background_color = (25,25,27)
        self.card_color = (61,61,67)
        pygame.display.set_caption("Basic Launcher")

    
        if not config.active_config["input"]["disable_controller"]:
            pygame.joystick.init()
            self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
            self.last_joystick_moves = [[0,0] for _ in self.joysticks]
            self.last_joystick_button_states = [[False]*joystick.get_numbuttons() for joystick in self.joysticks]
            print(f"found {len(self.joysticks)} joystick(s)")

        self.buttons:list[Card] = []
        self.corners_image = pygame.image.load(asset_corners)
        self.glow_image = pygame.image.load(asset_glow)
        self.card_font = pygame.font.SysFont("Arial",16)
        self.header_font = pygame.font.SysFont("Arial",32,bold=True)

        self.start_press_button = None
        self.scroll_position = 0
        self.scroll_amount = 40
        self.selected_card = 0
        self.selector_active = False
        self.using_controller = False

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

    def move_left(self):
        self.selected_card = max(self.selected_card-1, 0)
    def move_right(self):
        self.selected_card = min(self.selected_card+1, len(self.buttons)-1)
    def move_up(self):
        self.selected_card = max(self.selected_card-self.calc_buttons_per_row(), 0)
    def move_down(self):
        self.selected_card = min(self.selected_card+self.calc_buttons_per_row(), len(self.buttons)-1)
    
    def handle_controller(self)->bool:
        if config.active_config["input"]["disable_controller"]:
            return False
        using_controller = False
        axis_threshold = config.active_config["input"]["axis_threshold"]
        for index, joystick in enumerate(self.joysticks):
            joystick_moved = False
            x = joystick.get_axis(0)
            y = joystick.get_axis(1)
            
            if x > axis_threshold:
                if self.last_joystick_moves[index][0] != 1:
                    joystick_moved = True
                    self.last_joystick_moves[index][0] = 1
                    self.move_right()
            elif x < -axis_threshold:
                if self.last_joystick_moves[index][0] != -1:
                    joystick_moved = True
                    self.last_joystick_moves[index][0] = -1
                    self.move_left()
            else:
                self.last_joystick_moves[index][0] = 0
            if y > axis_threshold:
                if self.last_joystick_moves[index][1] != 1:
                    joystick_moved = True
                    self.last_joystick_moves[index][1] = 1
                    self.move_down()
            elif y < -axis_threshold:
                if self.last_joystick_moves[index][1] != -1:
                    joystick_moved = True
                    self.last_joystick_moves[index][1] = -1
                    self.move_up()
            else:
                self.last_joystick_moves[index][1] = 0
                
            using_controller = using_controller or joystick_moved
            
            for button_index in range(joystick.get_numbuttons()):
                button = joystick.get_button(button_index)
                old = self.last_joystick_button_states[index][button_index]
                self.last_joystick_button_states[index][button_index] = button
                
                using_controller = using_controller or button

                if button and not old:
                    game = self.buttons[self.selected_card].game
                    game.parent_source.run_game(game.id)
        return using_controller

    def run(self):
        self.update_buttons()
        self.last_frame = datetime.datetime.now()
        self.running = True
        while self.running:
            now = datetime.datetime.now()
            self.last_frame = now
            #time_delta = (now - self.last_frame).total_seconds()
            #print(f"FPS: {round(1/time_delta)}")
            events = pygame.event.get()

            self.using_controller = self.handle_controller()
            self.selector_active = self.selector_active or self.using_controller
            
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.update_buttons()
                elif event.type == pygame.KEYDOWN and not self.using_controller and not config.active_config["input"]["disable_keyboard_navigation"]:
                    # checking this here ensures the first directional input wont move the selection but instead only enable it
                    if self.selector_active:
                        if event.key == pygame.K_LEFT:
                            self.move_left()
                        if event.key == pygame.K_RIGHT:
                            self.move_right()
                        if event.key == pygame.K_DOWN:
                            self.move_down()
                        if event.key == pygame.K_UP:
                            self.move_up()
                        if event.key == pygame.K_RETURN:
                            game = self.buttons[self.selected_card].game
                            game.parent_source.run_game(game.id)
                    self.selector_active = True
                elif event.type == pygame.MOUSEWHEEL:
                    self.scroll_position += self.scroll_amount * event.y
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.selector_active = False
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
        if self.selector_active:
            position = self.calc_button_pos(self.selected_card)
            self.screen.blit(self.glow_image, (position[0]-21, position[1]+self.scroll_position-10))
            #print(button.game)
        for index, button in enumerate(self.buttons):
            if index == self.selected_card and self.selector_active:
                self.screen.blit(button.surface_glow, (button.position[0], button.position[1]+self.scroll_position))
            else:
                self.screen.blit(button.surface, (button.position[0], button.position[1]+self.scroll_position))

    def calc_buttons_per_row(self):
        container_width = self.screen.width - self.padding_x * 2
        buttons_per_row = (container_width + self.card_gap_x) // (self.card_width + self.card_gap_x)
        return buttons_per_row

    def calc_button_pos(self, index):
        buttons_per_row = self.calc_buttons_per_row()
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

if __name__ == "__main__":
    print(f"basic-launcher {version}")
    window = Window()
    for game in sources.get_games():
        window.add_game_button(game)
    window.run()