import random
import logging
import random

logger = logging.getLogger()

import merc
import tables
import affects
import bit
import const
import fight
import game_utils
import handler_game
import immortal
import location
import state_checks

class Grouping:
    def __init__(self):
        super().__init__()
        self.master = 0
        self.leader = 0
        self.pet = 0
        self.group = 0
        self._clan = ""
    # * It is very important that this be an equivalence relation:
    # * (1) A ~ A
    # * (2) if A ~ B then B ~ A
    # * (3) if A ~ B  and B ~ C, then A ~ C
    def is_same_group(self, bch):
        if self is None or bch is None:
            return False

        if self.leader is not None:
            self = self.leader
        if bch.leader is not None:
            bch = bch.leader
        return self == bch

    @property
    def clan(self):
        try:
            return tables.clan_table[self._clan]
        except KeyError as e:
            return tables.clan_table[""]

    @clan.setter
    def clan(self, value):
        if value not in tables.clan_table:
            return
        self._clan = value

    def stop_follower(self):
        if not self.master:
            logger.error("BUG: Stop_follower: null master.")
            return

        if self.is_affected(merc.AFF_CHARM):
            self.affected_by.rem_bit(merc.AFF_CHARM)
            self.affect_strip('charm person')

        if self.master.can_see(self) and self.in_room:
            handler_game.act("$n stops following you.", self, None, self.master, merc.TO_VICT)
            handler_game.act("You stop following $N.", self, None, self.master, merc.TO_CHAR)
        if self.master.pet == self:
            self.master.pet = None
        self.master = None
        self.leader = None
        return

    def is_clan(ch):
        return ch.clan.name != ""

    def is_same_clan(ch, victim):
        if ch.clan.independent:
            return False
        else:
            return ch.clan == victim.clan

    def can_loot(ch, obj):
        if ch.is_immortal():
            return True
        if not obj.owner or obj.owner is None:
            return True
        owner = None
        for wch in merc.char_list:
            if wch.name == obj.owner:
                owner = wch
        if owner is None:
            return True
        if ch.name == owner.name:
            return True
        if not owner.is_npc() and owner.act.is_set(merc.PLR_CANLOOT):
            return True
        if ch.is_same_group(owner):
            return True
        return False


class Physical:
    def __init__(self):
        super().__init__()
        self.name = ""
        self.short_descr = ""
        self.long_descr = ""
        self.description = ""
        self.form = bit.Bit(flags=tables.form_flags)
        self.parts = bit.Bit(flags=tables.part_flags)
        self.size = 0
        self.material = ""


class Fight:
    def __init__(self):
        super().__init__()
        self.fighting = 0
        self.hitroll = 0
        self.damroll = 0
        self.dam_type = 17
        self.armor = [100, 100, 100, 100]
        self.wimpy = 0
        self.saving_throw = 0
        self.timer = 0
        self.wait = 0
        self.daze = 0
        self.hit = 20
        self.max_hit = 20
        self.imm_flags = bit.Bit(flags=tables.imm_flags)
        self.res_flags = bit.Bit(flags=tables.imm_flags)
        self.vuln_flags = bit.Bit(flags=tables.imm_flags)

    def check_immune(self, dam_type):
        immune = -1
        defence = merc.IS_NORMAL

        if dam_type is merc.DAM_NONE:
            return immune

        if dam_type <= 3:
            if self.imm_flags.is_set(merc.IMM_WEAPON):
                defence = merc.IS_IMMUNE
            elif self.res_flags.is_set(merc.RES_WEAPON):
                defence = merc.IS_RESISTANT
            elif self.vuln_flags.is_set(merc.VULN_WEAPON):
                defence = merc.IS_VULNERABLE
        else:  # magical attack */
            if self.imm_flags.is_set(merc.IMM_MAGIC):
                defence = merc.IS_IMMUNE
            elif self.res_flags.is_set(merc.RES_MAGIC):
                defence = merc.IS_RESISTANT
            elif self.vuln_flags.is_set(merc.VULN_MAGIC):
                defence = merc.IS_VULNERABLE

        bit = {merc.DAM_BASH: merc.IMM_BASH,
               merc.DAM_PIERCE: merc.IMM_PIERCE,
               merc.DAM_SLASH: merc.IMM_SLASH,
               merc.DAM_FIRE: merc.IMM_FIRE,
               merc.DAM_COLD: merc.IMM_COLD,
               merc.DAM_LIGHTNING: merc.IMM_LIGHTNING,
               merc.DAM_ACID: merc.IMM_ACID,
               merc.DAM_POISON: merc.IMM_POISON,
               merc.DAM_NEGATIVE: merc.IMM_NEGATIVE,
               merc.DAM_HOLY: merc.IMM_HOLY,
               merc.DAM_ENERGY: merc.IMM_ENERGY,
               merc.DAM_MENTAL: merc.IMM_MENTAL,
               merc.DAM_DISEASE: merc.IMM_DISEASE,
               merc.DAM_DROWNING: merc.IMM_DROWNING,
               merc.DAM_LIGHT: merc.IMM_LIGHT,
               merc.DAM_CHARM: merc.IMM_CHARM,
               merc.DAM_SOUND: merc.IMM_SOUND}
        if dam_type not in bit:
            return defence
        bit = bit[dam_type]

        if self.imm_flags.is_set(bit):
            immune = merc.IS_IMMUNE
        elif self.res_flags.is_set(bit) and immune is not merc.IS_IMMUNE:
            immune = merc.IS_RESISTANT
        elif self.vuln_flags.is_set(bit):
            if immune == merc.IS_IMMUNE:
                immune = merc.IS_RESISTANT
            elif immune == merc.IS_RESISTANT:
                immune = merc.IS_NORMAL
        else:
            immune = merc.IS_VULNERABLE

        if immune == -1:
            return defence
        else:
            return immune
            # * Retrieve a character's trusted level for permission checking.

