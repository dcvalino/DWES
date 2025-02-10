import json

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import UsuarioPersonalizado, Eventos, Comentarios, Reservas
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsOrganizador, IsParticipante
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication

# Importamos las utilidades de drf-yasg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

##################################
# CRUD de eventos:

class ListarEventosView(APIView):
    """
    GET: Lista todos los eventos disponibles con filtros y paginación.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    # Definición de parámetros de query
    titulo_param = openapi.Parameter('titulo', openapi.IN_QUERY, description="Filtro por título", type=openapi.TYPE_STRING)
    fecha_param = openapi.Parameter('fecha', openapi.IN_QUERY, description="Filtro por fecha (YYYY-MM-DD)", type=openapi.TYPE_STRING)
    limite_param = openapi.Parameter('limite', openapi.IN_QUERY, description="Número de eventos por página", type=openapi.TYPE_INTEGER, default=5)
    pagina_param = openapi.Parameter('pagina', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER, default=1)

    @swagger_auto_schema(
        manual_parameters=[titulo_param, fecha_param, limite_param, pagina_param],
        responses={200: openapi.Response('Listado de eventos', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                'total_pages': openapi.Schema(type=openapi.TYPE_INTEGER),
                'current_page': openapi.Schema(type=openapi.TYPE_INTEGER),
                'next': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                'previous': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                'results': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'titulo': openapi.Schema(type=openapi.TYPE_STRING),
                            'descripcion': openapi.Schema(type=openapi.TYPE_STRING),
                            'fecha': openapi.Schema(type=openapi.TYPE_STRING),
                            'capacidad': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'url': openapi.Schema(type=openapi.TYPE_STRING),
                            'organizador': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'nombre': openapi.Schema(type=openapi.TYPE_STRING),
                                    'email': openapi.Schema(type=openapi.TYPE_STRING)
                                }
                            )
                        }
                    )
                )
            }
        ))}
    )
    def get(self, request):
        titulo_filtro = request.query_params.get("titulo", "")
        fecha_filtro = request.query_params.get("fecha", "")
        limite = int(request.query_params.get("limite", 5))
        pagina = int(request.query_params.get("pagina", 1))

        eventos = Eventos.objects.all()
        if titulo_filtro:
            eventos = eventos.filter(titulo__icontains=titulo_filtro)
        if fecha_filtro:
            eventos = eventos.filter(fecha=fecha_filtro)
        eventos = eventos.order_by('fecha')

        paginator = Paginator(eventos, limite)
        try:
            eventos_pagina = paginator.page(pagina)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        results = []
        for e in eventos_pagina:
            results.append({
                "id": e.id,
                "titulo": e.titulo,
                "descripcion": e.descripcion,
                "fecha": e.fecha.strftime("%Y-%m-%d") if e.fecha else "",
                "capacidad": e.capacidad,
                "url": e.url,
                "organizador": {
                    "id": e.organizador.id,
                    "nombre": e.organizador.nombre,
                    "email": e.organizador.email,
                } if e.organizador else None
            })

        data = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": pagina,
            "next": pagina + 1 if eventos_pagina.has_next() else None,
            "previous": pagina - 1 if eventos_pagina.has_previous() else None,
            "results": results,
        }
        return Response(data, status=status.HTTP_200_OK)


class CrearEventoView(APIView):
    """
    POST: Crea un evento. (Acceso solo para organizadores)
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsOrganizador]

    # Esquema del request para crear un evento
    evento_request = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['titulo', 'descripcion', 'fecha', 'capacidad', 'url'],
        properties={
            'titulo': openapi.Schema(type=openapi.TYPE_STRING, description="Título del evento"),
            'descripcion': openapi.Schema(type=openapi.TYPE_STRING, description="Descripción del evento"),
            'fecha': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha del evento (YYYY-MM-DD)"),
            'capacidad': openapi.Schema(type=openapi.TYPE_INTEGER, description="Capacidad del evento"),
            'url': openapi.Schema(type=openapi.TYPE_STRING, description="URL relacionada al evento")
        }
    )

    @swagger_auto_schema(
        request_body=evento_request,
        responses={201: openapi.Response('Evento creado', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'mensaje': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ))}
    )
    def post(self, request):
        data = request.data
        organizador = request.user  # Se asume que el usuario autenticado es el organizador
        evento = Eventos.objects.create(
            titulo=data.get("titulo", ""),
            descripcion=data.get("descripcion", ""),
            fecha=data.get("fecha"),
            capacidad=data.get("capacidad", 0),
            url=data.get("url", ""),
            organizador=organizador,
        )
        return Response({"id": evento.id, "mensaje": "Evento creado"}, status=status.HTTP_201_CREATED)


