# Biomass bot

def on_update_biomass(bot):
    bot.find_main_base()

    match (
            bot.work_step % 10
    ):  # save some cpu cycles by splitting work over multiple steps
        case 1:
            bot.attack_nearest_enemies()
        case 5:
            # self.assign_random_recipes()
            bot.build(bot.prototypes["Construction"]["drill"])
        case 6:
            if bot.get_constructions_count("refinery") is not None:
                return
            p = bot.find_first_entity("drill")
            if p is not None:
                bot.build(bot.prototypes["Construction"]["refinery"], 0, p)
