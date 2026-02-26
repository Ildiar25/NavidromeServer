# -*- coding: utf-8 -*-
import logging

# noinspection PyProtectedMember
from odoo import _
from odoo.models import TransientModel
from odoo.fields import Many2many, Many2one

_logger = logging.getLogger(__name__)


class ChangeOwnerWizard(TransientModel):
    _name = "music_manager.change_owner_wizard"
    _description = "change_owner_wizard_table"

    # Relational fields
    new_owner_id = Many2one(comodel_name='res.users', string=_("New owner"), required=True)
    current_owner_ids = Many2many(comodel_name='res.users', string=_("Current owners"))

    def default_get(self, fields_list):
        result = super(ChangeOwnerWizard, self).default_get(fields_list) or {}

        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids')

        if active_model and active_ids:
            records = self.env[active_model].browse(active_ids)

            owner_ids = records.mapped('custom_owner_id').filtered(lambda record: record.exists())

            if owner_ids:
                result.update({
                    'current_owner_ids': [(6, 0, owner_ids.ids)],
                })

        return result

    def apply_owner_changes(self):
        self.ensure_one()
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids')

        if active_model and active_ids:
            records = self.env[active_model].browse(active_ids)
            records.write({'custom_owner_id': self.new_owner_id.id})

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Music Manager says:"),
                'message': _("Nice! Now, all selected records belong to %s.", self.new_owner_id.name),
                'type': 'info',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