class ActualizarEventoView(APIView):
    """
    PUT/PATCH: Actualiza un evento. (Acceso solo para organizadores)
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsOrganizador]

    evento_update_request = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'titulo': openapi.Schema(type=openapi.TYPE_STRING, description="Título del evento"),
            'descripcion': openapi.Schema(type=openapi.TYPE_STRING, description="Descripción del evento"),
            'fecha': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha del evento (YYYY-MM-DD)"),
            'capacidad': openapi.Schema(type=openapi.TYPE_INTEGER, description="Capacidad del evento"),
            'url': openapi.Schema(type=openapi.TYPE_STRING, description="URL relacionada al evento"),
            'organizador': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID del organizador (opcional)")
        }
    )

    @swagger_auto_schema(
        request_body=evento_update_request,
        responses={200: openapi.Response('Evento actualizado', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'mensaje': openapi.Schema(type=openapi.TYPE_STRING)}
        ))}
    )
    def put(self, request, id):
        data = request.data
        evento = get_object_or_404(Eventos, id=id)
        evento.titulo = data.get("titulo", evento.titulo)
        evento.descripcion = data.get("descripcion", evento.descripcion)
        evento.fecha = data.get("fecha", evento.fecha)
        evento.capacidad = data.get("capacidad", evento.capacidad)
        evento.url = data.get("url", evento.url)
        if "organizador" in data:
            evento.organizador = get_object_or_404(UsuarioPersonalizado, id=data.get("organizador"))
        evento.save()
        return Response({"mensaje": "Evento actualizado"}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=evento_update_request,
        responses={200: openapi.Response('Evento actualizado', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'mensaje': openapi.Schema(type=openapi.TYPE_STRING)}
        ))}
    )
    def patch(self, request, id):
        return self.put(request, id)


class BorrarEventoView(APIView):
    """
    DELETE: Elimina un evento. (Acceso solo para organizadores)
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsOrganizador]

    @swagger_auto_schema(
        responses={200: openapi.Response('Evento eliminado', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'mensaje': openapi.Schema(type=openapi.TYPE_STRING)}
        ))}
    )
    def delete(self, request, id):
        evento = get_object_or_404(Eventos, id=id)
        evento.delete()
        return Response({"mensaje": "Evento eliminado"}, status=status.HTTP_200_OK)

##################################
# Gestión de reservas:

class ListarReservasView(APIView):
    """
    GET: Lista las reservas de un evento.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description="ID del evento", type=openapi.TYPE_INTEGER)
        ],
        responses={200: openapi.Response('Listado de reservas', schema=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'usuario': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'evento': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'entradas_reservadas': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'estado': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ))}
    )
    def get(self, request, id):
        evento = get_object_or_404(Eventos, id=id)
        reservas = Reservas.objects.filter(evento=evento)
        data = []
        for reserva in reservas:
            data.append({
                "id": reserva.id,
                "usuario": reserva.usuario.id if reserva.usuario else None,
                "evento": reserva.evento.id,
                "entradas_reservadas": reserva.entradas_reservadas,
                "estado": reserva.estado,
            })
        return Response(data, status=status.HTTP_200_OK)


class CrearReservaView(APIView):
    """
    POST: Crea una reserva. (Acceso solo para participantes)
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsParticipante]

    reserva_request = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['usuario', 'evento', 'entradas_reservadas', 'estado'],
        properties={
            'usuario': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID del usuario"),
            'evento': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID del evento"),
            'entradas_reservadas': openapi.Schema(type=openapi.TYPE_INTEGER, description="Número de entradas reservadas"),
            'estado': openapi.Schema(type=openapi.TYPE_STRING, description="Estado de la reserva")
        }
    )

    @swagger_auto_schema(
        request_body=reserva_request,
        responses={201: openapi.Response('Reserva creada', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'mensaje': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ))}
    )
    def post(self, request):
        data = request.data
        usuario = get_object_or_404(UsuarioPersonalizado, id=data["usuario"])
        evento = get_object_or_404(Eventos, id=data["evento"])
        reserva = Reservas.objects.create(
            usuario=usuario,
            evento=evento,
            entradas_reservadas=data["entradas_reservadas"],
            estado=data["estado"],
        )
        return Response({"id": reserva.id, "mensaje": "Se ha creado la reserva"}, status=status.HTTP_201_CREATED)


