import base64
import csv
import io

from odoo import _, fields, models
from odoo.exceptions import UserError, ValidationError


class ConstructionContractorImportWizard(models.TransientModel):
    _name = "construction.contractor.import.wizard"
    _description = "Importador de actas desde CSV"

    file_name = fields.Char(string="Archivo")
    file_data = fields.Binary(string="CSV", required=True)
    create_missing = fields.Boolean(
        string="Crear obra y contratista si no existen",
        default=True,
        help="Si esta activo, el importador crea catalogos basicos con el nombre recibido.",
    )

    def action_import(self):
        self.ensure_one()
        if not self.file_data:
            raise UserError(_("Debe adjuntar un archivo CSV."))

        decoded = base64.b64decode(self.file_data)
        text_buffer = io.StringIO(decoded.decode("utf-8-sig"))
        reader = csv.DictReader(text_buffer)
        required_headers = {"obra", "contratista", "fecha", "concepto", "valor"}
        if not reader.fieldnames or not required_headers.issubset(set(reader.fieldnames)):
            raise ValidationError(
                _("El CSV debe contener las columnas: obra, contratista, fecha, concepto, valor.")
            )

        site_model = self.env["construction.site"]
        contractor_model = self.env["construction.contractor"]
        record_model = self.env["construction.contractor.record"]
        touched_records = self.env["construction.contractor.record"]

        for row_number, row in enumerate(reader, start=2):
            obra_name = (row.get("obra") or "").strip()
            contratista_name = (row.get("contratista") or "").strip()
            concept = (row.get("concepto") or "").strip()
            date_value = (row.get("fecha") or "").strip()
            amount_text = (row.get("valor") or "").strip()

            if not obra_name or not contratista_name or not concept or not date_value or not amount_text:
                raise ValidationError(_("La fila %s tiene columnas vacias.") % row_number)

            try:
                amount = float(amount_text)
            except ValueError as error:
                raise ValidationError(_("La fila %s tiene un valor invalido.") % row_number) from error

            if amount <= 0:
                raise ValidationError(_("La fila %s tiene un valor menor o igual a cero.") % row_number)

            site = site_model.search([("name", "=", obra_name)], limit=1)
            if not site:
                if not self.create_missing:
                    raise ValidationError(_("No existe la obra '%s' en la fila %s.") % (obra_name, row_number))
                site = site_model.create(
                    {
                        "name": obra_name,
                        "code": obra_name.upper().replace(" ", "-")[:20],
                    }
                )

            contractor = contractor_model.search([("name", "=", contratista_name)], limit=1)
            if not contractor:
                if not self.create_missing:
                    raise ValidationError(
                        _("No existe el contratista '%s' en la fila %s.") % (contratista_name, row_number)
                    )
                contractor = contractor_model.create({"name": contratista_name})

            record = record_model.search(
                [
                    ("site_id", "=", site.id),
                    ("contractor_id", "=", contractor.id),
                    ("date", "=", date_value),
                    ("state", "=", "draft"),
                ],
                limit=1,
            )
            if not record:
                record = record_model.create(
                    {
                        "site_id": site.id,
                        "contractor_id": contractor.id,
                        "date": date_value,
                    }
                )
            touched_records |= record

            self.env["construction.contractor.record.line"].create(
                {
                    "record_id": record.id,
                    "concept": concept,
                    "subtotal": amount,
                }
            )

        return {
            "type": "ir.actions.act_window",
            "name": "Actas importadas",
            "res_model": "construction.contractor.record",
            "view_mode": "tree,form",
            "domain": [("id", "in", touched_records.ids)],
        }
