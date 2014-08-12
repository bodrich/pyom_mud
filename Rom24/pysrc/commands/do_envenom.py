import logging

logger = logging.getLogger()

import random
import merc
import interp
import const
import handler_game
import state_checks


# for poisoning weapons and food/drink
def do_envenom(ch, argument):
    # find out what
    if not argument:
        ch.send("Envenom what item?\n")
        return
    item = ch.get_item_list(argument, ch.contents)
    if not item:
        ch.send("You don't have that item.\n")
        return
    skill = ch.get_skill('envenom')
    if skill < 1:
        ch.send("Are you crazy? You'd poison yourself!\n")
        return
    if item.item_type == merc.ITEM_FOOD or item.item_type == merc.ITEM_DRINK_CON:
        if item.bless or item.burn_proof:
            handler_game.act("You fail to poison $p.", ch, item, None, merc.TO_CHAR)
            return
        if random.randint(1, 99) < skill:  # success!
            handler_game.act("$n treats $p with deadly poison.", ch, item, None, merc.TO_ROOM)
            handler_game.act("You treat $p with deadly poison.", ch, item, None, merc.TO_CHAR)
            if not item.value[3]:
                item.value[3] = 1
                if ch.is_pc():
                    ch.check_improve( "envenom", True, 4)
            state_checks.WAIT_STATE(ch, const.skill_table["envenom"].beats)
            return
        handler_game.act("You fail to poison $p.", ch, item, None, merc.TO_CHAR)
        if not item.value[3]:
            if ch.is_pc():
                ch.check_improve( "envenom", False, 4)
            state_checks.WAIT_STATE(ch, const.skill_table["envenom"].beats)
            return
    if item.item_type == merc.ITEM_WEAPON:
        if item.flaming or item.frost or item.vampiric or item.sharp or item.vorpal or item.shocking or item.bless \
                or item.burn_proof:
            handler_game.act("You can't seem to envenom $p.", ch, item, None, merc.TO_CHAR)
            return
        if item.value[3] < 0 or const.attack_table[item.value[3]].damage == merc.DAM_BASH:
            ch.send("You can only envenom edged weapons.\n")
            return
        if state_checks.IS_WEAPON_STAT(item, merc.WEAPON_POISON):
            handler_game.act("$p is already envenomed.", ch, item, None, merc.TO_CHAR)
            return
        percent = random.randint(1, 99)
        if percent < skill:
            af = handler_game.AFFECT_DATA()
            af.where = merc.TO_WEAPON
            af.type = "poison"
            af.level = ch.level * percent // 100
            af.duration = ch.level // 2 * percent // 100
            af.location = 0
            af.modifier = 0
            af.bitvector = merc.WEAPON_POISON
            item.affect_add(af)

            handler_game.act("$n coats $p with deadly venom.", ch, item, None, merc.TO_ROOM)
            handler_game.act("You coat $p with venom.", ch, item, None, merc.TO_CHAR)
            if ch.is_pc():
                ch.check_improve( "envenom", True, 3)
            state_checks.WAIT_STATE(ch, const.skill_table["envenom"].beats)
            return
        else:
            handler_game.act("You fail to envenom $p.", ch, item, None, merc.TO_CHAR)
            if ch.is_pc():
                ch.check_improve("envenom", False, 3)
            state_checks.WAIT_STATE(ch, const.skill_table["envenom"].beats)
            return
    handler_game.act("You can't poison $p.", ch, item, None, merc.TO_CHAR)
    return


interp.register_command(interp.cmd_type('envenom', do_envenom, merc.POS_RESTING, 0, merc.LOG_NORMAL, 1))
