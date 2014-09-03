__author__ = 'quixadhal'

import logging

logger = logging.getLogger()

import merc
import interp
import game_utils
import sys_utils
import instance
import world_classes
import handler_room
import handler_item
import handler_npc

previous_snapshot = None


def do_driver(ch, argument):
    global previous_snapshot

    output = ''
    string, arg = game_utils.read_word(argument)

    current_snapshot = sys_utils.ResourceSnapshot()
    output += current_snapshot.log_data(previous=previous_snapshot, do_indent=False)
    previous_snapshot = current_snapshot
    output += '\n\n'
    output += '%-12s %8s %8s %8s  %8s %8s %8s\n' % ('', 'Areas', 'Rooms', 'Shops', 'Items', 'NPCs', 'Players')
    output += '%-12s %8s %8s %8s  %8s %8s %8s\n' % ('' * 12, '-' * 8, '-' * 8, '-' * 8, '-' * 8, '-' * 8, '-' * 8)
    output += '%-12s %8d %8d %8d  %8d %8d %8s\n' % ('Templates:', world_classes.Area.template_count,
                                                    handler_room.Room.template_count, len(instance.shop_templates),
                                                    handler_item.Items.template_count, handler_npc.Npc.template_count,
                                                    '')
    output += '%-12s %8d %8d %8d  %8d %8d %8d\n' % ('Instances:', world_classes.Area.instance_count,
                                                    handler_room.Room.instance_count, len(instance.shops),
                                                    handler_item.Items.instance_count, handler_npc.Npc.instance_count,
                                                    len(merc.descriptor_list))
    output += '\n'
    ch.send(output)


interp.register_command(interp.cmd_type('driver', do_driver, merc.POS_DEAD, merc.IM, merc.LOG_NORMAL, 1))
