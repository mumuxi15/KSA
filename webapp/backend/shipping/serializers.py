from rest_framework import serializers
from .models import Supplier, Inventory

# class TrackSheetSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model = TrackSheet
# 		fields ='__all__'


class SupplierSerializer(serializers.ModelSerializer):
	class Meta:
		model = Supplier
		fields = ['SUPPLR','SUPPLR_NAME','EMAIL']

class InventorySerializer(serializers.ModelSerializer):
	class Meta:
		model = Inventory
		fields ='__all__'