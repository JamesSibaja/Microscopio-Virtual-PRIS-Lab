// var geojson_list = {{ geojson_list|safe }};
// var userId = {{user_id}}
$(document).ready(function() {
    
    // var project = "{{ project.id }}";
    // optionMenu = optionNum;
    // document.getElementById("slide").value = 1; 
    var abrirModal = document.getElementById('abrirModal');
    var modal = document.getElementById('miModal');
    var cerrarModal = document.getElementById('cerrarModal');
    var chatInput = document.getElementById('chatInput');
    var cerrarModal2 = document.getElementById('cerrarModal2');
    var numMessages = -15;
    var messageUpdate = false;
    
    String.prototype.hashCode = function() {
        var hash = 0;
        for (var i = 0; i < this.length; i++) {
            var character = this.charCodeAt(i);
            hash = (hash << 5) - hash + character;
        }
        return hash;
    };

    function generarColorAleatorio(cadena) {
        var semilla = cadena.hashCode().toString();  //
        Math.seedrandom(semilla);  // Usa una librería de generación de números aleatorios con semilla

        var r = Math.floor(Math.random() * 256);
        var g = Math.floor(Math.random() * 256);
        var b = Math.floor(Math.random() * 256);

        return `rgb(${r}, ${g}, ${b})`;
    }

    function actualizarDatos(url,option) {

        
        $.ajax({
        
            url: url , // Ruta configurada en urls.py
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                
                var listaActualizada = generarHTMLLista(data,option);
                $('#datos_actualizados').html(listaActualizada);                
                scrollToBottom();
                if(messageUpdate){
                    messageUpdate = false;
                }
            },
            error: function (error) {
                alert(' error');
                console.log(error);
            }
        });
    
    }
    function generarHTMLLista(data,option) {
        html='';
        switch(option) {
        case 'placas':
            if (data.name.length){ 
                for (var i = 0; i < data.name.length; i++) {
                    html += '<div style="position: relative; float: left;left: 2%; width: 96%">'+
                                '<div style="padding: 2%; box-shadow: 1px 1px 3px rgb(100, 99, 99);border-radius:10px;background-color:rgb(255, 255, 255);width: 100%">'+
                                '<h3 style="text-align: center;">'+data.name[i]+'</h3>'+
                                '<button style="width:100%"class="btn btn-outline-info js-tooltip" type="submit" onclick="location.href='+"'/projectDetail/"+project+"/1/"+data.id[i]+"'"+'"">Abrir</button>\n'+
                                // '<button class="btn btn-outline-info js-tooltip" type="submit"  onclick="location.href='+"'/projectSlideDetail/"+data.id[i]+"'"+'"">Detalles</button>\n'+
                                // '<button class="btn btn-outline-danger js-tooltip" type="submit"  onclick="location.href='+"'/projectDetail/23/"+data.id[i]+"'"+'"">Eliminar</button>'+
                                '</div>'+
                                '</div>'+
                                '<div style="float:left;height:1%;width:100%"></div>';
                    
                }
            }else{
                html += '<div style="position: relative; float: left;left: 2%; width: 90%;padding: 5%;">'+
                    '<h4> No se encontraron láminas virtules </h4>'+
                    '</div>';
            }
            break;
        case 'catalogo':
            if (data.name.length){ 
                for (var i = 0; i < data.name.length; i++) {
                    html += '<div style="position: relative; left: 8%;float: left;padding: 2%;width: 84%">'+
                                   
                                    '<div class="botonImagen" style="box-shadow: 1px 1px 10px rgb(100, 99, 99);width: 96%;padding-bottom: 65%;position: relative; float: left;left: 2%;">' +
                                        '<img  type="submit" onclick="location.href='+"'/projectDetail/"+project+"/2/"+data.id[i]+"'"+' "style="object-fit: cover;width: 100%;height: 100%;position: absolute;" src="'+data.image[i]+'" >'+ 
                                        '<div class="text-overlay">'+
                                            '<h4>'+data.name[i]+'</h4>'+
                                        '</div> '+
                                        '</div >' +
                                        
                                        // '<div style="padding: 2%;width: 40%;overflow-y: scroll;position: absolute;height:60%;right:5%;">' +
                                        //     '<h5 style="ptext-align: center">'+data.description[i]+'</h5>'+
                                        // '</div >' +
                                                        // '<div style="float:left;width:100%;padding:2%">'+
                                                        //     '<button style="width: 100%;"class="btn btn-outline-info js-tooltip" type="submit" onclick="location.href='+"'/projectDetail/"+project+"/2/"+data.id[i]+"'"+'"">Ver</button>\n'+
                                                        //     // '<button style="width: 49%;"class="btn btn-outline-primary js-tooltip" type="submit" onclick="location.href='+"'/projectDetail/"+project+"/2/"+data.id[i]+"'"+'"">Crear Lámina</button>'+
                                                        // '</div >' +
                                '</div >';
                                // '<button class="btn btn-outline-info js-tooltip" type="submit"  onclick="location.href='+"'/projectSlideDetail/"+data.id[i]+"'"+'"">Detalles</button>\n'+
                                // '<button class="btn btn-outline-danger js-tooltip" type="submit"  onclick="location.href='+"'/projectDetail/23/"+data.id[i]+"'"+'"">Eliminar</button>'+
                                                  
                }
            }else{
                html += '<div style="position: relative; float: left;left: 2%; width: 90%;padding: 5%;">'+
                    '<h4> No se encontraron láminas virtules en el catalogo</h4>'+
                    '</div>';
            }
            break;
        case 'chat':
            if (data.meessages.length){ 
                let names = data.name
                let messages = data.meessages
                let dates = data.date
                let usersId = data.userId
                let lastDate = 0;
                messages = messages.slice(numMessages);
                names = names.slice(numMessages);
                dates = dates.slice(numMessages);
                usersId = usersId.slice(numMessages);
                for (var i = 0; i < messages.length ; i++) {
                    if(usersId[i] != userId){
                        html += '<div style=" position: relative; left: 4%;float: left;padding: 2%; box-shadow: 1px 1px 3px rgb(100, 99, 99);border-radius:0px 10px 10px 10px;background-color:rgb(255, 255, 255);min-width:35%;max-width:80%">'+
                                '<p style="margin-bottom: 0px;font-size: 15px;color:'+generarColorAleatorio(names[i])+'"><b>'+names[i]+':</b></p>'+
                                messages[i]+
                                '<p style="margin-bottom: 0px;font-size: 12px;color:rgb(100,100,100);text-align: right; ">'+dates[i][1]+'</p>'+
                                '</div >' +
                                
                                '<div style="float:left;height:10px;width:100%"></div>';                    
                    }else{
                        html += '<div style="position: relative; right: 4%;float: right;padding: 2%; box-shadow: 1px 1px 3px rgb(100, 99, 99);border-radius:10px 0px 10px 10px;background-color:rgb(240, 240, 255);min-width:35%;max-width:80%">'+
                                
                                messages[i]+
                                '<p style="margin-bottom: 0px;font-size: 12px;color:rgb(100,100,100);text-align: right; ">'+dates[i][1]+'</p>'+
                                '</div >' +
                                
                                '<div style="float:left;height:10px;width:100%"></div>'; 

                    }
                    if (dates[i][0] != lastDate && i != 0) {
                        html += '<div style="position: relative;float:left;height:45px; width: 100%;">' +
                                    '<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); height: 30px; width: 100px; border-radius: 5px; background-color: rgba(220, 220, 220, 0.6); text-align: center;">' +
                                        '<p style="margin: 0;">' + dates[i][0] + '</p>' +
                                    '</div>' +
                                '</div>';
                        
                    }
                    lastDate = dates[i][0];
                }
                
            }else{
                html += '<div style="position: relative; float: left;left: 2%; width: 90%;padding: 5%;">'+
                    '<h4> No se encontraron mensajes relacionados</h4>'+
                    '</div>';
            }
                
            break;
        default:
            if (data.name){
                for (var i = 0; i < data.name.length; i++) {
                    html += '<div style="position: relative; float: left;left: 2%; width: 96%">'+
                                '<div style="padding: 2%; box-shadow: 1px 1px 3px rgb(100, 99, 99);border-radius:10px;background-color:rgb(255, 255, 255);width: 100%">'+
                                '<h3 style="text-align: center;"> Usuario: '+data.name[i]+'</h3>'+
                                '<h4 style="text-align: center;"> Nombre: '+data.fullname[i]+'</h4>'+
                                '<button style="width:100%" class="btn btn-outline-info js-tooltip" type="submit" onclick="location.href='+"'/newProjectInvitedUser/"+project+"/"+data.id[i]+"'"+'"">Añadir como colaborador</button>\n'+
                                // '<button class="btn btn-outline-info js-tooltip" type="submit"  onclick="location.href='+"'/projectSlideDetail/"+data.id[i]+"'"+'"">Detalles</button>\n'+
                                // '<button class="btn btn-outline-danger js-tooltip" type="submit"  onclick="location.href='+"'/projectDetail/23/"+data.id[i]+"'"+'"">Eliminar</button>'+
                                '</div>'+
                                '</div>'+
                                '<div style="float:left;height:1%;width:100%"></div>';
                    
                }  
                if(data.name.length==0){
                    html += '<div style="position: relative; float: left;left: 2%; width: 90%;padding: 5%;">'+
                    '<h4> No se encontraron usuarios con los terminos de busqueda. Para invitar a un nuevo colaborador, ingrese un usuario valido en el buscardor</h4>'+
                    '</div>';
                } 
            } else{
                if(data.nameInvite){
                    for (var i = 0; i < data.nameInvite.length; i++) {
                        html += '<div style="position: relative; float: left;left: 2%; width: 96%">'+
                                    '<div style="padding: 2%; box-shadow: 1px 1px 3px rgb(100, 99, 99);border-radius:10px;background-color:rgb(255, 255, 255);width: 100%">'+
                                    '<h3 style="text-align: center;"> Usuario: '+data.nameInvite[i]+'</h3>'+
                                    '<h4 style="text-align: center;"> Nombre: '+data.fullnameInvite[i]+'</h4>'+
                                    '<h4 style="color:green;text-align: center;"> Invitación Enviada</h4>'+
                                    '</div>'+
                                    '</div>'+
                                    '<div style="float:left;height:1%;width:100%"></div>';
                        
                    } 
                }
                html += '<div style="position: relative; float: left;left: 2%; width: 90%;padding: 5%;">'+
                    '<h4> Para invitar a un nuevo colaborador, ingrese un usuario valido en el buscardor</h4>'+
                    '</div>';
            }
            html +='</div>';
            break;
        } 
        
        return html;
    }

    // Agrega el evento para actualizar los datos al hacer clic en el botón
    $('#placas_btn').on('click', function() {
        //document.getElementById("make").value = true; 
        hideMenu();
        optionMenu = 1;
        chatInput.style.display = 'none';
        actualizarDatos('/datos_actualizados_placas/'+project+'/_','placas');

    });
    $('#catalogo_btn').on('click', function() {
        //document.getElementById("make").value = true; 
        chatInput.style.display = 'none';
        optionMenu = 2;
        hideMenu();
        actualizarDatos('/datos_actualizados_catalogo/'+project+'/_','catalogo');

    });
    $('#colaboradores_btn').on('click', function() {
        //document.getElementById("make").value = true; 
        optionMenu = 3;
        chatInput.style.display = 'none';
        hideMenu();
        actualizarDatos('/datos_actualizados_colaboradores/'+project+'/_','colaboradores');

    });
    $('#chat_btn').on('click', function() {
        //document.getElementById("make").value = true; 
        optionMenu = 4;
        hideMenu();

        chatInput.style.display = 'block';
        actualizarDatos('/datos_actualizados_chat/'+project+'/_','chat');
        

    });

    // function showMenu() {
    // var menu = document.getElementById("menuList");
    //     menu.style.display = "block";
    // }

    function hideMenu() {
        var menu = document.getElementById("menuList");
        menu.style.display = "none";
    }

    var menu = document.querySelector(".menu");
    var menuList = document.querySelector(".menu-list");

    menu.addEventListener("mouseover", function() {
        menuList.style.display = "block";
    });

    menu.addEventListener("mouseout", function() {
        menuList.style.display = "none";
    });

    $('#btn_buscar').on('click', function() {
        if(optionMenu<2){
            buscarInfo= document.getElementById("buscarDato").value;
            
            document.getElementById("buscarDato").value = '';
            actualizarDatos('/datos_actualizados_placas/'+project+'/'+buscarInfo,'placas');
        }
        if(optionMenu==2){
            
            buscarInfo= document.getElementById("buscarDato").value;
            document.getElementById("buscarDato").value = '';
            actualizarDatos('/datos_actualizados_catalogo/'+project+'/'+buscarInfo,'catalogo');
        }
        if(optionMenu==3){
            buscarInfo= document.getElementById("buscarDato").value;

            document.getElementById("buscarDato").value = '';
            actualizarDatos('/datos_actualizados_colaboradores/'+project+'/'+buscarInfo,'colaboradores');
        }
        if(optionMenu==4){
            buscarInfo= document.getElementById("buscarDato").value;

            document.getElementById("buscarDato").value = '';
            actualizarDatos('/datos_actualizados_chat/'+project+'/'+buscarInfo,'chat');
        }
    });
  

    if(optionNum==0){

        opcionClick('Láminas Virtuales')
        actualizarDatos('/datos_actualizados_placas/'+project+'/_','placas');
    }
    if(optionNum==1){
        opcionClick('Láminas Virtuales')
        actualizarDatos('/datos_actualizados_placas/'+project+'/_','placas');
    }
    if(optionNum==2){
        opcionClick('Catálogo')
        actualizarDatos('/datos_actualizados_catalogo/'+project+'/_','catalogo');
    }
    if(optionNum==3){
        opcionClick('Colaboradores')
        actualizarDatos('/datos_actualizados_colaboradores/'+project+'/_','colaboradores');

    }
    if(optionNum==4){
        opcionClick('Chat')
        numMessages = -15;
        actualizarDatos('/datos_actualizados_chat/'+project+'/_','chat');

    }
    

    if(mapSlide!='None'){
    //window.alert(JSON.stringify(datosGeoJSON));
        var polygon = [null];
        var polyLine = [null];
        var polygonPoints = [];
        var polygonDraw  = false;
        var numPoly = 0;
        

        var dataMap = initializeMap(slideMap);
        var map = dataMap[0];  

        // var imageBounds = L.latLngBounds(
        //     L.latLng(-62, -115),  // Coordenadas del borde inferior izquierdo
        //     L.latLng(62, 115)   // Coordenadas del borde superior derecho
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
        // var miniMap = new L.Control.MiniMap(
        //     L.tileLayer(slide_url_format),
        //     { toggleDisplay: true }
        // );

        // // Agrega el minimapa al mapa principal
        // miniMap.addTo(map);
            // var creditsControl = L.controlCredits({
            //     imageurl: '/media/2.jpg',
            //     tooltip: 'Made by PrisLab',
            //     width: '45px',
            //     height: '45px',

            //     imagealt: "Créditos personalizados alternativos",
            //     expandcontent: 'Interactive mapping<br/>by <a href="https://pris.eie.ucr.ac.cr/" target="_blank">GreenInfo Network</a>',
            // }).addTo(map);
        if(optionNum==1){
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
        // map.on('zoomstart', function () {
        //     map.setMaxBounds(null);
        // });

        // // Restablecer los límites cuando finaliza el zoom
        // map.on('zoomend', function () {
        //     map.setMaxBounds(imageBounds);
        // });
    }
    const chatSocket = new WebSocket(
    "ws://"+host+":80/ws/projects/"+project+"/"
    );
    const messageList = document.getElementById('datos_actualizados');
    const messageInput = document.getElementById('message-input');

    function scrollToBottom() {
        if(!messageUpdate ){
            messageList.scrollTop =  messageList.scrollHeight;
        }
    }

    messageList.addEventListener('scroll', function() {
        // Verifica si el usuario ha desplazado hasta la parte superior del panel
        
        if (messageList.scrollTop === 0 && optionMenu==4) {
            // Incrementa la cantidad de mensajes a mostrar (por ejemplo, de 30 a 60)
            console.log(60);
            numMessages = numMessages-15;
            messageUpdate = true;
            actualizarDatos('/datos_actualizados_chat/'+project+'/_','chat');
            
            // Vuelve a llamar a la función que renderiza los mensajes con la nueva cantidad de mensajes
            
        }
    });

    chatSocket.onmessage = (event) => {
        const messageData = JSON.parse(event.data);
        const messageItem = document.createElement('li');
        // messageItem.innerText = `${messageData.user}: ${messageData.message}`;
        if(`${messageData.user}` != userId){
            messageItem.innerHTML = '<div style=" position: relative; left: 4%;float: left;padding: 2%; box-shadow: 1px 1px 3px rgb(100, 99, 99);border-radius:0px 10px 10px 10px;background-color:rgb(255, 255, 255);min-width:35%;max-width:80%">'+
                    '<p style="margin-bottom: 0px;font-size: 15px;color:'+generarColorAleatorio(`${messageData.username}`)+'"><b>'+`${messageData.username}`+':</b></p>'+
                    `${messageData.message}`+
                    '<p style="margin-bottom: 0px;font-size: 12px;color:rgb(100,100,100);text-align: right; ">'+`${messageData.fecha}`+'</p>'+
                    '</div >' +
                    '<div style="float:left;height:10px;width:100%"></div>';                    
        }else{
            messageItem.innerHTML = '<div style="position: relative; right: 4%;float: right;padding: 2%; box-shadow: 1px 1px 3px rgb(100, 99, 99);border-radius:10px 0px 10px 10px;background-color:rgb(240, 240, 255);min-width:35%;max-width:80%">'+
                    
                `${messageData.message}`+
                    '<p style="margin-bottom: 0px;font-size: 12px;color:rgb(100,100,100);text-align: right; ">'+`${messageData.fecha}`+'</p>'+
                    '</div >' +
                    '<div style="float:left;height:10px;width:100%"></div>'; 

        }
        console.log(messageItem);
        messageList.appendChild(messageItem);
        numMessages=numMessages-1;
        scrollToBottom();
    };

    document.getElementById('message-form').addEventListener('submit', (event) => {
        event.preventDefault();
        const message = messageInput.value;
        const user = userId;
        const newMessage = JSON.stringify({ message,user });
        newMessage.user = user;
        console.log(newMessage);
        chatSocket.send(JSON.stringify({ message,user }));
        messageInput.value = '';
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
   
});  
function opcionClick(opcion) {
    var menuBtn = document.getElementById('menuBt');
    menuBtn.textContent = opcion;
}