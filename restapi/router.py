from api.viewsets import ProductViewSet
from  rest_framework import routers

router = routers.DefaultRouter()
router.register('products', ProductViewSet)

# url will be like this :
#   localhost:8000/api/employee/
# methods are GET , POST , PUT , DELETE