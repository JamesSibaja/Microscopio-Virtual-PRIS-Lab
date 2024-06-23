
$(document).ready(function() {
         
    var abrirModal = document.getElementById('abrirModal');
    var modal = document.getElementById('miModal');
    var cerrarModal = document.getElementById('cerrarModal');
    var cerrarModal2 = document.getElementById('cerrarModal2');
    var contenedor = document.getElementById('menuPrincipal');
    var dataMap = initializeMap(slideMap,'l','m','d','f','s');
    var map = dataMap[0];

    
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

});  