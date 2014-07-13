import logging

logger = logging.getLogger()

import random
import game_utils
import merc
import const
import interp
import fight
import state_checks


def do_trip(ch, argument):
    arghold, arg = game_utils.read_word(argument)
    chance = ch.get_skill('trip')
    if chance == 0 or (ch.is_npc() and not ch.off_flags.is_set(merc.OFF_TRIP)) \
    or ( not ch.is_npc() and ch.level < const.skill_table['trip'].skill_level[ch.guild.name]):
        ch.send("Tripping?  What's that?\n\r")
        return
    if not arg:
        victim = ch.fighting
        if victim is None:
            ch.send("But you aren't fighting anyone!\n\r")
            return
    else:
        victim = ch.get_char_room(arg)
        if victim is None:
            ch.send("They aren't here.\n\r")
            return
    if fight.is_safe(ch,victim):
        return
    if victim.is_npc() and victim.fighting and not ch.is_same_group(victim.fighting):
        ch.send("Kill stealing is not permitted.\n\r")
        return
    if victim.is_affected( merc.AFF_FLYING):
        act("$S feet aren't on the ground.",ch,None,victim, merc.TO_CHAR)
        return
    if victim.position < merc.POS_FIGHTING:
        act("$N is already down.",ch,None,victim, merc.TO_CHAR)
        return
    if victim == ch:
        ch.send("You fall flat on your face!\n\r")
        state_checks.WAIT_STATE(ch,2 * const.skill_table['trip'].beats)
        act("$n trips over $s own feet!",ch,None,None, merc.TO_ROOM)
        return

    if ch.is_affected(merc.AFF_CHARM) and ch.master == victim:
        act("$N is your beloved master.",ch,None,victim, merc.TO_CHAR)
        return
    # modifiers */
    # size */
    if ch.size < victim.size:
        chance += (ch.size - victim.size) * 10  # bigger = harder to trip */

    # dex */
    chance += ch.stat(merc.STAT_DEX)
    chance -= victim.stat(merc.STAT_DEX) * 3 // 2

    # speed */
    if ch.off_flags.is_set(merc.OFF_FAST) or ch.is_affected(merc.AFF_HASTE):
        chance += 10
    if victim.off_flags.is_set(merc.OFF_FAST) or victim.is_affected( merc.AFF_HASTE):
        chance -= 20
    # level */
    chance += (ch.level - victim.level) * 2
    # now the attack */
    if random.randint(1,99) < chance:
        act("$n trips you and you go down!",ch,None,victim, merc.TO_VICT)
        act("You trip $N and $N goes down!",ch,None,victim, merc.TO_CHAR)
        act("$n trips $N, sending $M to the ground.",ch,None,victim, merc.TO_NOTVICT)
        ch.check_improve('trip',True,1)

        state_checks.DAZE_STATE(victim,2 * merc.PULSE_VIOLENCE)
        state_checks.WAIT_STATE(ch,const.skill_table['trip'].beats)
        victim.position = merc.POS_RESTING
        fight.damage(ch,victim,random.randint(2, 2 +  2 * victim.size),'trip', merc.DAM_BASH,True)
    else:
        fight.damage(ch,victim,0,'trip', merc.DAM_BASH,True)
        state_checks.WAIT_STATE(ch,const.skill_table['trip'].beats*2 // 3)
        ch.check_improve('trip',False,1)
    fight.check_killer(ch,victim)

interp.register_command(interp.cmd_type('trip', do_trip, merc.POS_FIGHTING, 0, merc.LOG_NORMAL, 1))
