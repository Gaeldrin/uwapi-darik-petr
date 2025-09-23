# Technocracy bot

def on_update_technocracy(bot):
    match (
            bot.work_step % 10
    ):  # save some cpu cycles by splitting work over multiple steps
        case 1:
            if bot.get_constructions_count("drill") >= 4:
                return
            bot.build(bot.prototypes["Construction"]["drill"])
        case 2:
            if bot.get_constructions_count("refinery") >= 1:
                return
            refinery = bot.prototypes["Construction"]["refinery"]
            bot.build(refinery, 0, bot.find_drill_id("drill", 1))
        case 3:
            if (
                    bot.get_constructions_count("refinery") == 0
                    or bot.get_constructions_count("bots factory") >= 4
            ):
                return

            botsFactory = bot.prototypes["Construction"]["bots factory"]
            ytag = bot.prototypes["Recipe"]["yatag"]
            lurker = bot.prototypes["Recipe"]["lurker"]
            juggernaut = bot.prototypes["Recipe"]["juggernaut"]
            bot.build(botsFactory, ytag, bot.find_drill_id("drill", 1))
            bot.build(botsFactory, ytag, bot.find_drill_id("drill", 2))
            bot.build(botsFactory, lurker, bot.find_drill_id("drill", 1))
            bot.build(botsFactory, juggernaut, bot.find_drill_id("drill", 2))
        case 9:
            bot.attack_nearest_enemies()
