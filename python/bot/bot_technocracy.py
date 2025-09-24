# Technocracy bot


import random


def on_update_technocracy(bot):
    bot.find_main_base()

    match (
        bot.work_step % 10
    ):  # save some cpu cycles by splitting work over multiple steps
        case 1:
            drillsCount = bot.get_entities_count("drill")
            if drillsCount >= 3:
                return
            metal = 3161943147
            oil = bot.prototypes["Recipe"]["oil"]
            recipes = [
                metal,
                metal,
                oil,
            ]
            drill = 3871229408
            bot.build(drill, recipes[drillsCount - 1])
        case 2:
            if bot.get_entities_count("refinery") >= 1:
                return
            refinery = bot.prototypes["Construction"]["refinery"]
            p = bot.find_recipe_id(bot.prototypes["Recipe"]["oil"], 1)
            if p is not None:
                bot.build(refinery, 0, p)
        case 3:
            factoriesCount = bot.get_entities_count("bots factory")
            if (
                bot.get_units_count("drill") < 3
                or bot.get_units_count("refinery") < 1
                or factoriesCount >= 3
            ):
                return
            botsFactory = bot.prototypes["Construction"]["bots factory"]
            lurker = bot.prototypes["Recipe"]["lurker"]
            juggernaut = bot.prototypes["Recipe"]["juggernaut"]
            tripod = bot.prototypes["Recipe"]["tripod"]
            recipes = [
                juggernaut,
                lurker,
                tripod,
            ]
            metal = 3161943147
            pos1 = bot.find_recipe_id(metal, 1)
            pos2 = bot.find_recipe_id(metal, 2)
            pos = pos1
            if factoriesCount % 2 == 0:
                pos = pos2
            bot.build(botsFactory, recipes[factoriesCount - 1], pos)
        case 4:
            fabricatorsCount = bot.get_entities_count("fabricator")
            if (
                bot.get_units_count("drill") < 3
                or bot.get_units_count("refinery") < 1
                or bot.get_entities_count("bots factory") < 3
                or fabricatorsCount >= 2
            ):
                return
            fabricator = bot.prototypes["Construction"]["fabricator"]
            p = bot.find_recipe_id(bot.prototypes["Recipe"]["oil"], 1)
            if p is not None:
                bot.build(fabricator, 0, p)
        case 5:
            fabricatorsCount = bot.get_entities_count("fabricator")
            if fabricatorsCount < 2 or len(bot.get_constructions("talos")) > 0:
                return
            talos = bot.prototypes["Construction"]["talos"]
            bot.build(talos, 0, bot.find_random_building())
        case 6:
            bot.set_normal_priority_to_all()
        case 9:
            if bot.get_entities_count("lurker") > 10:
                bot.attack_nearest_enemies()
            else:
                bot.attack_close_enemies(400)
