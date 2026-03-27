from odoo import fields, models


class ConstructionSite(models.Model):
    _name = "construction.site"
    _description = "Obra"
    _order = "name"

    name = fields.Char(string="Nombre", required=True)
    code = fields.Char(string="Codigo", required=True, copy=False)
    active = fields.Boolean(default=True)
    partner_name = fields.Char(string="Cliente / Contratante")
    city = fields.Char(string="Ciudad")
    start_date = fields.Date(string="Fecha inicio")
    end_date = fields.Date(string="Fecha fin")
    supervisor_user_id = fields.Many2one(
        "res.users",
        string="Supervisor responsable",
        help="Supervisor que puede operar actas de esta obra.",
    )
    record_ids = fields.One2many("construction.contractor.record", "site_id", string="Actas")
    record_count = fields.Integer(string="Total de actas", compute="_compute_record_count")

    _sql_constraints = [
        ("construction_site_code_unique", "unique(code)", "El codigo de la obra debe ser unico."),
    ]

    def _compute_record_count(self):
        for site in self:
            site.record_count = len(site.record_ids)

    def action_view_records(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Actas",
            "res_model": "construction.contractor.record",
            "view_mode": "tree,form",
            "domain": [("site_id", "=", self.id)],
            "context": {"default_site_id": self.id},
        }
