from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from .models import Tjuegos
# Create your views here.
def pagina_de_prueba(request):
	return HttpResponse("<h1>Hola caracola</h1>");

def devolver_juegos(request):
	lista = Tjuegos.objects.all()
	respuesta_final = []
	for fila_sql in lista:
		diccionario = {} 
		diccionario['id'] = fila_sql.id
		diccionario['nombre'] = fila_sql.nombre
		diccionario['precio'] = fila_sql.precio
		diccionario['genero'] = fila_sql.genero
		respuesta_final.append(diccionario)
	return JsonResponse(respuesta_final, safe=False);

