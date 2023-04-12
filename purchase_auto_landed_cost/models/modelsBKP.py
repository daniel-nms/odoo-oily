# models.py

from odoo import models, fields, api

class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order')

    @api.model
    def create_landed_cost(self, purchase_order):
        landed_cost = self.env['stock.landed.cost'].create({
            'purchase_order_id': purchase_order.id,
            'picking_ids': purchase_order.picking_ids,
        })
        cost_lines = []
        if purchase_order.amount_freight_value:
            freight_product = self.env['product.product'].search([('default_code', '=', 'Frete')], limit=1)
            if not freight_product:
                freight_product = self.env['product.product'].create({
                    'name': 'Frete',
                    'default_code': 'Frete',
                    'type': 'service',
                })
            cost_lines.append((0, 0, {
                'product_id': freight_product.id,
                'name': 'Frete',
                'price_unit': purchase_order.amount_freight_value,
                'split_method': '"by_current_cost_price"',
                'quantity': sum(move.product_qty for move in purchase_order.picking_ids.move_lines),
                'company_id': purchase_order.company_id.id,
            }))
        if purchase_order.amount_insurance_value:
            insurance_product = self.env['product.product'].search([('default_code', '=', 'Seguro')], limit=1)
            if not insurance_product:
                insurance_product = self.env['product.product'].create({
                    'name': 'Seguro',
                    'default_code': 'Seguro',
                    'type': 'service',
                })
            cost_lines.append((0, 0, {
                'product_id': insurance_product.id,
                'name': 'Other Costs',
                'price_unit': purchase_order.amount_insurance_value,
                'split_method': '"by_current_cost_price"',
                'quantity': sum(move.product_qty for move in purchase_order.picking_ids.move_lines),
                'company_id': purchase_order.company_id.id,
            }))
        if purchase_order.amount_other_value:
            other_costs_product = self.env['product.product'].search([('default_code', '=', 'OUTROS_CUSTOS')], limit=1)
            if not other_costs_product:
                other_costs_product = self.env['product.product'].create({
                    'name': 'Outros Custos',
                    'default_code': 'OUTROS_CUSTOS',
                    'type': 'service',
                })
            cost_lines.append((0, 0, {
                'product_id': other_costs_product.id,
                'name': 'Other Costs',
                'price_unit': purchase_order.amount_other_value,
                'split_method': '"by_current_cost_price"',
                'quantity': sum(move.product_qty for move in purchase_order.picking_ids.move_lines),
                'company_id': purchase_order.company_id.id,
            }))
        if cost_lines:
            landed_cost.write({'cost_lines': cost_lines})
            landed_cost.compute_costs()
            landed_cost.action_validate()

# class PurchaseOrder(models.Model):
#     _inherit = 'purchase.order'

#     amount_freight_value = fields.Float(string='Freight Value')
#     amount_other_value = fields.Float(string='Other Costs')

#     def create_freight_and_other_products(self):
#         freight_product = self.env['product.product'].search([('default_code', '=', 'FREIGHT')], limit=1)
#         if not freight_product:
#             freight_product = self.env['product.product'].create({
#                 'name': 'Freight Cost',
#                 'default_code': 'FREIGHT',
#                 'type': 'service',
#             })
#         other_costs_product = self.env['product.product'].search([('default_code', '=', 'OTHER_COSTS')], limit=1)
#         if not other_costs_product:
           
