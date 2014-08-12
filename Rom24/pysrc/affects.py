import logging

logger = logging.getLogger()

import bit
import const
import handler_game
import merc
import tables


class Affects:
    def __init__(self):
        super().__init__()
        self.affected = []
        self.affected_by = bit.Bit(flags=tables.affect_flags)

    def is_affected(self, aff):
        if isinstance(aff, const.skill_type):
            aff = aff.name
        if type(aff) == str:
            return True if [paf for paf in self.affected if paf.type == aff][:1] else False
        return self.affected_by.is_set(aff)

    def affect_add(self, paf):
        paf_new = handler_game.AFFECT_DATA()
        paf_new.__dict__ = paf.__dict__.copy()
        self.affected.append(paf_new)
        self.affect_modify(paf_new, True)
        return


    # * Add or enhance an affect.
    def affect_join(self, paf):
        for paf_old in self.affected:
            if paf_old.type == paf.type:
                paf.level = (paf.level + paf_old.level) // 2
                paf.duration += paf_old.duration
                paf.modifier += paf_old.modifier
                self.affect_remove(paf_old)
                break

        self.affect_add(paf)
        return
    # * Remove an affect from a char.
    def affect_remove(self, paf):
        if not self.affected:
            logger.error("BUG: Affect_remove: no affect.")
            return

        self.affect_modify(paf, False)
        where = paf.where
        vector = paf.bitvector

        if paf not in self.affected:
            logger.error("Affect_remove: cannot find paf.")
            return
        self.affected.remove(paf)
        del paf
        self.affect_check(where, vector)
        return

    def affect_check(self, where, vector):
        if where in [merc.TO_OBJECT, merc.TO_WEAPON] or not vector:
            return

        for paf in self.affected:
            if paf.where == where and paf.bitvector == vector:
                if where == merc.TO_AFFECTS:
                    self.affected_by.set_bit(vector)
                elif where == merc.TO_IMMUNE:
                    self.imm_flags.set_bit(vector)
                elif where == merc.TO_RESIST:
                    self.res_flags.set_bit(vector)
                elif where == merc.TO_VULN:
                    self.vuln_flags.set_bit(vector)
                return

        for item_id in self.contents:
            item = merc.items[item_id]
            if not item.equipped_to:
                continue
            for paf in item.affected:
                if paf.where == where and paf.bitvector == vector:
                    if where == merc.TO_AFFECTS:
                        self.affected_by.set_bit(vector)
                    elif where == merc.TO_IMMUNE:
                        self.imm_flags.set_bit(vector)
                    elif where == merc.TO_RESIST:
                        self.res_flags.set_bit(vector)
                    elif where == merc.TO_VULN:
                        self.vuln_flags.set_bit(vector)
                    return
            if item.enchanted:
                continue
            for paf in item.pIndexData.affected:
                if paf.where == where and paf.bitvector == vector:
                    if where == merc.TO_AFFECTS:
                        self.affected_by.set_bit(vector)
                    elif where == merc.TO_IMMUNE:
                        self.imm_flags.set_bit(vector)
                    elif where == merc.TO_RESIST:
                        self.res_flags.set_bit(vector)
                    elif where == merc.TO_VULN:
                        self.vuln_flags.set_bit(vector)
                    return

    # * Apply or remove an affect to a character.
    def affect_modify(self, paf, fAdd):
        mod = paf.modifier
        if fAdd:
            if paf.where == merc.TO_AFFECTS:
                self.affected_by.set_bit(paf.bitvector)
            elif paf.where == merc.TO_IMMUNE:
                self.imm_flags.set_bit(paf.bitvector)
            elif paf.where == merc.TO_RESIST:
                self.res_flags.set_bit(paf.bitvector)
            elif paf.where == merc.TO_VULN:
                self.vuln_flags.set_bit(paf.bitvector)
        else:
            if paf.where == merc.TO_AFFECTS:
                self.affected_by.rem_bit(paf.bitvector)
            elif paf.where == merc.TO_IMMUNE:
                self.imm_flags.rem_bit(paf.bitvector)
            elif paf.where == merc.TO_RESIST:
                self.res_flags.rem_bit(paf.bitvector)
            elif paf.where == merc.TO_VULN:
                self.vuln_flags.rem_bit(paf.bitvector)
            mod = 0 - mod

        if paf.location == merc.APPLY_NONE:
            pass
        elif paf.location == merc.APPLY_STR:
            self.mod_stat[merc.STAT_STR] += mod
        elif paf.location == merc.APPLY_DEX:
            self.mod_stat[merc.STAT_DEX] += mod
        elif paf.location == merc.APPLY_INT:
            self.mod_stat[merc.STAT_INT] += mod
        elif paf.location == merc.APPLY_WIS:
            self.mod_stat[merc.STAT_WIS] += mod
        elif paf.location == merc.APPLY_CON:
            self.mod_stat[merc.STAT_CON] += mod
        elif paf.location == merc.APPLY_SEX:
            self.sex += mod
        elif paf.location == merc.APPLY_CLASS:
            pass
        elif paf.location == merc.APPLY_LEVEL:
            pass
        elif paf.location == merc.APPLY_AGE:
            pass
        elif paf.location == merc.APPLY_HEIGHT:
            pass
        elif paf.location == merc.APPLY_WEIGHT:
            pass
        elif paf.location == merc.APPLY_MANA:
            self.max_mana += mod
        elif paf.location == merc.APPLY_HIT:
            self.max_hit += mod
        elif paf.location == merc.APPLY_MOVE:
            self.max_move += mod
        elif paf.location == merc.APPLY_GOLD:
            pass
        elif paf.location == merc.APPLY_EXP:
            pass
        elif paf.location == merc.APPLY_AC:
            for i in range(4):
                self.armor[i] += mod
        elif paf.location == merc.APPLY_HITROLL:
            self.hitroll += mod
        elif paf.location == merc.APPLY_DAMROLL:
            self.damroll += mod
        elif paf.location == merc.APPLY_SAVES:
            self.saving_throw += mod
        elif paf.location == merc.APPLY_SAVING_ROD:
            self.saving_throw += mod
        elif paf.location == merc.APPLY_SAVING_PETRI:
            self.saving_throw += mod
        elif paf.location == merc.APPLY_SAVING_BREATH:
            self.saving_throw += mod
        elif paf.location == merc.APPLY_SAVING_SPELL:
            self.saving_throw += mod
        elif paf.location == merc.APPLY_SPELL_AFFECT:
            pass
        else:
            logger.error("Affect_modify: unknown location %d." % paf.location)
            return
        #
        # * Check for weapon wielding.
        # * Guard against recursion (for weapons with affects).
        wield = self.get_eq('main_hand')
        if not self.is_npc() and wield \
                and wield.get_weight() > (const.str_app[self.stat(merc.STAT_STR)].wield * 10):
            global depth

            if depth == 0:
                depth += 1
                handler_game.act("You drop $p.", self, wield, None, merc.TO_CHAR)
                handler_game.act("$n drops $p.", self, wield, None, merc.TO_ROOM)
                wield.from_environment()
                wield.to_environment(self.in_room)
                depth -= 1
        return

    # * Strip all affects of a given sn.
    def affect_strip(self, sn):
        [self.affect_remove(paf) for paf in self.affected[:] if paf.type == sn]
        return
