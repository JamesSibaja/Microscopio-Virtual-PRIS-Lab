// var geojson_list = {{ geojson_list|safe }};
$(document).ready(function() {
         
    var abrirModal = document.getElementById('abrirModal');
    var modal = document.getElementById('miModal');
    var cerrarModal = document.getElementById('cerrarModal');
    var cerrarModal2 = document.getElementById('cerrarModal2');
    var contenedor = document.getElementById('menuPrincipal');
    // var imprimir = document.getElementById('imprimir');
    var dataMap = initializeMap(slideMap,'l','m','d','f','s');
    var map = dataMap[0];
    // imprimir.addEventListener('click', function(event) {
    //     capturarImagen();
    // });
    
    contenedor.addEventListener('mouseenter', () => {
        map.dragging.enable(); // Desactiva la interacción de arrastre del mapa
        map.scrollWheelZoom.enable(); // Desactiva el zoom con la rueda del ratón
    });

    abrirModal.addEventListener('click', function() {
        modal.style.display = 'block';
    });

    cerrarModal.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    cerrarModal2.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    window.addEventListener('click', function(event) {
    if (event.target == modal) {
        modal.style.display = 'none';
    }
    });

    // var i = "{{projectSlide.slide.path}}";
    // var h = "{{projectSlide.slide.zoomI}}";
    // var j = "{{projectSlide.slide.zoomM}}";


    //var datosGeoJSON = JSON.parse('{% autoescape off %}{{ notes.geojson_data|escapejs }}{% endautoescape %}');

    //window.alert(datosGeoJSON);

    // var imageBounds = L.latLngBounds(
    // L.latLng(-62, -115),  // Coordenadas del borde inferior izquierdo
    // L.latLng(62, 115)   // Coordenadas del borde superior derecho
    // );
    
    // var slide_url_format = "/media/slides/"+i+"/{z}/{y}/{x}.jpg";
    
    // var map = L.map('map', {
    //     center: [0,0],
    //     zoom: h,
    //     animate: true,
    //     fullscreenControl: true,
    //     fullscreenControlOptions: {
    //         position: 'bottomright'
    //     }
    // });

    // var customZoomControl = L.control.zoom({
    //     position: 'bottomright'
    // }).addTo(map);

    
    // // Después de agregar el control de zoom personalizado,
    // // puedes eliminar el control de zoom por defecto.
    // map.removeControl(map.zoomControl);

    // var layer =  L.tileLayer(slide_url_format, {
    //     minZoom:0,
    //     noWrap: true,
    //     keepBuffer:8,
    //     maxZoom:j
    // }).addTo(map);

    // map.attributionControl.setPrefix(false);
    // var miniMap = new L.Control.MiniMap(
    //             L.tileLayer(slide_url_format),
    //             { position: 'bottomleft', toggleDisplay: true }
    //         );

    //         // Agrega el minimapa al mapa principal
    // miniMap.addTo(map);
    
    // L.control.bigImage({
    //     position: 'bottomright',
    //     title: 'Obtener imagen',
    //     printControlLabel:'📷',
    //     printControlClasses: ['custom-big-image-button'],
    //     minScale:1,
    //     maxScale:1,
    //     inputTitle:'Escala de foto',

    //     downloadTitle:'Descargar',
    // }).addTo(map);
    // });
    

    // L.control.fullscreen({
    //     position: 'topright',  // Posición del botón (topright, topleft, bottomright, bottomleft)
    //     title: 'Pantalla completa',  // Texto que aparecerá cuando el usuario pase el cursor sobre el botón
    //     titleCancel: 'Salir de pantalla completa',  // Texto para salir de pantalla completa
    //     forceSeparateButton: true  // Mostrar un botón separado para salir de pantalla completa
    // }).addTo(map);

// printPlugin.printMap('A4Portrait', 'MyFileName');
    // i18next.init({
    //     lng: 'es', // Idioma de localización
    //     resources: {
    //         es: {
    //             translation: {
    //                 version: 'Versión', // Ejemplo de traducción
    //                 lastpoint:  '',
    //                 // ... Más traducciones aquí
                    
    //             }
    //         }
    //     }
    // });

    
    // L.control.measure({
    //     primaryLengthUnit: 'meters', // Unidad de medida principal
    //     secondaryLengthUnit: 'kilometers', // Unidad de medida secundaria
    //     primaryAreaUnit: 'sqmeters', // Unidad de área principal
    //     secondaryAreaUnit: undefined, // Deja esto como undefined para deshabilitar el cálculo de áreas
    //     // Posición del control en el mapa
    //     activeColor: '#db4a29', // Color activo para las líneas y áreas medidas
    //     completedColor: '#9b2d14', // Color completado para las líneas y áreas medidas
    //     position: 'bottomright',
    //     localization: 'es', 
    //     className: 'custom-measure-control' 
    // }).addTo(map);

    var pos = map.getBounds();

    var pos11,ps12,pos21,pos22

    var popup = L.popup();    
    function onMapClick(e) {
    popup
        .openOn(map);
    
    }   
    var expandBtn = document.getElementById('botonDesplegar');
    var notasMenu = document.getElementById('notasMenu');
    let isSelected = false;
    console.log(geojson_list[0]);
    for (var i = 0; i < geojson_list.length; i++) {
        var geojson = JSON.parse(geojson_list[i].geojson);
        console.log(geojson);
        L.geoJSON(geojson, {
            style: function (feature) {
                return { color: feature.properties.color };
            },
            pointToLayer: function (feature, latlng) {
                
                if (feature.geometry.type === "Point" && feature.properties.radius) {
                    if (feature.properties.radius < 0){
                        return L.circleMarker(latlng);  
                    }else{
                        return L.circle(latlng, feature.properties.radius, { color: feature.properties.color });
                    // Crear un circle marker si la característica es un circle marker
                    }
                } else if (feature.geometry.type === "Point") {
                    // Crear un marcador estándar si la característica es un punto
                    return L.marker(latlng);
                }
                return L.layerGroup();
            }
        }).bindTooltip(function (layer) {
                return layer.feature.properties.tooltipMessage;
            }).bindPopup(function (layer) {
                return layer.feature.properties.clickMessage;
            }).addTo(map);
    }

    expandBtn.addEventListener('click', function () {
        isSelected = !isSelected;
        if (isSelected) {
            expandBtn.textContent = 'expand_more';
        } else {
            expandBtn.textContent = 'expand_less';
        }
        if (notasMenu.style.display === 'none') {
            notasMenu.style.display = 'block';
        } else {
            notasMenu.style.display = 'none';
        }
    });
    if (notasMenu.scrollHeight > notasMenu.clientHeight) {
        notasMenu.classList.add('has-overflow');
    }
    //var geojsonLayer = L.geoJSON(datosGeoJSON).addTo(map);

    // $('#MyButton').click(function(e){
    //     // map.fitBounds(pos);
    //     pos11 = parseFloat("{{notes.xUnoPos}}".replace(',', '.'));
    //     pos12 = parseFloat("{{notes.yUnoPos}}".replace(',', '.'));
    //     pos21 = parseFloat("{{notes.xDosPos}}".replace(',', '.'));
    //     pos22 = parseFloat("{{notes.yDosPos}}".replace(',', '.'));
    //     map.fitBounds([
    //         [pos11, pos12],
    //         [pos21, pos22]
    //     ]);
    // });


    // map.on('zoomstart', function () {
    //     map.setMaxBounds(null);
    // });

    // // Restablecer los límites cuando finaliza el zoom
    // map.on('zoomend', function () {
    //     map.setMaxBounds(imageBounds);
    // });
});  