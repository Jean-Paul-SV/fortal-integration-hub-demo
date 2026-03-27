import base64

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestActaWorkflow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_accounting = cls.env.ref("construction_operations_odoo.group_construction_accounting")
        cls.group_supervisor = cls.env.ref("construction_operations_odoo.group_construction_supervisor")

        cls.accounting_user = cls.env["res.users"].with_context(no_reset_password=True).create(
            {
                "name": "Usuario Contable",
                "login": "contabilidad_operaciones",
                "email": "contabilidad_operaciones@example.com",
                "groups_id": [(6, 0, [cls.group_accounting.id])],
            }
        )
        cls.supervisor_user = cls.env["res.users"].with_context(no_reset_password=True).create(
            {
                "name": "Supervisor de Obra",
                "login": "supervisor_obra",
                "email": "supervisor_obra@example.com",
                "groups_id": [(6, 0, [cls.group_supervisor.id])],
            }
        )

        cls.site = cls.env["construction.site"].create(
            {
                "name": "Torre Alameda",
                "code": "TORRE-ALAMEDA",
                "supervisor_user_id": cls.supervisor_user.id,
            }
        )
        cls.contractor = cls.env["construction.contractor"].create(
            {
                "name": "Concretos del Norte SAS",
                "vat": "900123456",
            }
        )

    def test_action_approve_registers_audit(self):
        record = self.env["construction.contractor.record"].create(
            {
                "site_id": self.site.id,
                "contractor_id": self.contractor.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "concept": "Vaciado de concreto",
                            "subtotal": 2500000,
                        },
                    )
                ],
            }
        )

        record.with_user(self.accounting_user).action_approve()

        self.assertEqual(record.state, "approved")
        self.assertEqual(record.approved_by_id, self.accounting_user)
        self.assertTrue(record.approved_at)

    def test_action_approve_requires_positive_total(self):
        record = self.env["construction.contractor.record"].create(
            {
                "site_id": self.site.id,
                "contractor_id": self.contractor.id,
            }
        )

        with self.assertRaises(UserError):
            record.with_user(self.accounting_user).action_approve()

    def test_import_wizard_groups_rows_into_single_acta(self):
        csv_content = "\n".join(
            [
                "obra,contratista,fecha,concepto,valor",
                "Torre Alameda,Concretos del Norte SAS,2026-03-26,Bombeo de concreto,1200000",
                "Torre Alameda,Concretos del Norte SAS,2026-03-26,Mano de obra placa,800000",
            ]
        )
        wizard = self.env["construction.contractor.import.wizard"].create(
            {
                "file_name": "actas.csv",
                "file_data": base64.b64encode(csv_content.encode("utf-8")),
                "create_missing": False,
            }
        )

        wizard.action_import()

        record = self.env["construction.contractor.record"].search(
            [
                ("site_id", "=", self.site.id),
                ("contractor_id", "=", self.contractor.id),
                ("date", "=", "2026-03-26"),
            ],
            limit=1,
        )
        self.assertTrue(record)
        self.assertEqual(len(record.line_ids), 2)
        self.assertEqual(record.total_amount, 2000000)
