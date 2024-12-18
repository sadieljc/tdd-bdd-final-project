# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
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

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

logger = logging.getLogger("flask.app")


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """It should Read a product from the database"""
        product = ProductFactory()
        logger.info("Product Name: %s", product.name)
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        db_product = product.find(product.id)
        self.assertEqual(db_product.name, product.name)
        self.assertEqual(db_product.description, product.description)
        self.assertEqual(Decimal(db_product.price), product.price)
        self.assertEqual(db_product.available, product.available)
        self.assertEqual(db_product.category, product.category)

    def test_update_a_product(self):
        """It should Update a Product from the database"""
        product = ProductFactory()
        logger.info("Product Name: %s", product.name)

        product.id = None
        product.create()
        logger.info("Product Name after creation: %s", product.name)

        product.description = "Test Description"
        product.update()

        products = Product.all()
        self.assertEqual(len(products), 1)

        updated_product = products[0]
        self.assertEqual(updated_product.id, product.id)
        self.assertEqual(updated_product.description, product.description)

    def test_update_a_product_with_empty_id(self):
        """It should not Update a Product with empty Id"""
        product = ProductFactory()
        logger.info("Product Name: %s", product.name)

        product.id = None
        product.create()
        logger.info("Product Id after creation: %s", product.id)
        product.id = 0

        with self.assertRaises(DataValidationError):
            product.update()

    def test_delete_a_product(self):
        """It should Delete a Product from the database"""
        product = ProductFactory()
        product.id = None
        product.create()

        products = Product.all()
        self.assertEqual(len(products), 1)

        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_products(self):
        """It should List all Products from the database"""
        products = Product.all()
        self.assertEqual(len(products), 0)

        for _ in range(1, 6):
            product = ProductFactory()
            product.Id = None
            product.create()

        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_product_by_name(self):
        """It should Find Products by Name from the database"""
        for _ in range(1, 6):
            product = ProductFactory()
            product.Id = None
            product.create()

        products = Product.all()
        first_product = products[0]

        occurrences = 0
        for i in range(0, 5):
            if first_product.name == products[i].name:
                occurrences += 1

        products_with_same_name = product.find_by_name(first_product.name)
        self.assertEqual(products_with_same_name.count(), occurrences)

        for i in range(0, products_with_same_name.count()):
            self.assertEqual(products_with_same_name[i].name, first_product.name)

    def test_find_product_by_availability(self):
        """It should Find Products by Availability from the database"""
        for _ in range(1, 11):
            product = ProductFactory()
            product.Id = None
            product.create()

        products = Product.all()
        first_product = products[0]

        occurrences = 0
        for i in range(0, 10):
            if first_product.available == products[i].available:
                occurrences += 1

        products_with_same_availability = product.find_by_availability(first_product.available)
        self.assertEqual(products_with_same_availability.count(), occurrences)

        for i in range(0, products_with_same_availability.count()):
            self.assertEqual(products_with_same_availability[i].available, first_product.available)

    def test_find_product_by_category(self):
        """It should Find Products by Category from the database"""
        for _ in range(1, 11):
            product = ProductFactory()
            product.Id = None
            product.create()

        products = Product.all()
        first_product = products[0]

        occurrences = 0
        for i in range(0, 10):
            if first_product.category == products[i].category:
                occurrences += 1

        products_with_same_category = product.find_by_category(first_product.category)
        self.assertEqual(products_with_same_category.count(), occurrences)

        for i in range(0, products_with_same_category.count()):
            self.assertEqual(products_with_same_category[i].category, first_product.category)

    def test_invalid_available_data_type_in_deserialize_(self):
        """It should throw exception for invalid available data type"""
        product = ProductFactory()
        product.Id = None
        product.create()

        product.available = 10
        with self.assertRaises(DataValidationError):
            product.deserialize(product)

    def test_find_product_by_price(self):
        """It should Find Products by Price from the database"""
        for _ in range(1, 11):
            product = ProductFactory()
            product.Id = None
            product.create()

        products = Product.all()
        first_product = products[0]

        occurrences = 0
        for i in range(0, 10):
            if first_product.price == products[i].price:
                occurrences += 1

        products_with_same_price = product.find_by_price(first_product.price)
        self.assertEqual(products_with_same_price.count(), occurrences)

        for i in range(0, products_with_same_price.count()):
            self.assertEqual(products_with_same_price[i].price, first_product.price)

    def test_find_product_by_price_string(self):
        """It should Find Products by Price string from the database"""
        for _ in range(1, 11):
            product = ProductFactory()
            product.Id = None
            product.create()

        products = Product.all()
        first_product = products[0]

        occurrences = 0
        for i in range(0, 10):
            if first_product.price == products[i].price:
                occurrences += 1

        products_with_same_price = product.find_by_price(str(first_product.price))
        self.assertEqual(products_with_same_price.count(), occurrences)

        for i in range(0, products_with_same_price.count()):
            self.assertEqual(products_with_same_price[i].price, first_product.price)
