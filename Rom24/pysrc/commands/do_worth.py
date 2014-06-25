import merc
import interp


def do_worth(ch, argument):
    if merc.IS_NPC(ch):
        ch.send("You have %ld gold and %ld silver.\n" % (ch.gold, ch.silver))
        return
    ch.send("You have %ld gold, %ld silver, and %d experience (%d exp to level).\n" % (
        ch.gold, ch.silver, ch.exp, (ch.level + 1) * ch.exp_per_level(ch.pcdata.points) - ch.exp))

interp.cmd_table['worth'] = interp.cmd_type('worth', do_worth, merc.POS_SLEEPING, 0, merc.LOG_NORMAL, 1)