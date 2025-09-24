# Biomass bot
import random
from uwapi import *
from uwapi.interop import *
# from python.uwapi import * # this helps with autocomplete in IDE, I use it when editing the file

ATTACK_UNIT_LIMIT = 26
MINE_LIMIT = 2
INCUBATOR_LIMIT = 3
DEFENSE_PERIMETER = 300

def build_base(bot):
    consider_repair(bot)
    if bot.game_phase == "early":
        build_base_early(bot)
    elif bot.game_phase == "mid":
        build_base_mid(bot)

def build_base_early(bot):
    tree_count = bot.get_entities_count("nutritree")
    phytomorph_count = bot.get_entities_count("phytomorph")
    expected_trees = (phytomorph_count + 1) * 4
    missing_tree = expected_trees - tree_count
    # uw_game.log_info("missing trees: "+str(missing_tree))
    if missing_tree > 0:
        bot.build(bot.prototypes["Construction"]["nutritree"],
                  position=random.choice(uw_map.area_neighborhood(bot.start_position, 60+(tree_count*5))),
                  max_ghosts=max(2, uw_world.my_force_statistics().logisticsUnitsIdle/2))

    missing_phytomorph = (tree_count / 4) - phytomorph_count + 1
    if missing_phytomorph >= 1:
        if phytomorph_count == 0:
            bot.build(bot.prototypes["Construction"]["phytomorph"], recipe_id=bot.prototypes["Recipe"]["jumpscare"])
        elif phytomorph_count == 1:
            bot.build(bot.prototypes["Construction"]["phytomorph"], recipe_id=bot.prototypes["Recipe"]["maggot"])
        # elif phytomorph_count % 3 == 2:
        #     bot.build(bot.prototypes["Construction"]["phytomorph"], recipe_id=bot.prototypes["Recipe"]["venomite"])
        else:
            bot.build(bot.prototypes["Construction"]["phytomorph"], recipe_id=bot.prototypes["Recipe"]["venomite"], max_ghosts=3)

def build_base_mid(bot):
    mine_count = bot.get_entities_count("deeproot")
    if mine_count < 1:
        bot.build(bot.prototypes["Construction"]["deeproot"], priority=Priority.High)
    if mine_count < MINE_LIMIT:
        bot.build(bot.prototypes["Construction"]["deeproot"])

    incubator_count = bot.get_entities_count("incubator")
    if mine_count > 0 and incubator_count == 0:
        bot.build(bot.prototypes["Construction"]["incubator"], recipe_id=bot.prototypes["Recipe"]["sunbeam"], priority=Priority.High)
    if mine_count > 1 and incubator_count < INCUBATOR_LIMIT:
        bot.build(bot.prototypes["Construction"]["incubator"], recipe_id=bot.prototypes["Recipe"]["rhino"], priority=Priority.High)

    build_base_early(bot)

def update_game_phase(bot):
    if bot.game_phase == "early" and bot.get_entities_count("phytomorph") >= 3:
        bot.game_phase = "mid"
        bot.rally_point = random.choice(uw_map.area_neighborhood(bot.start_position, 200)),
    if bot.game_phase != "early" and (bot.get_entities_count("phytomorph") < 3 or bot.get_entities_count("nutritree") < 10):
        bot.game_phase = "early"
        bot.rally_point = bot.start_position

def consider_repair(bot):
    for own in bot.get_constructions("nutritree"):
        # uw_commands.order(own.id, uw_commands.self_destruct(own.id))
        if own.Priority.priority == Priority.Disabled:
            uw_commands.self_destruct(own.id)
    nearest_enemy = bot.get_nearest_enemy()
    if uw_map.distance_estimate(nearest_enemy.pos(), bot.start_position) > DEFENSE_PERIMETER + 50:
        for own in bot.get_constructions():
            uw_commands.set_priority(own.id, Priority.Normal)

def consider_attack(bot):
    nearest_enemy = bot.get_nearest_enemy()
    if (len(bot.get_own_units()) > ATTACK_UNIT_LIMIT
            or uw_map.distance_estimate(nearest_enemy.pos(), bot.start_position) < DEFENSE_PERIMETER) :
        bot.attack_single_nearest_enemy()
    else:
        bot.send_units_to(bot.get_own_units(), bot.start_position)

def on_update_biomass(bot):
    bot.find_main_base()

    match (
            bot.work_step % 10
    ):  # save some cpu cycles by splitting work over multiple steps
        case 1:
            update_game_phase(bot)
        case 2:
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
