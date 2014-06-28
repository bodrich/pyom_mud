import logging

logger = logging.getLogger()

import merc
import interp
import fight
import save
import game_utils
import handler_game
import state_checks


def do_deny(ch, argument):
    argument, arg = game_utils.read_word(argument)
    if not arg:
        ch.send("Deny whom?\n")
        return
    victim = ch.get_char_world(arg)
    if not victim:
        ch.send("They aren't here.\n")
        return
    if state_checks.IS_NPC(victim):
        ch.send("Not on NPC's.\n")
        return
    if victim.get_trust() >= ch.get_trust():
        ch.send("You failed.\n")
        return
    victim.act = state_checks.SET_BIT(victim.act, merc.PLR_DENY)
    victim.send("You are denied access!\n")
    handler_game.wiznet("$N denies access to %s" % victim.name, ch, None, merc.WIZ_PENALTIES, merc.WIZ_SECURE, 0)
    ch.send("OK.\n")
    save.save_char_obj(victim)
    fight.stop_fighting(victim, True)
    victim.do_quit("")
    return


interp.register_command(interp.cmd_type("deny", do_deny, merc.POS_DEAD, merc.L1, merc.LOG_ALWAYS, 1))