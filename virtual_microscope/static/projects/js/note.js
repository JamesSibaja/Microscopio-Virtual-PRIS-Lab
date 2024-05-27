$(document).ready(function() {
         
    var abrirModal = document.getElementById('abrirModal');
    var modal = document.getElementById('miModal');
    var modal2 = document.getElementById('miModal2');
    var cerrarModal = document.getElementById('cerrarModal');
    var cerrarModal2 = document.getElementById('cerrarModal2');
    var cerrarModal3 = document.getElementById('cerrarModal3');
    var cerrarModal4 = document.getElementById('cerrarModal4');
    var contenedor = document.getElementById('menuPrincipal');
    var pos11 = document.getElementById('pos11');
    var ps12 = document.getElementById('pos12');
    var pos21 = document.getElementById('pos21');
    var pos22 = document.getElementById('pos22');
    var dataMap = initializeMap(slideMap,'l','m','d','f','s','c','v');
    var drawnItems = dataMap[1];
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
    cerrarModal3.addEventListener('click', function() {
        modal2.style.display = 'none';
    });

    cerrarModal4.addEventListener('click', function() {
        modal2.style.display = 'none';
    });

    window.addEventListener('click', function(event) {
    if (event.target == modal) {
        modal.style.display = 'none';
    }
    });

    function cerrar(){
        modal2.style.display = 'none';
    };

    // var i = "{{projectSlide.slide.path}}";
    // var h = "{{projectSlide.slide.zoomI}}";
    // var j = "{{projectSlide.slide.zoomM}}";

    var notasMenu = document.getElementById('notasMenu');

    if (notasMenu.scrollHeight > notasMenu.clientHeight) {
        notasMenu.classList.add('has-overflow');
    }

    
    var save = document.getElementById('custom-button');
    save.addEventListener('click', function() {
        var geojsonFeatures = [];
        drawnItems.eachLayer(function(layer) {
            var feature = {
                type: "Feature",
                geometry: layer.toGeoJSON().geometry,
                properties: {
                    color: layer.options.color || "#3388ff", 
                    tooltipMessage: name_slide,
                    clickMessage: description_slide
                }
            };
            
            if (layer instanceof L.CircleMarker && !(layer instanceof L.Circle)) {
                feature.geometry.type = "Point";
                feature.properties.radius = -1;
            } else if (layer instanceof L.Circle) {
                feature.geometry.type = "Point";
                feature.properties.radius = layer.getRadius();
            }
            
            geojsonFeatures.push(feature);
        });

        var geojson = {
            type: "FeatureCollection",
            features: geojsonFeatures
        };

        document.getElementById("geojson_data").value = JSON.stringify(geojson); 
        modal2.style.display = 'block';
    });
    
    
    // save.addEventListener('click', function() {
    //     var geojsonFeatures = [];
    //     drawnItems.eachLayer(function(layer) {
    //         var feature = {
    //             type: "Feature",
    //             geometry: layer.toGeoJSON().geometry,
    //             properties: {
    //                 color: layer.options.color || "#3388ff", 
    //                 tooltipMessage: "{{note.name}}",
    //                 clickMessage: "{{note.description}}"
    //             }
    //         };
            
    //         if (layer instanceof L.CircleMarker && !(layer instanceof L.Circle)) {
    //             feature.geometry.type = "Point";
    //             feature.properties.radius = -1;
    //         } else if (layer instanceof L.Circle) {
    //             feature.geometry.type = "Point";
    //             feature.properties.radius = layer.getRadius();
    //         }
            
    //         geojsonFeatures.push(feature);
    //     });

    //     var geojson = {
    //         type: "FeatureCollection",
    //         features: geojsonFeatures
    //     };

    //     document.getElementById("geojson_data").value = JSON.stringify(geojson); 
    //     modal2.style.display = 'block';
    // });

    console.log(geojson_list.length);
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
            }).addTo(map);
    }
    

    var pos = map.getBounds();

    // pos11,ps12,pos21,pos22

    var popup = L.popup();    
    function onMapClick(e) {
    popup
        .openOn(map);
    
    }   
    var expandBtn = document.getElementById('botonDesplegar');
    let isSelected = false;

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

});  