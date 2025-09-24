import os
import random
import time
from uwapi import *
from uwapi.interop import *
from .bot_biomass import on_update_biomass
from .bot_technocracy import on_update_technocracy
# from python.uwapi import * # this helps with autocomplete in IDE, I use it when editing the file


class Bot:
    is_configured: bool = False
    work_step: int = 0  # save some cpu cycles by splitting work over multiple steps
    prototypes = {}
    start_position = None
    race = None
    game_phase = "early"  # can also contain "mid" or "late"

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
        max_ghosts: int = -1,
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

        ghosts = self.get_construction_count()
        uw_game.log_info("bot-darik-petr found ghosts " + str(ghosts))
        if max_ghosts == -1 or max_ghosts > ghosts:
            # place construction:
            uw_commands.place_construction(
                construction_id, p, 0, recipe_id, priority
            )  # yaw, recipe, and priority are optional

        # # recipe and priority can be changed later:
        # uw_commands.set_recipe(own_id, ANOTHER_RECIPE_ID)
        # uw_commands.set_priority(own_id, Priority.Normal)

    def set_normal_priority_to_all(self):
        entities = [
            x
            for x in uw_world.entities().values()
            if x.own() and x.Unit is not None and x.proto().data.get("dps", 0) < 0.1
        ]

        for i in entities:
            uw_commands.set_priority(i.id, Priority.Normal)

    def find_first_entity(self, name):
        entities = [
            x
            for x in uw_world.entities().values()
            if x.own() and x.Unit is not None and x.proto().data.get("name") == name
        ]

        if len(entities) > 0:
            return entities[0].pos()

        return None

    def find_recipe_id(self, recipeId, id):
        entities = [
            x
            for x in uw_world.entities().values()
            if x.own()
            and x.Unit is not None
            and x.Recipe is not None
            and x.proto().data.get("name") == "drill"
            and x.Recipe.recipe == recipeId
        ]

        if len(entities) >= id:
            return entities[id - 1].pos()

        return None

    def find_drill_id(self, name, id):
        entities = [
            x
            for x in uw_world.entities().values()
            if x.own() and x.Unit is not None and x.proto().data.get("name") == name
        ]

        if len(entities) >= id:
            return entities[id - 1].pos()

        return None

    def find_random_building(self):
        entities = [
            x
            for x in uw_world.entities().values()
            if x.own() and x.Unit is not None and x.proto().data.get("dps", 0) < 0.1
        ]

        return random.choice(entities).pos()

    def get_constructions(self, name: str = "everything"):
        entities = [
            x
            for x in uw_world.entities().values()
            if x.own()
            and x.type() == PrototypeType.Construction
            and (name == "everything" or x.proto().data.get("name") == name)
        ]
        return entities

    def get_construction_count(self, name: str = "everything"):
        return len(self.get_constructions(name))

    def get_entities_count(self, name):
        entities = [
            x
            for x in uw_world.entities().values()
            if x.own() and x.Proto is not None and x.proto().data.get("name") == name
        ]

        return len(entities)

    def get_units_count(self, name):
        entities = [
            x
            for x in uw_world.entities().values()
            if x.own() and x.Unit is not None and x.proto().data.get("name") == name
        ]

        return len(entities)

    def get_own_units(self):
        return [
            x
            for x in uw_world.entities().values()
            if x.own() and x.Unit is not None and x.proto().data.get("dps", 0) > 0.1
        ]

    # any enemy counts - units, buildings
    def get_enemy_units(self):
        return [
            x for x in uw_world.entities().values() if x.enemy() and x.Unit is not None
        ]

    def get_enemy_buildings(self):
        return [
            x
            for x in uw_world.entities().values()
            if x.enemy()
            and x.Unit is not None
            and x.proto().data.get("movementSpeed", 0) < 0.01
        ]

    def get_nearest_enemy(self):
        enemy_units = self.get_enemy_units()
        if not enemy_units:
            return None
        enemy = min(
            enemy_units,
            key=lambda x: uw_map.distance_estimate(x.pos(), self.start_position),
        )

        return enemy

    def send_units_to(self, own_units: [], position: int):
        for own in own_units:
            if uw_map.distance_estimate(own.pos(), position) > 200:
                uw_game.log_info(str(own.id) + " move to " + str(position))
                uw_commands.order(own.id, uw_commands.run_to_position(position))

    def attack_single_nearest_enemy(self):
        own_units = self.get_own_units()
        if not own_units:
            return
        enemy_units = self.get_enemy_units()
        if not enemy_units:
            return
        closest_enemy = None
        for own in own_units:
            if (
                own.proto().id == self.prototypes["Unit"]["overlord"]
                or own.proto().id == self.prototypes["Unit"]["control core"]
            ):
                enemy = min(
                    enemy_units,
                    key=lambda x: uw_map.distance_estimate(own.pos(), x.pos()),
                )
                closest_enemy = enemy
        for own in own_units:
            if len(uw_commands.orders(own.id)) == 0:
                uw_commands.order(own.id, uw_commands.fight_to_entity(closest_enemy.id))

    def attack_nearest_enemies(self):
        own_units = self.get_own_units()
        if not own_units:
            return
        enemy_units = self.get_enemy_units()
        if not enemy_units:
            return
        for own in own_units:
            if len(uw_commands.orders(own.id)) == 0:
                enemy = min(
                    enemy_units,
                    key=lambda x: uw_map.distance_estimate(own.pos(), x.pos()),
                )
                uw_commands.order(own.id, uw_commands.fight_to_entity(enemy.id))

    def attack_close_enemies(self, distance):
        own_units = self.get_own_units()
        if not own_units:
            return
        enemy_units = self.get_enemy_units()
        if not enemy_units:
            return
        for own in own_units:
            if len(uw_commands.orders(own.id)) == 0:
                enemy = min(
                    enemy_units,
                    key=lambda x: uw_map.distance_estimate(own.pos(), x.pos()),
                )
                if uw_map.distance_estimate(own.pos(), enemy.pos()) < distance:
                    uw_commands.order(own.id, uw_commands.fight_to_entity(enemy.id))

    def go_to_random_building(self):
        own_units = self.get_own_units()
        if not own_units:
            return

        buildings = [
            x
            for x in uw_world.entities().values()
            if x.own() and x.Unit is not None and x.proto().data.get("dps", 0) < 0.1
        ]

        for own in own_units:
            if len(uw_commands.orders(own.id)) == 0:
                target = random.choice(buildings).id
                uw_commands.order(own.id, uw_commands.fight_to_entity(target))

    def attack_nearest_building(self):
        own_units = self.get_own_units()
        if not own_units:
            return
        enemy_units = self.get_enemy_buildings()
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
        time.sleep(0.4)
        uw_game.player_join_force(0)  # create new force
        uw_game.set_force_color(1, 0, 0)
        self.load_prototypes()

        # choose race
        self.race = self.load_race()
        uw_game.log_info(f"Loaded race: \033[93m{self.race}\033[0m")
        uw_game.set_force_race(
            self.prototypes["Race"][self.race]
        )  # todo championship => random selection (I guess)

        time.sleep(1)
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

        if self.race == "biomass":
            on_update_biomass(self)
        else:
            on_update_technocracy(self)

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
