# -*- coding: utf-8 -*-
import logging

# noinspection PyProtectedMember
from odoo import _
from odoo.models import TransientModel
from odoo.fields import Many2one


_logger = logging.getLogger(__name__)


class ChangeOwnerWizard(TransientModel):
    _name = "music_manager.change_owner_wizard"
    _description = "change_owner_wizard_table"

    # Relational fields
    new_owner_id = Many2one(comodel_name='res.users', string=_("New owner"))

    def apply_owner_changes(self):
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids')

        records = self.env[active_model].browse(active_ids)
        records.write({'owner': self.new_owner_id.id})

        return {'type': 'ir.actions.act_window_close'}