class ActualizarReservaView(APIView):
    """
    PUT/PATCH: Actualiza una reserva. (Acceso solo para organizadores)
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsOrganizador]

    reserva_update_request = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'usuario': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID del usuario"),
            'evento': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID del evento"),
            'entradas_reservadas': openapi.Schema(type=openapi.TYPE_INTEGER, description="Número de entradas reservadas"),
            'estado': openapi.Schema(type=openapi.TYPE_STRING, description="Estado de la reserva")
        }
    )

    @swagger_auto_schema(
        request_body=reserva_update_request,
        responses={200: openapi.Response('Reserva actualizada', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'mensaje': openapi.Schema(type=openapi.TYPE_STRING)}
        ))}
    )
    def put(self, request, id):
        data = request.data
        reserva = get_object_or_404(Reservas, id=id)
        if "usuario" in data:
            reserva.usuario = get_object_or_404(UsuarioPersonalizado, id=data["usuario"])
        if "evento" in data:
            reserva.evento = get_object_or_404(Eventos, id=data["evento"])
        reserva.entradas_reservadas = data.get("entradas_reservadas", reserva.entradas_reservadas)
        reserva.estado = data.get("estado", reserva.estado)
        reserva.save()
        return Response({"mensaje": "Reserva actualizada"}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=reserva_update_request,
        responses={200: openapi.Response('Reserva actualizada', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'mensaje': openapi.Schema(type=openapi.TYPE_STRING)}
        ))}
    )
    def patch(self, request, id):
        return self.put(request, id)


class CancelarReservaView(APIView):
    """
    DELETE: Cancela una reserva. (Solo el titular de la reserva, participante, puede cancelarla)
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsParticipante]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description="ID de la reserva", type=openapi.TYPE_INTEGER)
        ],
        responses={200: openapi.Response('Reserva eliminada', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'mensaje': openapi.Schema(type=openapi.TYPE_STRING)}
        ))}
    )
    def delete(self, request, id):
        reserva = get_object_or_404(Reservas, id=id)
        if request.user != reserva.usuario:
            return Response({"error": "¡No eres el titular!"}, status=status.HTTP_403_FORBIDDEN)
        reserva.delete()
        return Response({"mensaje": "Reserva eliminada"}, status=status.HTTP_200_OK)

##################################
# Comentarios:

class ListarComentariosView(APIView):
    """
    GET: Lista los comentarios de un evento.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description="ID del evento", type=openapi.TYPE_INTEGER)
        ],
        responses={200: openapi.Response('Listado de comentarios', schema=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'texto': openapi.Schema(type=openapi.TYPE_STRING),
                    'FechaC': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ))}
    )
    def get(self, request, id):
        evento = get_object_or_404(Eventos, id=id)
        comentarios = Comentarios.objects.filter(evento=evento)
        data = []
        for comentario in comentarios:
            data.append({
                "id": comentario.id,
                "texto": comentario.texto,
                "FechaC": comentario.FechaC.strftime("%Y-%m-%d %H:%M:%S") if comentario.FechaC else "",
            })
        return Response(data, status=status.HTTP_200_OK)


class CrearComentarioView(APIView):
    """
    POST: Crea un comentario asociado a un evento.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    comentario_request = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['texto'],
        properties={
            'texto': openapi.Schema(type=openapi.TYPE_STRING, description="Texto del comentario")
        }
    )

    @swagger_auto_schema(
        request_body=comentario_request,
        responses={201: openapi.Response('Comentario creado', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'mensaje': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ))}
    )
    def post(self, request, id):
        evento = get_object_or_404(Eventos, id=id)
        data = request.data
        comentario = Comentarios.objects.create(
            texto=data.get("texto", ""),
            evento=evento,
        )
        return Response({"id": comentario.id, "mensaje": "Se ha creado el comentario"}, status=status.HTTP_201_CREATED)

