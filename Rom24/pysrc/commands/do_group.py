import merc
import interp


def do_group(ch, argument):
    argument, arg = merc.read_word(argument)
    if not arg:
        leader = ch.leader if ch.leader else ch
        ch.send("%s's group:\n" % merc.PERS(leader, ch) )

        for gch in merc.char_list:
            if gch.is_same_group(ch):
                ch.send( "[%2d %s] %-16s %4d/%4d hp %4d/%4d mana %4d/%4d mv %5d xp\n" % (
                          gch.level,
                          "Mob" if merc.IS_NPC(gch) else gch.guild.who_name,
                          merc.PERS(gch, ch),
                          gch.hit, gch.max_hit,
                          gch.mana, gch.max_mana,
                          gch.move, gch.max_move,
                          gch.exp))
        return
    victim = ch.get_char_room(arg)
    if not victim:
        ch.send("They aren't here.\n")
        return
    if ch.master or (ch.leader and ch.leader != ch):
        ch.send("But you are following someone else:!\n")
        return
    if victim.master != ch and ch != victim:
        merc.act("$N isn't following you.", ch, None, victim, merc.TO_CHAR, merc.POS_SLEEPING)
        return
    if merc.IS_AFFECTED(victim, merc.AFF_CHARM):
        ch.send("You can't remove charmed mobs from your group.\n")
        return
    if merc.IS_AFFECTED(ch, AFF_CHARM):
        merc.act("You like your master too much to leave $m!", ch, None, victim, merc.TO_VICT, merc.POS_SLEEPING)
        return
    if victim.is_same_group(ch) and ch != victim:
        victim.leader = None
        merc.act("$n removes $N from $s group.", ch, None, victim, merc.TO_NOTVICT, merc.POS_RESTING)
        merc.act("$n removes you from $s group.", ch, None, victim, merc.TO_VICT, merc.POS_SLEEPING)
        merc.act("You remove $N from your group.", ch, None, victim, merc.TO_CHAR, merc.POS_SLEEPING)
        return
    victim.leader = ch
    merc.act("$N joins $n's group.", ch, None, victim, merc.TO_NOTVICT, merc.POS_RESTING)
    merc.act("You join $n's group.", ch, None, victim, merc.TO_VICT, merc.POS_SLEEPING)
    merc.act("$N joins your group.", ch, None, victim, merc.TO_CHAR, merc.POS_SLEEPING)
    return

interp.cmd_table['group'] = interp.cmd_type('group', do_group, merc.POS_SLEEPING, 0, merc.LOG_NORMAL, 1)