# Biomass bot
import random
from uwapi import *
from uwapi.interop import *
# from python.uwapi import * # this helps with autocomplete in IDE, I use it when editing the file

def build_base(bot):
    tree_count = bot.get_entities_count("nutritree")
    phytomorph_count = bot.get_entities_count("phytomorph")
    expected_trees = (phytomorph_count + 1) * 4
    missing_tree = expected_trees - tree_count
    # uw_game.log_info("missing trees: "+str(missing_tree))
    if missing_tree > 0:
        bot.build(bot.prototypes["Construction"]["nutritree"], position=random.choice(uw_map.area_neighborhood(bot.start_position, 120)), max_ghosts=uw_world.my_force_statistics().logisticsUnitsIdle/2)

    missing_phytomorph = 3 - phytomorph_count
    # uw_game.log_info("missing phyts: "+str(missing_phytomorph))
    if missing_phytomorph == 3:
        bot.build(bot.prototypes["Construction"]["phytomorph"], recipe_id=bot.prototypes["Recipe"]["jumpscare"], max_ghosts=1)
    if missing_phytomorph == 2:
        bot.build(bot.prototypes["Construction"]["phytomorph"], recipe_id=bot.prototypes["Recipe"]["jumpscare"], max_ghosts=1)
    if missing_phytomorph == 1:
        bot.build(bot.prototypes["Construction"]["phytomorph"], recipe_id=bot.prototypes["Recipe"]["jumpscare"], max_ghosts=1)
    # if missing_phytomorph == 1:
    #     bot.build(bot.prototypes["Construction"]["phytomorph"], recipe_id=bot.prototypes["Recipe"]["venomite"])


def update_game_phase(bot):
    pass


def consider_attack(bot):
    if (bot.get_entities_count("jumpscare") > 20):
        bot.attack_nearest_enemies()


def on_update_biomass(bot):
    bot.find_main_base()

    match (
            bot.work_step % 10
    ):  # save some cpu cycles by splitting work over multiple steps
        case 1:
            update_game_phase(bot)
            if bot.game_phase == "early":
                build_base(bot)
        # case 5:
        #     # self.assign_random_recipes()
        #     bot.build(bot.prototypes["Construction"]["drill"])
        case 6:
            consider_attack(bot)
        #     if bot.get_constructions_count("refinery") is not None:
        #         return
        #     p = bot.find_first_entity("drill")
        #     if p is not None:
        #         bot.build(bot.prototypes["Construction"]["refinery"], 0, p)
