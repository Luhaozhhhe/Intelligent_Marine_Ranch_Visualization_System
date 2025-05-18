# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.charts import blueprint
from flask import render_template
from flask_login import login_required, current_user
from apps.models import Product

@blueprint.route('/charts')
@login_required
def charts():
    products = [{'name': product.name, 'price': product.price} for product in Product.get_list()]
    return render_template('charts/index.html', segment='charts', products=products, username=current_user.username)