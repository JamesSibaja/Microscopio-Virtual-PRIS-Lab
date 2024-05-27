import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'virtual_microscope.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
# from django.conf.urls.static import static

from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from projects import routing

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': URLRouter(
        # path('ws/projects/', consumers.ChatConsumer.as_asgi()),
        routing.websocket_urlpatterns,
    ),
})

# import os
# from django.core.asgi import get_asgi_application
# from uvicorn.workers import UvicornWorker
# from channels.routing import ProtocolTypeRouter, URLRouter
# from Projects import routing

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'virtual_microscope.settings')
# os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

# application = ProtocolTypeRouter({
#     'http': get_asgi_application(),
#     'websocket': URLRouter(
#         routing.websocket_urlpatterns,
#     ),
# })

# # Este bloque es opcional, pero podría ser necesario dependiendo de tu configuración
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(application, worker_cls=UvicornWorker, host='0.0.0.0', port=8765)

