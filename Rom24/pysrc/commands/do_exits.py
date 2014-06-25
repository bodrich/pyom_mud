import merc
import interp


# * Thanks to Zrin for auto-exit part.
def do_exits(ch, argument):
    fAuto = argument == "auto"
    buf = ''
    if not merc.check_blind(ch):
        return
    if fAuto:
        buf += "[Exits:"
    elif merc.IS_IMMORTAL(ch):
        buf += "Obvious exits from room %d:\n" % ch.in_room.vnum
    else:
        buf += "Obvious exits:\n"
    found = False
    for door, pexit in enumerate(ch.in_room.exit):
        if pexit and pexit.to_room and (merc.IS_SET(ch.act, merc.PLR_OMNI) or (ch.can_see_room(pexit.to_room) \
        and not merc.IS_SET(pexit.exit_info, merc.EX_CLOSED))):
            found = True
            if fAuto:
                if merc.IS_SET(pexit.exit_info, merc.EX_CLOSED):
                    buf += " [%s]" % (merc.dir_name[door])
                else:
                    buf += " %s" % merc.dir_name[door]
                if merc.IS_SET(ch.act, merc.PLR_OMNI):
                    buf += "(%d)" % pexit.to_room.vnum
            else:
                buf += "%-5s - %s" % (merc.dir_name[door].capitalize(),
                  "Too dark to tell" if pexit.to_room.is_dark() else pexit.to_room.name)
                if merc.IS_IMMORTAL(ch): buf += " (room %d)\n" % pexit.to_room.vnum
                else: buf += "\n"
    if not found:
        buf += " none" if fAuto else "None.\n"
    if fAuto:
        buf += "]\n"
    ch.send(buf)
    return

interp.cmd_table['exits'] = interp.cmd_type('exits', do_exits, merc.POS_RESTING, 0, merc.LOG_NORMAL, 1)