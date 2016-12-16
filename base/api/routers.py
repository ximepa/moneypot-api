# -*- encoding: utf-8 -*-

# from rest_framework import routers
from rest_framework_nested import routers

from .viewsets import CategoryViewSet, VItemMovementViewSet, VSerialMovementViewSet, TransactionViewSet, PlaceViewSet, \
    TransactionItemViewSet

router = routers.SimpleRouter()
router.register(r'category', CategoryViewSet)
router.register(r'place', PlaceViewSet)
router.register(r'item_movement', VItemMovementViewSet)
router.register(r'serial_movement', VSerialMovementViewSet)
router.register(r'transaction', TransactionViewSet)

transactions_router = routers.NestedSimpleRouter(router, r'transaction', lookup='transaction')
transactions_router.register(r'item', TransactionItemViewSet, base_name='transaction-items')