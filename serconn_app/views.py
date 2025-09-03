from django.shortcuts import render, get_object_or_404, redirect
from .models import ServiceProvider, ServiceCategory, Service
from django.db.models import Q
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .models import ServiceRequest

# Vistas para la sección de búsqueda y perfiles
def service_search_view(request):
    """
    Vista principal para la búsqueda de servicios.
    """
    # Obtener todas las categorías de servicio para el menú desplegable
    categories = ServiceCategory.objects.all()
    
    # Inicializar la lista de proveedores
    providers = ServiceProvider.objects.all()
    query = None
    category = None
   
    # Procesar la búsqueda por palabra clave
    if 'query' in request.GET:
        query = request.GET['query']
        # Buscar en los campos del modelo que coincidan con la palabra clave
        providers = providers.filter(
            Q(description__icontains=query) |
            Q(services__name__icontains=query)
        ).distinct()

    # Procesar el filtro por categoría
    if 'category' in request.GET and request.GET['category']:
        category = request.GET['category']
        # Asumiendo una relación ManyToMany entre ServiceProvider y ServiceCategory
        providers = providers.filter(services__category__name=category).distinct()

    context = {
        'categories': categories,
        'providers': providers,
        'query': query,
        'selected_category': category,
    }
    return render(request, 'service_search.html', context)


def provider_detail_view(request, provider_id):
    """
    Vista para mostrar el perfil detallado de un proveedor.
    """

    try:
        provider = get_object_or_404(ServiceProvider, pk=provider_id)
    except Http404:
        return render(request, '404.html')


    services_offered = Service.objects.filter(provider=provider)

    context = {
        'provider': provider,
        'services_offered': services_offered,
    }
    return render(request, 'provider_detail.html', context)

@login_required
def seeker_dashboard(request):
    service_requests = ServiceRequest.objects.filter(seeker=request.user)
    return render(request, 'seeker_dashboard.html', {'service_requests': service_requests})

@login_required
def confirm_service(request, pk):
    service_request = get_object_or_404(ServiceRequest, pk=pk)
    user = request.user

    # Seeker confirma
    if user == service_request.seeker:
        service_request.seeker_confirmed = True
    # Provider confirma
    elif hasattr(service_request, 'provider') and user == service_request.provider.user:
        service_request.provider_confirmed = True

    service_request.save()
    return redirect('seeker_dashboard')
