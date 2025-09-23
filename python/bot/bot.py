import os
import random
import time
from uwapi import *
from uwapi.interop import *

# from python.uwapi import * # this helps with autocomplete in IDE, I use it when editing the file


class Bot:
    is_configured: bool = False
    work_step: int = 0  # save some cpu cycles by splitting work over multiple steps
    prototypes = {}
    start_position = None

    def __init__(self):
        uw_events.on_update(self.on_update)

    def find_main_base(self):
        if self.start_position:
            return
        self.start_position = uw_world.entity(
            uw_world.my_force_id()
        ).ForceDetails.startingPosition
        uw_game.log_info(
            "bot-darik-petr found main building at " + str(self.start_position)
        )

    def build(
        self,
        construction_id: int,
        recipe_id: int = 0,
        position: int = -1,
        priority: UwPriorityEnum = UwPriorityEnum.Normal,
    ):
        uw_game.log_info(
            "bot-darik-petr build "
            + str(construction_id)
            + " with priority "
            + str(priority)
        )
        # find closest viable position for miner:
        if position < 0:
            position = self.start_position
        p = uw_world.find_construction_placement(
            construction_id, position, recipe_id
        )  # recipe id is optional
        if p == INVALID:
            return
        uw_game.log_info(
            "bot-darik-petr found placement for building "
            + str(construction_id)
            + " at "
            + str(p)
        )

        # place construction:
        uw_commands.place_construction(
            construction_id, p, 0, recipe_id, priority
        )  # yaw, recipe, and priority are optional

        # # recipe and priority can be changed later:
        # uw_commands.set_recipe(own_id, ANOTHER_RECIPE_ID)
        # uw_commands.set_priority(own_id, Priority.Normal)

    def find_first_entity(self, name):
        entities = [
            x
            for x in uw_world.entities().values()
            if x.own()
            and x.Unit is not None
            and x.proto().data.get("name") == name
        ]

        if len(entities) > 0:
            return entities[0].pos()

        return None

    def attack_nearest_enemies(self):
        own_units = [
            x
            for x in uw_world.entities().values()
            if x.own() and x.Unit is not None and x.proto().data.get("dps", 0) > 0
        ]
        if not own_units:
            return
        enemy_units = [
            x for x in uw_world.entities().values() if x.enemy() and x.Unit is not None
        ]
        if not enemy_units:
            return
        for own in own_units:
            if len(uw_commands.orders(own.id)) == 0:
                enemy = min(
                    enemy_units,
                    key=lambda x: uw_map.distance_estimate(own.pos(), x.pos()),
                )
                uw_commands.order(own.id, uw_commands.fight_to_entity(enemy.id))

    def assign_random_recipes(self):
        for own in uw_world.entities().values():
            if not own.own() or own.Unit is None or own.Recipe is not None:
                continue
            # recipes = self.prototypes["Recipe"]["ATV"] # Worker recipe
            recipes = own.proto().data.get("recipes", [])
            if recipes:
                recipe = random.choice(recipes)
                uw_commands.set_recipe(own.id, recipe)

    # Requires prototypes.md generated via prototypes.py script
    def load_prototypes(self):
        current_section = None

        with open("prototypes.md", "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("##"):  # new section header
                    current_section = line.lstrip("#").strip()
                    self.prototypes[current_section] = {}
                elif ":" in line and current_section is not None:
                    key, value = line.split(":", 1)
                    self.prototypes[current_section][key.strip()] = int(value.strip())

    def load_race(self):
        filename = "race.md"
        race = "biomass"  # default
        if os.path.exists(filename):
            with open(filename, "r") as f:
                race = f.read()
        else:
            with open(filename, "w") as f:
                f.write(race)
        return race

    def configure(self):
        # auto start the game if available
        if (
            self.is_configured
            and uw_game.game_state() == GameState.Session
            and uw_world.is_admin()
        ):
            time.sleep(3)  # give the observer enough time to connect
            uw_admin.start_game()
            return
        # is configuring possible?
        if (
            self.is_configured
            or uw_game.game_state() != GameState.Session
            or uw_world.my_player_id() == 0
        ):
            return
        self.is_configured = True
        uw_game.log_info("configuration start")
        uw_game.set_player_name("bot-darik-petr")
        uw_game.player_join_force(0)  # create new force
        uw_game.set_force_color(1, 0, 0)
        self.load_prototypes()

        # choose race
        race = self.load_race()
        uw_game.log_info(f"Loaded race: \033[93m{race}\033[0m")
        uw_game.set_force_race(
            self.prototypes["Race"][race]
        )  # todo championship => random selection (I guess)

        # todo add bot separation by selected force
        if uw_world.is_admin():
            # uw_admin.set_map_selection("planets/tetrahedron.uwmap")
            uw_admin.set_map_selection("planets/disk.uwmap")
            # uw_admin.set_map_selection("special/risk.uwmap")
            uw_admin.add_ai()
            uw_admin.set_automatic_suggested_camera_focus(True)
        uw_game.log_info("configuration done")

    def on_update(self, stepping: bool):
        self.configure()
        if not stepping:
            return
        self.work_step += 1

        self.find_main_base()

        match (
            self.work_step % 10
        ):  # save some cpu cycles by splitting work over multiple steps
            case 1:
                self.attack_nearest_enemies()
            case 5:
                # self.assign_random_recipes()
                self.build(self.prototypes["Construction"]["drill"])
            case 6:
                if self.find_first_entity("refinery") is not None:
                    return
                p = self.find_first_entity("drill")
                if p is not None:
                    self.build(self.prototypes["Construction"]["refinery"], 0, p)

    def run(self):
        uw_game.log_info("bot-darik-petr start")
        if not uw_game.try_reconnect():
            uw_game.set_connect_start_gui(True, "--observer 2")
            if not uw_game.connect_environment():
                # automatically select map and start the game from here in the code
                if True:
                    uw_game.connect_new_server(0, "", "--allowUwApiAdmin 1")
                else:
                    uw_game.connect_new_server()
        uw_game.log_info("bot-darik-petr done")