##################################
# Usuario:

class LoginView(APIView):
    """
    POST: Realiza el login del usuario y devuelve un token de autenticación.
    """
    permission_classes = []

    login_request = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email', 'contrasenha'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description="Email del usuario"),
            'contrasenha': openapi.Schema(type=openapi.TYPE_STRING, description="Contraseña del usuario")
        }
    )

    @swagger_auto_schema(
        request_body=login_request,
        responses={
            200: openapi.Response('Login exitoso', schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'token': openapi.Schema(type=openapi.TYPE_STRING),
                    'mensaje': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )),
            400: "Credenciales inválidas."
        }
    )
    def post(self, request):
        data = request.data
        email = data.get("email")
        contrasenha = data.get("contrasenha")

        if not email or not contrasenha:
            return Response({"error": "Faltan datos requeridos."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            usuario = UsuarioPersonalizado.objects.get(email=email)
        except UsuarioPersonalizado.DoesNotExist:
            return Response({"error": "Credenciales inválidas."}, status=status.HTTP_400_BAD_REQUEST)

        if usuario.contrasenha != contrasenha:
            return Response({"error": "Credenciales inválidas."}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener o crear el token
        token, created = Token.objects.get_or_create(user=usuario)

        return Response({
            "token": token.key,
            "mensaje": "Inicio de sesión exitoso."
        }, status=status.HTTP_200_OK)


class RegisterView(APIView):
    """
    POST: Registra un nuevo usuario.
    """
    permission_classes = []

    register_request = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['nombre', 'email', 'contrasenha', 'tipo'],
        properties={
            'nombre': openapi.Schema(type=openapi.TYPE_STRING, description="Nombre del usuario"),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description="Email del usuario"),
            'contrasenha': openapi.Schema(type=openapi.TYPE_STRING, description="Contraseña del usuario"),
            'tipo': openapi.Schema(type=openapi.TYPE_STRING, description="Tipo de usuario (organizador, asistente, etc.)"),
            'biografia': openapi.Schema(type=openapi.TYPE_STRING, description="Biografía (opcional)")
        }
    )

    @swagger_auto_schema(
        request_body=register_request,
        responses={
            201: openapi.Response('Usuario registrado', schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'mensaje': openapi.Schema(type=openapi.TYPE_STRING)}
            )),
            400: "Faltan datos requeridos o el email ya está registrado."
        }
    )
    def post(self, request):
        data = request.data
        nombre = data.get("nombre")
        email = data.get("email")
        contrasenha = data.get("contrasenha")
        tipo = data.get("tipo")
        biografia = data.get("biografia", "")

        if not all([nombre, email, contrasenha, tipo]):
            return Response({"error": "Faltan datos requeridos."}, status=status.HTTP_400_BAD_REQUEST)
        if UsuarioPersonalizado.objects.filter(email=email).exists():
            return Response({"error": "El email ya está registrado."}, status=status.HTTP_400_BAD_REQUEST)

        usuario = UsuarioPersonalizado.objects.create(
            username=email,
            nombre=nombre,
            email=email,
            contrasenha=contrasenha,  # Se almacena en texto plano; en producción usar hash.
            tipo=tipo,
            biografia=biografia
        )
        usuario.save()
        return Response({"mensaje": "Usuario registrado correctamente."}, status=status.HTTP_201_CREATED)

