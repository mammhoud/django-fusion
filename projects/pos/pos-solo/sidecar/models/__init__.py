"""
POS Solo Package — POS core, Menu, Node Registry, Configuration, and Sync models.

NOTE: This __init__.py is minimal — only imports AppConfig to avoid
premature model loading during Django app registry initialization
(makemigrations / migrate). Server code and tests import directly
from sub-modules:
    from models.pos import Category, Product, Customer, ...
    from models.menu import MenuItem, Menu, MenuItemAssignment
    from models.node import Node, Heartbeat, NodeEvent
    from models.posapp import Product as PosProduct, ...
"""

from .apps import PosSoloConfig  # noqa: F401 - register AppConfig
