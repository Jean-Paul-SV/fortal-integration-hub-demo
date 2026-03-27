from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError


class ConstructionContractorRecord(models.Model):
    _name = "construction.contractor.record"
    _description = "Acta de contratista"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        string="Referencia",
        required=True,
        copy=False,
        default=lambda self: _("Nuevo"),
        tracking=True,
    )
    site_id = fields.Many2one("construction.site", string="Obra", required=True, tracking=True)
    contractor_id = fields.Many2one(
        "construction.contractor",
        string="Contratista",
        required=True,
        tracking=True,
    )
    date = fields.Date(string="Fecha acta", required=True, default=fields.Date.context_today, tracking=True)
    state = fields.Selection(
        [
            ("draft", "Borrador"),
            ("sent", "Enviado"),
            ("approved", "Aprobado"),
            ("rejected", "Rechazado"),
        ],
        string="Estado",
        required=True,
        default="draft",
        tracking=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Moneda",
        required=True,
        default=lambda self: self.env.company.currency_id.id,
    )
    line_ids = fields.One2many(
        "construction.contractor.record.line",
        "record_id",
        string="Lineas de acta",
        copy=True,
    )
    total_amount = fields.Monetary(
        string="Total",
        currency_field="currency_id",
        compute="_compute_total_amount",
        store=True,
        tracking=True,
    )
    created_by_id = fields.Many2one(
        "res.users",
        string="Creado por",
        default=lambda self: self.env.user,
        readonly=True,
    )
    approved_by_id = fields.Many2one("res.users", string="Aprobado por", readonly=True)
    approved_at = fields.Datetime(string="Fecha aprobacion", readonly=True)
    rejected_by_id = fields.Many2one("res.users", string="Rechazado por", readonly=True)
    rejected_at = fields.Datetime(string="Fecha rechazo", readonly=True)
    rejection_reason = fields.Text(string="Motivo de rechazo", readonly=True)

    @api.depends("line_ids.subtotal")
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped("subtotal"))

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("name", _("Nuevo")) == _("Nuevo"):
                vals["name"] = sequence.next_by_code("construction.contractor.record") or _("Nuevo")
        return super().create(vals_list)

    @api.constrains("line_ids")
    def _check_line_values(self):
        for record in self:
            if any(line.subtotal <= 0 for line in record.line_ids):
                raise ValidationError(_("Todas las lineas deben tener un valor mayor a cero."))

    def _check_can_approve(self):
        for record in self:
            if not record.site_id or not record.contractor_id:
                raise UserError(_("No puede aprobar un acta sin obra y contratista."))
            if record.total_amount <= 0:
                raise UserError(_("No puede aprobar un acta con total menor o igual a cero."))

    def _check_accounting_or_direction(self):
        if not (
            self.env.user.has_group("construction_operations_odoo.group_construction_direction")
            or self.env.user.has_group("construction_operations_odoo.group_construction_accounting")
        ):
            raise AccessError(_("Solo Direccion o Contabilidad pueden aprobar o rechazar actas."))

    def action_send(self):
        for record in self:
            if not record.line_ids:
                raise UserError(_("Debe registrar al menos una linea antes de enviar el acta."))
            record.state = "sent"

    def action_approve(self):
        self._check_accounting_or_direction()
        self._check_can_approve()
        now = fields.Datetime.now()
        for record in self:
            record.write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.user.id,
                    "approved_at": now,
                    "rejected_by_id": False,
                    "rejected_at": False,
                    "rejection_reason": False,
                }
            )

    def action_reject(self):
        self._check_accounting_or_direction()
        now = fields.Datetime.now()
        for record in self:
            record.write(
                {
                    "state": "rejected",
                    "rejected_by_id": self.env.user.id,
                    "rejected_at": now,
                }
            )

    def action_reset_to_draft(self):
        for record in self:
            record.write(
                {
                    "state": "draft",
                    "approved_by_id": False,
                    "approved_at": False,
                    "rejected_by_id": False,
                    "rejected_at": False,
                    "rejection_reason": False,
                }
            )


class ConstructionContractorRecordLine(models.Model):
    _name = "construction.contractor.record.line"
    _description = "Linea de acta de contratista"
    _order = "id"

    record_id = fields.Many2one(
        "construction.contractor.record",
        string="Acta",
        required=True,
        ondelete="cascade",
    )
    concept = fields.Char(string="Concepto", required=True)
    subtotal = fields.Monetary(string="Valor", required=True, currency_field="currency_id")
    currency_id = fields.Many2one(
        related="record_id.currency_id",
        string="Moneda",
        store=True,
        readonly=True,
    )

    @api.constrains("subtotal")
    def _check_subtotal(self):
        for line in self:
            if line.subtotal <= 0:
                raise ValidationError(_("El valor de la linea debe ser mayor a cero."))
