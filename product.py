# -*- coding: utf-8 -*-
"""
    product.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval

__all__ = [
    'Template', 'Product', 'ProductVariationAttributes',
]
__metaclass__ = PoolMeta


class Template:
    "Product Template"
    __name__ = 'product.template'

    variation_attributes = fields.One2Many(
        'product.variation_attributes', 'template', 'Variation Attributes',
    )

    @classmethod
    def __setup__(cls):
        super(Template, cls).__setup__()
        cls._error_messages.update({
            'missing_attributes':
                "Please define following attributes for product %s: %s"
        })

    def validate_variation_attributes(self):
        for product in self.products:
            product.validate_attributes()

    @classmethod
    def validate(cls, templates):
        super(Template, cls).validate(templates)
        for template in templates:
            template.validate_variation_attributes()


class Product:
    "Product"
    __name__ = 'product.product'

    @classmethod
    def __setup__(cls):
        super(Product, cls).__setup__()
        cls._error_messages.update({
            'missing_attributes':
                "Please define following attributes for product %s: %s"
        })

    def validate_attributes(self):
        """Check if product defines all the attributes specified in
        template variation attributes.
        """
        required_attrs = set(
            [v.attribute.name for v in self.template.variation_attributes]
        )
        missing = required_attrs - \
            set(self.attributes.keys() if self.attributes else [])
        if missing:
            self.raise_user_error(
                "missing_attributes",
                (self.rec_name, ','.join(map(unicode, missing)))
            )

    @classmethod
    def validate(cls, products):
        super(Product, cls).validate(products)
        for product in products:
            product.validate_attributes()


class ProductVariationAttributes(ModelSQL, ModelView):
    "Variation attributes for product template"
    __name__ = 'product.variation_attributes'

    template = fields.Many2One('product.template', 'Template', required=True)
    attribute = fields.Many2One(
        'product.attribute', 'Attribute', required=True,
        domain=[('sets', '=',
                Eval('_parent_template', {}).get('attribute_set', -1))],
    )
    widget = fields.Selection([
        ('dropdown', 'Dropdown'),
        ('swatches', 'Swatches'),
    ], 'Widget', required=True)

    @staticmethod
    def default_widget():
        return 'dropdown'
