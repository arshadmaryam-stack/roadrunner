import arcade

# Window constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Platformer"

# Game state (0 = start menu, 1 = level 1, 2 = level 2, etc.)
game_state = 0

# Scaling
TILE_SCALING = 0.5
COIN_SCALING = 0.5

# Player movement
PLAYER_MOVEMENT_SPEED = 9
GRAVITY = 1
PLAYER_JUMP_SPEED = 22


# ─────────────────────────────────────────
#  START SCREEN
# ─────────────────────────────────────────

class StartView(arcade.View):

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "starting screen",
            WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 50,
            arcade.color.WHITE, font_size=50, anchor_x="center"
        )
        arcade.draw_text(
            "Press SPACE to Start",
            WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 20,
            arcade.color.YELLOW, font_size=30, anchor_x="center"
        )

    def on_key_press(self, key, modifiers):
        global game_state
        if key == arcade.key.SPACE:
            game_state = 1
            game = GameView(level=1)
            game.setup()
            self.window.show_view(game)



# ─────────────────────────────────────────
#  GAME LEVEL VIEW
# ─────────────────────────────────────────

class GameView(arcade.View):

    def __init__(self, level):
        super().__init__()

        # Current level (1, 2, 3...)
        self.level = level

        self.player_sprite = None
        self.player_texture = None

        self.tile_map = None
        self.scene = None

        self.camera = None
        self.gui_camera = None

        self.score = 0
        self.reset_score = True

        self.end_of_map = 0

        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")
        self.gameover_sound = arcade.load_sound(":resources:sounds/gameover1.wav")

    def setup(self):
        layer_options = {
            "Platforms": {"use_spatial_hash": True}
        }

        # Load map
        self.tile_map = arcade.load_tilemap(
            f":resources:tiled_maps/map2_level_{self.level}.json",
            scaling=TILE_SCALING,
            layer_options=layer_options,
        )

        # Scene
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Player
        self.player_texture = arcade.load_texture("my_player.png")
        self.scene.add_sprite_list_after("Player", "Foreground")

        self.player_sprite = arcade.Sprite()
        self.player_sprite.texture = self.player_texture
        self.player_sprite.scale = 0.09
        self.player_sprite.center_x = 128
        self.player_sprite.center_y = 128

        self.scene.add_sprite("Player", self.player_sprite)

        # Physics
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=self.scene["Platforms"],
            gravity_constant=GRAVITY
        )

        # Cameras
        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        # Score text
        self.score_text = arcade.Text(f"Score: {self.score}", x=10, y=10)
        arcade.set_background_color(arcade.color.CORNFLOWER_BLUE)

        # End of map
        self.end_of_map = (self.tile_map.width * self.tile_map.tile_width) * TILE_SCALING

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()

        self.gui_camera.use()
        self.score_text.draw()

    def on_update(self, dt):
        self.physics_engine.update()

        # Coin collisions
        coin_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Coins"]
        )

        for coin in coin_list:
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)
            self.score += 75
            self.score_text.text = f"Score: {self.score}"

        # Death
        if arcade.check_for_collision_with_list(self.player_sprite, self.scene["Don't Touch"]):
            arcade.play_sound(self.gameover_sound)
            self.setup()

        # Finish level
        if self.player_sprite.center_x >= self.end_of_map:
            self.level += 1
            global game_state
            game_state = self.level
            next_level = GameView(level=self.level)
            next_level.setup()
            self.window.show_view(next_level)

        self.camera.position = self.player_sprite.position

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.UP, arcade.key.W):
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        if key in (arcade.key.LEFT, arcade.key.A):
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        if key in (arcade.key.RIGHT, arcade.key.D):
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        if key == arcade.key.ESCAPE:
            start = StartView()
            self.window.show_view(start)
        if key == arcade.key.R:
            global game_state
            game_state = 0
            start_view = StartView()
            self.window.show_view(start_view)

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A, arcade.key.RIGHT, arcade.key.D):
            self.player_sprite.change_x = 0



# ─────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────

def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    
    start_view = StartView()
    window.show_view(start_view)

    arcade.run()
    

if __name__ == "__main__":
    main()
