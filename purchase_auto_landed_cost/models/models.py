# models.py

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_landed_cost_added = fields.Boolean(string='Custos já adicionados', default=False)
    landed_cost_id = fields.Many2one('stock.landed.cost', readonly=True)

    def action_create_landed_cost(self):
        existing_landed_cost = self.env['stock.landed.cost'].search(
            [('picking_ids', '=', self.id)]
        )
        _logger.info(f"existing_landed_cost {existing_landed_cost}")
        if existing_landed_cost:
            self.landed_cost_id = existing_landed_cost
            notification = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': ("Os custos já foram adicionados"),
                    'message': ("A informação foi preenchida de acordo"),
                    'type': 'warning',
                    'sticky': False,
                },
            }
            return notification

        landed_cost = self.env['stock.landed.cost'].create(
            {
                'picking_ids': self,
            }
        )
        cost_lines = []
        if self.amount_freight_value:
            freight_product = self.env['product.product'].search(
                [('default_code', '=', 'Frete')], limit=1
            )
            if not freight_product:
                freight_product = self.env['product.product'].create(
                    {
                        'name': 'Frete',
                        'default_code': 'FRETE',
                        'type': 'service',
                    }
                )
            cost_lines.append(
                (
                    0,
                    0,
                    {
                        'product_id': freight_product.id,
                        'name': 'Frete',
                        'account_id': self.env['account.account']
                        .search([('code', '=', '1.1.9.3.15')], limit=1)
                        .id,
                        'price_unit': self.amount_freight_value,
                        'split_method': 'equal',
                    },
                )
            )
        if self.amount_insurance_value:
            insurance_product = self.env['product.product'].search(
                [('default_code', '=', 'Seguro')], limit=1
            )
            if not insurance_product:
                insurance_product = self.env['product.product'].create(
                    {
                        'name': 'Seguro',
                        'default_code': 'SEGURO',
                        'type': 'service',
                    }
                )
            cost_lines.append(
                (
                    0,
                    0,
                    {
                        'product_id': insurance_product.id,
                        'name': 'Seguro',
                        'account_id': self.env['account.account']
                        .search([('code', '=', '1.1.9.3.15')], limit=1)
                        .id,
                        'price_unit': self.amount_insurance_value,
                        'split_method': 'equal',
                    },
                )
            )
        if self.amount_other_value:
            other_costs_product = self.env['product.product'].search(
                [('default_code', '=', 'OUTROS_CUSTOS')], limit=1
            )
            if not other_costs_product:
                other_costs_product = self.env['product.product'].create(
                    {
                        'name': 'Outros Custos',
                        'default_code': 'OUTROS_CUSTOS',
                        'type': 'service',
                    }
                )
            cost_lines.append(
                (
                    0,
                    0,
                    {
                        'product_id': other_costs_product.id,
                        'name': 'Outros Custos',
                        'account_id': self.env['account.account']
                        .search([('code', '=', '1.1.9.3.15')], limit=1)
                        .id,
                        'price_unit': self.amount_other_value,
                        'split_method': 'equal',
                    },
                )
            )
        _logger.info(f"Preparing lines")
        if cost_lines:
            _logger.info(f"Inside lines")
            landed_cost.write({'cost_lines': cost_lines})
            landed_cost.compute_landed_cost()
            landed_cost.button_validate()
            self.landed_cost_id = landed_cost

    # def button_validate(self):
    #     _logger.info(f"Inside button")
    #     existing_landed_cost = self.env['stock.landed.cost'].search(
    #         [('picking_ids', '=', self.id)]
    #     )
    #     _logger.info(f"existing_landed_cost {existing_landed_cost}")
    #     if not existing_landed_cost:
    #         pass
    #         # self.create_landed_cost()
    #     # return super(StockPicking, self).button_validate()
    #     a = super(StockPicking, self).button_validate()
    #     _logger.info(f"a = {a}")
    #     if a:
    #         _logger.info(f"ITS TRUE!!!")
    #         return True

    # def _register_hook(self):
    #     super()._register_hook()
    #     self.env['stock.picking'].picking_done.add_listener(self.create_landed_cost)