class Communication:
    def __init__(self):
        super().__init__()
        self.reply = 0
        self.comm = bit.Bit(merc.COMM_COMBINE | merc.COMM_PROMPT, tables.comm_flags)

class Container:
    def __init__(self):
        super().__init__()
        self.contents = []
        self.carry_weight = 0
        self.carry_number = 0

    def can_carry_n(self):
        if not self.is_npc() and self.level >= merc.LEVEL_IMMORTAL:
            return 1000
        if self.is_npc() and self.act.is_set(merc.ACT_PET):
            return 0
        return merc.MAX_WEAR + 2 * self.stat(merc.STAT_DEX) + self.level

    # * Retrieve a character's carry capacity.
    def can_carry_w(self):
        if not self.is_npc() and self.level >= merc.LEVEL_IMMORTAL:
            return 10000000
        if self.is_npc() and self.act.is_set(merc.ACT_PET):
            return 0
        return const.str_app[self.stat(merc.STAT_STR)].carry * 10 + self.level * 25


class Living(immortal.Immortal, Fight, Grouping, Physical,
             location.Location, affects.Affects, Communication, Container):
    def __init__(self):
        super().__init__()
        self.id = 0
        self.instance_id = 0
        self.version = 5
        self.level = 0
        self.act = bit.Bit(merc.PLR_NOSUMMON, [tables.act_flags, tables.plr_flags])
        self._race = 'human'
        self._guild = None
        self.sex = 0
        self.level = 0
        # stats */
        self.perm_stat = [13 for x in range(merc.MAX_STATS)]
        self.mod_stat = [0 for x in range(merc.MAX_STATS)]
        self.mana = 100
        self.max_mana = 100
        self.move = 100
        self.max_move = 100
        self.gold = 0
        self.silver = 0
        self.exp = 0
        self.position = 0
        self.alignment = 0
        self.desc = None

    def send(self, str):
        pass

    def is_npc(self):
        return self.act.is_set(merc.ACT_IS_NPC)

    def is_good(self):
        return self.alignment >= 350

    def is_evil(self):
        return self.alignment <= -350

    def is_neutral(self):
        return not self.is_good() and not self.is_evil()

    def is_awake(self):
        return self.position > merc.POS_SLEEPING


    def check_blind(self):
        if not self.is_npc() and self.act.is_set(merc.PLR_HOLYLIGHT):
            return True

        if self.is_affected(merc.AFF_BLIND):
            self.send("You can't see a thing!\n\r")
            return False
        return True

    #/* command for retrieving stats */
    def stat(self, stat):
        stat_max = 0
        if self.is_npc() or self.level > merc.LEVEL_IMMORTAL:
            stat_max = 25
        else:
            stat_max = const.pc_race_table[self.race.name].max_stats[stat] + 4

            if self.guild.attr_prime == stat:
                stat_max += 2
            if self.race == const.race_table["human"]:
                stat_max += 1
            stat_max = min(stat_max, 25);
        return max(3, min(self.perm_stat[stat] + self.mod_stat[stat], stat_max))

    # Find a piece of eq on a character.
    def get_eq(self, iWear):
        if not self:
            return None
        obj = [obj for obj in self.contents if obj.wear_loc == iWear]
        if not obj:
            return None
        return obj[0]
    # * Equip a char with an obj.

    def equip(self, obj, iWear):
        if self.get_eq(iWear):
            logger.warning("Equip_char: already equipped (%d)." % iWear)
            return

        if (state_checks.IS_OBJ_STAT(obj, merc.ITEM_ANTI_EVIL) and self.is_evil()) \
                or (state_checks.IS_OBJ_STAT(obj, merc.ITEM_ANTI_GOOD) and self.is_good()) \
                or (state_checks.IS_OBJ_STAT(obj, merc.ITEM_ANTI_NEUTRAL) and self.is_neutral()):
            # Thanks to Morgenes for the bug fix here!
            handler_game.act("You are zapped by $p and drop it.", self, obj, None, merc.TO_CHAR)
            handler_game.act("$n is zapped by $p and drops it.", self, obj, None, merc.TO_ROOM)
            obj.from_char()
            obj.to_room(self.room_template)
            return

        for i in range(4):
            self.armor[i] -= obj.apply_ac(iWear, i)
        obj.wear_loc = iWear

        if not obj.enchanted:
            for paf in merc.global_instances[obj.instance_id].affected:
                if paf.location != merc.APPLY_SPELL_AFFECT:
                    self.affect_modify(paf, True)

        for paf in obj.affected:
            if paf.location == merc.APPLY_SPELL_AFFECT:
                self.affect_add(self, paf)
            else:
                self.affect_modify(paf, True)

        if obj.item_type == merc.ITEM_LIGHT and obj.value[2] != 0 and merc.room_templates[self.room_template] is not None:
            self.room_template.light += 1
        return

    # * Unequip a char with an obj.
    def unequip(self, obj):
        if obj.wear_loc == merc.WEAR_NONE:
            logger.warning("Unequip_char: already unequipped.")
            return

        for i in range(4):
            self.armor[i] += obj.apply_ac(obj.wear_loc, i)
        obj.wear_loc = -1

        if not obj.enchanted:
            for paf in merc.global_instances[obj.instance_id].affected:
                if paf.location == merc.APPLY_SPELL_AFFECT:
                    for lpaf in self.affected[:]:
                        if lpaf.type == paf.type and lpaf.level == paf.level and lpaf.location == merc.APPLY_SPELL_AFFECT:
                            self.affect_remove(lpaf)
                            break
                else:
                    self.affect_modify(paf, False)
                    self.affect_check(paf.where, paf.bitvector)

        for paf in obj.affected:
            if paf.location == merc.APPLY_SPELL_AFFECT:
                logger.error("Bug: Norm-Apply")
                for lpaf in self.affected:
                    if lpaf.type == paf.type and lpaf.level == paf.level and lpaf.location == merc.APPLY_SPELL_AFFECT:
                        logger.error("bug: location = %d" % lpaf.location)
                        logger.error("bug: type = %d" % lpaf.type)
                        self.affect_remove(lpaf)
                        break
            else:
                self.affect_modify(paf, False)
                self.affect_check(paf.where, paf.bitvector)

        if obj.item_type == merc.ITEM_LIGHT \
                and obj.value[2] != 0 \
                and merc.room_templates[self.room_template] \
                and merc.room_templates[self.room_template].light > 0:
            merc.room_templates[self.room_template].light -= 1
        return


    def exp_per_level(self, points):
        if self.is_npc():
            return 1000
        expl = 1000
        inc = 500

        if points < 40:
            return 1000 * const.pc_race_table[self.race.name].class_mult[self.guild.name] // 100 if \
                const.pc_race_table[self.race.name].class_mult[self.guild.name] else 1
        # processing */
        points -= 40

        while points > 9:
            expl += inc
            points -= 10
            if points > 9:
                expl += inc
                inc *= 2
                points -= 10
        expl += points * inc // 10
        return expl * const.pc_race_table[self.race.name].class_mult[self.guild.name] // 100
    @property
    def race(self):
        try:
            return const.race_table[self._race]
        except KeyError:
            return const.race_table['human']
    @race.setter
    def race(self, value):
        if isinstance(value, const.race_type):
            self._race = value.name
        elif value in const.race_table:
            self._race = value

    @property
    def guild(self):
        return const.guild_table.get(self._guild, None)
    @guild.setter
    def guild(self, value):
        if isinstance(value, const.guild_type):
            self._guild = value.name
        else:
            self._guild = value
    @property
    def pcdata(self):
        return self

    def reset(self):
        if self.is_npc():
            return

        if self.perm_hit == 0 \
                or self.perm_mana == 0 \
                or self.perm_move == 0 \
                or self.last_level == 0:
            # do a FULL reset */
            for loc in range(merc.MAX_WEAR):
                obj = self.get_eq(loc)
                if not obj:
                    continue
                affected = obj.affected
                if not obj.enchanted:
                    affected.extend(merc.global_instances[obj.instance_id].affected)
                for af in affected:
                    mod = af.modifier
                    if af.location == merc.APPLY_SEX:
                        self.sex -= mod
                        if self.sex < 0 or self.sex > 2:
                            self.sex = 0 if self.is_npc() else self.true_sex
                    elif af.location == merc.APPLY_MANA:
                        self.max_mana -= mod
                    elif af.location == merc.APPLY_HIT:
                        self.max_hit -= mod
                    elif af.location == merc.APPLY_MOVE:
                        self.max_move -= mod
            # now reset the permanent stats */
            self.perm_hit = self.max_hit
            self.perm_mana = self.max_mana
            self.perm_move = self.max_move
            self.last_level = self.played // 3600
            if self.true_sex < 0 or self.true_sex > 2:
                if 0 < self.sex < 3:
                    self.true_sex = self.sex
                else:
                    self.true_sex = 0

        # now restore the character to his/her true condition */
        for stat in range(merc.MAX_STATS):
            self.mod_stat[stat] = 0

        if self.true_sex < 0 or self.true_sex > 2:
            self.true_sex = 0
        self.sex = self.true_sex
        self.max_hit = self.perm_hit
        self.max_mana = self.perm_mana
        self.max_move = self.perm_move

        for i in range(4):
            self.armor[i] = 100

        self.hitroll = 0
        self.damroll = 0
        self.saving_throw = 0

        # now start adding back the effects */
        for loc in range(merc.MAX_WEAR):
            obj = self.get_eq(loc)
            if not obj:
                continue
            for i in range(4):
                self.armor[i] -= obj.apply_ac(loc, i)
            affected = obj.affected
            if not obj.enchanted:
                affected.extend(merc.global_instances[obj.instance_id].affected)

            for af in affected:
                mod = af.modifier
                if af.location == merc.APPLY_STR:
                    self.mod_stat[merc.STAT_STR] += mod
                elif af.location == merc.APPLY_DEX:
                    self.mod_stat[merc.STAT_DEX] += mod
                elif af.location == merc.APPLY_INT:
                    self.mod_stat[merc.STAT_INT] += mod
                elif af.location == merc.APPLY_WIS:
                    self.mod_stat[merc.STAT_WIS] += mod
                elif af.location == merc.APPLY_CON:
                    self.mod_stat[merc.STAT_CON] += mod
                elif af.location == merc.APPLY_SEX:
                    self.sex += mod
                elif af.location == merc.APPLY_MANA:
                    self.max_mana += mod
                elif af.location == merc.APPLY_HIT:
                    self.max_hit += mod
                elif af.location == merc.APPLY_MOVE:
                    self.max_move += mod
                elif af.location == merc.APPLY_AC:
                    self.armor = [i + mod for i in self.armor]
                elif af.location == merc.APPLY_HITROLL:
                    self.hitroll += mod
                elif af.location == merc.APPLY_DAMROLL:
                    self.damroll += mod
                elif af.location == merc.APPLY_SAVES:
                    self.saving_throw += mod
                elif af.location == merc.APPLY_SAVING_ROD:
                    self.saving_throw += mod
                elif af.location == merc.APPLY_SAVING_PETRI:
                    self.saving_throw += mod
                elif af.location == merc.APPLY_SAVING_BREATH:
                    self.saving_throw += mod
                elif af.location == merc.APPLY_SAVING_SPELL:
                    self.saving_throw += mod

        # now add back spell effects */
        for af in self.affected:
            mod = af.modifier
            if af.location == merc.APPLY_STR:
                self.mod_stat[merc.STAT_STR] += mod
            elif af.location == merc.APPLY_DEX:
                self.mod_stat[merc.STAT_DEX] += mod
            elif af.location == merc.APPLY_INT:
                self.mod_stat[merc.STAT_INT] += mod
            elif af.location == merc.APPLY_WIS:
                self.mod_stat[merc.STAT_WIS] += mod
            elif af.location == merc.APPLY_CON:
                self.mod_stat[merc.STAT_CON] += mod
            elif af.location == merc.APPLY_SEX:
                self.sex += mod
            elif af.location == merc.APPLY_MANA:
                self.max_mana += mod
            elif af.location == merc.APPLY_HIT:
                self.max_hit += mod
            elif af.location == merc.APPLY_MOVE:
                self.max_move += mod
            elif af.location == merc.APPLY_AC:
                self.armor = [i + mod for i in self.armor]
            elif af.location == merc.APPLY_HITROLL:
                self.hitroll += mod
            elif af.location == merc.APPLY_DAMROLL:
                self.damroll += mod
            elif af.location == merc.APPLY_SAVES:
                self.saving_throw += mod
            elif af.location == merc.APPLY_SAVING_ROD:
                self.saving_throw += mod
            elif af.location == merc.APPLY_SAVING_PETRI:
                self.saving_throw += mod
            elif af.location == merc.APPLY_SAVING_BREATH:
                self.saving_throw += mod
            elif af.location == merc.APPLY_SAVING_SPELL:
                self.saving_throw += mod
        # make sure sex is RIGHT!!!! */
        if self.sex < 0 or self.sex > 2:
            self.sex = self.true_sex

    # * True if char can see victim.
    def can_see(self, victim):
        # RT changed so that WIZ_INVIS has levels */
        if self == victim:
            return True
        if self.trust < victim.invis_level:
            return False
        if self.trust < victim.incog_level and self.room_template != victim.room_template:
            return False
        if (not self.is_npc()
            and self.act.is_set(merc.PLR_HOLYLIGHT)) \
                or (self.is_npc()
                    and self.is_immortal()):
            return True
        if self.is_affected(merc.AFF_BLIND):
            return False
        if self.room_template.is_dark() and not self.is_affected(merc.AFF_INFRARED):
            return False
        if victim.is_affected(merc.AFF_INVISIBLE) \
                and not self.is_affected(merc.AFF_DETECT_INVIS):
            return False
        # sneaking */

        if victim.is_affected(merc.AFF_SNEAK) \
                and not self.is_affected(merc.AFF_DETECT_HIDDEN) \
                and victim.fighting is None:
            chance = victim.get_skill("sneak")
            chance += victim.stat(merc.STAT_DEX) * 3 // 2
            chance -= self.stat(merc.STAT_INT) * 2
            chance -= self.level - victim.level * 3 // 2

            if random.randint(1, 99) < chance:
                return False

        if victim.is_affected(merc.AFF_HIDE) \
                and not self.is_affected(merc.AFF_DETECT_HIDDEN) \
                and victim.fighting is None:
            return False

        return True

    # * True if char can see obj.
    def can_see_obj(self, obj):
        if not self.is_npc() \
                and self.act.is_set(merc.PLR_HOLYLIGHT):
            return True
        if state_checks.IS_SET(obj.extra_flags, merc.ITEM_VIS_DEATH):
            return False
        if self.is_affected(merc.AFF_BLIND) \
                and obj.item_type != merc.ITEM_POTION:
            return False
        if obj.item_type == merc.ITEM_LIGHT \
                and obj.value[2] != 0:
            return True
        if state_checks.IS_SET(obj.extra_flags, merc.ITEM_INVIS) \
                and not self.is_affected(merc.AFF_DETECT_INVIS):
            return False
        if state_checks.IS_OBJ_STAT(obj, merc.ITEM_GLOW):
            return True
        if self.room_template.is_dark() \
                and not self.is_affected(merc.AFF_DARK_VISION):
            return False
        return True

    def can_see_room(self, pRoomIndex):
        if state_checks.IS_SET(pRoomIndex.room_flags, merc.ROOM_IMP_ONLY) and self.trust < merc.MAX_LEVEL:
            return False
        if state_checks.IS_SET(pRoomIndex.room_flags, merc.ROOM_GODS_ONLY) and not self.is_immortal():
            return False
        if state_checks.IS_SET(pRoomIndex.room_flags, merc.ROOM_HEROES_ONLY) and not self.is_immortal():
            return False
        if state_checks.IS_SET(pRoomIndex.room_flags,
                               merc.ROOM_NEWBIES_ONLY) and self.level > 5 and not self.is_immortal():
            return False
        if not self.is_immortal() and pRoomIndex.clan and self.clan != pRoomIndex.clan:
            return False
        return True

    # * Extract a char from the world.
    def extract(self, fPull):
        # doesn't seem to be necessary
        #if not ch.in_room:
        #    print "Extract_char: None."
        #    return

        #    nuke_pets(ch)
        self.pet = None  # just in case */

        #if fPull:
        #    die_follower( ch )
        fight.stop_fighting(self, True)

        for obj in self.contents[:]:
            obj.extract()

        if self.room_template:
            self.from_room()

        # Death room is set in the clan tabe now */
        if not fPull:
            self.to_room(merc.room_templates[self.clan.hall])
            return

        if self.desc and self.desc.original:
            self.do_return("")
            self.desc = None

        for wch in merc.player_list:
            if wch.reply == self:
                wch.reply = None

        if self not in merc.char_list:
            logger.error("Extract_char: char not found.")
            return

        merc.char_list.remove(self)
        if self in merc.player_list:
            merc.player_list.remove(self)

        if self.desc:
            self.desc.character = None
        return

    # * Find a char in the room.
    def get_char_room(ch, argument):
        number, word = game_utils.number_argument(argument)
        count = 0
        word = word.lower()
        if word == "self":
            return ch
        for rch in merc.room_instances[ch.in_room_instance].people:
            if not ch.can_see(rch):
                continue
            if not rch.is_npc() and not rch.name.lower().startswith(word):
                continue
            if rch.is_npc() and not game_utils.is_name(word, rch.name):
                continue
            count += 1
            if count == number:
                return rch
        return None

    # * Find a char in the world.
    def get_char_world(ch, argument):
        wch = ch.get_char_room(argument)
        if wch:
            return wch

        number, arg = game_utils.number_argument(argument)
        count = 0
        for wch in merc.char_list:
            if wch.in_instance is 0 or not ch.can_see(wch):
                continue
            if not wch.is_npc() and not game_utils.is_name(arg, wch.name.lower()):
                continue
            if wch.is_npc() and arg not in wch.name:
                continue
            count += 1
            if count == number:
                return wch
        return None

    # * Find an obj in a list.
    def get_obj_list(ch, argument, contents):
        number, arg = game_utils.number_argument(argument)
        count = 0
        for obj in contents:
            if ch.can_see_obj(obj) and game_utils.is_name(arg, obj.name.lower()):
                count += 1
                if count == number:
                    return obj
        return None

    # * Find an obj in player's inventory.
    def get_obj_carry(ch, argument, viewer):
        number, arg = game_utils.number_argument(argument)
        count = 0
        for obj in ch.contents:
            if obj.wear_loc == merc.WEAR_NONE and viewer.can_see_obj(obj) and game_utils.is_name(arg, obj.name.lower()):
                count += 1
                if count == number:
                    return obj
        return None

    # * Find an obj in player's equipment.
    def get_obj_wear(ch, argument):
        number, arg = game_utils.number_argument(argument)
        count = 0
        for obj in ch.contents:
            if obj.wear_loc != merc.WEAR_NONE and ch.can_see_obj(obj) and game_utils.is_name(arg, obj.name.lower()):
                count += 1
                if count == number:
                    return obj
        return None

    # * Find an obj in the room or in inventory.
    def get_obj_here(ch, argument):
        obj = ch.get_obj_list(argument, ch.room_template.contents)
        if obj:
            return obj
        obj = ch.get_obj_carry(argument, ch)
        if obj:
            return obj
        obj = ch.get_obj_wear(argument)
        if obj:
            return obj
        return None

    # * Find an obj in the world.
    def get_obj_world(ch, argument):
        obj = ch.get_obj_here(argument)
        if obj:
            return obj
        number, arg = game_utils.number_argument(argument)
        arg = arg.lower()
        instance = game_utils.find_name_instance('obj', number, arg)
        if instance is not -1:
            obj = merc.obj_instances[instance]
            return obj
        return None
    # * True if char can drop obj.
    def can_drop_obj(self, obj):
        if not state_checks.IS_SET(obj.extra_flags, merc.ITEM_NODROP):
            return True
        if not self.is_npc() \
                and self.level >= merc.LEVEL_IMMORTAL:
            return True
        return False

    def get_skill(self, sn):
        if sn == -1:  # shorthand for level based skills */
            skill = self.level * 5 // 2
        elif sn not in const.skill_table:
            logger.error("BUG: Bad sn %s in get_skill." % sn)
            skill = 0
        elif not self.is_npc():
            if self.level < const.skill_table[sn].skill_level[self.guild.name] \
                    or sn not in self.learned:
                skill = 0
            else:
                skill = self.learned[sn]
        else:  # mobiles */
            if const.skill_table[sn].spell_fun is not None:
                skill = 40 + 2 * self.level
            elif sn == 'sneak' or sn == 'hide':
                skill = self.level * 2 + 20
            elif (sn == 'dodge' and self.off_flags.is_set(merc.OFF_DODGE)) \
                    or (sn == 'parry' and self.off_flags.is_set(merc.OFF_PARRY)):
                skill = self.level * 2
            elif sn == 'shield block':
                skill = 10 + 2 * self.level
            elif sn == 'second attack' \
                    and (self.act.is_set(merc.ACT_WARRIOR)
                         or self.act.is_set(merc.ACT_THIEF)):
                skill = 10 + 3 * self.level
            elif sn == 'third attack' and self.act.is_set(merc.ACT_WARRIOR):
                skill = 4 * self.level - 40
            elif sn == 'hand to hand':
                skill = 40 + 2 * self.level
            elif sn == "trip" and self.off_flags.is_set(merc.OFF_TRIP):
                skill = 10 + 3 * self.level
            elif sn == "bash" and self.off_flags.is_set(merc.OFF_BASH):
                skill = 10 + 3 * self.level
            elif sn == "disarm" and (self.off_flags.is_set(merc.OFF_DISARM)
                                     or self.act.is_set(merc.ACT_WARRIOR)
                                     or self.act.is_set(merc.ACT_THIEF)):
                skill = 20 + 3 * self.level
            elif sn == "berserk" and self.off_flags.is_set(merc.OFF_BERSERK):
                skill = 3 * self.level
            elif sn == "kick":
                skill = 10 + 3 * self.level
            elif sn == "backstab" and self.act.is_set(merc.ACT_THIEF):
                skill = 20 + 2 * self.level
            elif sn == "rescue":
                skill = 40 + self.level
            elif sn == "recall":
                skill = 40 + self.level
            elif sn in ["sword", "dagger", "spear", "mace", "axe", "flail", "whip", "polearm"]:
                skill = 40 + 5 * self.level // 2
            else:
                skill = 0
        if self.daze > 0:
            if const.skill_table[sn].spell_fun is not None:
                skill //= 2
            else:
                skill = 2 * skill // 3
        if not self.is_npc() \
                and self.condition[merc.COND_DRUNK] > 10:
            skill = 9 * skill // 10

        return max(0, min(skill, 100))

    # for returning weapon information */
    def get_weapon_sn(self):
        wield = self.get_eq(merc.WEAR_WIELD)
        if not wield or wield.item_type != merc.ITEM_WEAPON:
            sn = "hand to hand"
            return sn
        else:
            return wield.value[0]

    def get_weapon_skill(self, sn):
        # -1 is exotic */
        skill = 0
        if self.is_npc():
            if sn == -1:
                skill = 3 * self.level
            elif sn == "hand to hand":
                skill = 40 + 2 * self.level
            else:
                skill = 40 + 5 * self.level / 2
        elif sn in self.learned:
            if sn == -1:
                skill = 3 * self.level
            else:
                skill = self.learned[sn]
        return max(0, min(skill, 100))

    # deduct cost from a character */
    def deduct_cost(self, cost):
        silver = min(self.silver, cost)
        gold = 0
        if silver < cost:
            gold = ((cost - silver + 99) // 100)
            silver = cost - 100 * gold
        self.gold -= gold
        self.silver -= silver

        if self.gold < 0:
            logger.error("Bug: deduct costs: gold %d < 0" % self.gold)
            self.gold = 0
        if self.silver < 0:
            logger.error("BUG: deduct costs: silver %d < 0" % self.silver)
            self.silver = 0
