// var geojson_list = {{ geojson_list|safe }};
    $(document).ready(function() {
        
        // var project = "{{ project.id }}";
        // optionMenu = "{{optionNum}}";
        // var ver = 0;
        // var cat = 1;
        // document.getElementById("slide").value = 1; 
        if(mapSlide!='None'){
            var dataMap = initializeMap(slideMap);
            var map = dataMap[0];  
        }
        var abrirModal = document.getElementById('abrirModal');
        var modal = document.getElementById('miModal');
        var cerrarModal = document.getElementById('cerrarModal');
        var cerrarModal2 = document.getElementById('cerrarModal2');
        
        // String.prototype.hashCode = function() {
        //     var hash = 0;
        //     for (var i = 0; i < this.length; i++) {
        //         var character = this.charCodeAt(i);
        //         hash = (hash << 5) - hash + character;
        //     }
        //     return hash;
        // };

        // function generarColorAleatorio(cadena) {
        //     var semilla = cadena.hashCode().toString();  //
        //     Math.seedrandom(semilla);  // Usa una librería de generación de números aleatorios con semilla

        //     var r = Math.floor(Math.random() * 256);
        //     var g = Math.floor(Math.random() * 256);
        //     var b = Math.floor(Math.random() * 256);

        //     return `rgb(${r}, ${g}, ${b})`;
        // }

        
    
        // Agrega el evento para actualizar los datos al hacer clic en el botón
        $('#placas_btn').on('click', function() {
            //document.getElementById("make").value = true; 
            hideMenu()
            optionMenu = 1;
            actualizarDatos('/datos_actualizados_placas/'+project+'/_','placas');

        });

        // function showMenu() {
        // var menu = document.getElementById("menuList");
        //     menu.style.display = "block";
        // }


    

        if("{{optionNum}}"==0){

            opcionClick('Láminas Virtuales')
            actualizarDatos('/datos_actualizados_placas/'+project+'/_','placas');
        }
       
        // var i = "{{mapSlide.slide.path}}";
        // var h = "{{mapSlide.slide.zoomI}}";
        // var j = "{{mapSlide.slide.zoomM}}";

        // var slide_url_format = "/media/slides/"+i+"/{z}/{y}/{x}.jpg";

        
        // //window.alert(JSON.stringify(datosGeoJSON));
        // var polygon = [null];
        // var polyLine = [null];
        // var polygonPoints = [];
        // var polygonDraw  = false;
        // var numPoly = 0;
        
        // var imageBounds = L.latLngBounds(
        // L.latLng(-62, -115),  // Coordenadas del borde inferior izquierdo
        // L.latLng(62, 115)   // Coordenadas del borde superior derecho
        // );

        // var map = L.map('map', {
        //     center: [0,0],
        //     zoom: h,
        //     animate: true
        // });
        // var layer =  L.tileLayer(slide_url_format, {
        //     minZoom:2,
        //     noWrap: true,
        //     keepBuffer:8,
        //     maxZoom:j
        // }).addTo(map);
        // map.attributionControl.setPrefix(false);
        if( optionNum ==1){
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
        }
        //var capaGeoJSON = L.geoJSON(datosGeoJSON).addTo(map);
        
        // var pos = map.getBounds();
        // var pos2 = pos.getNorthWest();
        // var pos11 = pos2.lat;
        // var pos12 = pos2.lng;
        // var pos3 = pos.getSouthEast()
        // var pos21 = pos3.lat;
        // var pos22 = pos3.lng;
        // var popup = L.popup();  
    
        
        // var mapContainer = map.getContainer();
        // mapContainer.addEventListener('mouseenter', function() {
        //     if(polygonDraw){
        //         mapContainer.classList.add('custom-cursor');
        //     }
        // });
        // mapContainer.addEventListener('mouseleave', function() {
        //     if(polygonDraw){
        //         mapContainer.classList.remove('custom-cursor');
        //     }
        // });

                  

     
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
    }
    );  
    // <html += '<td><i style="position: relative;right:1%" onclick="location.href='+"'/deleteProjectUser/{{project.id}}/"+data.id[i]+"'"+'"" class="material-icons">person_remove</i></td>';
    //     