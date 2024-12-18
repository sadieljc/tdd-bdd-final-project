######################################################################
# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

# spell: ignore Rofrano jsonify restx dbname
"""
Product Store Service with UI
"""
from flask import jsonify, request, abort
from flask import url_for  # noqa: F401 pylint: disable=unused-import
from service.models import Product, Category
from service.common import status  # HTTP Status Codes
from . import app


######################################################################
# H E A L T H   C H E C K
######################################################################
@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="OK"), status.HTTP_200_OK


######################################################################
# H O M E   P A G E
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


def str_to_bool(str_value):
    """
    Map string to bool
    """
    bool_map = {
        'true': True,
        '1': True,
        't': True,
        'y': True,
        'yes': True,
        'false': False,
        '0': False,
        'f': False,
        'n': False,
        'no': False
    }

    try:
        return bool_map[str_value.lower()]
    except KeyError as exc:
        raise ValueError(f"Cannot convert {str_value} to a boolean") from exc


######################################################################
# C R E A T E   A   N E W   P R O D U C T
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    """
    Creates a Product
    This endpoint will create a Product based the data in the body that is posted
    """
    app.logger.info("Request to Create a Product...")
    check_content_type("application/json")

    data = request.get_json()
    app.logger.info("Processing: %s", data)
    product = Product()
    product.deserialize(data)
    product.create()
    app.logger.info("Product with new id [%s] saved!", product.id)

    message = product.serialize()

    location_url = url_for("get_products", product_id=product.id, _external=True)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# L I S T   A L L   P R O D U C T S
######################################################################

@app.route("/products", methods=["GET"])
def list_products():
    """
    Get all Products
    This endpoint will get all Products
    """
    app.logger.info("Request to Get all Products...")

    name = request.args.get("name")
    app.logger.info(f"name={name}")

    category = request.args.get("category")
    app.logger.info(f"category={category}")

    available = request.args.get("available")
    app.logger.info(f"available={available}")

    if name:
        products = Product.find_by_name(name)
    elif category:
        products = Product.find_by_category(getattr(Category, category.upper()))
    elif available:
        products = Product.find_by_availability(str_to_bool(available))
    else:
        products = Product.all()

    product_response = [product.serialize() for product in products]

    return product_response, status.HTTP_200_OK


######################################################################
# R E A D   A   P R O D U C T
######################################################################

@app.route("/products/<product_id>", methods=["GET"])
def get_products(product_id):
    """
    Get a Product
    This endpoint will get a Product by Id
    """
    app.logger.info("Request to Get a Product...")
    product = Product.find(product_id)

    if product is None:
        app.logger.error("Product not found.")
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Product Id not found {product_id}"
        )

    message = product.serialize()

    return message, status.HTTP_200_OK


######################################################################
# U P D A T E   A   P R O D U C T
######################################################################

@app.route("/products/<product_id>", methods=["PUT"])
def update_products(product_id):
    """
    Update a Product
    This endpoint will update a Product
    """
    app.logger.info("Request to Update a Product...")
    check_content_type("application/json")
    product = Product.find(product_id)

    if product is None:
        app.logger.error("Product not found.")
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Product Id not found {product_id}"
        )

    data = request.get_json()
    product.deserialize(data)

    product.update()

    return product.serialize(), status.HTTP_200_OK


######################################################################
# D E L E T E   A   P R O D U C T
######################################################################

@app.route("/products/<product_id>", methods=["DELETE"])
def delete_product(product_id):
    """
    Delete a Product
    This endpoint will delete a Product
    """
    app.logger.info("Request to Delete a Product...")

    product = Product.find(product_id)

    if product is None:
        app.logger.error("Product not found.")
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Product Id not found {product_id}"
        )

    product.delete()

    return "", status.HTTP_204_NO_CONTENT
