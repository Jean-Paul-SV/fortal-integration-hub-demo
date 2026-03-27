from odoo import fields, models


class ConstructionContractor(models.Model):
    _name = "construction.contractor"
    _description = "Contratista"
    _order = "name"

    name = fields.Char(string="Razon social", required=True)
    vat = fields.Char(string="NIT")
    email = fields.Char(string="Correo")
    phone = fields.Char(string="Telefono")
    active = fields.Boolean(default=True)
    notes = fields.Text(string="Notas")
    record_ids = fields.One2many("construction.contractor.record", "contractor_id", string="Actas")
    record_count = fields.Integer(string="Total de actas", compute="_compute_record_count")

    def _compute_record_count(self):
        for contractor in self:
            contractor.record_count = len(contractor.record_ids)

    def action_view_records(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Actas",
            "res_model": "construction.contractor.record",
            "view_mode": "tree,form",
            "domain": [("contractor_id", "=", self.id)],
            "context": {"default_contractor_id": self.id},
        }
